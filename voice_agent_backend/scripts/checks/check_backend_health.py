import asyncio
import logging
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.ollama_service import health_check as ollama_health
from app.services.qdrant_service import health_check as qdrant_health
from app.services.groq_service import health_check as groq_health
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_health_checks():
    print("\n" + "="*50)
    print("BACKEND HEALTH CHECKS")
    print("="*50)
    
    print(f"Ollama ({settings.OLLAMA_BASE}): ", end="", flush=True)
    o_ok = await ollama_health()
    print("OK" if o_ok else "FAILED")
    
    print(f"Qdrant ({settings.QDRANT_BASE}): ", end="", flush=True)
    q_ok = await qdrant_health()
    print("OK" if q_ok else "FAILED")
    
    print(f"Groq ({settings.GROQ_BASE}):   ", end="", flush=True)
    g_ok = await groq_health()
    print("OK" if g_ok else "FAILED")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(run_health_checks())
