"""
Classify intent node — async wrapper around intent.py classify_intent().
MUST be async because classify_intent() in intent.py is async (Finding 1).
"""

import logging
import asyncio
from langgraph.config import get_stream_writer

from app.core.intent import classify_intent, classify_intent_fast
from app.core.langchain_rag import retrieve_context
from app.core.graph_state import VoiceAgentState

logger = logging.getLogger(__name__)


async def classify_intent_node(state: VoiceAgentState) -> dict:
    """
    Classify user intent using two-tier classifier (fast regex + LLM fallback).
    Parallel retrieval is now handled at the graph level in voice_graph.py.
    """
    writer = get_stream_writer()
    writer({"stage": "classifying"})

    english_query = state.get("english_query", "")
    has_documents = state.get("has_documents", False)
    last_intent_was_document = state.get("last_intent_was_document", False)

    # --- Tier 1: Fast Regex Matching ---
    intent, flags = classify_intent_fast(
        text=english_query,
        has_documents=has_documents,
        last_intent_was_document=last_intent_was_document,
    )

    # If Tier 1 was confident, we skip the slow LLM classifier entirely
    if intent:
        logger.info(f"Fast intent match: {intent}. Proceeding.")
    else:
        # Tier 2: LLM fallback (only if Tier 1 failed)
        intent, flags = await classify_intent(
            text=english_query,
            has_documents=has_documents,
            last_intent_was_document=last_intent_was_document,
        )

    logger.info(f"Intent classified: {intent} (flags={flags})")

    return {
        "intent": intent,
        "intent_flags": flags,
        "current_stage": "classifying",
    }


def route_after_classify(state: VoiceAgentState) -> str:
    """
    Route after intent classification:
    - DOCUMENT_QUERY -> retrieve_context
    - Others -> handle_early_exit
    """
    intent = state.get("intent", "GENERAL_CHAT")
    is_injection = state.get("is_injection", False)

    # Injection always goes to early exit (blocked response)
    if is_injection:
        return "handle_early_exit"

    if intent == "DOCUMENT_QUERY":
        return "retrieve_context"

    if intent == "GENERAL_CHAT" and state.get("intent_flags", {}).get("isWebSearch"):
        return "search_web"

    # All other intents (STOP_COMMAND, etc.) go to early exit handler
    return "handle_early_exit"
