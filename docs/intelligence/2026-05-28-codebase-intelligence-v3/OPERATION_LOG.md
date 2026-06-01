# Operation Log

Generated: 2026-05-28 11:20:25 +0530
Project root: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent
Runtime app root: voice_agent_backend/
Output directory: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


## Agent Status
- [x] SA-0 Discovery + File Map
- [x] SA-1 Architecture + Data Flow
- [x] SA-2 Backend / Server-Side
- [x] SA-3 Frontend / UI / Client
- [x] SA-4 Data Layer / Database
- [x] SA-5 Integrations / External Services
- [x] SA-6 Security + Quality + Bug Audit
- [x] SA-8 Ecosystem + Comparative Benchmark
- [x] SA-9 Product Surface + UI Pattern
- [x] SA-10 Deployment & Hosting Readiness
- [x] SA-11 Deployment Config Generator
- [x] SA-7 Synthesis + Master Brief

## Inventory Summary
| Metric | Value |
| --- | --- |
| files inventoried | 124 |
| readable files read | 120 |
| LOC read | 16691 |
| secret files excluded | 1 |
| binary/local artifacts excluded | 3 |

## File Category Counts
| Category | Count |
| --- | --- |
| CONFIG | 3 |
| CORE | 49 |
| DATA | 4 |
| DOC | 32 |
| FRONTEND | 3 |
| INFRA | 8 |
| SCRIPT | 16 |
| TEST | 6 |
| UNKNOWN | 3 |

## Verification
| Command | Result |
| --- | --- |
| git check-ignore voice_agent_backend/.env voice_agent_backend/data/models/kokoro-v1.0.onnx voice_agent_backend/data/models/voices-v1.0.bin voice_agent_backend/data/sqlite/voice_agent.db | PASS |
| python -m compileall app scripts tests | PASS |
| node --check frontend/script.js | PASS |
| python -m pytest tests/backend tests/frontend -q | PASS: 33 passed |
| python -m pytest --collect-only -q | PASS: 7 backend tests, 26 frontend tests |
| python scripts/checks/import_smoke.py | PASS: ALL 20 IMPORTS PASSED |
| python -c "from app.main import app; print(app.title)" | PASS: Voice Agent API |
| python -m pip_audit -r requirements.txt | BLOCKED: timed out after about 124 seconds |

## Critical Flags
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

## Deployment Blockers
| ID | Blocker | Evidence |
| --- | --- | --- |
| DEPLOY_BLOCKER-1 | Externalize Qdrant/Ollama; localhost defaults cannot work on hosted app service. | .env.example:25-26 |
| DEPLOY_BLOCKER-2 | Change Docker/start command to bind to ${PORT:-8000}. | voice_agent_backend/Dockerfile:12 |
| DEPLOY_BLOCKER-3 | Choose persistent SQLite disk or managed Postgres plus migrations. | voice_agent_backend/app/core/database.py:8-33 |
| DEPLOY_BLOCKER-4 | Decide public auth/rate limits for chat/STT/TTS before internet exposure. | docs/deployment.md:49 |
| DEPLOY_BLOCKER-5 | Disable or sidecar Kokoro native TTS unless model artifacts and compute are provisioned. | .env.example:52-55 |

## Operation Summary
- Entry points: voice_agent_backend/app/main.py, voice_agent_backend/Dockerfile, voice_agent_backend/frontend/index.html, .github/workflows/ci.yml.
- Routes: auth, chat, ingest, collections, STT, TTS, health, models, static frontend.
- External services: Groq, Ollama, Qdrant, Kokoro ONNX/sidecar, optional Tavily/DuckDuckGo.
- Deployment topology: one FastAPI web service serving vanilla JS plus backing AI/vector/data services.
- Deployment readiness: Render 68/100, Railway 62/100, Vercel 35/100.
- Recommended platform: Render container web service after blocker fixes.

OPERATION COMPLETE
