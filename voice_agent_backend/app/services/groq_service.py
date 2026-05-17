import httpx
from app.core.config import settings
from typing import AsyncGenerator, Optional
from app.services.http_client import get_http_client
import logging

logger = logging.getLogger(__name__)

def chat_complete(
    messages: list[dict],
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    stream: bool = True,
):
    """
    Call Groq chat completions API.
    If stream=True, returns an async generator yielding tokens (no await needed).
    If stream=False, returns a coroutine that resolves to the full response string (must await).

    NOTE: This is a regular function (not async def) so that:
      - stream=True callers can do:  async for token in chat_complete(..., stream=True)
      - stream=False callers can do: result = await chat_complete(..., stream=False)
    """
    url = f"{settings.GROQ_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
    }

    if stream:
        return _stream_chat(url, headers, payload)
    else:
        return _non_stream_chat(url, headers, payload)


async def _stream_chat(
    url: str, headers: dict, payload: dict
) -> AsyncGenerator[str, None]:
    """Stream tokens from Groq API."""
    client = await get_http_client()
    async with client.stream("POST", url, json=payload, headers=headers, timeout=120.0) as resp:
        resp.raise_for_status()
        async for line in resp.aiter_lines():
            if not line.startswith("data: "):
                continue
            data = line[6:].strip()
            if data == "[DONE]":
                return
            try:
                import json
                obj = json.loads(data)
                delta = obj.get("choices", [{}])[0].get("delta", {})
                token = delta.get("content", "")
                if token:
                    yield token
            except Exception:
                continue


async def _non_stream_chat(
    url: str, headers: dict, payload: dict
) -> str:
    """Non-streaming call — returns full response text."""
    payload["stream"] = False
    client = await get_http_client()
    resp = await client.post(url, json=payload, headers=headers, timeout=60.0)
    resp.raise_for_status()
    data = resp.json()
    return data.get("choices", [{}])[0].get("message", {}).get("content", "")


async def transcribe_audio(
    audio_bytes: bytes, filename: str, language: str = "en"
) -> str:
    """
    Transcribe audio using Groq Whisper API.
    Replicates the direct Groq Whisper call from script.js processAudioChunks().
    """
    url = f"{settings.GROQ_BASE}/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
    }

    # Determine content type from filename extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"
    content_type_map = {
        "webm": "audio/webm",
        "ogg": "audio/ogg",
        "mp3": "audio/mpeg",
        "mp4": "audio/mp4",
        "wav": "audio/wav",
        "m4a": "audio/mp4",
        "flac": "audio/flac",
    }
    content_type = content_type_map.get(ext, "audio/webm")

    files = {
        "file": (filename, audio_bytes, content_type),
    }
    data = {
        "model": "whisper-large-v3",
        "language": language,
        "response_format": "json",
    }

    client = await get_http_client()
    resp = await client.post(url, files=files, data=data, headers=headers, timeout=60.0)
    resp.raise_for_status()
    result = resp.json()
    return result.get("text", "")


async def health_check() -> bool:
    """Check if Groq API is reachable."""
    try:
        url = f"{settings.GROQ_BASE}/models"
        headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
        client = await get_http_client()
        resp = await client.get(url, headers=headers, timeout=10.0)
        if resp.status_code == 200:
            return True
        logger.error(f"Groq health check failed: HTTP {resp.status_code}")
        return False
    except Exception as e:
        logger.error(f"Groq health check failed: {str(e)}")
        return False

async def list_models() -> list[str]:
    """List available Groq models."""
    try:
        url = f"{settings.GROQ_BASE}/models"
        headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
        client = await get_http_client()
        resp = await client.get(url, headers=headers, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        # Filter for active models if possible, otherwise return IDs
        return [m.get("id", "") for m in data.get("data", [])]
    except Exception:
        return []
