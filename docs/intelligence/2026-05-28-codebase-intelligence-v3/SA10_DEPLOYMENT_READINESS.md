# SA-10: Deployment & Hosting Readiness Report

Generated: 2026-05-28 11:20:25 +0530
Project root: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent
Runtime app root: voice_agent_backend/
Output directory: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


## Deployment Topology
Single FastAPI web service serving vanilla JS plus external/backing services: Qdrant, Ollama, Groq, Kokoro, SQLite/Postgres.

## Serverless vs Container Classification
Container is recommended. Vercel supports FastAPI/Python, but this code shape is stateful and local-artifact heavy. Render/Railway align better with a long-running FastAPI service.

## Twelve-Factor Audit
| Factor | Status | Evidence |
| --- | --- | --- |
| dependencies | PARTIAL | voice_agent_backend/requirements.txt:1-28; not pinned exact |
| config | PARTIAL | voice_agent_backend/app/core/config.py:170; .env based |
| backing services | NEEDS WORK | .env.example:25-26 localhost defaults |
| port binding | NEEDS WORK | voice_agent_backend/Dockerfile:12 fixed port |
| concurrency | NEEDS WORK | voice_agent_backend/app/core/voice_graph.py:114-119 process-local |
| logs | PARTIAL | voice_agent_backend/app/main.py:18-20 |
| admin processes | MISSING | no migration tooling detected |

## Platform Scores
| Platform | Score | Compatibility | Reason |
| --- | --- | --- | --- |
| Render | 68/100 | NEEDS_CHANGES | best fit after PORT, env, disk/DB, provider topology, auth scope |
| Railway | 62/100 | NEEDS_CHANGES | viable after PORT, service graph, volume/DB, health decisions |
| Vercel | 35/100 | MAJOR_WORK | FastAPI supported, but local artifacts and process state are poor serverless fit |

## Deployment Blockers
| ID | Blocker | Evidence |
| --- | --- | --- |
| DEPLOY_BLOCKER-1 | Externalize Qdrant/Ollama; localhost defaults cannot work on hosted app service. | .env.example:25-26 |
| DEPLOY_BLOCKER-2 | Change Docker/start command to bind to ${PORT:-8000}. | voice_agent_backend/Dockerfile:12 |
| DEPLOY_BLOCKER-3 | Choose persistent SQLite disk or managed Postgres plus migrations. | voice_agent_backend/app/core/database.py:8-33 |
| DEPLOY_BLOCKER-4 | Decide public auth/rate limits for chat/STT/TTS before internet exposure. | docs/deployment.md:49 |
| DEPLOY_BLOCKER-5 | Disable or sidecar Kokoro native TTS unless model artifacts and compute are provisioned. | .env.example:52-55 |

## Cost Analysis
| Platform | Inspected cost signal | Project-specific note |
| --- | --- | --- |
| Render | Hobby $0/mo + compute; Starter web $7/mo; Standard $25/mo; disks $0.25/GB/mo from pricing page | native TTS likely needs more than free tier |
| Railway | Free $0/mo with $1 resources; Hobby $5/mo; Pro $20/mo plus resource usage | Ollama/Kokoro services can raise compute cost |
| Vercel | Hobby includes Python functions within limits; Pro usage applies beyond included resources | serverless refactor needed before meaningful cost estimate |
