# SA-2: Backend Report

> Historical snapshot: this file is preserved from an earlier audit and may contain superseded route/auth findings. Use `docs/architecture/README.md`, `docs/features/README.md`, and `docs/operations/VERIFICATION_MATRIX.md` for current contribution planning.

## Summary
The live FastAPI app includes `chat`, `ingest`, `stt`, `collections`, `health`, `models`, and `tts` routers at `voice_agent_backend/app/main.py:102` through `voice_agent_backend/app/main.py:108`. `auth` is imported at `voice_agent_backend/app/main.py:15`, and auth routes exist at `voice_agent_backend/app/api/routes/auth.py:20` and `voice_agent_backend/app/api/routes/auth.py:39`, but the auth router is not included.

## Complete Route Inventory
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

## Auth And Rate Limits
`get_current_user()` validates JWT bearer tokens at `voice_agent_backend/app/core/auth.py:40`, but no included route depends on it. SlowAPI is configured at `voice_agent_backend/app/core/limiter.py:5` and attached at `voice_agent_backend/app/main.py:42`. Only `/chat`, `/chat/stream`, `/chat/interrupt`, and `/ingest` have rate decorators.

## Validation Report
`ChatRequest` validates session/message/collection/language at `voice_agent_backend/app/models/schemas.py:5`. `ChatStreamRequest` validates the same core fields at `voice_agent_backend/app/models/schemas.py:41`, but TTS controls are plain fields at `voice_agent_backend/app/models/schemas.py:55`. `/ingest` reads the entire uploaded file before size validation at `voice_agent_backend/app/api/routes/ingest.py:408`, validates extension at `voice_agent_backend/app/api/routes/ingest.py:416`, computes `safe_filename` at `voice_agent_backend/app/api/routes/ingest.py:423`, but still stores/returns raw `file.filename` at `voice_agent_backend/app/api/routes/ingest.py:432` and `voice_agent_backend/app/api/routes/ingest.py:438`.

## Middleware Analysis
Security headers are added in `voice_agent_backend/app/main.py:23`. Audit logging avoids request bodies and logs request metadata in `voice_agent_backend/app/middleware/logging.py:13` and `voice_agent_backend/app/middleware/logging.py:22`. CORS is hardcoded in `voice_agent_backend/app/main.py:94` even though settings define CORS origins separately.

## Service Layer Analysis
| Service | LOC | Primary Role |
| --- | --- | --- |
| app/services/groq_service.py | 148 | Groq chat/STT/models/health |
| app/services/ollama_service.py | 132 | Ollama embeddings/chat/models/health |
| app/services/qdrant_service.py | 246 | Qdrant collection, search, upsert, delete |
| app/services/speech_service.py | 464 | Kokoro/browser-side voice pipeline helpers |
| app/services/http_client.py | 32 | Shared HTTPX client pool |
| app/services/llm_router.py | 34 | Provider routing between Groq/Ollama |

## Error Handling Report
Qdrant helpers often convert connection/status errors into empty dictionaries, for example helper exception paths in `voice_agent_backend/app/services/qdrant_service.py:20`, `voice_agent_backend/app/services/qdrant_service.py:35`, and `voice_agent_backend/app/services/qdrant_service.py:50`. The global exception handler sanitizes unknown failures at `voice_agent_backend/app/main.py:80`, but several route handlers return raw exception text in `HTTPException(detail=str(e))` style paths.

## Streaming Behavior
Legacy `/chat` emits SSE token frames at `voice_agent_backend/app/api/routes/chat.py:249` through `voice_agent_backend/app/api/routes/chat.py:259`. LangGraph `/chat/stream` creates a queue, backchannel task, and graph task around `voice_agent_backend/app/api/routes/chat.py:413`, `voice_agent_backend/app/api/routes/chat.py:439`, and `voice_agent_backend/app/api/routes/chat.py:456`. The graph task is not awaited or cancelled in the loop, so exceptions can leave a hanging stream.

