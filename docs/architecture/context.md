# Status

This is a legacy architecture note preserved for historical context. For current contribution planning, use `docs/architecture/README.md` and `docs/features/README.md` first. Some statements below predate the current bearer-token auth boundary and may not describe the live app.

# Voice Agent & Document Assistant - Project Context
*Last Updated: 2026-04-16 (Post-Guest Refactor & Hardware Optimization)*

## 📍 Overview

This project is a high-performance **Voice-to-Voice RAG (Retrieval Augmented Generation) Assistant**. It is built on a **Thin Frontend + Powerful FastAPI Backend** architecture. The system has been refactored from a secured monolithic setup into a **Guest-First, Session-Based** system optimized for speed and natural speech interaction.

The assistant can:
- **Talk & Listen**: Real-time voice interaction with noise-aware VAD (Voice Activity Detection) interruptions.
- **Learn from Files**: Ingest PDF, DOCX, TXT, and CSV files, storing them as optimized vector chunks in Qdrant.
- **Answer with Facts**: Use a hybrid RAG pipeline (search + rerank) to answer questions specifically from your documents.
- **Naturalize Speech**: (SRT Pipeline) Automatically convert currency, emails, and numbers into spoken form for smooth TTS output.
- **Switch Models Dynamically**: Choose between local models (Ollama) or cloud models (Groq) in real-time.

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python 3.12) |
| **Frontend** | Vanilla JavaScript / CSS / HTML |
| **Intelligence** | Groq API (Cloud - Primary) & Ollama (Local - Fallback) |
| **Vector DB** | Qdrant (for document memory and similarity search) |
| **Primary DB** | SQLite (`voice_agent_backend/data/sqlite/voice_agent.db`) via SQLAlchemy (for Logs and Metadata) |
| **Embeddings** | Ollama / Groq (Multi-model support) |
| **Speech (TTS)** | **Kokoro-82M** (Native ONNX/CUDA for GPU acceleration) |
| **Optimization** | Nitro 5 Hardware Profile (i5-11400H / GTX 1650) |

---

## 🏗️ Project Architecture

### 1. The Optimized Entryway (`app/main.py`)
The system is optimized for high-throughput I/O and low-latency TTS:
- **Hardware Tuning**: The thread pool and ONNX runtime are tuned for 12 CPU threads and 4GB VRAM.
- **Audit Logging**: Every request is logged with latency metrics to `INFO` logs for performance monitoring.
- **Rate Limiting**: Protected by `slowapi` to prevent API abuse.

### 2. The Session Store (`app/core/memory.py`)
Authentication has been removed in favor of a guest-friendly, **Session-Based** architecture:
- **Session IDs**: The frontend generates a unique UUID per session, which the backend uses to manage conversation history.
- **Persistence**: Conversation "turns" are saved to the `memory_store` to maintain context during the thread.

### 3. The Multi-Model Hub (`app/services/llm_router.py`)
The system follows a **Spoken-First** philosophy:
- **Natural Prompts**: System prompts enforce natural speech (contractions, no lists, price-to-words conversion).
- **LLM Routing**: Decides between Groq (high speed) and Ollama (privacy/offline) based on UI selection.

### 4. The RAG Pipeline (`app/api/routes/ingest.py` & `chat.py`)
- **Speculative Retrieval**: The `/chat` endpoint fires off RAG retrieval in parallel with intent classification to reduce TTFT (Time to First Token).
- **Hybrid Reranking**: Scores chunks based on vector similarity and model-specific reranking logic.

---

## 📁 Key File Map

- **`app/main.py`**: Entry point. Optimized startup with TTS GPU warm-up.
- **`app/api/routes/chat.py`**: Main orchestration endpoint. Handles both standard SSE and LangGraph streams.
- **`app/services/speech_service.py`**: Contains the **SRT (Speech-Ready Text)** normalize pipeline and Kokoro-ONNX logic.
- **`app/core/voice_graph.py`**: The LangGraph definition for the voice pipeline.
- **`app/core/config.py`**: Central config, system prompts, and hardware-specific constants.
- **`frontend/script.js`**: Managed audio capture, VAD interruptions, and PCM playback.

