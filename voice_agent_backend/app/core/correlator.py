"""
Query correlator — determines if a new query relates to the previous one.
Uses Groq cloud API (meta-llama/llama-4-scout-17b-16e-instruct).
"""

import logging
from app.services.llm_router import chat_complete

logger = logging.getLogger(__name__)

CORRELATOR_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

SYSTEM_PROMPT = """You are a query correlation classifier. Given a previous query and a new query, determine if they are related (asking about the same topic/information).

Respond with ONLY "related" or "new", nothing else.

Examples:
Previous: "What is the vacation policy?" → New: "How many days do I get?" → related
Previous: "What is the vacation policy?" → New: "Tell me a joke" → new
Previous: "What is the salary range?" → New: "And the deadline?" → related
Previous: "Who is the manager?" → New: "What's the weather?" → new"""


async def correlate_query(previous_query: str, new_query: str) -> str:
    """
    Determine if new_query is related to previous_query.
    Returns "related" or "new".
    Falls back to "new" on any error.
    """
    if not previous_query or not new_query:
        return "new"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Previous: \"{previous_query}\"\nNew: \"{new_query}\""},
    ]

    try:
        result = await chat_complete(
            messages=messages,
            model=CORRELATOR_MODEL,
            provider="groq",
            temperature=0,
            max_tokens=10,
            stream=False,
        )
        answer = result.strip().lower()
        if "related" in answer:
            return "related"
        return "new"
    except Exception as e:
        logger.warning(f"Correlator failed, defaulting to 'new': {e}")
        return "new"