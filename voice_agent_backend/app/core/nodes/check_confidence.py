"""
Check confidence node — verifies RAG results have sufficient confidence.
Acts as the Join point for the Parallel Pipeline.
"""

import logging
from langgraph.config import get_stream_writer

from app.core.langchain_rag import has_sufficient_confidence
from app.core.graph_state import VoiceAgentState
from app.core.config import settings

logger = logging.getLogger(__name__)


def check_confidence_node(state: VoiceAgentState) -> dict:
    """
    Acts as the synchronization point for the Parallel Pipeline.
    Verifies if document retrieval had sufficient confidence AND if the 
    intent actually requires that context.
    """
    writer = get_stream_writer()
    writer({"stage": "reranking"})

    intent = state.get("intent", "GENERAL_CHAT")
    context = state.get("retrieved_context", {})
    flags = state.get("intent_flags", {"isSummary": False, "isFollowUp": False})
    is_summary = flags.get("isSummary", False)

    # If the user is just chatting (not a document query), we don't care about document scores
    if intent != "DOCUMENT_QUERY":
        logger.info(f"Intent {intent} does not require confidence check. Synchronized.")
        return {"current_stage": "reranking"}

    # Build results list for confidence check
    top_score = context.get("top_score", 0)
    results_for_check = [{"combined_score": top_score, "score": top_score}]

    confident = has_sufficient_confidence(results_for_check, is_summary)

    if not confident:
        logger.info(f"Low confidence (top_score={top_score:.3f}). Routing to early exit.")
    else:
        logger.info(f"Sufficient confidence (top_score={top_score:.3f}). Proceeding to generate.")
        # Push sources to UI as soon as we are confident
        sources = context.get("sources", [])
        if sources:
            writer({"sources": sources})

    return {
        "current_stage": "reranking",
    }


def route_after_confidence(state: VoiceAgentState) -> str:
    """
    Route after confidence check:
    - Sufficient confidence → generate_response
    - GENERAL_CHAT / IDENTITY_QUERY → handle_early_exit (or direct to generate if we want LLM to talk)
    - Insufficient confidence → handle_early_exit (no info response)
    """
    intent = state.get("intent", "GENERAL_CHAT")
    context = state.get("retrieved_context", {})
    flags = state.get("intent_flags", {"isSummary": False, "isFollowUp": False})
    is_summary = flags.get("isSummary", False)
    top_score = context.get("top_score", 0)

    # General chat and identity queries go to response generation directly
    if intent in ["GENERAL_CHAT", "IDENTITY_QUERY"]:
        return "generate_response"

    if intent == "ULTRATHINK_REASONING":
        return "ultrathink_critic"

    # If intent is doc query but no context at all, go to early exit
    if not context.get("has_context", False):
        return "handle_early_exit"

    results_for_check = [{"combined_score": top_score, "score": top_score}]
    confident = has_sufficient_confidence(results_for_check, is_summary)

    if confident:
        if state.get("intent_flags", {}).get("original_intent") == "DOCUMENT_QUERY" and intent == "ULTRATHINK_REASONING":
            return "ultrathink_critic"
        return "generate_response"
    
    return "handle_early_exit"