---

### 5. LangGraph Pipeline (`app/core/voice_graph.py`)
The system uses **LangGraph** for advanced multi-step orchestration:
- **Modular Nodes**: specialized logic for Translation, Classification, Retrieval, and Generation.
- **Internal Streaming TTS**: The `generate_response_node` synthesizes audio sentence-by-sentence in parallel with LLM tokens.
- **Custom Streaming**: Uses `stream_mode=["custom"]` to pipe audio chunks and tokens through a single SSE connection.

---

## 🔄 Core Data Flows

### A. The Chat Loop (Voice-to-Voice)
1. **STT**: User audio → Groq Whisper (Text).
2. **Translate & Normalize**: Input is converted to English and slang is removed.
3. **Intent Classification**: Decides if the user is asking about documents or just chatting.
4. **Retrieve (In Parallel)**: Context pulled from Qdrant if document query detected.
5. **Generate & SRT**: 
   - LLM produces text tokens.
   - **SRT Pipeline**: Text is normalized (e.g., "$100" → "one hundred dollars") before TTS.
6. **Sentence-by-Sentence TTS**: High-speed synthesis on GPU, streaming PCM chunks to frontend.

### B. Document Ingestion
1. **Extract/Chunk**: PDF/DOCX split into ~1200 character chunks with overlap.
2. **Embed/Upsert**: Vectors stored in Qdrant indexed by collection name and model metadata.

---

## 🤖 Guide for Future LLMs
To work on this project effectively:
1. **Preserve SRT**: Always run text through `speech_service._normalize_tts_text()` before calling TTS.
2. **Hardware Awareness**: Do not exceed hardware thread limits defined in `config.py` (Nitro 5 Profile).
3. **Natural Speech**: When modifying system prompts, ensure the model is instructed to avoid tables, citations, and list-heavy formatting.
4. **Schema Discipline**: New API parameters MUST be defined in `app/models/schemas.py`.


# 🗺️ Project Architecture & Logic Map (`file_str.md`)

This document is the **Full Source of Truth** for the Voice Agent codebase. Combined with `docs/architecture/context.md`, it provides every technical detail needed for an LLM to navigate, debug, and extend the system without missing a single dependency or data flow.

---

## 📂 1. Directory Structure

```yaml
voice_agent_backend/
├── app/
│   ├── api/routes/        # FastAPI Endpoint Definitions
│   ├── core/              # Main Logic & Agent Orchestration
│   │   ├── nodes/         # LangGraph Node Functions (Atomic steps)
│   ├── middleware/        # FastAPI Middlewares (Logging, etc.)
│   ├── models/            # Pydantic Schemas & Data Models
│   ├── services/          # Integration Services (LLM, TTS, STT, VectorDB)
│   └── main.py            # Entry point & Hardware Tuning
├── data/
│   ├── models/            # Kokoro ONNX and voice artifacts
│   └── sqlite/            # SQLite runtime database
├── frontend/              # Vanilla JavaScript UI
├── scripts/checks/        # Developer verification scripts
├── scripts/manual_tests/  # Manual smoke checks and experiments
├── tests/frontend/        # Playwright frontend tests
└── .env                   # Environment & Secret variables
```

---

## 📄 2. Detailed File Logic

### 🏛️ Data Models & Infrastructure
- **[schemas.py](../../voice_agent_backend/app/models/schemas.py)**: Defines strict Pydantic models for every request/response (ChatStream, Ingestion, Interrupts).
- **[logging.py](../../voice_agent_backend/app/middleware/logging.py)**: Middleware that captures TTTF (Time to First Token), STT duration, and RAG search latency for every turn.

