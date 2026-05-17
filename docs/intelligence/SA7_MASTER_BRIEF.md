# SA-7: Master Brief

## 1. What Is This System?
This is a local full-stack voice-agent/RAG assistant. It serves a vanilla browser frontend from FastAPI, supports typed and spoken chat, can ingest documents into Qdrant, retrieves context with Ollama embeddings, generates answers with Groq or Ollama, transcribes audio with Groq, and synthesizes speech with Kokoro/native or sidecar paths. The app boundary is `voice_agent_backend/app/main.py:41`.

Technology stack: FastAPI, Uvicorn, Pydantic, SQLAlchemy, aiosqlite, httpx, SlowAPI, python-jose/passlib, LangGraph, LangChain core, Qdrant, Ollama, Groq, Kokoro ONNX, vanilla HTML/CSS/JavaScript, Playwright-based frontend tests.

## 2. How Does It Work?
A browser opens `/`, served by StaticFiles at `voice_agent_backend/app/main.py:121`. API calls pass middleware and route into chat, ingest, STT, collection, model, health, or TTS handlers. Chat state is process-local memory. RAG searches Qdrant vectors created from Ollama embeddings. Groq or Ollama streams model output. Kokoro/browser audio paths turn text into speech.

```text
Browser SPA -> FastAPI middleware -> route handler
/chat/stream -> SessionMemory -> LangGraph -> RAG/Qdrant/Ollama -> Groq/Ollama -> SSE/audio
/ingest -> UploadFile -> extract/chunk -> Ollama embed -> Qdrant upsert
/collections -> Qdrant REST helpers -> JSON
/stt -> Groq transcription -> JSON
/tts/generate -> SpeechService/Kokoro -> audio
```

The three most important paths are `/chat/stream` at `voice_agent_backend/app/api/routes/chat.py:353`, `/ingest` at `voice_agent_backend/app/api/routes/ingest.py:396`, and `/collections` at `voice_agent_backend/app/api/routes/collections.py:15`. Auth endpoints exist in `voice_agent_backend/app/api/routes/auth.py` but are not mounted by `voice_agent_backend/app/main.py`.

## 3. What Are All The Components?
| Method | Path | File | Handler | Auth | Rate Limit |
| --- | --- | --- | --- | --- | --- |
| POST | /auth/register | voice_agent_backend/app/api/routes/auth.py:20 | register | no explicit dependency | no |
| POST | /auth/login | voice_agent_backend/app/api/routes/auth.py:39 | login | no explicit dependency | no |
| POST | /chat | voice_agent_backend/app/api/routes/chat.py:52 | chat_endpoint | no explicit dependency | yes |
| POST | /chat/predict | voice_agent_backend/app/api/routes/chat.py:291 | chat_predict_endpoint | no explicit dependency | no |
| POST | /chat/backchannel/{session_id} | voice_agent_backend/app/api/routes/chat.py:328 | chat_backchannel_endpoint | no explicit dependency | no |
| POST | /chat/stream | voice_agent_backend/app/api/routes/chat.py:353 | chat_stream_endpoint | no explicit dependency | yes |
| POST | /chat/interrupt/{thread_id} | voice_agent_backend/app/api/routes/chat.py:488 | interrupt_endpoint | no explicit dependency | yes |
| GET | /collections | voice_agent_backend/app/api/routes/collections.py:15 | get_collections | no explicit dependency | no |
| POST | /collections | voice_agent_backend/app/api/routes/collections.py:25 | create_collection_endpoint | no explicit dependency | no |
| DELETE | /collections/{collection_name} | voice_agent_backend/app/api/routes/collections.py:39 | delete_collection_endpoint | no explicit dependency | no |
| GET | /collections/{collection_name}/documents | voice_agent_backend/app/api/routes/collections.py:51 | get_documents | no explicit dependency | no |
| DELETE | /collections/{collection_name}/documents/{filename} | voice_agent_backend/app/api/routes/collections.py:61 | delete_document | no explicit dependency | no |
| GET | /health | voice_agent_backend/app/api/routes/health.py:10 | health | no explicit dependency | no |
| POST | /ingest | voice_agent_backend/app/api/routes/ingest.py:396 | ingest_endpoint | no explicit dependency | yes |
| GET | /models | voice_agent_backend/app/api/routes/models.py:34 | list_available_models | no explicit dependency | no |
| POST | /stt | voice_agent_backend/app/api/routes/stt.py:8 | speech_to_text | no explicit dependency | no |
| POST | /tts/generate | voice_agent_backend/app/api/routes/tts.py:17 | generate_tts | no explicit dependency | no |

