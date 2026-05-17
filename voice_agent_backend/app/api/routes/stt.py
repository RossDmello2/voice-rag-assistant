from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.schemas import STTResponse
from app.services.groq_service import transcribe_audio

router = APIRouter()


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(
    file: UploadFile = File(...),
    language: str = Form(default="en")
):
    """
    Accept audio file, forward to Groq Whisper, return transcribed text.
    """
    try:
        audio_bytes = await file.read()
        if len(audio_bytes) < 1000:
            raise HTTPException(status_code=400, detail="Audio file too small")

        text = await transcribe_audio(audio_bytes, file.filename or "audio", language)
        return {"text": text, "language": language}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {str(e)}")