### 🛰️ API Layer (`app/api/routes/`)
- **[chat.py](../../voice_agent_backend/app/api/routes/chat.py)**: The primary gateway for voice and text chat.
    - **SSE Connection**: Manages the persistent Server-Sent Events stream.
    - **LangGraph Integration**: Invokes the `compiled_graph` and uses `stream_mode="custom"` to pipe out tokens/audio.
    - **Interrupts**: Supports a POST `/interrupt` endpoint to stop the agent mid-sentence.
- **[ingest.py](../../voice_agent_backend/app/api/routes/ingest.py)**: The knowledge ingestion pipeline.
    - **Format Agnostic**: Supports PDF, DOCX, TXT, and CSV.
    - **Smart Chunking**: Uses `chunk_structured_lines` to preserve section headers and context.
    - **GPU Batching**: Parallelizes embeddings using `asyncio.gather` for max Nitro 5 performance.

### 🧠 Core Intelligence (`app/core/`)
- **[voice_graph.py](../../voice_agent_backend/app/core/voice_graph.py)**: The Orchestrator. Defines the LangGraph state machine structure and conditional edges.
- **[graph_state.py](../../voice_agent_backend/app/core/graph_state.py)**: Defines **`VoiceAgentState`**, the TypedDict that flows through every node (holds history, intent, context, and tts settings).
- **[intent.py](../../voice_agent_backend/app/core/intent.py)**: Two-tier classification. Uses fast Regex for common commands (STOP, UPLOAD) and LLM fallback for nuanced query detection.
- **[langchain_rag.py](../../voice_agent_backend/app/core/langchain_rag.py)**:
    - **RRF (Reciprocal Rank Fusion)**: Merges results from multiple query variants.
    - **Hybrid Reranking**: Applies score boosts for Rare Words, Proper Nouns, and Data points (numbers/dates).
- **[memory.py](../../voice_agent_backend/app/core/memory.py)**: Singleton session manager. Stores the last `retrieval` and `history` per `session_id`.

### ⚡ Atomic Nodes (`app/core/nodes/`)
1. **`translate_input`**: Normalizes slang and translates non-English input for the LLM.
2. **`correlator`**: Checks if the query is a stand-alone question or a follow-up to previous turns.
3. **`classify_intent`**: Determines destination: `DOCUMENT_QUERY`, `GENERAL_CHAT`, etc.
4. **`retrieve_context`**: Fires vector search variant embeddings to Qdrant.
5. **`check_confidence`**: Blocks hallucinated answers if retrieval scores are too low.
6. **`generate_response`**: **THE STREAMER**. Emits LLM tokens and chunks text at sentence/clause boundaries for TTS.
7. **`update_context`**: Final check. Appends the Q&A pair to persistent session history.

### 🛠️ Execution Services (`app/services/`)
- **[speech_service.py](../../voice_agent_backend/app/services/speech_service.py)**:
    - **SRT (Speech-Ready Text)**: Crucial regex substitution to convert `$10` → "ten dollars" and email symbols into words to prevent Kokoro errors.
    - **Kokoro-ONNX**: Native implementation using 24kHz PCM output. Uses a thread-safe producer-consumer queue for audio streaming.
- **[onnx_runtime.py](../../voice_agent_backend/app/core/onnx_runtime.py)**: Configures the ONNX environment (CUDA EP, IO threads) for the Nitro 5's GTX 1650.
- **[ollama_service.py](../../voice_agent_backend/app/services/ollama_service.py)**: Handles local embedding generation for documents and queries.
- **[http_client.py](../../voice_agent_backend/app/services/http_client.py)**: **Singleton I/O**. Manages a shared `httpx.AsyncClient` pool to eliminate repeated handshake latency for Groq/Ollama API calls.

