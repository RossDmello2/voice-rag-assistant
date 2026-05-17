import asyncio
import re
import difflib
import logging
import numpy as np
from typing import Optional
from app.core.config import settings, get_embed_dim, SYSTEM_PROMPT_BASE, SYSTEM_PROMPT_DOCUMENT
from app.services.ollama_service import generate_embedding
from app.services.qdrant_service import search_vectors


# ── STOP WORDS (from script.js line 3585) ──────────────────────────
STOP_WORDS = {
    "the", "is", "at", "which", "on", "a", "an", "and", "are", "as",
    "be", "been", "being", "by", "for", "from", "has", "had", "have",
    "he", "her", "his", "in", "into", "it", "its", "of", "or", "our",
    "out", "than", "that", "their", "them", "then", "there", "they",
    "this", "to", "was", "we", "were", "will", "with", "you", "your",
    "do", "did", "does", "but", "not", "no", "so", "up", "me", "my",
    "she", "what", "who", "when", "where", "why", "how", "all", "each",
    "if", "more", "most", "other", "some", "very", "just", "about",
    "also", "many", "much", "tell", "give", "find", "know", "think",
    "say", "make", "go", "take", "come", "see", "look", "get", "i"
}

# ── CONCEPT EXPANSIONS (for better reach) ───────────────────────────
CONCEPT_EXPANSIONS = {
    "contact": ["phone", "email", "reach", "support", "address", "help"],
    "time": ["hours", "deadline", "duration", "schedule", "period", "when", "date"],
    "cost": ["price", "usd", "total", "fee", "payment", "amount", "cost"],
    "data": ["table", "statistics", "figures", "numbers", "percentage"]
}

ALL_KNOWN_TERMS = list(CONCEPT_EXPANSIONS.keys())


def tokenize(text: str) -> list[str]:
    """Tokenize text into meaningful words, removing stop words and single chars."""
    words = re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()
    return [w for w in words if len(w) > 1 and w not in STOP_WORDS]


def build_query_variants(query: str, flags: dict, last_retrieval: Optional[dict] = None) -> list[str]:
    """
    Generate variations of the query for expanded search reach.
    Now includes Typo-Tolerance and Deep Intelligence categories.
    """
    is_summary = flags.get("isSummary", False)
    topic_hint = flags.get("topicHint")
    if last_retrieval:
        parts = [last_retrieval.get("query",""), last_retrieval.get("resolvedQuery",""), last_retrieval.get("answer","")]
        topic_hint = " ".join(p for p in parts if p)
    
    # ── Step 1: Fuzzy Normalization (Typo Resilience) ──
    tokens = tokenize(query)
    normalized_tokens = []
    for t in tokens:
        matches = difflib.get_close_matches(t.lower(), ALL_KNOWN_TERMS, n=1, cutoff=0.75)
        if matches:
            normalized_tokens.append(matches[0])
        else:
            normalized_tokens.append(t)
    
    normalized_query = " ".join(normalized_tokens)
    query_lower = normalized_query.lower()

    variants = [query]  # Always keep original
    if normalized_query != query:
        variants.append(normalized_query)

    variants.append("exact details for " + " ".join(normalized_tokens))
    # Concept expansion
    query_lower = query.lower()
    for term, syns in CONCEPT_EXPANSIONS.items():
        if term in query_lower:
            for s in syns:
                variants.append(f"document details for {s}")

    if topic_hint:
        variants.append(query + " " + topic_hint)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for v in variants:
        v = v.strip()
        if v and v not in seen:
            seen.add(v)
            unique.append(v)
    return unique


