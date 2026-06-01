# Product Shape Decision

**Date:** 2026-05-17  
**Project:** VoiceRAG Agent
**Resolved root:** `C:\Users\rossd\OneDrive\Desktop\logic\voice_agent`

## Selected Shape

Primary shape: **Full-stack AI/RAG voice application**.

Secondary shapes: **API backend**, **static same-origin frontend**, **agent/RAG pipeline**, and **local model/data application**.

## Evidence

| Evidence | Meaning |
|---|---|
| `voice_agent_backend/app/main.py` defines the FastAPI app, middleware, routers, startup, and static frontend mount. | Backend API and frontend are deployed as one app. |
| `voice_agent_backend/frontend/index.html`, `script.js`, and `style.css` implement the browser voice/chat/document UI. | The UI is a product surface, not documentation only. |
| `voice_agent_backend/app/api/routes/chat.py`, `ingest.py`, `collections.py`, `stt.py`, and `tts.py` expose chat, RAG ingestion, vector collection management, speech-to-text, and text-to-speech. | The app has repeated human workflows and provider-backed API calls. |
| `voice_agent_backend/app/core/voice_graph.py`, `langchain_rag.py`, and `memory.py` implement the LangGraph/RAG/session core. | AI/agent behavior is the runtime center. |
| `voice_agent_backend/data/models/` and `voice_agent_backend/data/sqlite/` hold local Kokoro and SQLite runtime artifacts. | Productionization must preserve local binary/data artifacts while excluding them from git. |

## Audience

Developers and local users who want to run a self-hosted voice-to-voice RAG assistant with Groq, Ollama, Qdrant, and Kokoro. Future open-source contributors need clear setup, security boundaries, tests, and maintenance docs.

## Minimum Production Artifact

- FastAPI app serving the frontend and documented API.
- Browser UI for chat, document ingestion, collection selection, voice controls, and auth.
- Local `.env` configuration with safe `.env.example`.
- Automated frontend and backend tests.
- GitHub-ready repo files, CI, Dependabot, security policy, and verification matrix.

## Accepted Surfaces

- API: accepted and required.
- Static same-origin UI: accepted and required.
- Docker deployment: accepted as the primary deploy baseline.
- CLI/package publishing: rejected for this pass because the project is an app, not a library.
- Expo/mobile: rejected for this pass because the live repo has no Expo app files.

## Risks If Forced Into Wrong Shape

- Treating this as backend-only would leave the browser auth and XSS risks unhandled.
- Treating this as static-only would ignore Qdrant, Groq, Ollama, Kokoro, SQLite, and server-side file processing.
- Treating this as a package would add release complexity without improving the product workflow.

## Verification Gates

- File preservation and git ignore checks for `.env`, model binaries, and SQLite data.
- Backend import, compile, auth, protected-route, ingest, and config tests.
- Frontend syntax, UI, auth, authorized fetch, and Markdown sanitization tests.
- App import/startup smoke.
- Browser smoke against the served UI.
- Security scans where tooling is available.
