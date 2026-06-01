# SA-8: Open-Source Landscape Report

Generated: 2026-05-28 11:20:25 +0530
Project root: <repo-root>
Runtime app root: voice_agent_backend/
Output directory: <repo-root>/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


Line-count note: standard research mode was used; source URLs are in `RESEARCH_SOURCES.md`.

## Comparable Source Matrix
| Project | Comparable axis | voice-agent differentiation |
| --- | --- | --- |
| LangGraph | stateful agent orchestration | voice-agent uses it internally but ships an end-user voice/RAG app |
| LlamaIndex | document agents, parsing, indexing, RAG | voice-agent is narrower with same-origin voice UI and Qdrant/Ollama/Groq choices |
| Haystack | production RAG/agent pipelines | voice-agent is app-level, not a broad framework |
| Dify | production agent workflow and RAG platform | voice-agent is code-first/local-first, not low-code multi-tenant |
| Open WebUI | self-hosted local AI UI | voice-agent adds bespoke voice pipeline, document ingest, Kokoro TTS, and graph flow |

## Ecosystem Position
Best category: local-first AI voice/RAG application. Secondary category: FastAPI + vanilla JS document voice assistant.

## AI/RAG/MCP Pattern Audit
| Pattern | Status | Evidence |
| --- | --- | --- |
| Agent graph | implemented | voice_agent_backend/app/core/voice_graph.py:35-119 |
| Document ingest/RAG | implemented | voice_agent_backend/app/api/routes/ingest.py:296-418 |
| Self-hosted local model UI | partial | voice_agent_backend/frontend/index.html:230-244 |
| Voice I/O | implemented | voice_agent_backend/app/api/routes/stt.py:8; voice_agent_backend/app/api/routes/tts.py:17 |
| MCP | not detected | no MCP route/package found in ledger |
| LLMOps/observability | minimal | SA6 observability gaps |

## Open-Source Readiness Gaps
| Gap | Severity | Evidence |
| --- | --- | --- |
| Dockerfile not production-hardened | HIGH | voice_agent_backend/Dockerfile:1-12 |
| No compose recipe for app + Qdrant/Ollama/Kokoro | HIGH | deployment file search found only Dockerfile |
| No package metadata because this is an app repo | LOW | no pyproject/package config detected |
| No remote printed locally | LOW | git remote -v output empty |
