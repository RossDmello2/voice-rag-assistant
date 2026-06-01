# Feature Catalog

Generated: 2026-06-01

This folder is the contributor-facing feature map for VoiceRAG Agent. It gives future contributors one place to understand current features before touching the runtime code. The application itself still uses the existing layered FastAPI structure; this folder documents feature ownership without moving core files.

## Current Features

| Feature | User outcome | Runtime owners | Tests | Security notes |
| --- | --- | --- | --- | --- |
| Auth | Register/login and store a bearer token for document writes | `voice_agent_backend/app/api/routes/auth.py`, `voice_agent_backend/app/core/auth.py`, `voice_agent_backend/app/models/user.py`, `voice_agent_backend/frontend/script.js` | `voice_agent_backend/tests/backend/test_auth_and_protection.py`, `voice_agent_backend/tests/frontend/test_frontend.py` | Tokens protect write operations; do not broaden or remove protection without an explicit security decision. |
| Chat SSE | Stream assistant responses from text input | `voice_agent_backend/app/api/routes/chat.py`, `voice_agent_backend/app/services/llm_router.py`, `voice_agent_backend/frontend/script.js` | Frontend chat smoke tests in `voice_agent_backend/tests/frontend/test_frontend.py` | Chat is public by local-first design; internet deployments should revisit auth/cost controls. |
| LangGraph voice pipeline | Translate, classify, retrieve, generate, update memory, and stream voice-oriented events | `voice_agent_backend/app/core/voice_graph.py`, `voice_agent_backend/app/core/graph_state.py`, `voice_agent_backend/app/core/nodes/` | `python scripts/manual_tests/graph_smoke.py` plus import smoke | Keep each node small and preserve graph state keys. |
| Document ingestion | Upload PDF/DOCX/TXT/CSV files, chunk text, embed, and write vectors | `voice_agent_backend/app/api/routes/ingest.py`, `voice_agent_backend/app/services/qdrant_service.py`, `voice_agent_backend/app/services/ollama_service.py` | Backend ingest tests in `voice_agent_backend/tests/backend/test_auth_and_protection.py` | `/ingest` is bearer-protected; filenames must stay sanitized; vector writes must be acknowledged. |
| Collection management | List, create, delete collections and indexed documents | `voice_agent_backend/app/api/routes/collections.py`, `voice_agent_backend/app/services/qdrant_service.py`, `voice_agent_backend/frontend/script.js` | Backend protected-route tests and frontend token-header tests | Reads are public; create/delete operations require bearer auth. |
| Speech-to-text | Transcribe uploaded audio with Groq Whisper | `voice_agent_backend/app/api/routes/stt.py`, `voice_agent_backend/app/services/groq_service.py` | Import smoke; add endpoint tests before changing behavior | Public endpoint can spend provider credits if internet-exposed. |
| Text-to-speech | Generate Kokoro audio output | `voice_agent_backend/app/api/routes/tts.py`, `voice_agent_backend/app/services/speech_service.py`, `voice_agent_backend/app/core/onnx_runtime.py` | Manual Kokoro checks under `voice_agent_backend/scripts/checks/` and `scripts/manual_tests/` | Native model artifacts are local-only and ignored by git. |
| Health and model options | Show service status and available model choices | `voice_agent_backend/app/api/routes/health.py`, `voice_agent_backend/app/api/routes/models.py`, `voice_agent_backend/frontend/script.js` | Frontend health/status tests | Health currently reports dependency booleans; do not treat it as full hosted readiness. |
| Safe Markdown rendering | Render assistant Markdown without script/event handler injection | `voice_agent_backend/frontend/script.js`, `voice_agent_backend/frontend/index.html` | `test_agent_markdown_is_sanitized` in frontend tests | Assistant content must pass through `renderMarkdownSafe()` before DOM insertion. |

## New Feature Workflow

1. Pick the closest feature in the table above.
2. Write the intended behavior and owner files in the PR description.
3. Add schema changes in `app/models/` first when API inputs or outputs change.
4. Keep route code thin; put provider, vector-store, or TTS implementation details in `app/services/`.
5. Add or update a LangGraph node only when the feature needs graph orchestration.
6. Update the frontend only through the vanilla JavaScript app unless a framework migration is explicitly approved.
7. Add focused backend and/or frontend tests.
8. Update this catalog when the feature creates a new product capability or changes ownership.

## When To Create A Runtime `app/features/` Package

Do not add an empty runtime features package just for appearance. A future migration to `voice_agent_backend/app/features/<feature>/` is justified only when a feature owns enough routes, schemas, services, tests, and docs that the current layer-based structure becomes harder to navigate. If that migration happens, do it as its own refactor with no behavior changes and a full movement map.

## Required Checks

```bash
cd voice_agent_backend
python -m compileall app scripts tests
python -m pytest tests/backend tests/frontend -q
python scripts/checks/import_smoke.py
```

Run browser smoke testing for UI changes and provider smoke testing only when Qdrant, Ollama, Kokoro artifacts, and Groq credentials are available.