def rerank_results(results: list[dict], query: str) -> list[dict]:
    """
    Reranks documents using hybrid BM25-lite keyword overlap + vector/RRF scores.
    Prioritizes chunks with exact entity hits and rare words.
    """
    query_tokens = tokenize(query)
    query_lower = query.lower()
    
    # Rare words identification (words not in query_tokens common set)
    # Simple IDF proxy: longer words and specific entities are more valuable
    rare_tokens = [t for t in query_tokens if len(t) > 4]

    # Improved Proper Noun detection (Case-insensitive check for user query)
    # We look for Capitalized words in the chunk that match tokens in the query
    proper_nouns_in_query = [t for t in query_tokens if len(t) > 2] # Fallback

    scored = []
    for r in results:
        payload = r.get("payload", {})
        chunk_text = payload.get("text", "")
        chunk_lower = chunk_text.lower()

        # Keyword overlap score
        match_count = sum(1 for t in query_tokens if t in chunk_lower)
        keyword_score = match_count / len(query_tokens) if query_tokens else 0
        
        # Rare word bonus (+0.10 for each rare token matched)
        rare_matches = sum(1 for t in rare_tokens if t in chunk_lower)
        rare_bonus = min(rare_matches * 0.10, 0.30)

        # Proper noun bonus (+0.10 per noun found, max 0.20)
        # We look for the exact tokens in the chunk, prioritizing ones that are capitalized in chunk
        noun_bonus = 0
        for pn in proper_nouns_in_query:
            if pn in chunk_lower:
                # If it's capitalized in the chunk, it's likely a true entity hit
                if re.search(r'\b[A-Z]' + re.escape(pn[1:]), chunk_text):
                    noun_bonus += 0.10
                else:
                    noun_bonus += 0.05
        noun_bonus = min(noun_bonus, 0.20)

        # NEW: Data & Number Boost (+0.15)
        # Promote chunks that contain dense formatting like numbers or symbols if the query asks for data
        data_boost = 0
        if any(qk in query_lower for qk in ["how much", "how many", "price", "cost", "date", "number", "figure", "table", "amount"]):
            if bool(re.search(r'\d+', chunk_text)) or "$" in chunk_text or "%" in chunk_text:
                data_boost = 0.15

        # Identity & Pattern Boost (+0.20 if matches @ or phone and query has contact intent)
        identity_boost = 0
        if any(tk in query_lower for tk in ["email", "contact", "support", "reach", "id", "address"]):
            if "@" in chunk_text or re.search(r'\d{3}[-\s]?\d{3}[-\s]?\d{4}', chunk_text):
                identity_boost = 0.20

        # Negation & Exception Boost (+0.15)
        negation_boost = 0
        negations = ["except", "excluding", "only", "must", "unless"]
        if any(neg in chunk_lower for neg in negations):
            # Prioritize chunks that contain logical limits
            negation_boost = 0.15

        # RRF integration: RRF score is typically < 1, so we scale it
        rrf_contrib = r.get("rrf_score", 0) * 15 

        vector_score = r.get("score", 0)
        
        # Scale retrieval parameters
        combined_score = (
            vector_score * 0.40
            + rrf_contrib * 0.30
            + keyword_score * 0.20
            + rare_bonus
            + noun_bonus
            + data_boost
            + identity_boost
            + negation_boost
        )
        scored.append({**r, "combined_score": combined_score})

    scored.sort(key=lambda x: x["combined_score"], reverse=True)
    return scored


def diversify_for_summary(results: list[dict], top_n: int) -> list[dict]:
    """Source+section diversity for summary queries — replicates diversifyRerankedResults()"""
    selected = []
    seen = set()
    for item in results:
        if len(selected) >= top_n:
            break
        p = item.get("payload", {})
        key = f"{p.get('source','')}|{p.get('section','')}|{p.get('page',0)}"
        if key not in seen:
            seen.add(key)
            selected.append(item)
    # Fill remaining if diversity left gaps
    for item in results:
        if len(selected) >= top_n:
            break
        if item not in selected:
            selected.append(item)
    return selected[:top_n]


def has_sufficient_confidence(results: list[dict], is_summary: bool) -> bool:
    """
    Checks if top result has sufficient combined score.
    Now accounts for RRF + rare word boosts.
    """
    if not results:
        return False
    floor = settings.SUMMARY_CONFIDENCE_FLOOR if is_summary else settings.RETRIEVAL_CONFIDENCE_FLOOR
    top_score = results[0].get("combined_score", 0)
    return top_score >= floor


def format_context(results: list[dict]) -> dict:
    """Replicates formatRetrievalResults() from script.js lines 3741-3773"""
    context_parts = []
    sources = []
    pages = []
    source_details = []

    for r in results:
        p = r.get("payload", {})
        src = p.get("source", "unknown")
        page_part = f" | Page {p['page']}" if p.get("page") else ""
        section_part = f" | Section: {p['section']}" if p.get("section") else ""
        subsection_part = f" | Subsection: {p['subsection']}" if p.get("subsection") else ""
        context_parts.append(f"[Source: {src}{page_part}{section_part}{subsection_part}]\n{p.get('text','')}")
        if src not in sources:
            sources.append(src)
        if p.get("page") and p["page"] not in pages:
            pages.append(p["page"])
        source_details.append({
            "source": src,
            "page": p.get("page", 0),
            "section": p.get("section", ""),
            "subsection": p.get("subsection", ""),
            "chunk_type": p.get("chunk_type", "")
        })

    return {
        "has_context": len(context_parts) > 0,
        "context_text": "\n---\n".join(context_parts),
        "sources": sources,
        "pages": sorted(pages),
        "source_details": source_details,
        "result_count": len(results),
        "top_score": results[0].get("combined_score", 0) if results else 0
    }


