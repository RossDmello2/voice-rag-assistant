# Agent Guidance

## Runtime Shape

The app root is `voice_agent_backend/`. FastAPI entrypoint: `voice_agent_backend/app/main.py`. The served frontend is `voice_agent_backend/frontend/`.

## Safe Edit Boundaries

- Do not read or print `voice_agent_backend/.env`.
- Do not commit `voice_agent_backend/data/models/*.onnx`, `*.bin`, or `voice_agent_backend/data/sqlite/*.db`.
- Keep `docs/intelligence/` as historical evidence; use `docs/operations/` for current productionization truth.
- Preserve the vanilla JavaScript frontend unless a task explicitly approves a framework migration.

## Auth And Security

- `/auth/register` and `/auth/login` issue bearer tokens.
- Mutating endpoints must stay protected: `/ingest`, `POST /collections`, `DELETE /collections/{name}`, and `DELETE /collections/{name}/documents/{filename}`.
- Read-only local-first endpoints remain public unless a task explicitly expands auth scope.
- Assistant Markdown must pass through `renderMarkdownSafe()` before DOM insertion.

## Verification

Run these before claiming completion:

```bash
git check-ignore voice_agent_backend/.env voice_agent_backend/data/models/kokoro-v1.0.onnx voice_agent_backend/data/sqlite/voice_agent.db
cd voice_agent_backend
python -m compileall app scripts tests
python -m pytest tests/backend tests/frontend -q
python scripts/checks/import_smoke.py
python -c "from app.main import app; print(app.title)"
```

Use browser smoke testing after frontend changes. Provider-level runtime checks may be blocked unless Qdrant, Ollama, Kokoro artifacts, and Groq credentials are available.