### 🧪 Utilities & Testing (`scripts/`)
- **`scripts/checks/verify_kokoro.py`**: Manual script to test GPU acceleration and SRT normalization without firing the full web server.
- **`scripts/checks/check_backend_health.py`**: Pings core dependencies (Qdrant, Ollama, Groq) to ensure the environment is ready for production.
- **`scripts/manual_tests/`**: Manual smoke checks that are intentionally outside pytest collection.
- **`tests/frontend/test_frontend.py`**: Playwright suite for the vanilla JavaScript frontend.

---

## 📊 3. The Data Model Lifecycle

### `ChatStreamRequest` (Incoming)
- `session_id`: Unique persistent identifier.
- `message`: Text transcribed from user voice.
- `tts_voice/speed`: Voice persona control.
- `chat_model/provider`: Allows UI-driven toggling between Groq and Ollama.

### `VoiceAgentState` (The Internal Journey)
1. **Transcribing Stage**: Raw audio is being processed.
2. **Understanding Stage**: Intent and correlation logic running.
3. **Searching Stage**: RAG hitting Qdrant/Ollama.
4. **Speaking Stage**: LLM is streaming and TTS chunks are being emitted base64-encoded.

---

## 🚀 4. Critical Pipeline Mechanics

### The Parallel RAG Strategy
Inside `app/api/routes/chat.py`, the system fires `retrieve_context` *speculatively* even before intent is fully decided. This hides the 200-500ms latency of local embeddings (Ollama) behind the LLM's TTFT.

### The TTS Interruption Protocol
If the VAD (Voice Activity Detection) on the frontend detects user speech during playback, it fires a POST to `/interrupt`. The backend sets `state["interrupt_flag"] = True`, which nodes like `generate_response` monitors to instantly kill the LLM generation and clear the audio buffer.

### Robust Search (RRF)
We generate 3-5 variants of every query. We use **Reciprocal Rank Fusion (RRF)** so that chunks appearing in multiple variant searches are promoted to the top, ensuring extreme accuracy for specific dates or names.

# Voice Agent & Document Assistant - Project Context
*Last Updated: 2026-04-16 (Post-Guest Refactor & Hardware Optimization)*

## 📍 Overview

This project is a high-performance **Voice-to-Voice RAG (Retrieval Augmented Generation) Assistant**. It is built on a **Thin Frontend + Powerful FastAPI Backend** architecture. The system has been refactored from a secured monolithic setup into a **Guest-First, Session-Based** system optimized for speed and natural speech interaction.

The assistant can:
- **Talk & Listen**: Real-time voice interaction with noise-aware VAD (Voice Activity Detection) interruptions.
- **Learn from Files**: Ingest PDF, DOCX, TXT, and CSV files, storing them as optimized vector chunks in Qdrant.
- **Answer with Facts**: Use a hybrid RAG pipeline (search + rerank) to answer questions specifically from your documents.
- **Naturalize Speech**: (SRT Pipeline) Automatically convert currency, emails, and numbers into spoken form for smooth TTS output.
- **Switch Models Dynamically**: Choose between local models (Ollama) or cloud models (Groq) in real-time.

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python 3.12) |
| **Frontend** | Vanilla JavaScript / CSS / HTML |
| **Intelligence** | Groq API (Cloud - Primary) & Ollama (Local - Fallback) |
| **Vector DB** | Qdrant (for document memory and similarity search) |
| **Primary DB** | SQLite (`voice_agent_backend/data/sqlite/voice_agent.db`) via SQLAlchemy (for Logs and Metadata) |
| **Embeddings** | Ollama / Groq (Multi-model support) |
| **Speech (TTS)** | **Kokoro-82M** (Native ONNX/CUDA for GPU acceleration) |
| **Optimization** | Nitro 5 Hardware Profile (i5-11400H / GTX 1650) |

---

## 🏗️ Project Architecture

### 1. The Optimized Entryway (`app/main.py`)
The system is optimized for high-throughput I/O and low-latency TTS:
- **Hardware Tuning**: The thread pool and ONNX runtime are tuned for 12 CPU threads and 4GB VRAM.
- **Audit Logging**: Every request is logged with latency metrics to `INFO` logs for performance monitoring.
- **Rate Limiting**: Protected by `slowapi` to prevent API abuse.