def build_contextual_prompt(user_message: str, context: dict, flags: dict, last_answer: str = "") -> str:
    """Replicates buildContextualPrompt() from script.js lines 4056-4088"""
    if not context or not context.get("has_context"):
        return user_message

    ctx_text = context["context_text"]
    is_summary = flags.get("isSummary", False)
    is_follow_up = flags.get("isFollowUp", False)

    if is_summary:
        return (
            f"Document content from the uploaded files:\n---\n{ctx_text}\n---\n\n"
            f"User request: {user_message}\n\n"
            "Instructions: Provide a structured summary. Start with the single most important finding or theme, "
            "then cover the remaining key topics one by one. Keep each point brief (1-2 sentences). "
            "Mention specific dates, numbers, and key facts. "
            "The user can ask for more detail on any specific point."
        )

    if is_follow_up and last_answer:
        return (
            f"Previous context from knowledge base:\n---\n{ctx_text}\n---\n\n"
            f"Previous answer given: {last_answer}\n\n"
            f"Follow-up question: {user_message}\n\n"
            "Instructions: Re-examine the context carefully. Verify or elaborate on the previous answer. "
            "Pay careful attention to exact dates, numbers, names, and table data."
        )

    if context.get("source_type") == "web":
        return (
            f"LATEST INFORMATION FROM THE WEB:\n---\n{ctx_text}\n---\n\n"
            f"User Research Query: {user_message}\n\n"
            "Instructions: You just searched the web for this information. Summarize the findings "
            "into a natural, conversational response (1-3 sentences). "
            "Always use a helpful and informative tone. If you're reporting news or prices, "
            "be precise but conversational. Finish with a short follow-up question."
        )

    return (
        f"Information you know:\n---\n{ctx_text}\n---\n\n"
        f"User question: {user_message}\n\n"
        "Instructions: Extract the precise answer from the information above. "
        "Pay careful attention to dates, numbers, names, qualifications, and table data. "
        "Do not include inline citations, page references, file names, or source brackets in the answer text. "
        "If the answer is truly not present in the provided information, state conversationally that you do not have that information."
    )


async def retrieve_context(
    query: str,
    collection: str,
    flags: dict,
    last_retrieval: Optional[dict] = None,
    retry_count: int = 0,
    embed_model: Optional[str] = None
) -> dict:
    """
    Full RAG retrieval pipeline — replicates retrieveContextWithRetry() from script.js.
    Steps: query variants → embed each → search Qdrant → merge → rerank → confidence check → return context
    """
    is_summary = flags.get("isSummary", False)
    fetch_k = settings.SUMMARY_TOP_K if is_summary else settings.RETRIEVAL_TOP_K
    score_threshold = settings.SCORE_THRESHOLD * (0.5 ** retry_count)  # Lower on retry

    variants = build_query_variants(query, flags, last_retrieval)

    # Determine active embedding model
    active_embed_model = embed_model or settings.EMBED_MODEL
    
    # NEW: BATCH EMBEDDING for massive speed boost
    # Send all variants in one single call to Ollama
    embeddings = await generate_embedding(variants, active_embed_model)

    # Search Qdrant for each variant (concurrently)
    all_results = await asyncio.gather(*[
        search_vectors(collection, emb, fetch_k, score_threshold)
        for emb in embeddings
    ])

    # NEW: RECIPROCAL RANK FUSION (RRF) for variants
    # Chunks that appear for multiple variants rank much higher.
    # Score = sum( 1.0 / (rank + k) )
    rrf_k = 60
    merged: dict[str, dict] = {}
    
    for result_set in all_results:
        for rank, r in enumerate(result_set, start=1):
            p = r.get("payload", {})
            key = f"{p.get('source','unknown')}::{p.get('chunk_index', 0)}"
            rrf_score = 1.0 / (rank + rrf_k)
            
            if key not in merged:
                merged[key] = {**r, "rrf_score": rrf_score, "variant_count": 1}
            else:
                merged[key]["rrf_score"] += rrf_score
                merged[key]["variant_count"] += 1
                # Keep the best raw vector score too
                if r.get("score", 0) > merged[key].get("score", 0):
                    merged[key]["score"] = r["score"]

    merged_list = list(merged.values())

    if not merged_list:
        return {"has_context": False, "context_text": "", "sources": [], "pages": [], "result_count": 0, "top_score": 0}

    # Rerank
    reranked = rerank_results(merged_list, query)
    top_n = settings.RERANK_TOP_N

    if is_summary:
        final = diversify_for_summary(reranked, settings.SUMMARY_TOP_K)
    else:
        final = reranked[:top_n]

    return format_context(final)
