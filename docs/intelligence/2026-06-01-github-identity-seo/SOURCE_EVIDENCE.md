# Source Evidence for Public Identity Claims

This file lists the repo facts used to update public docs and metadata. Every behavior claim below is backed by the inspected source path and line.

## Runtime Shape

- `voice_agent_backend/app/main.py:41` defines the FastAPI app title as `Voice Agent API`.
- `voice_agent_backend/app/main.py:102-109` registers the chat, auth, ingest, STT, collections, health, models, and TTS routers.
- `voice_agent_backend/app/main.py:122` mounts the same-origin frontend from `voice_agent_backend/frontend/`.
- `voice_agent_backend/frontend/index.html:8` describes the UI as `VoiceRAG Agent` with FastAPI, LangGraph, Qdrant, Ollama embeddings, Groq STT/chat, Kokoro ONNX TTS, and vanilla JavaScript.

## AI, RAG, Voice, and Storage Claims

- `.env.example:23-26` exposes Groq, Ollama, and Qdrant service configuration placeholders.
- `.env.example:29-33` configures chat provider/model and the Ollama embedding model.
- `.env.example:38` sets the default Qdrant collection name.
- `.env.example:52-56` documents Kokoro mode, model path, voices path, and language code placeholders.
- `voice_agent_backend/app/core/config.py:61-64` defines Ollama, Qdrant, Groq, and Groq API key settings.
- `voice_agent_backend/app/core/config.py:68-75` defines embedding model, chat provider, and default collection settings.
- `voice_agent_backend/app/core/config.py:92-100` defines Kokoro mode and local model/voice artifact paths.
- `voice_agent_backend/app/core/config.py:132` allows an optional `DATABASE_URL`; `.env.example:14` leaves it blank so the local SQLite path is used by default.

## API Surface and Auth Boundary

- `voice_agent_backend/app/api/routes/auth.py:20-40` provides `/auth/register` and `/auth/login`.
- `voice_agent_backend/app/api/routes/chat.py:52`, `chat.py:292`, `chat.py:329`, `chat.py:354`, and `chat.py:489` define the chat, predictive RAG, backchannel, streaming graph, and interrupt routes.
- `voice_agent_backend/app/api/routes/ingest.py:421-428` defines protected document ingestion with `Depends(get_current_user)`.
- `voice_agent_backend/app/api/routes/collections.py:17-69` defines collection listing plus protected create/delete and document-delete routes.
- `voice_agent_backend/app/api/routes/stt.py:8` defines the STT endpoint.
- `voice_agent_backend/app/api/routes/tts.py:17-25` defines Kokoro TTS audio streaming.
- `voice_agent_backend/app/api/routes/health.py:10` defines `/health`.
- `voice_agent_backend/app/api/routes/models.py:34` defines `/models`.

## Frontend and Safety Claims

- `voice_agent_backend/frontend/script.js:482` calls `/chat/stream` for the primary streaming workflow.
- `voice_agent_backend/frontend/script.js:545`, `script.js:572`, `script.js:1816`, and `script.js:1834` route assistant-rendered Markdown through `renderMarkdownSafe()`.
- `voice_agent_backend/frontend/script.js:1356-1362` implements `renderMarkdownSafe()` using `marked` and `DOMPurify`.
- `voice_agent_backend/frontend/script.js:1957` sends document uploads to `/ingest` through the authenticated fetch wrapper.
- `voice_agent_backend/frontend/script.js:2242`, `script.js:2262`, and `script.js:2375` use authenticated collection mutation calls.

## Verification and Maintenance Claims

- `.github/workflows/ci.yml:1-47` defines CI for Node syntax checks, Python syntax checks, backend/frontend tests, pytest collection, and import smoke.
- `.github/workflows/codeql.yml:1-24` defines CodeQL analysis for Python and JavaScript/TypeScript.
- `.github/dependabot.yml:1-25` schedules pip and GitHub Actions dependency update checks.
- `voice_agent_backend/tests/backend/test_auth_and_protection.py:57-120` verifies auth routes, protected collection creation, protected ingestion, and sanitized ingestion behavior.
- `voice_agent_backend/tests/frontend/test_frontend.py:147-152` verifies the frontend title, and `test_frontend.py:443-497` verifies auth modal, token persistence, and authorized write behavior.

## Public-Claim Boundaries

- The project can be described as **local-first/self-hosted**, but not fully offline by default, because `.env.example:23-25` and `voice_agent_backend/app/core/config.py:63-64` include Groq cloud API configuration.
- The project should not be described as hosted, deployed, benchmarked, enterprise-ready, or fully offline because no source file or current verification evidence proves those claims.
- The GitHub social preview asset exists in-repo, but GitHub's upload is a repository settings action and is not controlled by committed files.
