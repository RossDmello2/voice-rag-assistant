# SA-7: Knowledge Graph

Generated: 2026-05-28 11:20:25 +0530
Project root: <repo-root>
Runtime app root: voice_agent_backend/
Output directory: <repo-root>/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


## Route Index
| Method | Path | Auth | Evidence | Behavior |
| --- | --- | --- | --- | --- |
| POST | /auth/register | public | voice_agent_backend/app/api/routes/auth.py:20 | register and return bearer token |
| POST | /auth/login | public | voice_agent_backend/app/api/routes/auth.py:39 | OAuth2 form login |
| POST | /chat | public | voice_agent_backend/app/api/routes/chat.py:52 | legacy SSE chat/RAG |
| POST | /chat/predict | public | voice_agent_backend/app/api/routes/chat.py:291 | speculative RAG warmup |
| POST | /chat/backchannel/{session_id} | public | voice_agent_backend/app/api/routes/chat.py:328 | backchannel audio |
| POST | /chat/stream | public | voice_agent_backend/app/api/routes/chat.py:353 | LangGraph SSE |
| POST | /chat/interrupt/{thread_id} | public | voice_agent_backend/app/api/routes/chat.py:488 | resume graph thread |
| GET | /collections | public | voice_agent_backend/app/api/routes/collections.py:17 | list collections |
| POST | /collections | bearer | voice_agent_backend/app/api/routes/collections.py:27-30 | create collection |
| DELETE | /collections/{collection_name} | bearer | voice_agent_backend/app/api/routes/collections.py:42-45 | delete collection |
| GET | /collections/{collection_name}/documents | public | voice_agent_backend/app/api/routes/collections.py:55 | list documents |
| DELETE | /collections/{collection_name}/documents/{filename} | bearer | voice_agent_backend/app/api/routes/collections.py:65-69 | delete document vectors |
| POST | /ingest | bearer | voice_agent_backend/app/api/routes/ingest.py:421-428 | upload and index PDF/DOCX/TXT/CSV |
| POST | /stt | public | voice_agent_backend/app/api/routes/stt.py:8 | Groq Whisper STT |
| POST | /tts/generate | public | voice_agent_backend/app/api/routes/tts.py:17 | Kokoro TTS stream |
| GET | /health | public | voice_agent_backend/app/api/routes/health.py:10 | service status booleans |
| GET | /models | public | voice_agent_backend/app/api/routes/models.py:34 | model options |
| GET | /* | public | voice_agent_backend/app/main.py:122 | static frontend |

## Function/Class Index
| Symbol | Evidence | Purpose |
| --- | --- | --- |
| Settings | voice_agent_backend/app/core/config.py:56 | runtime config |
| get_current_user | voice_agent_backend/app/core/auth.py:40 | bearer auth |
| chat_endpoint | voice_agent_backend/app/api/routes/chat.py:52 | legacy SSE |
| chat_stream_endpoint | voice_agent_backend/app/api/routes/chat.py:353 | LangGraph SSE |
| ingest_document | voice_agent_backend/app/api/routes/ingest.py:296 | document ingest |
| retrieve_context | voice_agent_backend/app/core/langchain_rag.py:295 | RAG retrieval |
| build_voice_graph | voice_agent_backend/app/core/voice_graph.py:35 | graph assembly |
| QdrantWriteError | voice_agent_backend/app/services/qdrant_service.py:10 | write ack failure |

## Data Model Index
`User`, `UserSession`, `ChatRequest`, `ChatStreamRequest`, `CollectionCreateRequest`, `IngestResponse`, `InterruptRequest`, Qdrant payload metadata.

## Config/Env Index
See `SA10_ENV_MANIFEST.md`.

## Known Risk Index
See `SA6_SECURITY_QUALITY.md` R-01 through R-12 and `SA10_DEPLOYMENT_READINESS.md` blockers.

## Test Index
Backend: 7 tests. Frontend: 26 tests. Import smoke: 20 imports passed.
