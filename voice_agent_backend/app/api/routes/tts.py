from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.services.speech_service import speech_service
from pydantic import BaseModel, Field


router = APIRouter(prefix="/tts", tags=["tts"])


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    voice: str = Field("af_heart", min_length=1, max_length=64)
    speed: float = Field(1.0, ge=0.5, le=2.0)


@router.post("/generate")
async def generate_tts(req: TTSRequest):
    async def audio_stream():
        async for chunk in speech_service.synthesize_stream(
            req.text, voice=req.voice, speed=req.speed
        ):
            yield chunk

    return StreamingResponse(
        audio_stream(), media_type="audio/L16; rate=24000; channels=1"
    )
