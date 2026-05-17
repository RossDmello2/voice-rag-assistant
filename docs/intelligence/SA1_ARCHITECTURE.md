# SA-1: Architecture Report

## System Purpose
The system is a local voice-agent web app: a FastAPI backend serves a single-page frontend, receives chat/audio/document requests, performs RAG over Qdrant using Ollama embeddings, routes generation to Groq or Ollama, and synthesizes speech through Kokoro/browser flows. Process setup begins at `voice_agent_backend/app/main.py:41`; API routers are included at `voice_agent_backend/app/main.py:102`; the static frontend is mounted at `voice_agent_backend/app/main.py:121`.

## Architectural Pattern
The code is a modular monolith. `app/main.py` owns middleware, startup, and route mounting; `app/api/routes` owns HTTP endpoints; `app/services` owns provider adapters; `app/core` owns config, auth, memory, RAG, LangGraph, and shared logic. Routes import services directly, so this is not a strict hexagonal or clean architecture boundary.

## Entrypoint And App Shell
`uvicorn app.main:app` is used by scripts and Docker (`voice_agent_backend/start_server.bat:17`, `voice_agent_backend/start_server.sh:14`, `voice_agent_backend/Dockerfile:12`). `app/main.py` creates the FastAPI singleton at `voice_agent_backend/app/main.py:41`. Security headers, audit logging, CORS, router inclusion, and static frontend mount are all in this file.

## Middleware Stack
Security headers are defined at `voice_agent_backend/app/main.py:22` and mounted at `voice_agent_backend/app/main.py:91`. Audit logging is mounted at `voice_agent_backend/app/main.py:92` and logs method/path/status/latency/client IP at `voice_agent_backend/app/middleware/logging.py:22`. CORS is hardcoded at `voice_agent_backend/app/main.py:94`, while settings also define CORS origins at `voice_agent_backend/app/core/config.py:120` but those settings are not used by `main.py`.

## Router Registration
| Method | Path | File | Handler | Auth | Rate Limit |
| --- | --- | --- | --- | --- | --- |
| POST | /auth/register | voice_agent_backend/app/api/routes/auth.py:20 | register | no explicit dependency | no |
| POST | /auth/login | voice_agent_backend/app/api/routes/auth.py:39 | login | no explicit dependency | no |
| POST | /chat | voice_agent_backend/app/api/routes/chat.py:52 | chat_endpoint | no explicit dependency | yes |
| POST | /chat/predict | voice_agent_backend/app/api/routes/chat.py:291 | chat_predict_endpoint | no explicit dependency | no |
| POST | /chat/backchannel/{session_id} | voice_agent_backend/app/api/routes/chat.py:328 | chat_backchannel_endpoint | no explicit dependency | no |
| POST | /chat/stream | voice_agent_backend/app/api/routes/chat.py:353 | chat_stream_endpoint | no explicit dependency | yes |
| POST | /chat/interrupt/{thread_id} | voice_agent_backend/app/api/routes/chat.py:488 | interrupt_endpoint | no explicit dependency | yes |
| GET | /collections | voice_agent_backend/app/api/routes/collections.py:15 | get_collections | no explicit dependency | no |
| POST | /collections | voice_agent_backend/app/api/routes/collections.py:25 | create_collection_endpoint | no explicit dependency | no |
| DELETE | /collections/{collection_name} | voice_agent_backend/app/api/routes/collections.py:39 | delete_collection_endpoint | no explicit dependency | no |
| GET | /collections/{collection_name}/documents | voice_agent_backend/app/api/routes/collections.py:51 | get_documents | no explicit dependency | no |
| DELETE | /collections/{collection_name}/documents/{filename} | voice_agent_backend/app/api/routes/collections.py:61 | delete_document | no explicit dependency | no |
| GET | /health | voice_agent_backend/app/api/routes/health.py:10 | health | no explicit dependency | no |
| POST | /ingest | voice_agent_backend/app/api/routes/ingest.py:396 | ingest_endpoint | no explicit dependency | yes |
| GET | /models | voice_agent_backend/app/api/routes/models.py:34 | list_available_models | no explicit dependency | no |
| POST | /stt | voice_agent_backend/app/api/routes/stt.py:8 | speech_to_text | no explicit dependency | no |
| POST | /tts/generate | voice_agent_backend/app/api/routes/tts.py:17 | generate_tts | no explicit dependency | no |

## Request Lifecycle - Primary Path
1. The frontend calls `/chat/stream` at `voice_agent_backend/frontend/script.js:331`.
2. FastAPI receives the request through `voice_agent_backend/app/main.py:41`.
3. Middleware adds security headers, audit logs, and CORS handling.
4. `/chat/stream` starts at `voice_agent_backend/app/api/routes/chat.py:353`.
5. The route builds `initial_state` and `thread_id` for LangGraph.
6. It starts graph streaming with `compiled_graph.astream()` around `voice_agent_backend/app/api/routes/chat.py:444`.
7. The graph emits custom events, which are forwarded as SSE token/stage/audio/source frames.
8. Session memory is updated by graph nodes and/or chat route helpers.

