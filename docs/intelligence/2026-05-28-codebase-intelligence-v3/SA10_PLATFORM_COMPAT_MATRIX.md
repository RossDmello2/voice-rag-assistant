# Platform Compatibility Matrix

Generated: 2026-05-28 11:20:25 +0530
Project root: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent
Runtime app root: voice_agent_backend/
Output directory: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


## Summary Matrix
| Platform | Compatibility | Readiness | Blocking Issues |
| --- | --- | --- | --- |
| Vercel | MAJOR_WORK | 35/100 | entrypoint adapter, local artifacts, process-local state, serverless bundle/runtime concerns |
| Render | NEEDS_CHANGES | 68/100 | PORT, persistence/DB, Qdrant/Ollama URLs, auth scope |
| Railway | NEEDS_CHANGES | 62/100 | PORT, service graph, volumes, health, auth scope |

## Vercel
FastAPI and Python runtime are supported by inspected Vercel docs. Current project still needs major work because `app.main:app` is nested, local ONNX/SQLite artifacts exist, and runtime state is process-local.

## Render
Best first target. Render web services support Python/FastAPI/Docker and health checks. Must fix `$PORT`, persistence, provider URLs, and public endpoint policy.

## Railway
Viable. Railway injects `PORT` and healthchecks `/health`; service graph and volume behavior need explicit design.
