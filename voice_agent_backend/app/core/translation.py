from app.core.config import settings
from app.services.llm_router import chat_complete


async def translate_to_english(text: str, source_language: str) -> str:
    """
    Translate text from source_language to English.
    Uses Groq llama-3.1-8b-instant.
    """
    prompt = (
        f"Translate the following {source_language} text to English. "
        f"Return ONLY the English translation, no explanation:\n{text}"
    )
    messages = [{"role": "user", "content": prompt}]

    try:
        result = await chat_complete(
            messages=messages,
            model=settings.TRANSLATION_MODEL,
            provider=settings.TRANSLATION_PROVIDER,
            temperature=0,
            max_tokens=512,
            stream=False
        )
        return result.strip()
    except Exception:
        # Fallback: return original text if translation fails
        return text


async def translate_from_english(text: str, target_language: str) -> str:
    """
    Translate text from English to target_language.
    Uses Groq llama-3.1-8b-instant.
    """
    prompt = (
        f"Translate the following English text to {target_language}. "
        f"Return ONLY the translation, no explanation, no markdown:\n{text}"
    )
    messages = [{"role": "user", "content": prompt}]

    try:
        result = await chat_complete(
            messages=messages,
            model=settings.TRANSLATION_MODEL,
            provider=settings.TRANSLATION_PROVIDER,
            temperature=0,
            max_tokens=512,
            stream=False
        )
        return result.strip()
    except Exception:
        # Fallback: return original text if translation fails
        return text
