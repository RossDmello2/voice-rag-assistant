# Deployment Checklist

Generated: 2026-05-28 11:20:25 +0530
Project root: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent
Runtime app root: voice_agent_backend/
Output directory: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


## Pre-Deploy: Fix Blocking Issues
| ID | Action | Evidence |
| --- | --- | --- |
| DEPLOY_BLOCKER-1 | Externalize Qdrant/Ollama; localhost defaults cannot work on hosted app service. | .env.example:25-26 |
| DEPLOY_BLOCKER-2 | Change Docker/start command to bind to ${PORT:-8000}. | voice_agent_backend/Dockerfile:12 |
| DEPLOY_BLOCKER-3 | Choose persistent SQLite disk or managed Postgres plus migrations. | voice_agent_backend/app/core/database.py:8-33 |
| DEPLOY_BLOCKER-4 | Decide public auth/rate limits for chat/STT/TTS before internet exposure. | docs/deployment.md:49 |
| DEPLOY_BLOCKER-5 | Disable or sidecar Kokoro native TTS unless model artifacts and compute are provisioned. | .env.example:52-55 |

## Pre-Deploy: Environment Variables
Use `SA10_ENV_MANIFEST.md`; set `SECRET_KEY`, `GROQ_API_KEY`, `QDRANT_BASE`, `OLLAMA_BASE`, and optional `DATABASE_URL` in the platform secret manager. Do not upload the local `.env`.

## Pre-Deploy: Database
Use persistent SQLite disk only for private single-instance demos. For production, add a Postgres driver and migrations before setting `DATABASE_URL`.

## Deploy to Render
1. Review and copy `deploy-configs/Dockerfile.production` into `voice_agent_backend/`.
2. Review and copy `deploy-configs/render.yaml` to repo root.
3. Set secrets and provider URLs.
4. Configure disk if using SQLite/Kokoro local files.
5. Set health check path `/health`.

## Deploy to Railway
1. Review Dockerfile and `railway.toml`.
2. Set env vars and service topology.
3. Confirm app listens on injected `$PORT`.
4. Configure healthcheck `/health`.

## Deploy to Vercel
Not recommended as first target. Requires adapter/refactor for nested app, local artifacts, and process-local state.

## Post-Deploy Verification
- [ ] App loads.
- [ ] `/health` returns expected status.
- [ ] Auth register/login works.
- [ ] Unauthenticated mutation routes return 401.
- [ ] Qdrant/Ollama/Groq paths work intentionally.
- [ ] STT/TTS usage is gated or deliberately private.
