# SA-9: Product Surface and UI Pattern Report

Generated: 2026-05-28 11:20:25 +0530
Project root: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent
Runtime app root: voice_agent_backend/
Output directory: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


Line-count note: product surface is a single app UI; required sections are present.

## Current Product Surface
Full-stack local-first voice/RAG application. The first screen is the actual assistant UI, with status, transcript, controls, settings, documents, history, and auth modal (`voice_agent_backend/frontend/index.html:16-383`).

## Recommended Product Shape
Keep it as an operational developer/personal AI tool. Do not position as a generic RAG framework unless the app is split into reusable library plus reference UI.

## AI App UX Checklist
| Item | Status | Evidence |
| --- | --- | --- |
| Provider health status | PASS | voice_agent_backend/frontend/index.html:16-32 |
| Document upload/manager | PASS | voice_agent_backend/frontend/index.html:80-88, :298-333 |
| Model and voice controls | PASS | voice_agent_backend/frontend/index.html:158-244 |
| Auth gate for writes | PASS | voice_agent_backend/frontend/index.html:352-367 |
| Markdown sanitization | PASS | voice_agent_backend/frontend/script.js:1344-1353 |
| Public usage controls | GAP | chat/STT/TTS public routes |
| Production observability | GAP | SA6 observability gaps |

## Product Risks
| Risk | Severity | Evidence |
| --- | --- | --- |
| Public deployment can expose cost-bearing endpoints | HIGH | docs/deployment.md:49 |
| API key input may imply client-side key entry though backend manages keys | MEDIUM | voice_agent_backend/frontend/index.html:262-271; voice_agent_backend/frontend/script.js:2371 |
| GPU/native TTS narrows hosting options | MEDIUM | voice_agent_backend/app/core/config.py:161-168 |
| Mojibake hurts polish | LOW | voice_agent_backend/frontend/index.html:21 |

## Productionization Recommendations
Add public/private mode, provider readiness distinctions, deployment profile docs, self-hosted compose, and hosted auth/usage controls.
