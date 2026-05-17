"""
Generate response node — streams LLM tokens via get_stream_writer().
MUST be async because chat_complete() returns async generator when stream=True (Finding 2).
Uses build_contextual_prompt() when intent is DOCUMENT_QUERY (Finding 8).
"""

import re
import logging
import asyncio
from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer

from app.services.llm_router import chat_complete
from app.core.langchain_rag import build_contextual_prompt
from app.core.config import settings, SYSTEM_PROMPT_BASE, SYSTEM_PROMPT_DOCUMENT
from app.core.graph_state import VoiceAgentState

logger = logging.getLogger(__name__)


def _extract_ready_tts_chunks(buffer: str, flush_all: bool = False, is_first_chunk: bool = False) -> tuple[list[str], str]:
    """
    Split the buffered response into chunks that are safe to synthesize.
    Prefer sentence boundaries, but also flush long clauses to reduce TTS latency.
    is_first_chunk: If True, uses more aggressive splitting (35 chars) to start speech faster.
    """
    working = buffer.replace("\n", " ")
    chunks = []

    if flush_all:
        final = working.strip()
        return ([final] if final else []), ""

    while True:
        # Standard sentence boundaries
        sentence_match = re.search(r'[.!?](?:\s+|$)', working)
        if sentence_match:
            end = sentence_match.end()
            chunk = working[:end].strip()
            if chunk:
                chunks.append(chunk)
            working = working[end:].lstrip()
            is_first_chunk = False # Subsequent chunks use normal rules
            continue

        # Long clause fallback: don't wait forever for a final period.
        # Phase 1: Aggressive first-chunk splitting (35 chars) vs normal (60 chars)
        threshold = 35 if is_first_chunk else 60
        
        if len(working) >= threshold:
            # Try splitting on mid-sentence punctuation (comma, semicolon, etc.)
            # Added digit check to avoid splitting prices like $1,450
            clause_matches = list(re.finditer(r'(?<!\d)[,;:](?!\d)(?:\s+|$)', working))
            if clause_matches:
                end = clause_matches[-1].end()
                chunk = working[:end].strip()
                if chunk:
                    chunks.append(chunk)
                working = working[end:].lstrip()
                is_first_chunk = False
                continue
            
            # If no mid-sentence punctuation, try splitting on conjunctions for long strings
            if len(working) >= 75:
                conjunction_match = re.search(r'\s+(and|but|or|so|because|then)\s+', working, re.IGNORECASE)
                if conjunction_match:
                    end = conjunction_match.start()
                    chunk = working[:end].strip()
                    if chunk:
                        chunks.append(chunk)
                    working = working[end:].lstrip()
                    is_first_chunk = False
                    continue

        break

    return chunks, working

