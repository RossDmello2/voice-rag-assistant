from app.services import groq_service, ollama_service
from app.core.config import settings

def chat_complete(
    messages: list[dict],
    model: str,
    provider: str = "groq",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    stream: bool = True,
):
    """
    Unified entry point for LLM chat completions.
    Routes to either Groq or Ollama based on the provider.
    """
    print(f"\n[LLM] Provider: {provider.upper()} | Model: {model}")
    
    if provider.lower() == "ollama":
        return ollama_service.chat_complete(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
    else:
        # Default to groq
        return groq_service.chat_complete(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
