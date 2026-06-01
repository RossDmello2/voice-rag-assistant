import logging
import time
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.limiter import limiter
from app.core.database import init_db
from app.middleware.logging import AuditLoggingMiddleware
from app.api.routes import chat, ingest, stt, collections, health, auth, models, tts
from app.services.http_client import AsyncHttpClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Security Headers Middleware ────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000 "
            "https://api.groq.com http://localhost:11434 http://127.0.0.1:11434"
        )
        return response


app = FastAPI(title="Voice Agent API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.on_event("startup")
async def startup_event():
    # Nitro 5 Optimization: Match i5-11400H total threads for I/O tasks
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_running_loop()
    loop.set_default_executor(ThreadPoolExecutor(max_workers=settings.IO_THREAD_POOL_SIZE))
    logger.info(f"Asynchronous IO loop optimized for hardware: {settings.IO_THREAD_POOL_SIZE} workers.")

    await init_db()
    from app.services.speech_service import speech_service

    async def warm_tts():
        try:
            await asyncio.to_thread(speech_service.get_available_voices)
            if getattr(settings, "KOKORO_MODE", "native") == "native":
                # Warm up the GPU pipeline for GTX 1650
                await asyncio.to_thread(speech_service._get_kokoro_pipeline, "gpu")
            
            # Pre-compute zero-latency backchannels
            await speech_service.precompute_backchannels()
            
            logger.info("TTS warm-up and backchannel pre-computation finished.")
        except Exception as exc:
            logger.warning(f"TTS warm-up failed or using CPU: {exc}")

    asyncio.create_task(warm_tts())


@app.on_event("shutdown")
async def shutdown_event():
    await AsyncHttpClient.close()


# ── Global Error Sanitization ──────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"UNHANDLED ERROR: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please contact support."
        },
    )


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(ingest.router)
app.include_router(stt.router)
app.include_router(collections.router)
app.include_router(health.router)
app.include_router(models.router)
app.include_router(tts.router)

import os
from pathlib import Path

# Serve the frontend
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if not os.path.exists(FRONTEND_DIR):
    # Fallback for structural differences
    FRONTEND_DIR = "frontend"

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