## LangGraph Pipeline
The graph is built with `StateGraph(VoiceAgentState)` at `voice_agent_backend/app/core/voice_graph.py:38`. Nodes include `translate_input`, `check_interrupt`, `supervisor`, `ultrathink_critic`, `retrieve_context`, `check_confidence`, `generate_response`, `update_context`, `handle_early_exit`, and `search_web` at `voice_agent_backend/app/core/voice_graph.py:41`. The entry point is `translate_input` at `voice_agent_backend/app/core/voice_graph.py:53`. The compiled graph uses in-memory `MemorySaver` at `voice_agent_backend/app/core/voice_graph.py:114`.

## Data Flow Diagram
```text
[Browser SPA]
  -> [FastAPI app: voice_agent_backend/app/main.py:41]
  -> [Security/Audit/CORS middleware]
  -> [/chat or /chat/stream]
  -> [SessionMemory + LangGraph/RAG]
  -> [Qdrant search + Ollama embeddings]
  -> [Groq or Ollama generation]
  -> [Kokoro/backend audio or browser TTS]
  -> [SSE/JSON response]

[/ingest]
  -> [upload validation]
  -> [document extraction]
  -> [chunking]
  -> [Ollama embeddings]
  -> [Qdrant upsert]

[/collections]
  -> [Qdrant collection/document REST]

[/stt]
  -> [Groq audio transcription]
```

## State Ownership Map
| State | Owner | Mutated By | Risk |
| --- | --- | --- | --- |
| SQLite users | voice_agent_backend/app/models/user.py:6 | auth register/login if mounted | auth router is disconnected |
| SQLite user_sessions | voice_agent_backend/app/models/user.py:15 | no live usage found | dead or future table |
| SessionMemory | voice_agent_backend/app/core/memory.py:12 | chat route and LangGraph update node | process-local |
| Rate limit memory | voice_agent_backend/app/core/limiter.py:8 | SlowAPI | process-local |
| Graph checkpoints | voice_agent_backend/app/core/voice_graph.py:114 | LangGraph | process-local |
| Predictive/backchannel caches | voice_agent_backend/app/api/routes/chat.py:40 | chat route | limited eviction |
| Speech service caches | voice_agent_backend/app/services/speech_service.py:35 | TTS startup and route paths | mutable singleton |

## Configuration Flow
Settings are loaded once via `Settings(BaseSettings)` at `voice_agent_backend/app/core/config.py:56` and instantiated at `voice_agent_backend/app/core/config.py:163`. The env file path is declared at `voice_agent_backend/app/core/config.py:52`. Groq, Ollama, Qdrant, Kokoro, CORS, security, RAG, and hardware settings all have source defaults.

