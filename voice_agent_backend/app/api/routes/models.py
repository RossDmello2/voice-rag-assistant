from fastapi import APIRouter
from app.services.ollama_service import list_models as list_ollama
from app.services.groq_service import list_models as list_groq
from app.core.onnx_runtime import configure_onnxruntime_gpu_environment
import asyncio
from pathlib import Path

router = APIRouter(prefix="/models", tags=["models"])


def _kokoro_gpu_usable() -> bool:
    """Return True only if ONNX Runtime can actually create a CUDA session."""
    try:
        configure_onnxruntime_gpu_environment()
        import onnxruntime as ort

        ort.preload_dlls(cuda=True, cudnn=True, msvc=True)
        if "CUDAExecutionProvider" not in ort.get_available_providers():
            return False

        from app.core.config import settings
        model_path = Path(settings.KOKORO_MODEL_PATH)
        if not model_path.exists():
            return False

        sess = ort.InferenceSession(
            str(model_path),
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        return "CUDAExecutionProvider" in sess.get_providers()
    except Exception:
        return False

@router.get("")
async def list_available_models():
    """
    Aggregate all available models from Ollama and Groq.
    Categorize them so the frontend knows which provider to use.
    """
    ollama_models, groq_models = await asyncio.gather(
        list_ollama(),
        list_groq(),
        return_exceptions=True
    )
    
    # Handle potential exceptions gracefully
    if isinstance(ollama_models, Exception):
        ollama_models = []
    if isinstance(groq_models, Exception):
        groq_models = []
        
    # Get TTS info
    from app.services.speech_service import speech_service
    tts_voices = speech_service.get_available_voices()
    
    hardware_available = {
        "cpu": True,
        "gpu": _kokoro_gpu_usable()
    }

    return {
        "chat": {
            "ollama": ollama_models,
            "groq": groq_models
        },
        "embeddings": {
            "ollama": [m for m in ollama_models if "embed" in m.lower()],
            "groq": []
        },
        "tts": {
            "voices": tts_voices,
            "hardware": hardware_available
        }
    }
