"""
Update context node — maintains the sliding context window (capped at 3 turns).
Also handles back-translation of response for non-English mode.
"""

import logging
from langgraph.config import get_stream_writer

from app.core.translation import translate_from_english
from app.core.config import settings
from app.core.graph_state import VoiceAgentState
from app.core.memory import memory_store

logger = logging.getLogger(__name__)

# Context window max turns (Finding: capped at 3)
CONTEXT_WINDOW_MAX_TURNS = getattr(settings, "CONTEXT_WINDOW_TURNS", 3)


async def update_context_node(state: VoiceAgentState) -> dict:
    """
    Update the sliding context window with the current Q&A pair.
    Cap at 3 turns (6 messages). Back-translate if non-English.
    Also update last_retrieval state for follow-up queries.
    """
    writer = get_stream_writer()

    english_query = state.get("english_query", "")
    clean_response = state.get("clean_response", "")
    intent = state.get("intent", "GENERAL_CHAT")
    language = state.get("language", "en")
    context_window = state.get("context_window", [])
    retrieved_context = state.get("retrieved_context")
    session_id = state.get("session_id")

    # Back-translate response if non-English
    display_response = clean_response
    if language != "en" and clean_response:
        try:
            display_response = await translate_from_english(clean_response, language)
            writer({"translated": display_response})
        except Exception as e:
            logger.warning(f"Back-translation failed: {e}")
            display_response = clean_response

    # Add current Q&A pair to context window
    new_pair = {"q": english_query, "a": clean_response}
    updated_window = list(context_window) + [new_pair]

    # Enforce sliding window cap at 3 turns
    if len(updated_window) > CONTEXT_WINDOW_MAX_TURNS:
        updated_window = updated_window[-CONTEXT_WINDOW_MAX_TURNS:]

    # Update last_retrieval with answer if this was a document query
    last_retrieval = state.get("last_retrieval")
    if intent == "DOCUMENT_QUERY" and retrieved_context:
        last_retrieval = {
            "query": english_query,
            "resolvedQuery": english_query,
            "answer": clean_response,
            "sources": state.get("sources", []),
            "context_text": retrieved_context.get("context_text", ""),
            "pages": retrieved_context.get("pages", []),
            "result_count": retrieved_context.get("result_count", 0),
            "top_score": retrieved_context.get("top_score", 0),
        }

    # PERSIST TO MEMORY_STORE (Parity with legacy endpoint)
    if session_id:
        # Save turn to history
        current_query_raw = state.get("current_query", english_query) # use raw if possible
        memory_store.append_turn(session_id, current_query_raw, clean_response)
        
        # Save last retrieval
        if last_retrieval:
            memory_store.set_last_retrieval(session_id, last_retrieval)

    writer({"stage": "done"})

    return {
        "context_window": updated_window,
        "display_response": display_response,
        "last_retrieval": last_retrieval,
        "last_intent_was_document": intent == "DOCUMENT_QUERY",
        "current_stage": "done",
    }