| Setting | Defined At | Used At Count | Default |
| --- | --- | --- | --- |
| OLLAMA_BASE | voice_agent_backend/app/core/config.py:58 | 7 | "http://localhost:11434" |
| QDRANT_BASE | voice_agent_backend/app/core/config.py:59 | 8 | "http://localhost:6333" |
| GROQ_BASE | voice_agent_backend/app/core/config.py:60 | 8 | "https://api.groq.com/openai/v1" |
| GROQ_API_KEY | voice_agent_backend/app/core/config.py:61 | 9 | "" |
| CHAT_MODEL | voice_agent_backend/app/core/config.py:64 | 5 | "llama-3.1-8b-instant" |
| EMBED_MODEL | voice_agent_backend/app/core/config.py:65 | 7 | "mxbai-embed-large:latest" |
| TRANSLATION_MODEL | voice_agent_backend/app/core/config.py:66 | 3 | "llama-3.1-8b-instant" |
| CHAT_PROVIDER | voice_agent_backend/app/core/config.py:68 | 4 | "groq"  # "groq" or "ollama" |
| TRANSLATION_PROVIDER | voice_agent_backend/app/core/config.py:69 | 2 | "groq"  # "groq" or "ollama" |
| DEFAULT_COLLECTION | voice_agent_backend/app/core/config.py:72 | 0 | "agent_knowledge" |
| RETRIEVAL_TOP_K | voice_agent_backend/app/core/config.py:73 | 1 | 12  # Increased from 8 for better recall on rare entities |
| SUMMARY_TOP_K | voice_agent_backend/app/core/config.py:74 | 2 | 16 |
| RERANK_TOP_N | voice_agent_backend/app/core/config.py:75 | 1 | 6 |
| SCORE_THRESHOLD | voice_agent_backend/app/core/config.py:76 | 1 | 0.25  # Lowered slightly to capture more candidates for consensus |
| RETRIEVAL_CONFIDENCE_FLOOR | voice_agent_backend/app/core/config.py:77 | 1 | 0.40  # Unified scale for RRF + Vector |
| SUMMARY_CONFIDENCE_FLOOR | voice_agent_backend/app/core/config.py:78 | 1 | 0.35 |
| CHUNK_SIZE | voice_agent_backend/app/core/config.py:81 | 3 | 1200 |
| CHUNK_OVERLAP | voice_agent_backend/app/core/config.py:82 | 2 | 200 |
| MEMORY_PAIRS | voice_agent_backend/app/core/config.py:85 | 1 | 10 |
| KOKORO_MODE | voice_agent_backend/app/core/config.py:89 | 0 | "native" |
| KOKORO_DOCKER_URL | voice_agent_backend/app/core/config.py:91 | 0 | "http://127.0.0.1:8880" |
| KOKORO_MODEL_PATH | voice_agent_backend/app/core/config.py:93 | 1 | "../kokoro-v1.0.onnx" |
| KOKORO_VOICES_PATH | voice_agent_backend/app/core/config.py:95 | 0 | "../voices-v1.0.bin" |
| KOKORO_LANG_CODE | voice_agent_backend/app/core/config.py:97 | 0 | "a" |
| TTS_HARDWARE | voice_agent_backend/app/core/config.py:99 | 0 | "gpu" |
| TTS_SAMPLE_RATE | voice_agent_backend/app/core/config.py:101 | 0 | 24000 |
| CONTEXT_WINDOW_TURNS | voice_agent_backend/app/core/config.py:103 | 0 | 3 |
| CORRELATOR_MODEL | voice_agent_backend/app/core/config.py:105 | 0 | "meta-llama/llama-4-scout-17b-16e-instruct" |
| CORRELATOR_PROVIDER | voice_agent_backend/app/core/config.py:107 | 0 | "groq" |
| BACKCHANNEL_PHRASES | voice_agent_backend/app/core/config.py:110 | 0 | ["mm-hmm", "yeah", "I see", "got it", "right"] |
| BACKCHANNEL_COOLDOWN_SECONDS | voice_agent_backend/app/core/config.py:111 | 2 | 6.0 |
| PREDICTIVE_RAG_TIMEOUT_MS | voice_agent_backend/app/core/config.py:112 | 0 | 500 |
| ENABLE_SEARCH | voice_agent_backend/app/core/config.py:115 | 0 | True |
| SEARCH_PROVIDER | voice_agent_backend/app/core/config.py:116 | 0 | "duckduckgo" # "duckduckgo" or "tavily" |
| TAVILY_API_KEY | voice_agent_backend/app/core/config.py:117 | 0 | "" |
| CORS_ORIGINS | voice_agent_backend/app/core/config.py:120 | 0 | ["http://localhost:8000", "http://127.0.0.1:8000"] |
| ALLOWED_HOSTS | voice_agent_backend/app/core/config.py:121 | 0 | ["localhost", "127.0.0.1"] |
| SECRET_KEY | voice_agent_backend/app/core/config.py:124 | 2 | [REDACTED fallback secret default] |
| ALGORITHM | voice_agent_backend/app/core/config.py:125 | 2 | "HS256" |
| ACCESS_TOKEN_EXPIRE_MINUTES | voice_agent_backend/app/core/config.py:126 | 1 | 60 |
| MAX_FILE_SIZE | voice_agent_backend/app/core/config.py:127 | 2 | 50 * 1024 * 1024  # 50 MB |
| ENABLE_RATE_LIMIT | voice_agent_backend/app/core/config.py:128 | 1 | True |
| HOST | voice_agent_backend/app/core/config.py:148 | 0 | "0.0.0.0" |
| PORT | voice_agent_backend/app/core/config.py:149 | 0 | 8000 |
| IO_THREAD_POOL_SIZE | voice_agent_backend/app/core/config.py:153 | 2 | 12 |
| GPU_BATCH_SIZE | voice_agent_backend/app/core/config.py:154 | 1 | 4 |
| ONNX_INTRA_OP_THREADS | voice_agent_backend/app/core/config.py:155 | 1 | 4 |
| ONNX_INTER_OP_THREADS | voice_agent_backend/app/core/config.py:156 | 1 | 2 |
| MODELS_TO_CUDA | voice_agent_backend/app/core/config.py:157 | 0 | ["kokoro", "embed"] |
| STT_LOCAL_DEVICE | voice_agent_backend/app/core/config.py:158 | 0 | "cpu"  # Keep STT on CPU to save 4GB VRAM for RAG/TTS |

## Background Processes
Startup initializes the DB and schedules TTS warm-up with `asyncio.create_task` at `voice_agent_backend/app/main.py:71`. Legacy chat starts concurrent intent and retrieval work around `voice_agent_backend/app/api/routes/chat.py:111`. `/chat/stream` starts side-car backchannel and graph tasks around `voice_agent_backend/app/api/routes/chat.py:439` and `voice_agent_backend/app/api/routes/chat.py:456`. Response generation starts a TTS worker around `voice_agent_backend/app/core/nodes/generate_response.py:174`.

## Architectural Risks
1. Auth is present but disconnected: `auth.router` exists at `voice_agent_backend/app/api/routes/auth.py:10` but is not mounted in `main.py`.
2. State is process-local: sessions, graph checkpoints, rate limits, predictive caches, and speech caches do not survive restart or multiple workers.
3. Two chat orchestrators exist: legacy `/chat` and LangGraph `/chat/stream`, which can drift.
4. Predictive RAG appears written but not consumed outside the predictor endpoint.
5. The default secret permits insecure startup if env is missing.
6. Background tasks lack centralized cancellation and exception propagation.