## Module Index
| File | LOC | Role |
| --- | --- | --- |
| docs/intelligence/_generate_docs.py | 538 | Python backend |
| voice_agent_backend/app/__init__.py | 0 | Python backend |
| voice_agent_backend/app/api/__init__.py | 0 | Python backend |
| voice_agent_backend/app/api/routes/__init__.py | 0 | Python backend |
| voice_agent_backend/app/api/routes/auth.py | 52 | Python backend |
| voice_agent_backend/app/api/routes/chat.py | 543 | Python backend |
| voice_agent_backend/app/api/routes/collections.py | 75 | Python backend |
| voice_agent_backend/app/api/routes/health.py | 33 | Python backend |
| voice_agent_backend/app/api/routes/ingest.py | 446 | Python backend |
| voice_agent_backend/app/api/routes/models.py | 74 | Python backend |
| voice_agent_backend/app/api/routes/stt.py | 26 | Python backend |
| voice_agent_backend/app/api/routes/tts.py | 27 | Python backend |
| voice_agent_backend/app/core/__init__.py | 0 | Python backend |
| voice_agent_backend/app/core/agents/supervisor.py | 76 | Python backend |
| voice_agent_backend/app/core/agents/ultrathink_critic.py | 70 | Python backend |
| voice_agent_backend/app/core/auth.py | 69 | Python backend |
| voice_agent_backend/app/core/config.py | 163 | Python backend |
| voice_agent_backend/app/core/correlator.py | 53 | Python backend |
| voice_agent_backend/app/core/database.py | 23 | Python backend |
| voice_agent_backend/app/core/graph_state.py | 81 | Python backend |
| voice_agent_backend/app/core/intent.py | 271 | Python backend |
| voice_agent_backend/app/core/langchain_rag.py | 361 | Python backend |
| voice_agent_backend/app/core/limiter.py | 9 | Python backend |
| voice_agent_backend/app/core/memory.py | 73 | Python backend |
| voice_agent_backend/app/core/nodes/__init__.py | 1 | Python backend |
| voice_agent_backend/app/core/nodes/check_confidence.py | 87 | Python backend |
| voice_agent_backend/app/core/nodes/check_interrupt.py | 52 | Python backend |
| voice_agent_backend/app/core/nodes/classify_intent.py | 76 | Python backend |
| voice_agent_backend/app/core/nodes/generate_response.py | 223 | Python backend |
| voice_agent_backend/app/core/nodes/handle_early_exit.py | 137 | Python backend |
| voice_agent_backend/app/core/nodes/retrieve_context.py | 52 | Python backend |
| voice_agent_backend/app/core/nodes/search_web.py | 62 | Python backend |
| voice_agent_backend/app/core/nodes/synthesize_speech.py | 53 | Python backend |
| voice_agent_backend/app/core/nodes/translate_input.py | 54 | Python backend |
| voice_agent_backend/app/core/nodes/update_context.py | 86 | Python backend |
| voice_agent_backend/app/core/onnx_runtime.py | 67 | Python backend |
| voice_agent_backend/app/core/translation.py | 54 | Python backend |
| voice_agent_backend/app/core/voice_graph.py | 146 | Python backend |
| voice_agent_backend/app/main.py | 126 | Python backend |
| voice_agent_backend/app/middleware/logging.py | 32 | Python backend |
| voice_agent_backend/app/models/__init__.py | 0 | Python backend |
| voice_agent_backend/app/models/schemas.py | 63 | Python backend |
| voice_agent_backend/app/models/user.py | 21 | Python backend |
| voice_agent_backend/app/services/__init__.py | 0 | Python backend |
| voice_agent_backend/app/services/groq_service.py | 148 | Python backend |
| voice_agent_backend/app/services/http_client.py | 32 | Python backend |
| voice_agent_backend/app/services/llm_router.py | 34 | Python backend |
| voice_agent_backend/app/services/ollama_service.py | 132 | Python backend |
| voice_agent_backend/app/services/qdrant_service.py | 246 | Python backend |
| voice_agent_backend/app/services/speech_service.py | 464 | Python backend |
| voice_agent_backend/context.md | 302 | Frontend/static/docs/config |
| voice_agent_backend/Dockerfile | 12 | Frontend/static/docs/config |
| voice_agent_backend/file_str.md | 101 | Frontend/static/docs/config |
| voice_agent_backend/frontend/index.html | 366 | Frontend/static/docs/config |
| voice_agent_backend/frontend/script.js | 2253 | Frontend/static/docs/config |
| voice_agent_backend/frontend/style.css | 1494 | Frontend/static/docs/config |
| voice_agent_backend/HANDOFF_README.md | 270 | Frontend/static/docs/config |
| voice_agent_backend/plan.md | 1495 | Frontend/static/docs/config |
| voice_agent_backend/requirements.txt | 29 | Frontend/static/docs/config |
| voice_agent_backend/scratch/benchmark_tts.py | 141 | Python backend |
| voice_agent_backend/scratch/inspect_kokoro.py | 8 | Python backend |
| voice_agent_backend/scratch/sim_scoring.py | 25 | Python backend |
| voice_agent_backend/scratch/test_chunking.py | 66 | Python backend |
| voice_agent_backend/scratch/test_hardware.py | 39 | Python backend |
| voice_agent_backend/scratch/test_normalization.py | 68 | Python backend |
| voice_agent_backend/scratch/test_pipeline.py | 66 | Python backend |
| voice_agent_backend/scratch/test_rag.py | 32 | Python backend |
| voice_agent_backend/scratch/test_speech_norm.py | 39 | Python backend |
| voice_agent_backend/scripts/check_backend_health.py | 31 | Python backend |
| voice_agent_backend/scripts/test_imports.py | 74 | Python backend |
| voice_agent_backend/scripts/test_search_node.py | 37 | Python backend |
| voice_agent_backend/scripts/verify_kokoro.py | 52 | Python backend |
| voice_agent_backend/sop(voice_agent).md | 100 | Frontend/static/docs/config |
| voice_agent_backend/start_server.bat | 18 | Frontend/static/docs/config |
| voice_agent_backend/start_server.sh | 14 | Frontend/static/docs/config |
| voice_agent_backend/test_graph.py | 23 | Python backend |
| voice_agent_backend/tests/__init__.py | 0 | Python backend |
| voice_agent_backend/tests/test_frontend.py | 427 | Python backend |

