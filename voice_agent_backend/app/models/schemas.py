from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128, pattern=r'^[a-zA-Z0-9_-]+$')
    message: str = Field(..., min_length=1, max_length=4000)
    collection: str = Field("agent_knowledge", min_length=1, max_length=128, pattern=r'^[a-zA-Z0-9_-]+$')
    language: str = Field("en", min_length=2, max_length=3, pattern=r'^[a-z]{2,3}$')
    stream: bool = True
    chat_model: Optional[str] = None
    chat_provider: Optional[str] = None
    embed_model: Optional[str] = None


class STTResponse(BaseModel):
    text: str
    language: str = "en"


class CollectionCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, pattern=r'^[a-zA-Z0-9_-]+$')
    embed_model: Optional[str] = Field(None, max_length=128)


class DocumentInfo(BaseModel):
    filename: str
    chunks: int = 0
    uploaded_at: Optional[float] = None


class IngestResponse(BaseModel):
    filename: str
    chunks_created: int
    collection: str
    status: str = "success"


# ── New schemas for LangGraph voice pipeline ──────────────────────

class ChatStreamRequest(BaseModel):
    """Request model for the /chat/stream endpoint (LangGraph pipeline)."""
    session_id: Optional[str] = Field(None, min_length=1, max_length=128, pattern=r'^[a-zA-Z0-9_-]+$')
    message: str = Field(..., min_length=1, max_length=4000)
    collection: str = Field("agent_knowledge", min_length=1, max_length=128, pattern=r'^[a-zA-Z0-9_-]+$')
    language: str = Field("en", min_length=2, max_length=3, pattern=r'^[a-z]{2,3}$')
    chat_model: Optional[str] = None
    chat_provider: Optional[str] = None
    embed_model: Optional[str] = None
    thread_id: Optional[str] = None  # LangGraph thread ID (defaults to user_id)
    has_documents: bool = False
    last_intent_was_document: bool = False
    
    # ── Advanced TTS controls (Kokoro) ──
    tts_voice: str = "af_heart"
    tts_speed: float = 1.0
    hardware: str = "gpu" # "cpu" or "gpu"



class InterruptRequest(BaseModel):
    """Request model for the /chat/interrupt endpoint."""
    new_query: Optional[str] = Field(None, max_length=4000)
