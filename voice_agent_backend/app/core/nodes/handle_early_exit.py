"""
Handle early exit node — handles STOP_COMMAND, UPLOAD_INTENT, IDENTITY_QUERY,
GENERAL_CHAT, injection-blocked, and low-confidence "no info" responses.
These paths skip RAG retrieval and LLM streaming.
"""

import random
import logging
import base64
from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer

from app.core.config import SYSTEM_PROMPT_BASE
from app.core.graph_state import VoiceAgentState

logger = logging.getLogger(__name__)

NO_INFO_PHRASES = [
    "Hmm I don't really know about that.",
    "I'm not sure I have that information.",
    "That's not something I'm currently aware of.",
    "I don't think I have that info.",
]

IDENTITY_RESPONSE = (
    "I'm your helpful voice assistant! I can answer questions about your uploaded documents "
    "or just chat. What would you like to know?"
)

UPLOAD_RESPONSE = (
    "You can upload a document through the Documents panel. "
    "Just click the folder icon and select your file."
)

STOP_RESPONSE = "Okay, stopping."

INJECTION_RESPONSE = (
    "I can only help with questions about uploaded documents and general conversation."
)

GENERAL_CHAT_FALLBACK = "I'm here to help! Feel free to ask me anything."


async def handle_early_exit_node(state: VoiceAgentState) -> dict:
    """
    Handle all early-exit paths that don't need RAG + LLM streaming:
    - STOP_COMMAND → "Okay, stopping."
    - UPLOAD_INTENT → upload instructions
    - IDENTITY_QUERY → identity response
    - GENERAL_CHAT → simple LLM call (non-streaming)
    - Injection blocked → rejection message
    - Low confidence → "no info" response
    """
    writer = get_stream_writer()

    intent = state.get("intent", "GENERAL_CHAT")
    is_injection = state.get("is_injection", False)
    english_query = state.get("english_query", "")
    context_window = state.get("context_window", [])
    tts_voice = state.get("tts_voice", "af_heart")
    tts_speed = state.get("tts_speed", 1.0)
    hardware = state.get("hardware", "cpu")

    # Determine response based on intent
    if is_injection:
        response = INJECTION_RESPONSE
    elif intent == "STOP_COMMAND":
        response = STOP_RESPONSE
    elif intent == "UPLOAD_INTENT":
        response = UPLOAD_RESPONSE
    elif intent == "IDENTITY_QUERY":
        response = IDENTITY_RESPONSE
    else:
        # GENERAL_CHAT or low-confidence DOCUMENT_QUERY
        # For GENERAL_CHAT: try a simple non-streaming LLM call
        # For low-confidence: use "no info" phrases
        context = state.get("retrieved_context", {})
        if intent == "DOCUMENT_QUERY" and not context.get("has_context", False):
            response = random.choice(NO_INFO_PHRASES)
        elif intent == "DOCUMENT_QUERY":
            # Low confidence
            response = random.choice(NO_INFO_PHRASES)
        else:
            # GENERAL_CHAT — make a simple LLM call
            try:
                from app.services.llm_router import chat_complete
                from app.core.config import settings

                chat_model = state.get("chat_model") or settings.CHAT_MODEL
                chat_provider = state.get("chat_provider") or settings.CHAT_PROVIDER

                messages = [{"role": "system", "content": SYSTEM_PROMPT_BASE}]
                for pair in context_window[-3:]:
                    if pair.get("q"):
                        messages.append({"role": "user", "content": pair["q"]})
                    if pair.get("a"):
                        messages.append({"role": "assistant", "content": pair["a"]})
                messages.append({"role": "user", "content": english_query})

                result = await chat_complete(
                    messages=messages,
                    model=chat_model,
                    provider=chat_provider,
                    stream=False,
                )
                response = result.strip() if result else GENERAL_CHAT_FALLBACK
            except Exception as e:
                logger.error(f"General chat LLM call failed: {e}")
                response = GENERAL_CHAT_FALLBACK

    # Emit the full response as a single token event
    writer({"token": response})
    writer({"stage": "speaking"})

    try:
        from app.services.speech_service import speech_service

        async for pcm_bytes in speech_service.synthesize_stream(
            response,
            voice=tts_voice,
            speed=tts_speed,
            hardware=hardware,
        ):
            audio_b64 = base64.b64encode(pcm_bytes).decode("ascii")
            writer({"audio": audio_b64})
    except Exception as tts_err:
        logger.error(f"Early-exit TTS failed: {tts_err}")

    writer({"audio_done": True})

    return {
        "generated_response": response,
        "clean_response": response,
        "display_response": response,
        "current_stage": "done",
        "messages": [AIMessage(content=response)],
    }
