# SA-2: Backend Report

Generated: 2026-05-28 11:20:25 +0530
Project root: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent
Runtime app root: voice_agent_backend/
Output directory: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


## Complete Route Inventory
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

## Middleware Analysis
- Security headers/CSP middleware is custom (`voice_agent_backend/app/main.py:24-38`).
- CORS uses `settings.CORS_ORIGINS` and allows credentials (`voice_agent_backend/app/main.py:94-100`).
- Audit logging middleware is registered (`voice_agent_backend/app/main.py:92`).
- SlowAPI rate limit handler is registered (`voice_agent_backend/app/main.py:42-43`).
- `ALLOWED_HOSTS` exists in settings but TrustedHostMiddleware is not registered (`voice_agent_backend/app/core/config.py:124`, `voice_agent_backend/app/main.py:91-100`).

## Service Layer Analysis
| Service | Evidence | Role |
| --- | --- | --- |
| llm_router | voice_agent_backend/app/services/llm_router.py:4-34 | routes Groq vs Ollama chat |
| qdrant_service | voice_agent_backend/app/services/qdrant_service.py:36-82 | REST wrapper for vector store |
| ollama_service | voice_agent_backend/app/services/ollama_service.py:14, :60 | embeddings and optional chat |
| groq_service | voice_agent_backend/app/services/groq_service.py:25, :87 | chat/models/STT |
| speech_service | voice_agent_backend/app/services/speech_service.py:157-227 | Kokoro TTS load/synthesis |

## Error Handling Report
- Global exceptions are logged with traceback and returned as sanitized 500 body (`voice_agent_backend/app/main.py:80-88`).
- Qdrant write failures raise/propagate errors, but read connection failures can collapse to empty results (`voice_agent_backend/app/services/qdrant_service.py:43-63`).
- STT and chat can return `str(e)` in user-visible errors (`voice_agent_backend/app/api/routes/stt.py:25-26`, `voice_agent_backend/app/api/routes/chat.py:260-263`).

## Input Validation Report
| Input | Validation | Evidence |
| --- | --- | --- |
| chat/session/collection/language | Pydantic length and patterns | voice_agent_backend/app/models/schemas.py:5-14 |
| collection create | name pattern and max length | voice_agent_backend/app/models/schemas.py:21-23 |
| stream chat | message max 4000 and TTS fields | voice_agent_backend/app/models/schemas.py:41-58 |
| ingest file | size, extension, sanitized filename | voice_agent_backend/app/api/routes/ingest.py:434-449 |
| TTS | text/voice/speed bounds | voice_agent_backend/app/api/routes/tts.py:11-14 |

## Business Logic Bugs
| ID | Severity | Finding | Evidence |
| --- | --- | --- | --- |
| R-01 | HIGH | Docker CMD hardcodes port 8000; Render/Railway expect platform PORT. | voice_agent_backend/Dockerfile:12 |
| R-02 | HIGH | Qdrant and Ollama default to localhost, which fails in hosted deployments. | .env.example:25-26 |
| R-03 | HIGH | Public STT can call Groq without auth if internet exposed. | voice_agent_backend/app/api/routes/stt.py:8 |
| R-04 | HIGH | Public TTS can consume compute without auth if internet exposed. | voice_agent_backend/app/api/routes/tts.py:17 |
| R-05 | HIGH | SQLite default and model artifacts require persistent storage or managed replacements. | voice_agent_backend/app/core/database.py:8-10; .env.example:54-55 |
| R-06 | MEDIUM | Process-local caches and LangGraph MemorySaver are not scale-out safe. | voice_agent_backend/app/api/routes/chat.py:40-49; voice_agent_backend/app/core/voice_graph.py:114-119 |
| R-07 | MEDIUM | CSP allows inline scripts and external CDNs; scripts lack SRI. | voice_agent_backend/app/main.py:30-37; voice_agent_backend/frontend/index.html:378-381 |
| R-08 | MEDIUM | ALLOWED_HOSTS is configured but no TrustedHostMiddleware was found. | voice_agent_backend/app/core/config.py:124; voice_agent_backend/app/main.py:91-100 |
| R-09 | MEDIUM | Health endpoint returns 200 with dependency booleans, so readiness may pass while dependencies are down. | voice_agent_backend/app/api/routes/health.py:20-33 |
| R-10 | MEDIUM | pip-audit timed out; gitleaks/semgrep/trivy/detect-secrets/osv-scanner missing locally. | verification output |
| R-11 | LOW | FastAPI on_event hooks emit deprecation warnings. | voice_agent_backend/app/main.py:46; voice_agent_backend/app/main.py:74 |
| R-12 | LOW | Mojibake appears in some frontend text/comments. | voice_agent_backend/frontend/index.html:21 |

## Deployment Footprint Report (v3)
- Runtime command: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` from backend root (`README.md:77-79`).
- Dockerfile installs backend requirements and starts uvicorn on fixed 8000 (`voice_agent_backend/Dockerfile:5-12`).
- Health endpoint exists but returns dependency booleans with 200 (`voice_agent_backend/app/api/routes/health.py:10-33`).
