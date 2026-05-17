from fastapi import APIRouter
from app.services.ollama_service import health_check as ollama_health
from app.services.qdrant_service import health_check as qdrant_health
from app.services.groq_service import health_check as groq_health
import asyncio

router = APIRouter()


@router.get("/health")
async def health():
    """Ping all three services concurrently and return their status."""
    ollama_ok, qdrant_ok, groq_ok = await asyncio.gather(
        ollama_health(),
        qdrant_health(),
        groq_health(),
        return_exceptions=True
    )

    return {
        "ollama": {
            "online": ollama_ok is True,
            "error": str(ollama_ok) if isinstance(ollama_ok, Exception) else None
        },
        "qdrant": {
            "online": qdrant_ok is True,
            "error": str(qdrant_ok) if isinstance(qdrant_ok, Exception) else None
        },
        "groq": {
            "online": groq_ok is True,
            "error": str(groq_ok) if isinstance(groq_ok, Exception) else None
        }
    }
