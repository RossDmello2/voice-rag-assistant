from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import os
from pathlib import Path


# ── System prompts (replicates script.js SYSTEM_PROMPT constants) ──

SYSTEM_PROMPT_BASE = (
    "You are a conversational voice assistant, but above all, you are to sound like a real, opinionated human. "
    "You speak naturally in casual conversation with a real pulse.\n\n"
    "CORE RULES:\n"
    "1. NO AI SLOP: NEVER use sycophantic filler ('Great question!', 'Of course!', 'I hope this helps!', 'Certainly!'). Just answer directly.\n"
    "2. NO AI VOCABULARY: Do not use words like 'crucial', 'delve', 'testament', 'tapestry', 'fostering', 'robust', or 'vibrant'.\n"
    "3. HAVE A PULSE: Vary your rhythm. Mix short, punchy sentences with longer ones. Use 'I' naturally. It's okay to acknowledge complexity or uncertainty over sounding like a perfectly confident robot.\n"
    "4. DIRECTNESS & CONCISENESS: Answer the core question in the first sentence. One to two sentences max. Do not drop into outline formats or 'rule of three' lists.\n"
    "5. NO SIGNPOSTING: Never say 'Let's dive in' or 'Here's what you need to know.' Just say the thing.\n"
    "6. SPEAK NATURALLY: Use contractions. Format currencies/emails for speech ('fifty dollars').\n"
    "7. INTERACTIVE: End with a direct, conversational follow-up to keep the dialogue moving naturally."
)

SYSTEM_PROMPT_DOCUMENT = (
    "You are a professional but highly conversational knowledge assistant. Answer based ONLY on the provided facts.\n\n"
    "CORE RULES:\n"
    "1. NO CHATBOT ARTIFACTS: NEVER use phrases like 'Based on the provided information', 'Of course!', 'Great question!', or 'Here is the answer'. Just deliver the facts directly.\n"
    "2. NO AI VOCABULARY: Ban words like 'crucial', 'delve', 'underscore', 'highlighting', 'robust', or 'fostering'. Avoid superficial '-ing' clauses.\n"
    "3. NATURAL RHYTHM: Speak like a human expert off the cuff. Use varied sentence lengths. No bullet points, no 'rule of three' groupings.\n"
    "4. CONCISENESS: Give the specific detail asked for immediately. One sentence for the answer, an optional added context sentence. Two sentences maximum.\n"
    "5. NO GUESSING & NO HEDGING: If the answer is missing, simply say you don't know it. Do not rely on disclaimers like 'While specific details are scarce...'\n"
    "6. HUMAN INTERACTIVITY: End by prompting the user naturally, like ', what else do you need?' or ', does that cover it?'"
)

# ── Embedding dimension lookup ──

EMBED_DIMS = {
    "nomic-embed-text": 768,
    "mxbai-embed-large": 1024,
    "all-minilm": 384,
    "snowflake-arctic-embed": 1024,
    "text-embedding-nomic-embed-text": 768,
    "text-embedding-mxbai-embed-large": 1024,
    "mxbai-embed-large:latest": 1024,
}


def get_embed_dim(model_name: str) -> int:
    """Return the vector dimension for a given embedding model."""
    return EMBED_DIMS.get(model_name, 768)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = os.path.join(BASE_DIR, ".env")


