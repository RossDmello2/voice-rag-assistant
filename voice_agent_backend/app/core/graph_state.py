"""
VoiceAgentState TypedDict + STAGE_LABELS for the LangGraph pipeline.
"""

from typing import TypedDict, List, Optional, Annotated, Dict, Any
from langchain_core.messages import BaseMessage
import operator


class VoiceAgentState(TypedDict):
    """
    State that flows through every node in the LangGraph pipeline.
    LangGraph merges list fields via operator.add (appends, not replaces).
    Scalar fields are replaced by each node's return dict.
    """
    # Conversation history (LangGraph merges lists via operator.add)
    messages: Annotated[List[BaseMessage], operator.add]

    # Context window: last N completed Q&A pairs (capped at 3)
    context_window: List[dict]  # [{"q": "...", "a": "..."}, ...]

    # Per-turn working state
    current_query: str              # transcribed text this turn
    english_query: str              # translated to English (if non-English)
    intent: Optional[str]           # "DOCUMENT_QUERY" | "GENERAL_CHAT" | "IDENTITY_QUERY" | "STOP_COMMAND" | "UPLOAD_INTENT"
    intent_flags: dict              # {"isSummary": bool, "isFollowUp": bool}
    has_documents: bool             # whether documents exist in the collection
    last_intent_was_document: bool  # whether previous intent was DOCUMENT_QUERY
    is_injection: bool              # whether prompt injection was detected
    retrieved_context: Optional[dict]  # full RAG result dict from retrieve_context
    generated_response: str         # full LLM response text (for TTS and memory)
    clean_response: str             # after citation stripping
    display_response: str           # after back-translation (if non-English)

    # Interruption state
    interrupt_flag: bool            # set True by /chat/interrupt endpoint
    interrupted_query: str          # the new query that triggered interruption

    # LangGraph identity
    thread_id: str                  # = user_id from JWT (persistent pointer per user)
    session_id: str                 # = session_id from memory_store

    # Model selection (from frontend UI)
    chat_model: str                 # e.g. "llama-3.3-70b-versatile"
    chat_provider: str              # e.g. "groq" or "ollama"
    embed_model: str                # e.g. "mxbai-embed-large"
    collection: str                 # Qdrant collection name
    language: str                   # source language code (e.g. "en", "hi")
    
    # TTS Settings (Kokoro)
    tts_voice: str                  # e.g. "af_heart"
    tts_speed: float                # e.g. 1.0
    hardware: str                   # "cpu" or "gpu"


    # Sources from RAG retrieval
    sources: List[str]              # source filenames from RAG

    # Last retrieval context (for follow-up queries)
    last_retrieval: Optional[dict]  # last RAG retrieval dict

    # Multi-Agent State
    scratchpad: Annotated[List[dict], operator.add]  # intermediate notes from sub-agents
    ultrathink_logs: Annotated[List[str], operator.add] # Chain of thought logs

    # Progress tracking
    current_stage: str              # emitted to frontend as custom event


# ── Stage labels for frontend progress UI ──────────────────────────

STAGE_LABELS = {
    "transcribing": "Listening...",
    "classifying":  "Understanding...",
    "retrieving":   "Searching documents...",
    "reranking":    "Sorting results...",
    "generating":   "Thinking...",
    "ultrathinking": "Deep Thinking (ULTRATHINK)...",
    "speaking":     "Speaking...",
    "done":         "",
}