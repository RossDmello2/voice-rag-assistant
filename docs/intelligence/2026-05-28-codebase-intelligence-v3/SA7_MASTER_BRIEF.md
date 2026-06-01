# SA-7: Master Brief

Generated: 2026-05-28 11:20:25 +0530
Project root: <repo-root>
Runtime app root: voice_agent_backend/
Output directory: <repo-root>/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


## What is this system?
`voice-agent` is a local-first FastAPI voice/RAG assistant with a vanilla JS UI, Qdrant/Ollama retrieval, Groq cloud model/STT support, Kokoro ONNX TTS, and SQLite auth (`README.md:7`).

## How does it work?
FastAPI registers routers, initializes SQLite, warms TTS, and mounts the frontend (`voice_agent_backend/app/main.py:41-122`). The browser posts chat/audio/document actions to same-origin endpoints. Backend routes classify intent, retrieve context, call model providers, and stream SSE/audio responses.

## Components
API/middleware, auth/database, chat/RAG routes, LangGraph graph/nodes, Qdrant/Ollama/Groq/Kokoro services, vanilla frontend, tests/CI, docs.

## Data
Users and sessions are SQLAlchemy models (`voice_agent_backend/app/models/user.py:6-20`). Document chunks become Qdrant payloads with source/page/section metadata (`voice_agent_backend/app/api/routes/ingest.py:390-403`). Graph/session state is process-local.

## What can go wrong?
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

## Not Tested / Blocked
Real provider smoke was not run. Docker build/run was not run. pip-audit timed out. Browser smoke against live FastAPI was not separately run because frontend source was not changed.

## How to run locally
Use README flow: install requirements, copy `.env.example` to `voice_agent_backend/.env`, start Qdrant/Ollama, then run uvicorn from `voice_agent_backend` (`README.md:55-79`).

## How to deploy
Best first target: Render container web service. Fix `$PORT`, externalize Qdrant/Ollama, choose DB/persistence, disable or sidecar native TTS, and protect public cost-bearing endpoints. Review configs are in `deploy-configs/`.

## Platform Readiness
| Platform | Score | Verdict |
| --- | --- | --- |
| Render | 68/100 | best first target after changes |
| Railway | 62/100 | viable after service topology |
| Vercel | 35/100 | major refactor needed |

## Future Agent Read-First List
1. `AGENTS.md`
2. `README.md`
3. `docs/deployment.md`
4. `voice_agent_backend/app/main.py`
5. `voice_agent_backend/app/core/config.py`
6. `voice_agent_backend/app/api/routes/chat.py`
7. `voice_agent_backend/app/api/routes/ingest.py`
8. `voice_agent_backend/frontend/script.js`
9. `SA10_DEPLOYMENT_READINESS.md`
10. `SA6_SECURITY_QUALITY.md`

## Final Verification
All required artifacts exist. `OPERATION_LOG.md` contains `OPERATION COMPLETE`. `SA10_ENV_MANIFEST.md`, `DEPLOY_CHECKLIST.md`, and `SA10_PLATFORM_COMPAT_MATRIX.md` are present and non-empty.
