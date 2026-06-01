# Productionization Plan

**Date:** 2026-05-17  
**Project:** VoiceRAG Agent
**Production depth:** strict

## Product Shape

Full-stack AI/RAG voice app with a FastAPI backend, same-origin vanilla JavaScript frontend, LangGraph/RAG pipeline, local SQLite auth data, Qdrant/Ollama/Groq integrations, and Kokoro local TTS artifacts.

## Preserve

- All existing source, docs, tests, scripts, model artifacts, and SQLite data.
- `voice_agent_backend/.env` remains local-only and must not be read, printed, or committed.
- `docs/intelligence/` remains historical evidence and is not rewritten as current truth.

## Modify

- `voice_agent_backend/app/main.py`: mount auth router, use configured CORS origins, update CSP for sanitizer CDN.
- `voice_agent_backend/app/core/config.py`: add `APP_ENV` and `DATABASE_URL`, reject fallback secret outside local/dev/test.
- `voice_agent_backend/app/core/database.py`: use configurable SQLite URL/path and enable SQLite FK pragma.
- `voice_agent_backend/app/api/routes/collections.py`: require auth for create/delete operations.
- `voice_agent_backend/app/api/routes/ingest.py`: require auth, use sanitized filenames, validate Qdrant upsert result.
- `voice_agent_backend/app/services/qdrant_service.py`: expose strict write helpers for create/upsert/delete failures.
- `voice_agent_backend/frontend/index.html`, `script.js`, `style.css`: auth modal/token flow and Markdown sanitization.
- `README.md`, `.env.example`, `SECURITY.md`, `.github/workflows/ci.yml`, `.github/dependabot.yml`: sync with productionized behavior.

## Create

- `voice_agent_backend/tests/backend/` with auth, protected-route, ingest, and config tests.
- `.github/workflows/codeql.yml`.
- `docs/deployment.md`.
- `docs/operations/VERIFICATION_MATRIX.md`.
- `docs/operations/PRODUCTIONIZATION_SUMMARY.md`.
- `AGENTS.md`.

## Move/Delete

- No runtime files are moved in this pass.
- No deprecated components are removed.

## Tests To Add

- Auth routes are mounted and registration/login returns bearer tokens.
- Protected mutation endpoints return 401 without a token.
- Protected mutation endpoints accept a valid token with mocked Qdrant/service dependencies.
- Ingest returns a sanitized filename and fails when Qdrant upsert does not acknowledge the write.
- Production `APP_ENV` rejects fallback/blank `SECRET_KEY`.
- Frontend auth modal appears on 401 and stores token on login/register.
- Protected frontend writes send `Authorization: Bearer <token>`.
- Assistant Markdown rendering strips script/event-handler payloads.

## Verification Commands

- `git status --short`
- `git check-ignore voice_agent_backend/.env voice_agent_backend/data/models/kokoro-v1.0.onnx voice_agent_backend/data/sqlite/voice_agent.db`
- `cd voice_agent_backend; python -m compileall app scripts tests`
- `cd voice_agent_backend; python -m pytest tests/backend tests/frontend -q`
- `cd voice_agent_backend; python scripts/checks/import_smoke.py`
- `cd voice_agent_backend; python scripts/manual_tests/graph_smoke.py`
- `cd voice_agent_backend; python -c "from app.main import app; print(app.title)"`
- Browser smoke against `http://127.0.0.1:8000`.
- `pip-audit` and `gitleaks detect --source .` when available.
- `coderabbit review --agent -t uncommitted` after CodeRabbit auth is available.

## Rollback/Safety Notes

- Do not edit or print `voice_agent_backend/.env`.
- Do not commit ignored model/SQLite artifacts.
- If external Qdrant/Ollama/Groq are unavailable, document provider smoke as blocked rather than hiding it.
- If CodeRabbit CLI/auth is unavailable, document the exact failure and do not claim a CodeRabbit review.
