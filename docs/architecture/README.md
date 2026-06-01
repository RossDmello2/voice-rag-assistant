# Architecture Guide

Generated: 2026-06-01

This is the current architecture entry point for contributors. The runtime app is a modular FastAPI monolith under `voice_agent_backend/` with a same-origin vanilla JavaScript frontend. Older files in this folder are preserved as historical notes; prefer this guide and `docs/features/README.md` for new contribution planning.

## Product Shape

VoiceRAG Agent is a local-first voice and document RAG application:

| Surface | Current owner | Evidence |
| --- | --- | --- |
| FastAPI app shell | `voice_agent_backend/app/main.py` | `app = FastAPI(...)` at `voice_agent_backend/app/main.py:41`; routers mounted at `voice_agent_backend/app/main.py:102-109`; frontend mounted at `voice_agent_backend/app/main.py:122` |
| Browser UI | `voice_agent_backend/frontend/` | Auth modal markup at `voice_agent_backend/frontend/index.html:352-366`; Markdown sanitizer use at `voice_agent_backend/frontend/script.js:1344-1353` |
| Auth and protected writes | `app/api/routes/auth.py`, `app/core/auth.py`, selected routes | Tokens issued at `voice_agent_backend/app/api/routes/auth.py:20-52`; mutating collection endpoints depend on `get_current_user` at `voice_agent_backend/app/api/routes/collections.py:27-69`; ingest depends on auth at `voice_agent_backend/app/api/routes/ingest.py:421-428` |
| RAG ingestion and retrieval | `app/api/routes/ingest.py`, `app/core/langchain_rag.py`, `app/services/qdrant_service.py` | Ingest chunks, embeds, and upserts documents at `voice_agent_backend/app/api/routes/ingest.py:296-419` |
| Voice pipeline | `app/core/voice_graph.py`, `app/core/nodes/`, `app/services/speech_service.py` | Graph nodes and edges are assembled at `voice_agent_backend/app/core/voice_graph.py:35-122` |
| Runtime config | `app/core/config.py`, root `.env.example` | `Settings` lives at `voice_agent_backend/app/core/config.py:56`; safe template values live in `.env.example:8-65` |
| Tests and checks | `voice_agent_backend/tests/`, `scripts/checks/` | Backend auth/security tests live in `voice_agent_backend/tests/backend/test_auth_and_protection.py`; frontend Playwright tests live in `voice_agent_backend/tests/frontend/test_frontend.py` |

## Runtime Flow

```text
Browser UI
  -> FastAPI route
  -> schema/config/auth boundary
  -> core graph or service layer
  -> Qdrant / Ollama / Groq / Kokoro / SQLite
  -> SSE, JSON, or audio response
```

The app intentionally serves the frontend from the backend process. That keeps local setup simple and avoids a framework migration that the project does not currently need.

## Module Boundaries

| Boundary | Belongs here | Keep out |
| --- | --- | --- |
| `app/api/routes/` | HTTP transport, request validation, status codes, auth dependencies | Provider-specific networking, frontend state, long-lived process caches |
| `app/models/` | Pydantic request/response models and SQLAlchemy models | Route branching and provider calls |
| `app/core/` | settings, auth, database setup, graph state, orchestration, reusable local logic | Direct DOM assumptions or GitHub/deployment docs |
| `app/core/nodes/` | Atomic LangGraph steps with narrow inputs/outputs | Route handlers and UI-specific formatting |
| `app/services/` | External service adapters and shared HTTP/provider clients | Endpoint-level auth decisions |
| `frontend/` | Same-origin UI state, browser events, DOM updates, sanitized rendering | Backend secrets, provider keys, database writes |
| `tests/backend/` | API/config/auth/service-boundary tests with mocked external services | Browser layout assertions |
| `tests/frontend/` | Browser behavior, auth modal, token headers, DOM safety | Real provider calls |
| `docs/features/` | Contributor-facing feature ownership and extension notes | Runtime implementation code |

## Feature Ownership

Use `docs/features/README.md` as the contributor-facing feature folder. It maps each product feature to the current runtime modules, tests, docs, and security constraints. Runtime code remains layer-based for now; moving to `app/features/<feature>/` would be a separate architecture migration and should not be mixed into ordinary feature work.

## Adding A Feature

1. Start in `docs/features/README.md` to identify the closest existing feature and its owners.
2. Add or update schemas in `voice_agent_backend/app/models/` before changing route bodies.
3. Keep HTTP concerns in `app/api/routes/`; put provider or vector-store logic behind `app/services/`.
4. For LangGraph changes, add or update one narrow node in `app/core/nodes/` and wire it in `app/core/voice_graph.py`.
5. For frontend output, render assistant Markdown through `renderMarkdownSafe()` only.
6. Preserve auth rules: `/ingest`, `POST /collections`, `DELETE /collections/{name}`, and document deletion stay bearer-protected.
7. Add backend tests for route/service behavior and frontend tests for visible browser behavior when the UI changes.
8. Update README, `docs/features/README.md`, and CHANGELOG when the feature affects contributor setup, user behavior, API shape, or security posture.

## Verification Gates

Run the project checks from the repository root unless noted:

```bash
git check-ignore voice_agent_backend/.env voice_agent_backend/data/models/kokoro-v1.0.onnx voice_agent_backend/data/sqlite/voice_agent.db
cd voice_agent_backend
python -m compileall app scripts tests
python -m pytest tests/backend tests/frontend -q
python scripts/checks/import_smoke.py
python -c "from app.main import app; print(app.title)"
```

Use browser smoke testing for frontend changes. Provider-level checks may require Qdrant, Ollama, Kokoro model files, and Groq credentials.
