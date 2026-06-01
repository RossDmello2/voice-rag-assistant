# SA-0: Discovery Report

Generated: 2026-05-28 11:20:25 +0530
Project root: <repo-root>
Runtime app root: voice_agent_backend/
Output directory: <repo-root>/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


Line-count note: this report is tabular and may be under 100 lines because the live project surface is compact; required sections are present.

## Project Identity
- Name: `voice-agent` (`README.md:1`).
- Description: local voice-to-voice RAG assistant with FastAPI, vanilla JavaScript, LangGraph, Qdrant, Ollama, Groq, Kokoro ONNX TTS, and SQLite auth (`README.md:7`).
- Runtime app root: `voice_agent_backend/` (`AGENTS.md:5`).
- FastAPI entrypoint: `voice_agent_backend/app/main.py` (`AGENTS.md:5`, `voice_agent_backend/app/main.py:41`).
- Served frontend: `voice_agent_backend/frontend/` (`AGENTS.md:5`, `voice_agent_backend/app/main.py:115-122`).
- Existing docs boundary: keep `docs/intelligence/` historical and use `docs/operations/` for productionization truth (`AGENTS.md:13`).
- Git HEAD: `cb36562 chore: establish productionization baseline`; `git remote -v` printed no remote.

## File Ledger Summary
| Read status | Count |
| --- | --- |
| EXCLUDED_BINARY_OR_LOCAL_ARTIFACT | 3 |
| EXCLUDED_SECRET | 1 |
| READ | 120 |

## Technology Stack
| Layer | Technology | Evidence |
| --- | --- | --- |
| API | FastAPI/Uvicorn | voice_agent_backend/app/main.py:4, voice_agent_backend/Dockerfile:12 |
| Config | pydantic-settings | voice_agent_backend/app/core/config.py:1, :56 |
| DB | SQLAlchemy async; SQLite default | voice_agent_backend/app/core/database.py:1-12 |
| Auth | JWT + bcrypt | voice_agent_backend/app/core/auth.py:3-14 |
| RAG | Qdrant + Ollama embeddings | voice_agent_backend/app/services/qdrant_service.py:36-82; voice_agent_backend/app/services/ollama_service.py:14 |
| LLM/STT | Groq OpenAI-compatible API | voice_agent_backend/app/services/groq_service.py:25, :87 |
| Graph | LangGraph StateGraph + MemorySaver | voice_agent_backend/app/core/voice_graph.py:17-18, :114-119 |
| TTS | Kokoro ONNX / ONNX Runtime GPU | voice_agent_backend/app/services/speech_service.py:157-227 |
| Frontend | Vanilla JavaScript | AGENTS.md:14; voice_agent_backend/frontend/script.js:2420 |

## Entry Points
| Entry | Evidence | Notes |
| --- | --- | --- |
| FastAPI app | voice_agent_backend/app/main.py:41 | app title Voice Agent API |
| Router include list | voice_agent_backend/app/main.py:102-109 | chat/auth/ingest/stt/collections/health/models/tts |
| Static frontend mount | voice_agent_backend/app/main.py:115-122 | served at / |
| Dockerfile | voice_agent_backend/Dockerfile:1-12 | local container, fixed 8000 |
| CI | .github/workflows/ci.yml:44-65 | syntax, tests, collection, import smoke |
| CodeQL | .github/workflows/codeql.yml:15-30 | Python and JS/TS analysis |

## Deployment Signal Summary
- Existing deployment config found: `voice_agent_backend/Dockerfile` only.
- No root `render.yaml`, `railway.toml`, `vercel.json`, `fly.toml`, `Procfile`, or `netlify.toml` existed before this output run.
- Local artifacts recorded but not read: Kokoro ONNX 325532387 bytes, voices bin 28214398 bytes, SQLite DB 28672 bytes.
- `.env` exists at `voice_agent_backend/.env`, 1032 bytes, not read.

## Priority Read Targets
1. `AGENTS.md`
2. `README.md`
3. `docs/deployment.md`
4. `voice_agent_backend/app/main.py`
5. `voice_agent_backend/app/core/config.py`
6. `voice_agent_backend/app/api/routes/chat.py`
7. `voice_agent_backend/app/api/routes/ingest.py`
8. `voice_agent_backend/frontend/script.js`
