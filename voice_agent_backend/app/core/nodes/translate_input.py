"""
Translate input node — translate non-English input, normalize slang, detect injection.
"""

import logging
from langchain_core.messages import HumanMessage
from langgraph.config import get_stream_writer

from app.core.translation import translate_to_english
from app.core.intent import map_slang_to_formal, detect_prompt_injection
from app.core.graph_state import VoiceAgentState

logger = logging.getLogger(__name__)


async def translate_input_node(state: VoiceAgentState) -> dict:
    """
    1. Translate non-English input to English
    2. Normalize slang
    3. Check for prompt injection
    4. Emit progress via stream writer
    """
    writer = get_stream_writer()
    writer({"stage": "transcribing"})

    raw_query = state.get("current_query", "")
    language = state.get("language", "en")

    # Translate if non-English
    if language != "en" and raw_query:
        try:
            english_query = await translate_to_english(raw_query, language)
            writer({"translated": english_query})
        except Exception as e:
            logger.warning(f"Translation failed, using raw query: {e}")
            english_query = raw_query
    else:
        english_query = raw_query

    # Normalize slang
    english_query = map_slang_to_formal(english_query)

    # Detect prompt injection
    is_injection = detect_prompt_injection(english_query)

    if is_injection:
        logger.warning(f"Prompt injection detected: {english_query[:80]}")

    return {
        "english_query": english_query,
        "is_injection": is_injection,
        "current_stage": "translating",
        "messages": [HumanMessage(content=english_query)],
    }