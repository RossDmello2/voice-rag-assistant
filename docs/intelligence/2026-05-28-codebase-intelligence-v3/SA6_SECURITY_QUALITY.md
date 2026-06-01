# SA-6: Security and Quality Report

Generated: 2026-05-28 11:20:25 +0530
Project root: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent
Runtime app root: voice_agent_backend/
Output directory: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


## Authentication/Authorization Audit
- Register/login issue bearer tokens (`voice_agent_backend/app/api/routes/auth.py:20-52`).
- `get_current_user` rejects missing or invalid token (`voice_agent_backend/app/core/auth.py:40-69`).
- Mutating endpoints are bearer protected (`voice_agent_backend/app/api/routes/ingest.py:421-428`, `voice_agent_backend/app/api/routes/collections.py:27-69`).
- Tests verify mutation 401 and authorized create (`voice_agent_backend/tests/backend/test_auth_and_protection.py:70-97`).

## Injection and Dangerous Operations
- Chat/collection/input schemas bound lengths and patterns (`voice_agent_backend/app/models/schemas.py:5-63`).
- Prompt injection detector gates legacy chat (`voice_agent_backend/app/api/routes/chat.py:78-87`).
- SQLAlchemy queries are parameterized (`voice_agent_backend/app/api/routes/auth.py:23`, `voice_agent_backend/app/core/auth.py:65`).
- Markdown is sanitized before DOM insertion (`voice_agent_backend/frontend/script.js:1344-1353`).

## Secrets
- `.env` exists but was not read.
- `.env.example` contains blank secret placeholders only (`.env.example:17`, `.env.example:24`, `.env.example:65`).
- Production rejects fallback `SECRET_KEY` (`voice_agent_backend/app/core/config.py:134-145`).

## Dependency Risk
- `pip-audit` timed out; vulnerability status is NOT DETERMINED.
- gitleaks/semgrep/trivy/detect-secrets/osv-scanner missing locally.
- CodeQL workflow exists (`.github/workflows/codeql.yml:15-30`).

## Test Coverage and Quality
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

## Observability
Stdlib logging and audit middleware exist (`voice_agent_backend/app/main.py:18-20`, `voice_agent_backend/app/main.py:92`). No metrics/tracing/Sentry/OpenTelemetry found.

## MASTER RISK REGISTER
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