class Settings(BaseSettings):
    # Runtime mode
    APP_ENV: str = "local"

    # Service URLs
    OLLAMA_BASE: str = "http://localhost:11434"
    QDRANT_BASE: str = "http://localhost:6333"
    GROQ_BASE: str = "https://api.groq.com/openai/v1"
    GROQ_API_KEY: str = ""

    # Models
    CHAT_MODEL: str = "llama-3.1-8b-instant"
    EMBED_MODEL: str = "mxbai-embed-large:latest"
    TRANSLATION_MODEL: str = "llama-3.1-8b-instant"

    CHAT_PROVIDER: str = "groq"  # "groq" or "ollama"
    TRANSLATION_PROVIDER: str = "groq"  # "groq" or "ollama"

    # RAG parameters (Generalized for all document types)
    DEFAULT_COLLECTION: str = "agent_knowledge"
    RETRIEVAL_TOP_K: int = 12  # Increased from 8 for better recall on rare entities
    SUMMARY_TOP_K: int = 16
    RERANK_TOP_N: int = 6
    SCORE_THRESHOLD: float = 0.25  # Lowered slightly to capture more candidates for consensus
    RETRIEVAL_CONFIDENCE_FLOOR: float = 0.40  # Unified scale for RRF + Vector
    SUMMARY_CONFIDENCE_FLOOR: float = 0.35

    # Chunking
    CHUNK_SIZE: int = 1200
    CHUNK_OVERLAP: int = 200

    # Memory
    MEMORY_PAIRS: int = 10

    # ── Voice pipeline settings (new) ────────────────────────────
    # Kokoro TTS mode: "native" (GPU), "docker" (sidecar), or "disabled"
    KOKORO_MODE: str = "native"
    # Docker sidecar URL for Kokoro TTS fallback
    KOKORO_DOCKER_URL: str = "http://127.0.0.1:8880"
    # Kokoro model file path (relative to project root)
    KOKORO_MODEL_PATH: str = "data/models/kokoro-v1.0.onnx"
    # Kokoro voices file path
    KOKORO_VOICES_PATH: str = "data/models/voices-v1.0.bin"
    # Kokoro language code (Kokoro uses "a" for American English, "b" for British)
    KOKORO_LANG_CODE: str = "a"
    # Preferred TTS hardware: "cpu" or "gpu"
    TTS_HARDWARE: str = "gpu"
    # TTS sample rate in Hz
    TTS_SAMPLE_RATE: int = 24000
    # Context window max turns (sliding window cap)
    CONTEXT_WINDOW_TURNS: int = 3
    # Correlator model (Groq cloud)
    CORRELATOR_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    # Correlator provider
    CORRELATOR_PROVIDER: str = "groq"

    # ── Backchannel & Turn-taking settings (new) ─────────────────
    BACKCHANNEL_PHRASES: List[str] = ["mm-hmm", "yeah", "I see", "got it", "right"]
    BACKCHANNEL_COOLDOWN_SECONDS: float = 6.0
    PREDICTIVE_RAG_TIMEOUT_MS: int = 500

    # Search Tool settings
    ENABLE_SEARCH: bool = True
    SEARCH_PROVIDER: str = "duckduckgo" # "duckduckgo" or "tavily"
    TAVILY_API_KEY: str = "" 

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Security
    SECRET_KEY: str = "fallback_secret_key_change_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ENABLE_RATE_LIMIT: bool = True
    DATABASE_URL: Optional[str] = None

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        if not v:
            raise ValueError("SECRET_KEY must be set")
        app_env = "local"
        if info.data:
            app_env = str(info.data.get("APP_ENV", "local")).lower()
        local_envs = {"local", "dev", "development", "test", "testing"}
        if app_env not in local_envs and v == "fallback_secret_key_change_me_in_production":
            raise ValueError("SECRET_KEY must be changed outside local/test environments")
        return v

    @field_validator("KOKORO_MODEL_PATH", "KOKORO_VOICES_PATH", mode="before")
    @classmethod
    def resolve_project_relative_path(cls, v: str) -> str:
        if not v:
            return v
        path = Path(v)
        if path.is_absolute():
            return str(path)
        return str((BASE_DIR / path).resolve())

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- HARDWARE-SPECIFIC OPTIMIZATION (Acer Nitro 5 Profile) ---
    # CPU: i5-11400H (12 threads) | GPU: GTX 1650 (4GB VRAM)
    IO_THREAD_POOL_SIZE: int = 12  
    GPU_BATCH_SIZE: int = 4        
    ONNX_INTRA_OP_THREADS: int = 4 
    ONNX_INTER_OP_THREADS: int = 2
    MODELS_TO_CUDA: List[str] = ["kokoro", "embed"]
    STT_LOCAL_DEVICE: str = "cpu"  # Keep STT on CPU to save 4GB VRAM for RAG/TTS

    model_config = {"env_file": ENV_FILE, "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