## Routing Logic Map
The graph registers nodes in `voice_agent_backend/app/core/voice_graph.py:41` and starts at `translate_input` in `voice_agent_backend/app/core/voice_graph.py:53`. `check_interrupt` routes to `supervisor`; standalone `classify_intent_node` exists but is not added to the graph. Complex document/general queries can route to ultrathink directly, which may bypass retrieval if the supervisor promotes the intent before RAG.

## Business Logic Bugs
1. HIGH: Auth endpoints are not live through `app.main` because `auth.router` is not included.
2. HIGH: Unauthenticated collection delete and ingest routes mutate Qdrant data.
3. HIGH: Qdrant write failures can be hidden because helpers return empty results and ingest does not inspect upsert response.
4. MEDIUM: `/chat/stream` graph task can fail without signaling the SSE queue.
5. MEDIUM: CORS settings exist in config but `main.py` uses hardcoded origins.
6. MEDIUM: Process-local caches and memory can drift across workers.
7. MEDIUM: `/stt` uses direct Groq service instead of fallback-capable `SpeechService.transcribe()`.

## Test Coverage
The only `voice_agent_backend/tests` file is frontend-focused and mocks API responses. Backend tests are missing for auth mounting, rate limits, collection delete protection, ingest failure semantics, SSE disconnect/error behavior, LangGraph routing, Qdrant failure handling, and STT/TTS fallback behavior.

## Backend Evidence Appendix

- `docs/intelligence/_generate_docs.py:163`: if re.search(r"class .*BaseModel|class .*Base\)|mapped_column\(|ForeignKey\(|Base\.metadata|create_all", line):

- `docs/intelligence/_generate_docs.py:169`: if re.search(r"select\(|db\.execute|commit\(|create_all|_qdrant_|search_vectors|upsert_points|scroll|points/delete", line):

- `voice_agent_backend/app/api/routes/auth.py:23`: result = await db.execute(select(User).where(User.email == user_data.email))

- `voice_agent_backend/app/api/routes/auth.py:33`: await db.commit()

- `voice_agent_backend/app/api/routes/auth.py:41`: result = await db.execute(select(User).where(User.email == form_data.username))

- `voice_agent_backend/app/api/routes/ingest.py:4`: from app.services.qdrant_service import create_collection, upsert_points

- `voice_agent_backend/app/api/routes/ingest.py:391`: await upsert_points(collection, points)

- `voice_agent_backend/app/core/auth.py:65`: result = await db.execute(select(User).where(User.email == email))

- `voice_agent_backend/app/core/database.py:23`: await conn.run_sync(Base.metadata.create_all)

- `voice_agent_backend/app/core/langchain_rag.py:9`: from app.services.qdrant_service import search_vectors

- `voice_agent_backend/app/core/langchain_rag.py:322`: search_vectors(collection, emb, fetch_k, score_threshold)

- `voice_agent_backend/app/services/qdrant_service.py:13`: async def _qdrant_get(path: str, timeout: float = 10.0) -> dict:

- `voice_agent_backend/app/services/qdrant_service.py:28`: async def _qdrant_post(path: str, payload: dict, timeout: float = 30.0) -> dict:

- `voice_agent_backend/app/services/qdrant_service.py:43`: async def _qdrant_put(path: str, payload: dict, timeout: float = 30.0) -> dict:

- `voice_agent_backend/app/services/qdrant_service.py:58`: async def _qdrant_delete(path: str, timeout: float = 10.0) -> dict:

- `voice_agent_backend/app/services/qdrant_service.py:78`: data = await _qdrant_get("/collections")

- `voice_agent_backend/app/services/qdrant_service.py:98`: return await _qdrant_put(f"/collections/{name}", payload)

- `voice_agent_backend/app/services/qdrant_service.py:104`: return await _qdrant_delete(f"/collections/{name}")

