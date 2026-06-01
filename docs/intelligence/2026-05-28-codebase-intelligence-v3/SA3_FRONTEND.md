# SA-3: Frontend Report

Generated: 2026-05-28 11:20:25 +0530
Project root: <repo-root>
Runtime app root: voice_agent_backend/
Output directory: <repo-root>/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


Line-count note: the frontend is a single-page vanilla JS surface; required sections are present.

## UI Architecture
- Vanilla JavaScript UI served from `voice_agent_backend/frontend/` (`AGENTS.md:5`, `AGENTS.md:14`).
- FastAPI mounts the frontend at `/` (`voice_agent_backend/app/main.py:115-122`).
- `index.html` defines status, stage, transcript, controls, settings, documents, history, auth modal, file input, and CDN scripts (`voice_agent_backend/frontend/index.html:16-383`).

## API Call Inventory
| Endpoint | Frontend evidence | Auth | Backend evidence |
| --- | --- | --- | --- |
| /auth/register | voice_agent_backend/frontend/script.js:166 | no | voice_agent_backend/app/api/routes/auth.py:20 |
| /auth/login | voice_agent_backend/frontend/script.js:175 | no | voice_agent_backend/app/api/routes/auth.py:39 |
| /chat/stream | voice_agent_backend/frontend/script.js:470 | no | voice_agent_backend/app/api/routes/chat.py:353 |
| /chat/interrupt | voice_agent_backend/frontend/script.js:601 | no | voice_agent_backend/app/api/routes/chat.py:488 |
| /stt | voice_agent_backend/frontend/script.js:1564 | no | voice_agent_backend/app/api/routes/stt.py:8 |
| /ingest | voice_agent_backend/frontend/script.js:1943 | yes | voice_agent_backend/app/api/routes/ingest.py:421 |
| /collections | voice_agent_backend/frontend/script.js:2213, :2228 | mixed | voice_agent_backend/app/api/routes/collections.py:17, :27 |
| /health | voice_agent_backend/frontend/script.js:2262 | no | voice_agent_backend/app/api/routes/health.py:10 |

## State Management Map
- Auth token/email stored in localStorage (`voice_agent_backend/frontend/script.js:70-91`).
- Storage helpers wrap localStorage JSON (`voice_agent_backend/frontend/script.js:768-770`).
- Assistant Markdown passes through `renderMarkdownSafe` before insertion (`voice_agent_backend/frontend/script.js:1319`, `voice_agent_backend/frontend/script.js:1344-1353`).

## Frontend Build & CDN Profile (v3)
- No frontend build step or package manifest found.
- CDN scripts: marked, DOMPurify, onnxruntime-web, VAD (`voice_agent_backend/frontend/index.html:378-381`).
- CSP permits cdnjs/jsdelivr and inline scripts/styles (`voice_agent_backend/app/main.py:30-37`).

## UI Bugs Found
| Severity | Finding | Evidence |
| --- | --- | --- |
| MEDIUM | CDN scripts have no SRI. | voice_agent_backend/frontend/index.html:378-381 |
| MEDIUM | localStorage bearer token is acceptable local-first but weaker for public hosting. | voice_agent_backend/frontend/script.js:70-91 |
| LOW | Mojibake appears in visible text. | voice_agent_backend/frontend/index.html:21 |

## Deployment Compatibility Notes
Render/Railway can serve this frontend through FastAPI. Static-only hosting is not a fit without backend API base refactor.
