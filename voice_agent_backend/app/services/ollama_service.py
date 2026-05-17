import httpx
from app.core.config import settings
from typing import Optional, Union
from app.services.http_client import get_http_client
import logging

logger = logging.getLogger(__name__)

async def generate_embedding(text: Union[str, list[str]], model: str) -> Union[list[float], list[list[float]]]:
    """
    Generate embedding vector(s) for text using Ollama embedding API.
    Supports batch input (list of strings) for higher performance.
    """
    url = f"{settings.OLLAMA_BASE}/api/embed"
    payload = {
        "model": model,
        "input": text,
    }

    client = await get_http_client()
    try:
        resp = await client.post(url, json=payload, timeout=60.0)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ValueError(
                f"Ollama returned 404 for model '{model}'. "
                f"Please ensure you have pulled it: 'ollama pull {model}'"
            ) from e
        raise e

    data = resp.json()
    # Ollama /api/embed returns {"model": ..., "embeddings": [[...], [...]]}
    embeddings = data.get("embeddings", [])
    
    # If input was a single string, return the first embedding
    if isinstance(text, str):
        if embeddings and len(embeddings) > 0:
            return embeddings[0]
        # Fallback for older API format: {"embedding": [...]}
        embedding = data.get("embedding", [])
        if embedding:
            return embedding
        raise ValueError(f"No embedding returned from Ollama for model {model}")
    
    # If input was a list, return all embeddings
    return embeddings


def chat_complete(
    messages: list[dict],
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    stream: bool = True,
):
    """
    Call Ollama chat completions API (OpenAI compatible).
    """
    url = f"{settings.OLLAMA_BASE}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
    }

    if stream:
        return _stream_chat(url, payload)
    else:
        return _non_stream_chat(url, payload)


async def _stream_chat(url: str, payload: dict):
    """Stream tokens from Ollama API."""
    client = await get_http_client()
    async with client.stream("POST", url, json=payload, timeout=120.0) as resp:
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


async def _non_stream_chat(url: str, payload: dict) -> str:
    """Non-streaming call — returns full response text."""
    payload["stream"] = False
    client = await get_http_client()
    resp = await client.post(url, json=payload, timeout=60.0)
    resp.raise_for_status()
    data = resp.json()
    return data.get("choices", [{}])[0].get("message", {}).get("content", "")


async def list_models() -> list[str]:
    """List available Ollama models."""
    try:
        url = f"{settings.OLLAMA_BASE}/api/tags"
        client = await get_http_client()
        resp = await client.get(url, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []


async def health_check() -> bool:
    """Check if Ollama is reachable."""
    try:
        url = f"{settings.OLLAMA_BASE}/api/tags"
        client = await get_http_client()
        resp = await client.get(url, timeout=5.0)
        if resp.status_code == 200:
            return True
        logger.error(f"Ollama health check failed: HTTP {resp.status_code}")
        return False
    except Exception as e:
        logger.error(f"Ollama health check failed: {str(e)}")
        return False