- `voice_agent_backend/app/services/qdrant_service.py:140`: data = await _qdrant_post(

- `voice_agent_backend/app/services/qdrant_service.py:141`: f"/collections/{collection}/points/scroll", payload

- `voice_agent_backend/app/services/qdrant_service.py:175`: return await _qdrant_post(

- `voice_agent_backend/app/services/qdrant_service.py:176`: f"/collections/{collection}/points/delete", payload

- `voice_agent_backend/app/services/qdrant_service.py:183`: async def upsert_points(collection: str, points: list[dict]) -> dict:

- `voice_agent_backend/app/services/qdrant_service.py:196`: return await _qdrant_put(

- `voice_agent_backend/app/services/qdrant_service.py:201`: async def search_vectors(

- `voice_agent_backend/app/services/qdrant_service.py:217`: data = await _qdrant_post(

- `docs/intelligence/_generate_docs.py:142`: if "fetch(" in line:

- `docs/intelligence/_generate_docs.py:175`: if re.search(r"httpx\.|fetch\(|Authorization|GROQ|OLLAMA|QDRANT|KOKORO|duckduckgo|TAVILY", line):

- `docs/intelligence/_generate_docs.py:225`: ("R-002", "HIGH", "Authorization", "voice_agent_backend/app/api/routes/collections.py:39", "Unauthenticated write/delete routes can mutate Qdrant collections and documents.", "Prot

- `docs/intelligence/_generate_docs.py:283`: ("duckduckgo-search", "Web search integration"),

- `docs/intelligence/_generate_docs.py:360`: "## Auth And LocalStorage\nThe script has an auth-module heading at `voice_agent_backend/frontend/script.js:51`, but no implemented AUTH object, login form logic, fetch interceptor

- `docs/intelligence/_generate_docs.py:387`: ("Groq", "`settings.GROQ_BASE`, default `https://api.groq.com/openai/v1`", "Bearer `GROQ_API_KEY`", "httpx call-level/shared client", "no central retry found", "service/route excep

- `docs/intelligence/_generate_docs.py:388`: ("Ollama", "`settings.OLLAMA_BASE`, default `http://localhost:11434`", "none/local", "httpx call-level/shared client", "no central retry found", "empty model list/offline health/er

- `docs/intelligence/_generate_docs.py:389`: ("Qdrant", "`settings.QDRANT_BASE`, default `http://localhost:6333`", "none observed", "10-30 second helper timeouts", "no central retry found", "empty dict/results or route error"

- `docs/intelligence/_generate_docs.py:390`: ("Kokoro native ONNX", "`KOKORO_MODEL_PATH`, `KOKORO_VOICES_PATH`", "local file assets", "startup/runtime load time", "fallback depends on mode", "TTS warning/degradation"),

- `docs/intelligence/_generate_docs.py:391`: ("Kokoro Docker sidecar", "`KOKORO_DOCKER_URL`", "none/local", "httpx/service specific", "no central retry found", "TTS error/degradation"),

- `docs/intelligence/_generate_docs.py:392`: ("DuckDuckGo/Tavily", "`SEARCH_PROVIDER`, `TAVILY_API_KEY`", "Tavily API key if used", "provider specific", "not centrally observed", "search node fallback/error"),

- `docs/intelligence/_generate_docs.py:395`: "## LLM Integration Details\nGroq chat builds chat-completion URLs from `settings.GROQ_BASE` in `voice_agent_backend/app/services/groq_service.py:25` and sends bearer auth from `se

- `docs/intelligence/_generate_docs.py:400`: "## Environment Variable Completeness\n" + table(["Var", "Defined At", "Used At", "Default / Example", "Risk If Missing"], [(name, where, ", ".join(settings_use.get(name, [])[:5])

- `docs/intelligence/_generate_docs.py:409`: "## Authentication/Authorization Audit\n" + table(["Endpoint", "Auth Required", "Rate Limit", "Risk"], [(f"{m} {path}", auth, rate, "high write/delete risk" if m in {"POST", "DELET

- `docs/intelligence/_generate_docs.py:415`: "## Dependency Vulnerabilities\nThe requirements use lower bounds (`>=`) rather than exact pins, so the vulnerability posture depends on the installed environment. High-impact pack

- `docs/intelligence/_generate_docs.py:458`: "## Config/Env Index\n" + table(["Var", "Defined At", "Where Used", "Required/Optional", "Default"], [(name, where, ", ".join(settings_use.get(name, [])[:8]) or "no direct settings

- `docs/intelligence/_generate_docs.py:460`: ("Groq", "GROQ_API_KEY", "route/service exception or health offline", "no central retry found"),

- `docs/intelligence/_generate_docs.py:464`: ("DuckDuckGo/Tavily", "TAVILY_API_KEY if Tavily selected", "search degradation/error", "not centrally determined"),

- `voice_agent_backend/app/api/routes/models.py:22`: model_path = Path(settings.KOKORO_MODEL_PATH)

- `voice_agent_backend/app/core/config.py:58`: OLLAMA_BASE: str = "http://localhost:11434"

- `voice_agent_backend/app/core/config.py:59`: QDRANT_BASE: str = "http://localhost:6333"

- `voice_agent_backend/app/core/config.py:60`: GROQ_BASE: str = "https://api.groq.com/openai/v1"

- `voice_agent_backend/app/core/config.py:61`: GROQ_API_KEY: str = ""

- `voice_agent_backend/app/core/config.py:89`: KOKORO_MODE: str = "native"

- `voice_agent_backend/app/core/config.py:91`: KOKORO_DOCKER_URL: str = "http://127.0.0.1:8880"

- `voice_agent_backend/app/core/config.py:93`: KOKORO_MODEL_PATH: str = "../kokoro-v1.0.onnx"

- `voice_agent_backend/app/core/config.py:95`: KOKORO_VOICES_PATH: str = "../voices-v1.0.bin"

- `voice_agent_backend/app/core/config.py:97`: KOKORO_LANG_CODE: str = "a"

- `voice_agent_backend/app/core/config.py:116`: SEARCH_PROVIDER: str = "duckduckgo" # "duckduckgo" or "tavily"

- `voice_agent_backend/app/core/config.py:117`: TAVILY_API_KEY: str = ""

- `voice_agent_backend/app/core/config.py:137`: @field_validator("KOKORO_MODEL_PATH", "KOKORO_VOICES_PATH", mode="before")

- `voice_agent_backend/app/core/nodes/search_web.py:7`: from duckduckgo_search import DDGS

- `voice_agent_backend/app/main.py:60`: if getattr(settings, "KOKORO_MODE", "native") == "native":

- `voice_agent_backend/app/services/groq_service.py:25`: url = f"{settings.GROQ_BASE}/chat/completions"

- `voice_agent_backend/app/services/groq_service.py:27`: "Authorization": f"Bearer {settings.GROQ_API_KEY}",

- `voice_agent_backend/app/services/groq_service.py:87`: url = f"{settings.GROQ_BASE}/audio/transcriptions"

- `voice_agent_backend/app/services/groq_service.py:89`: "Authorization": f"Bearer {settings.GROQ_API_KEY}",

- `voice_agent_backend/app/services/groq_service.py:124`: url = f"{settings.GROQ_BASE}/models"

- `voice_agent_backend/app/services/groq_service.py:125`: headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

- `voice_agent_backend/app/services/groq_service.py:139`: url = f"{settings.GROQ_BASE}/models"

- `voice_agent_backend/app/services/groq_service.py:140`: headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

- `voice_agent_backend/app/services/http_client.py:11`: _client: Optional[httpx.AsyncClient] = None

- `voice_agent_backend/app/services/http_client.py:14`: async def get_client(cls) -> httpx.AsyncClient:

- `voice_agent_backend/app/services/http_client.py:17`: cls._client = httpx.AsyncClient(