### 2. The Session Store (`app/core/memory.py`)
Authentication has been removed in favor of a guest-friendly, **Session-Based** architecture:
- **Session IDs**: The frontend generates a unique UUID per session, which the backend uses to manage conversation history.
- **Persistence**: Conversation "turns" are saved to the `memory_store` to maintain context during the thread.

### 3. The Multi-Model Hub (`app/services/llm_router.py`)
The system follows a **Spoken-First** philosophy:
- **Natural Prompts**: System prompts enforce natural speech (contractions, no lists, price-to-words conversion).
- **LLM Routing**: Decides between Groq (high speed) and Ollama (privacy/offline) based on UI selection.

### 4. The RAG Pipeline (`app/api/routes/ingest.py` & `chat.py`)
- **Speculative Retrieval**: The `/chat` endpoint fires off RAG retrieval in parallel with intent classification to reduce TTFT (Time to First Token).
- **Hybrid Reranking**: Scores chunks based on vector similarity and model-specific reranking logic.

---

## 📁 Key File Map

- **`app/main.py`**: Entry point. Optimized startup with TTS GPU warm-up.
- **`app/api/routes/chat.py`**: Main orchestration endpoint. Handles both standard SSE and LangGraph streams.
- **`app/services/speech_service.py`**: Contains the **SRT (Speech-Ready Text)** normalize pipeline and Kokoro-ONNX logic.
- **`app/core/voice_graph.py`**: The LangGraph definition for the voice pipeline.
- **`app/core/config.py`**: Central config, system prompts, and hardware-specific constants.
- **`frontend/script.js`**: Managed audio capture, VAD interruptions, and PCM playback.

---

### 5. LangGraph Pipeline (`app/core/voice_graph.py`)
The system uses **LangGraph** for advanced multi-step orchestration:
- **Modular Nodes**: specialized logic for Translation, Classification, Retrieval, and Generation.
- **Internal Streaming TTS**: The `generate_response_node` synthesizes audio sentence-by-sentence in parallel with LLM tokens.
- **Custom Streaming**: Uses `stream_mode=["custom"]` to pipe audio chunks and tokens through a single SSE connection.

---

## 🔄 Core Data Flows

### A. The Chat Loop (Voice-to-Voice)
1. **STT**: User audio → Groq Whisper (Text).
2. **Translate & Normalize**: Input is converted to English and slang is removed.
3. **Intent Classification**: Decides if the user is asking about documents or just chatting.
4. **Retrieve (In Parallel)**: Context pulled from Qdrant if document query detected.
5. **Generate & SRT**: 
   - LLM produces text tokens.
   - **SRT Pipeline**: Text is normalized (e.g., "$100" → "one hundred dollars") before TTS.
6. **Sentence-by-Sentence TTS**: High-speed synthesis on GPU, streaming PCM chunks to frontend.

### B. Document Ingestion
1. **Extract/Chunk**: PDF/DOCX split into ~1200 character chunks with overlap.
2. **Embed/Upsert**: Vectors stored in Qdrant indexed by collection name and model metadata.

---

## 🤖 Guide for Future LLMs
To work on this project effectively:
1. **Preserve SRT**: Always run text through `speech_service._normalize_tts_text()` before calling TTS.
2. **Hardware Awareness**: Do not exceed hardware thread limits defined in `config.py` (Nitro 5 Profile).
3. **Natural Speech**: When modifying system prompts, ensure the model is instructed to avoid tables, citations, and list-heavy formatting.
4. **Schema Discipline**: New API parameters MUST be defined in `app/models/schemas.py`.

this is my current voice agent is it better or understand my project and its comfirt zone and tech used and ur voice agents tech used and come up with an final conclusion and create an new  ultimate-voice-agent use sub agents and  ULTRATHINK
