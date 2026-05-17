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
- **[schemas.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/models/schemas.py)**: Defines strict Pydantic models for every request/response (ChatStream, Ingestion, Interrupts).
- **[logging.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/middleware/logging.py)**: Middleware that captures TTTF (Time to First Token), STT duration, and RAG search latency for every turn.

### 🛰️ API Layer (`app/api/routes/`)
- **[chat.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/api/routes/chat.py)**: The primary gateway for voice and text chat.
    - **SSE Connection**: Manages the persistent Server-Sent Events stream.
    - **LangGraph Integration**: Invokes the `compiled_graph` and uses `stream_mode="custom"` to pipe out tokens/audio.
    - **Interrupts**: Supports a POST `/interrupt` endpoint to stop the agent mid-sentence.
- **[ingest.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/api/routes/ingest.py)**: The knowledge ingestion pipeline.
    - **Format Agnostic**: Supports PDF, DOCX, TXT, and CSV.
    - **Smart Chunking**: Uses `chunk_structured_lines` to preserve section headers and context.
    - **GPU Batching**: Parallelizes embeddings using `asyncio.gather` for max Nitro 5 performance.

### 🧠 Core Intelligence (`app/core/`)
- **[voice_graph.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/core/voice_graph.py)**: The Orchestrator. Defines the LangGraph state machine structure and conditional edges.
- **[graph_state.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/core/graph_state.py)**: Defines **`VoiceAgentState`**, the TypedDict that flows through every node (holds history, intent, context, and tts settings).
- **[intent.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/core/intent.py)**: Two-tier classification. Uses fast Regex for common commands (STOP, UPLOAD) and LLM fallback for nuanced query detection.
- **[langchain_rag.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/core/langchain_rag.py)**:
    - **RRF (Reciprocal Rank Fusion)**: Merges results from multiple query variants.
    - **Hybrid Reranking**: Applies score boosts for Rare Words, Proper Nouns, and Data points (numbers/dates).
- **[memory.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/core/memory.py)**: Singleton session manager. Stores the last `retrieval` and `history` per `session_id`.

### ⚡ Atomic Nodes (`app/core/nodes/`)
1. **`translate_input`**: Normalizes slang and translates non-English input for the LLM.
2. **`correlator`**: Checks if the query is a stand-alone question or a follow-up to previous turns.
3. **`classify_intent`**: Determines destination: `DOCUMENT_QUERY`, `GENERAL_CHAT`, etc.
4. **`retrieve_context`**: Fires vector search variant embeddings to Qdrant.
5. **`check_confidence`**: Blocks hallucinated answers if retrieval scores are too low.
6. **`generate_response`**: **THE STREAMER**. Emits LLM tokens and chunks text at sentence/clause boundaries for TTS.
7. **`update_context`**: Final check. Appends the Q&A pair to persistent session history.

### 🛠️ Execution Services (`app/services/`)
- **[speech_service.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/services/speech_service.py)**:
    - **SRT (Speech-Ready Text)**: Crucial regex substitution to convert `$10` → "ten dollars" and email symbols into words to prevent Kokoro errors.
    - **Kokoro-ONNX**: Native implementation using 24kHz PCM output. Uses a thread-safe producer-consumer queue for audio streaming.
- **[onnx_runtime.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/core/onnx_runtime.py)**: Configures the ONNX environment (CUDA EP, IO threads) for the Nitro 5's GTX 1650.
- **[ollama_service.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/services/ollama_service.py)**: Handles local embedding generation for documents and queries.
- **[http_client.py](file:///c:/Users/rossd/Dropbox/PC/Downloads/rag-demo-n8n-to-web/chatbot_static_files_fixed/voice%20agent/voice%20agent%20migration/voice_agent/voice_agent_backend/app/services/http_client.py)**: **Singleton I/O**. Manages a shared `httpx.AsyncClient` pool to eliminate repeated handshake latency for Groq/Ollama API calls.

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
