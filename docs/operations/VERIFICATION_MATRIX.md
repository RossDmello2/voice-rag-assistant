# Verification Matrix

**Date:** 2026-06-01
**Project:** VoiceRAG Agent

| Gate | Command/Evidence | Result | Notes |
| --- | --- | --- | --- |
| Branch created | `git branch --show-current` | PASS | Working branch: `codex/open-source-readiness`. |
| GitHub repository created | `gh repo view RossDmello2/voice-rag-agent --json nameWithOwner,visibility,description,url` | PASS | Repository is public and `origin` points to `https://github.com/RossDmello2/voice-rag-agent.git`. |
| GitHub topics configured | `gh repo view RossDmello2/voice-rag-agent --json repositoryTopics` | PASS | All 20 planned topics are configured. |
| Local artifact ignore | `git check-ignore voice_agent_backend/.env voice_agent_backend/data/models/kokoro-v1.0.onnx voice_agent_backend/data/sqlite/voice_agent.db` | PASS | `.env`, Kokoro ONNX, and SQLite DB are ignored. |
| No tracked secrets/artifacts | `git ls-files \| rg "(^|/)\\.env$|\\.onnx$|\\.bin$|voice_agent_backend/data/sqlite/.*\\.(db|sqlite|sqlite3)$"` | PASS | No tracked `.env`, model binary, or runtime DB artifacts. |
| JavaScript syntax | `node --check voice_agent_backend/frontend/script.js` | PASS | Exit 0. |
| Python compile | `cd voice_agent_backend; python -m compileall app scripts tests` | PASS | Exit 0. |
| Automated tests | `cd voice_agent_backend; python -m pytest tests/backend tests/frontend -q` | PASS | 33 passed. |
| Pytest collection | `cd voice_agent_backend; python -m pytest --collect-only -q` | PASS | 7 backend tests and 26 frontend tests collected. |
| Import smoke | `cd voice_agent_backend; python scripts/checks/import_smoke.py` | PASS | `ALL 20 IMPORTS PASSED`. |
| App import | `cd voice_agent_backend; python -c "from app.main import app; print(app.title)"` | PASS | Printed `Voice Agent API`. |
| Browser smoke | Temporary Uvicorn on `http://127.0.0.1:8023` plus Playwright DOM/auth check | PASS | Page title was `VoiceRAG Agent | Local Voice-to-Voice RAG Assistant`; auth modal opened; no page errors. |
| Screenshot assets | Playwright screenshots and generated social preview | PASS | Created `docs/assets/screenshots/home.png`, `docs/assets/screenshots/auth-documents.png`, and `docs/assets/social-preview.png`. |
| Git diff whitespace | `git diff --check` | PASS | Exit 0; Git only emitted Windows CRLF conversion warnings. |

## Known External Limits

- GitHub social preview upload is available in repository settings, but `gh repo edit` does not expose a supported image-upload flag. The source image is committed at `docs/assets/social-preview.png` and the upload step is documented in `docs/guides/GITHUB_PUBLISHING_CHECKLIST.md`.
- Full provider smoke depends on local Qdrant, Ollama, Kokoro artifacts, and valid Groq credentials.
- FastAPI `on_event` and SQLAlchemy `datetime.utcnow()` deprecation warnings remain pre-existing follow-up items.