async def generate_response_node(state: VoiceAgentState) -> dict:
    """
    Stream LLM response token by token.
    MUST be async because chat_complete() returns async generator (Finding 2).
    Uses build_contextual_prompt() for DOCUMENT_QUERY intent (Finding 8).
    """
    writer = get_stream_writer()
    writer({"stage": "generating"})

    intent = state.get("intent", "GENERAL_CHAT")
    english_query = state.get("english_query", "")
    context = state.get("retrieved_context", {})
    flags = state.get("intent_flags", {"isSummary": False, "isFollowUp": False})
    last_retrieval = state.get("last_retrieval", {})
    last_intent_was_document = state.get("last_intent_was_document", False)
    context_window = state.get("context_window", [])

    # Build system prompt and user message
    system_prompt = SYSTEM_PROMPT_BASE
    user_message = english_query

    # Parity with Main project: use DOCUMENT_QUERY or WEB_SEARCH context
    if (intent == "DOCUMENT_QUERY" or intent == "WEB_SEARCH") and context.get("has_context"):
        system_prompt = SYSTEM_PROMPT_DOCUMENT
        last_answer = ""
        # If it's a follow-up, pass the last answer for context linkage
        if last_intent_was_document and last_retrieval:
            last_answer = last_retrieval.get("answer", "")
        
        # Build prompt using the same logic as the main project
        user_message = build_contextual_prompt(
            english_query, context, flags, last_answer
        )
    elif intent == "IDENTITY_QUERY":
        user_message = (
            "KNOWLEDGE ABOUT ME:\n"
            "- I am your helpful and professional voice assistant.\n"
            "- I speak naturally, use contractions, and keep things simple.\n\n"
            f"User asked: {english_query}"
        )

    # Build messages array with sliding context window
    messages = [{"role": "system", "content": system_prompt}]

    # Inject ULTRATHINK reasoning if present
    scratchpad = state.get("scratchpad", [])
    if scratchpad:
        for note in scratchpad:
            messages.append(note)

    # Add context window (previous Q&A pairs) - capped at 3 turns by update_context_node
    for pair in context_window:
        if pair.get("q"):
            messages.append({"role": "user", "content": pair["q"]})
        if pair.get("a"):
            messages.append({"role": "assistant", "content": pair["a"]})

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # Determine model and provider
    chat_model = state.get("chat_model") or settings.CHAT_MODEL
    chat_provider = state.get("chat_provider") or settings.CHAT_PROVIDER
    tts_voice = state.get("tts_voice", "af_heart")
    tts_speed = state.get("tts_speed", 1.0)
    hardware = state.get("hardware", "gpu")

    # Stream LLM response
    full_response = ""
    sentence_buffer = ""
    
    from app.services.speech_service import speech_service
    import base64
    # Phase 2: Set maxsize=1 to prevent GPU memory overflow on GTX 1650
    tts_queue: asyncio.Queue = asyncio.Queue(maxsize=1)
    tts_error = None
    has_emitted_first_chunk = False

    async def tts_worker():
        nonlocal tts_error
        while True:
            sentence = await tts_queue.get()
            if sentence is None:
                break
            try:
                writer({"stage": "speaking"})
                async for pcm_bytes in speech_service.synthesize_stream(
                    sentence, voice=tts_voice, speed=tts_speed, hardware=hardware
                ):
                    audio_b64 = base64.b64encode(pcm_bytes).decode("ascii")
                    writer({"audio": audio_b64})
            except Exception as tts_err:
                tts_error = tts_err
                logger.error(f"TTS sentence error: {tts_err}")

    tts_task = asyncio.create_task(tts_worker())
    
    try:
        async for token in chat_complete(
            messages, chat_model, provider=chat_provider, stream=True
        ):
            full_response += token
            sentence_buffer += token
            # Emit token to frontend immediately
            writer({"token": token})
            
            # Phase 1: Aggressive first-chunk splitting
            ready_chunks, sentence_buffer = _extract_ready_tts_chunks(
                sentence_buffer, is_first_chunk=not has_emitted_first_chunk
            )
            for sentence in ready_chunks:
                if len(sentence) > 2:
                    has_emitted_first_chunk = True
                    await tts_queue.put(sentence)

    except Exception as e:
        logger.error(f"LLM streaming error: {e}")
        error_msg = "Sorry, I encountered an error. Could you try again?"
        full_response = error_msg
        writer({"token": error_msg})

    # Flush remaining buffer for TTS
    remaining_chunks, sentence_buffer = _extract_ready_tts_chunks(sentence_buffer, flush_all=True)
    for sentence in remaining_chunks:
        if len(sentence) > 2:
            await tts_queue.put(sentence)

    await tts_queue.put(None)
    await tts_task

    writer({"audio_done": True})

    # Strip inline citations for the final clean response
    clean_response = re.sub(
        r"【[^】]+】|\[\s*Source:[^\]]+\]|\(\s*Source:[^)]+\)",
        "",
        full_response,
    ).strip()

    return {
        "generated_response": full_response,
        "clean_response": clean_response,
        "current_stage": "generating",
        "messages": [AIMessage(content=clean_response)],
    }