## 4. What Does The Data Look Like?
SQLite has `users` and `user_sessions` tables. Pydantic request models define chat, stream chat, collection create, document info, ingest response, interrupt, auth, and TTS payloads. Qdrant payloads represent document chunks with text/source/chunk/page/section metadata. Client localStorage stores local documents, conversation, retrieval history, sessions, and session id under `ssa_` keys.

## 5. What Can Go Wrong?
The biggest issues are disconnected auth router, unauthenticated mutating routes, fallback JWT secret, hidden Qdrant write failures, graph streaming task errors, unsanitized Markdown-to-innerHTML rendering, process-local state, missing env template, raw filename use after sanitization is computed, and weak backend test coverage.

## 6. What Is Not Tested?
Backend route handlers, auth mounting, rate limits, collection delete protection, Qdrant failure semantics, ingest partial failure, STT/TTS fallback behavior, LangGraph routing, stream disconnects, database FK behavior, and real provider health are not covered by discovered automated tests. The frontend test suite mocks APIs and does not assert the real default `/chat/stream` success path.

## 7. What Is Missing Or Incomplete?
No `.env.example` exists despite startup references. No migration system exists. Auth UI/docs and backend auth router are disconnected. Predictive RAG appears stored but not consumed. Some graph routing paths are partially wired. Git history is unavailable because the checkout is not a git repository.

## 8. How Do You Run This System?
From `voice_agent_backend`: install dependencies with `python -m pip install -r requirements.txt`; start Qdrant on port 6333; configure `.env` with at least Groq and secret settings; start with `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`, `start_server.bat`, or `bash start_server.sh`; open `http://localhost:8000`. Run collection with `python -m pytest --collect-only -q`; run frontend tests with `python -m pytest tests/test_frontend.py -v` if pytest and Playwright dependencies are installed.

## Risk Summary
| ID | Severity | Category | Location | Description | Recommended Fix |
| --- | --- | --- | --- | --- | --- |
| R-001 | HIGH | Routing/Auth | voice_agent_backend/app/main.py:102 | Auth router is imported but not mounted; register/login endpoints are not live through the app entrypoint. | Include auth.router or remove disconnected auth UI/docs. |
| R-002 | HIGH | Authorization | voice_agent_backend/app/api/routes/collections.py:39 | Unauthenticated write/delete routes can mutate Qdrant collections and documents. | Protect write/delete routes or explicitly document guest-only local trust boundary. |
| R-003 | HIGH | Secrets | voice_agent_backend/app/core/config.py:124 | A fallback JWT secret lets the app start insecurely if production env omits SECRET_KEY. | Fail startup when SECRET_KEY is default outside local dev. |
| R-004 | HIGH | Data Integrity | voice_agent_backend/app/api/routes/ingest.py:390 | Ingest ignores Qdrant upsert response; failed vector writes can still return success. | Check and propagate Qdrant write failures. |
| R-005 | MEDIUM | Streaming | voice_agent_backend/app/api/routes/chat.py:456 | Graph task is created without await/cancel plumbing; exceptions can leave SSE waiting. | Capture task exceptions, cancel on disconnect, and always signal done. |
| R-006 | MEDIUM | Frontend Security | voice_agent_backend/frontend/script.js:1195 | Markdown is rendered into innerHTML without sanitizer. | Sanitize LLM Markdown output before DOM insertion. |
| R-007 | MEDIUM | State | voice_agent_backend/app/core/memory.py:13 | Session/cache/checkpoint state is process-local and not multi-worker safe. | Use durable storage or document single-worker limitation. |
| R-008 | MEDIUM | Config Drift | voice_agent_backend/start_server.bat:8 | Scripts mention .env.example, but no template exists in the live file tree. | Create a sanitized env template. |
| R-009 | MEDIUM | Data Integrity | voice_agent_backend/app/api/routes/ingest.py:422 | safe_filename is computed but raw filename remains in payload/source paths. | Use sanitized filename consistently. |
| R-010 | MEDIUM | Testing | voice_agent_backend/tests/test_frontend.py:4 | Tests mock frontend APIs and do not exercise backend routes/providers. | Add backend route and service tests with mocked providers. |
