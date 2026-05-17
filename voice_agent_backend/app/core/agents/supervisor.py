"""
Supervisor Agent: Evaluates the query to decide if it requires deep reasoning (ULTRATHINK)
or fast response (System 1).
"""
import logging
from langgraph.config import get_stream_writer
from app.core.graph_state import VoiceAgentState
from app.core.intent import classify_intent, classify_intent_fast

logger = logging.getLogger(__name__)

async def supervisor_node(state: VoiceAgentState) -> dict:
    """
    Acts as the main router. First uses fast intent classification.
    If the query is complex, routes to ULTRATHINK.
    """
    writer = get_stream_writer()
    writer({"stage": "classifying"})

    english_query = state.get("english_query", "")
    has_documents = state.get("has_documents", False)
    last_intent_was_document = state.get("last_intent_was_document", False)

    # Fast check first
    intent, flags = classify_intent_fast(
        text=english_query,
        has_documents=has_documents,
        last_intent_was_document=last_intent_was_document,
    )

    if not intent:
        # LLM classification
        intent, flags = await classify_intent(
            text=english_query,
            has_documents=has_documents,
            last_intent_was_document=last_intent_was_document,
        )

    # ULTRATHINK Heuristic: If it's a complex general chat or document query that requires synthesis
    complex_keywords = ["analyze", "compare", "why", "how", "evaluate", "synthesize", "code", "explain in detail", "summarize"]
    is_complex = len(english_query.split()) > 12 or any(kw in english_query.lower() for kw in complex_keywords)

    if is_complex and intent in ["GENERAL_CHAT", "DOCUMENT_QUERY"]:
        logger.info(f"Supervisor promoting intent {intent} to ULTRATHINK.")
        flags["original_intent"] = intent
        intent = "ULTRATHINK_REASONING"

    logger.info(f"Supervisor finalized intent: {intent} (flags={flags})")

    return {
        "intent": intent,
        "intent_flags": flags,
        "current_stage": "classifying",
    }

def route_after_supervisor(state: VoiceAgentState) -> str:
    """
    Route after supervisor classification.
    """
    intent = state.get("intent", "GENERAL_CHAT")
    is_injection = state.get("is_injection", False)

    if is_injection:
        return "handle_early_exit"

    if intent == "ULTRATHINK_REASONING":
        return "ultrathink_critic"
        
    if intent == "DOCUMENT_QUERY":
        return "retrieve_context"

    if intent == "GENERAL_CHAT" and state.get("intent_flags", {}).get("isWebSearch"):
        return "search_web"

    # Fast path generation
    return "generate_response"
