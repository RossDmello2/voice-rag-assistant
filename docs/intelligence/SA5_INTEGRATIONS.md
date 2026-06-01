# SA-5: Integrations Report

## External Service Catalog
| Service | URL / Source | Auth | Timeout | Retry | Failure Behavior |
| --- | --- | --- | --- | --- | --- |
| Groq | `settings.GROQ_BASE`, default `https://api.groq.com/openai/v1` | Bearer `GROQ_API_KEY` | httpx call-level/shared client | no central retry found | service/route exceptions or offline health |
| Ollama | `settings.OLLAMA_BASE`, default `http://localhost:11434` | none/local | httpx call-level/shared client | no central retry found | empty model list/offline health/errors |
| Qdrant | `settings.QDRANT_BASE`, default `http://localhost:6333` | none observed | 10-30 second helper timeouts | no central retry found | empty dict/results or route error |
| Kokoro native ONNX | `KOKORO_MODEL_PATH`, `KOKORO_VOICES_PATH` | local file assets | startup/runtime load time | fallback depends on mode | TTS warning/degradation |
| Kokoro Docker sidecar | `KOKORO_DOCKER_URL` | none/local | httpx/service specific | no central retry found | TTS error/degradation |
| DuckDuckGo/Tavily | `SEARCH_PROVIDER`, `TAVILY_API_KEY` | Tavily API key if used | provider specific | not centrally observed | search node fallback/error |

## External HTTP Call Inventory
| File:Line | Evidence |
| --- | --- |
| docs/intelligence/_generate_docs.py:142 | if "fetch(" in line: |
| docs/intelligence/_generate_docs.py:175 | if re.search(r"httpx\.\|fetch\(\|Authorization\|GROQ\|OLLAMA\|QDRANT\|KOKORO\|duckduckgo\|TAVILY", line): |
| docs/intelligence/_generate_docs.py:225 | ("R-002", "HIGH", "Authorization", "voice_agent_backend/app/api/routes/collections.py:39", "Unauthenticated write/delete routes can mutate Qdrant collections and documents.", "Prot |
| docs/intelligence/_generate_docs.py:283 | ("duckduckgo-search", "Web search integration"), |
| docs/intelligence/_generate_docs.py:360 | "## Auth And LocalStorage\nThe script has an auth-module heading at `voice_agent_backend/frontend/script.js:51`, but no implemented AUTH object, login form logic, fetch interceptor |
| docs/intelligence/_generate_docs.py:387 | ("Groq", "`settings.GROQ_BASE`, default `https://api.groq.com/openai/v1`", "Bearer `GROQ_API_KEY`", "httpx call-level/shared client", "no central retry found", "service/route excep |
| docs/intelligence/_generate_docs.py:388 | ("Ollama", "`settings.OLLAMA_BASE`, default `http://localhost:11434`", "none/local", "httpx call-level/shared client", "no central retry found", "empty model list/offline health/er |
| docs/intelligence/_generate_docs.py:389 | ("Qdrant", "`settings.QDRANT_BASE`, default `http://localhost:6333`", "none observed", "10-30 second helper timeouts", "no central retry found", "empty dict/results or route error" |
| docs/intelligence/_generate_docs.py:390 | ("Kokoro native ONNX", "`KOKORO_MODEL_PATH`, `KOKORO_VOICES_PATH`", "local file assets", "startup/runtime load time", "fallback depends on mode", "TTS warning/degradation"), |
| docs/intelligence/_generate_docs.py:391 | ("Kokoro Docker sidecar", "`KOKORO_DOCKER_URL`", "none/local", "httpx/service specific", "no central retry found", "TTS error/degradation"), |
| docs/intelligence/_generate_docs.py:392 | ("DuckDuckGo/Tavily", "`SEARCH_PROVIDER`, `TAVILY_API_KEY`", "Tavily API key if used", "provider specific", "not centrally observed", "search node fallback/error"), |
| docs/intelligence/_generate_docs.py:395 | "## LLM Integration Details\nGroq chat builds chat-completion URLs from `settings.GROQ_BASE` in `voice_agent_backend/app/services/groq_service.py:25` and sends bearer auth from `se |
| docs/intelligence/_generate_docs.py:400 | "## Environment Variable Completeness\n" + table(["Var", "Defined At", "Used At", "Default / Example", "Risk If Missing"], [(name, where, ", ".join(settings_use.get(name, [])[:5])  |
| docs/intelligence/_generate_docs.py:409 | "## Authentication/Authorization Audit\n" + table(["Endpoint", "Auth Required", "Rate Limit", "Risk"], [(f"{m} {path}", auth, rate, "high write/delete risk" if m in {"POST", "DELET |
| docs/intelligence/_generate_docs.py:415 | "## Dependency Vulnerabilities\nThe requirements use lower bounds (`>=`) rather than exact pins, so the vulnerability posture depends on the installed environment. High-impact pack |
| docs/intelligence/_generate_docs.py:458 | "## Config/Env Index\n" + table(["Var", "Defined At", "Where Used", "Required/Optional", "Default"], [(name, where, ", ".join(settings_use.get(name, [])[:8]) or "no direct settings |
| docs/intelligence/_generate_docs.py:460 | ("Groq", "GROQ_API_KEY", "route/service exception or health offline", "no central retry found"), |
| docs/intelligence/_generate_docs.py:464 | ("DuckDuckGo/Tavily", "TAVILY_API_KEY if Tavily selected", "search degradation/error", "not centrally determined"), |
| voice_agent_backend/app/api/routes/models.py:22 | model_path = Path(settings.KOKORO_MODEL_PATH) |
| voice_agent_backend/app/core/config.py:58 | OLLAMA_BASE: str = "http://localhost:11434" |
| voice_agent_backend/app/core/config.py:59 | QDRANT_BASE: str = "http://localhost:6333" |
| voice_agent_backend/app/core/config.py:60 | GROQ_BASE: str = "https://api.groq.com/openai/v1" |
| voice_agent_backend/app/core/config.py:61 | GROQ_API_KEY: str = "" |
| voice_agent_backend/app/core/config.py:89 | KOKORO_MODE: str = "native" |
| voice_agent_backend/app/core/config.py:91 | KOKORO_DOCKER_URL: str = "http://127.0.0.1:8880" |
| voice_agent_backend/app/core/config.py:93 | KOKORO_MODEL_PATH: str = "../kokoro-v1.0.onnx" |
| voice_agent_backend/app/core/config.py:95 | KOKORO_VOICES_PATH: str = "../voices-v1.0.bin" |
| voice_agent_backend/app/core/config.py:97 | KOKORO_LANG_CODE: str = "a" |
| voice_agent_backend/app/core/config.py:116 | SEARCH_PROVIDER: str = "duckduckgo" # "duckduckgo" or "tavily" |
| voice_agent_backend/app/core/config.py:117 | TAVILY_API_KEY: str = "" |
| voice_agent_backend/app/core/config.py:137 | @field_validator("KOKORO_MODEL_PATH", "KOKORO_VOICES_PATH", mode="before") |
| voice_agent_backend/app/core/nodes/search_web.py:7 | from duckduckgo_search import DDGS |
| voice_agent_backend/app/main.py:60 | if getattr(settings, "KOKORO_MODE", "native") == "native": |
| voice_agent_backend/app/services/groq_service.py:25 | url = f"{settings.GROQ_BASE}/chat/completions" |
| voice_agent_backend/app/services/groq_service.py:27 | "Authorization": f"Bearer {settings.GROQ_API_KEY}", |
| voice_agent_backend/app/services/groq_service.py:87 | url = f"{settings.GROQ_BASE}/audio/transcriptions" |
| voice_agent_backend/app/services/groq_service.py:89 | "Authorization": f"Bearer {settings.GROQ_API_KEY}", |
| voice_agent_backend/app/services/groq_service.py:124 | url = f"{settings.GROQ_BASE}/models" |
| voice_agent_backend/app/services/groq_service.py:125 | headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"} |
| voice_agent_backend/app/services/groq_service.py:139 | url = f"{settings.GROQ_BASE}/models" |
| voice_agent_backend/app/services/groq_service.py:140 | headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"} |
| voice_agent_backend/app/services/http_client.py:11 | _client: Optional[httpx.AsyncClient] = None |
| voice_agent_backend/app/services/http_client.py:14 | async def get_client(cls) -> httpx.AsyncClient: |
| voice_agent_backend/app/services/http_client.py:17 | cls._client = httpx.AsyncClient( |
| voice_agent_backend/app/services/http_client.py:18 | timeout=httpx.Timeout(60.0, connect=10.0), |
| voice_agent_backend/app/services/http_client.py:19 | limits=httpx.Limits(max_connections=100, max_keepalive_connections=20), |
| voice_agent_backend/app/services/http_client.py:31 | async def get_http_client() -> httpx.AsyncClient: |
| voice_agent_backend/app/services/ollama_service.py:14 | url = f"{settings.OLLAMA_BASE}/api/embed" |
| voice_agent_backend/app/services/ollama_service.py:24 | except httpx.HTTPStatusError as e: |
| voice_agent_backend/app/services/ollama_service.py:60 | url = f"{settings.OLLAMA_BASE}/v1/chat/completions" |
| voice_agent_backend/app/services/ollama_service.py:110 | url = f"{settings.OLLAMA_BASE}/api/tags" |
| voice_agent_backend/app/services/ollama_service.py:123 | url = f"{settings.OLLAMA_BASE}/api/tags" |
| voice_agent_backend/app/services/qdrant_service.py:14 | url = f"{settings.QDRANT_BASE}{path}" |
| voice_agent_backend/app/services/qdrant_service.py:20 | except (httpx.ConnectError, httpx.TimeoutException) as e: |
| voice_agent_backend/app/services/qdrant_service.py:29 | url = f"{settings.QDRANT_BASE}{path}" |
| voice_agent_backend/app/services/qdrant_service.py:35 | except (httpx.ConnectError, httpx.TimeoutException) as e: |
| voice_agent_backend/app/services/qdrant_service.py:44 | url = f"{settings.QDRANT_BASE}{path}" |
| voice_agent_backend/app/services/qdrant_service.py:50 | except (httpx.ConnectError, httpx.TimeoutException) as e: |
| voice_agent_backend/app/services/qdrant_service.py:59 | url = f"{settings.QDRANT_BASE}{path}" |
| voice_agent_backend/app/services/qdrant_service.py:65 | except (httpx.ConnectError, httpx.TimeoutException) as e: |
| voice_agent_backend/app/services/qdrant_service.py:237 | url = f"{settings.QDRANT_BASE}/collections" |
| voice_agent_backend/app/services/speech_service.py:170 | model_path = getattr(settings, "KOKORO_MODEL_PATH", "../kokoro-v1.0.onnx") |
| voice_agent_backend/app/services/speech_service.py:171 | voices_path = getattr(settings, "KOKORO_VOICES_PATH", "../voices-v1.0.bin") |
| voice_agent_backend/app/services/speech_service.py:245 | voices_path = getattr(settings, "KOKORO_VOICES_PATH", "../voices-v1.0.bin") |
| voice_agent_backend/app/services/speech_service.py:302 | kokoro_mode = getattr(settings, "KOKORO_MODE", "native") |
| voice_agent_backend/app/services/speech_service.py:355 | docker_url = getattr(settings, "KOKORO_DOCKER_URL", "http://localhost:8880") |
| voice_agent_backend/app/services/speech_service.py:373 | docker_url = getattr(settings, "KOKORO_DOCKER_URL", "http://localhost:8880") |
| voice_agent_backend/app/services/speech_service.py:407 | groq_api_key = settings.GROQ_API_KEY |
| voice_agent_backend/app/services/speech_service.py:408 | groq_base = settings.GROQ_BASE |
| voice_agent_backend/app/services/speech_service.py:413 | "Authorization": f"Bearer {groq_api_key}", |
| voice_agent_backend/context.md:168 | Legacy local file link redacted; current source is `voice_agent_backend/app/services/http_client.py`. |
| voice_agent_backend/file_str.md:68 | Legacy local file link redacted; current source is `voice_agent_backend/app/services/http_client.py`. |
| voice_agent_backend/frontend/script.js:331 | fetch('/chat/stream', { |
| voice_agent_backend/frontend/script.js:462 | fetch('/chat/interrupt/' + this.activeThreadId, { |
| voice_agent_backend/frontend/script.js:605 | return fetch(url, merged).then(function (resp) { |
| voice_agent_backend/frontend/script.js:1311 | fetch('/chat/backchannel/' + getOrCreateSessionId(), { method: 'POST' }) |
| voice_agent_backend/frontend/script.js:1329 | fetch('/chat/predict', { |
| voice_agent_backend/frontend/script.js:1407 | fetch('/stt', { method: 'POST', body: formData }).then(function (r) { if (!r.ok) throw new Error('STT error ' + r.status); return r.json(); }).then(function (data) { |
| voice_agent_backend/frontend/script.js:1704 | fetch('/chat', { |
| voice_agent_backend/frontend/script.js:1785 | fetch('/ingest', { method: 'POST', body: formData }).then(function (r) { |
| voice_agent_backend/frontend/script.js:1823 | fetch('/collections/' + getActiveCollection() + '/documents/' + encodeURIComponent(doc.filename), { method: 'DELETE' }).then(function (r) { if (!r.ok) throw new Error('Delete faile |
| voice_agent_backend/frontend/script.js:1982 | return fetch('/models').then(function (r) { if (!r.ok) throw new Error('Models error'); return r.json(); }).then(function (data) { |
| voice_agent_backend/frontend/script.js:2051 | return fetch('/collections').then(function (r) { if (!r.ok) throw new Error('Collections error'); return r.json(); }).then(function (data) { |
| voice_agent_backend/frontend/script.js:2065 | return fetch('/collections', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: col }) }).then(function (r) { if (!r.ok) return r.json( |
| voice_agent_backend/frontend/script.js:2085 | fetch('/collections', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name }) }).then(function (r) { if (!r.ok) throw new Error('Cre |
| voice_agent_backend/frontend/script.js:2096 | return fetch('/health').then(function (r) { if (!r.ok) throw new Error('Health check failed'); return r.json(); }).then(function (data) { |
| voice_agent_backend/frontend/script.js:2192 | fetch('/collections/' + col, { method: 'DELETE' }).then(function () { |
| voice_agent_backend/HANDOFF_README.md:40 | GROQ_API_KEY=[REDACTED example value] |
| voice_agent_backend/HANDOFF_README.md:90 | ├── .env                    ← YOUR CONFIG (edit GROQ_API_KEY here) |
| voice_agent_backend/HANDOFF_README.md:135 | \| GROQ_API_KEY \| (empty) \| **REQUIRED** — Get from console.groq.com \| |
| voice_agent_backend/HANDOFF_README.md:136 | \| GROQ_BASE \| https://api.groq.com/openai/v1 \| Groq API base URL \| |
| voice_agent_backend/HANDOFF_README.md:139 | \| OLLAMA_BASE \| http://localhost:11434 \| Ollama URL (only if using Ollama) \| |
| voice_agent_backend/HANDOFF_README.md:141 | \| QDRANT_BASE \| http://localhost:6333 \| Qdrant URL \| |
| voice_agent_backend/HANDOFF_README.md:144 | \| KOKORO_MODE \| disabled \| TTS: "disabled", "native", or "docker" \| |
| voice_agent_backend/HANDOFF_README.md:153 | - Adding `window.fetch` interceptor that auto-injects `Authorization: Bearer <token>` on every same-origin request |
| voice_agent_backend/HANDOFF_README.md:162 | 5. **[HIGH] `requirements.txt` included `kokoro`** — Kokoro TTS library is hard to install and only needed if `KOKORO_MODE=native`. Made optional (commented out). `KOKORO_MODE=disa |
| voice_agent_backend/HANDOFF_README.md:180 | 5. `window.fetch` is patched — all API calls auto-include `Authorization: Bearer <token>` |
| voice_agent_backend/HANDOFF_README.md:221 | → Edit `.env` and set a real `GROQ_API_KEY` |
| voice_agent_backend/HANDOFF_README.md:238 | ## RUNNING WITHOUT OLLAMA (Groq-only mode) |
| voice_agent_backend/HANDOFF_README.md:255 | - **Frontend token**: Stored in `localStorage.ssa_auth_token`, injected into all fetch() calls via patched `window.fetch` |
| voice_agent_backend/plan.md:188 | # - get_current_user() dependency — validate JWT from Authorization header |
| voice_agent_backend/plan.md:427 | `app/services/ollama_service.py`: Single function `generate_embedding(text, model) -> list[float]` that calls `POST {OLLAMA_BASE}/api/embed` via httpx. |
| voice_agent_backend/plan.md:451 | base_url=settings.OLLAMA_BASE, |
| voice_agent_backend/plan.md:543 | self._client = QdrantClient(url=settings.QDRANT_BASE) |
| voice_agent_backend/plan.md:683 | groq_api_key=settings.GROQ_API_KEY, |
| voice_agent_backend/plan.md:689 | groq_api_key=settings.GROQ_API_KEY, |
| voice_agent_backend/plan.md:695 | groq_api_key=settings.GROQ_API_KEY, |
| voice_agent_backend/requirements.txt:21 | # ── Optional: Kokoro TTS (only needed if KOKORO_MODE=native or docker) ── |
| voice_agent_backend/requirements.txt:29 | duckduckgo-search>=6.0.0 |
| voice_agent_backend/scripts/check_backend_health.py:16 | print(f"Ollama ({settings.OLLAMA_BASE}): ", end="", flush=True) |
| voice_agent_backend/scripts/check_backend_health.py:20 | print(f"Qdrant ({settings.QDRANT_BASE}): ", end="", flush=True) |
| voice_agent_backend/scripts/check_backend_health.py:24 | print(f"Groq ({settings.GROQ_BASE}):   ", end="", flush=True) |
| voice_agent_backend/scripts/verify_kokoro.py:10 | print("VERIFYING KOKORO-ONNX INITIALIZATION") |
| voice_agent_backend/scripts/verify_kokoro.py:13 | model_path = getattr(settings, "KOKORO_MODEL_PATH", "../kokoro-v1.0.onnx") |
| voice_agent_backend/scripts/verify_kokoro.py:14 | voices_path = getattr(settings, "KOKORO_VOICES_PATH", "voices.bin") |
| voice_agent_backend/scripts/verify_kokoro.py:39 | print(f"KOKORO INIT FAILED: {e}") |
| voice_agent_backend/sop(voice_agent).md:35 | GROQ_API_KEY=[REDACTED example value] |

## LLM Integration Details
Groq chat builds chat-completion URLs from `settings.GROQ_BASE` in `voice_agent_backend/app/services/groq_service.py:25` and sends bearer auth from `settings.GROQ_API_KEY` in `voice_agent_backend/app/services/groq_service.py:27`. Streaming yields delta content at `voice_agent_backend/app/services/groq_service.py:61`. Groq transcription uses the audio transcriptions path around `voice_agent_backend/app/services/groq_service.py:87`. Ollama embeddings call `/api/embed` at `voice_agent_backend/app/services/ollama_service.py:14`; local chat calls `/v1/chat/completions` at `voice_agent_backend/app/services/ollama_service.py:60`; model listing calls `/api/tags` at `voice_agent_backend/app/services/ollama_service.py:110`.

## Prompt Inventory
Voice/system prompts live in `voice_agent_backend/app/core/config.py:9` and document-grounded prompt rules live in `voice_agent_backend/app/core/config.py:28`. Additional prompt construction exists in correlator, intent, RAG, ultrathink, translation, and generation nodes. These prompts are production behavior because they directly shape voice-agent responses.

## Webhook Handlers
No third-party webhook receiver endpoints were discovered in route inventory. All discovered HTTP routes are direct browser/API flows.

## File/Object Storage Analysis
No S3/GCS/Azure storage integration was discovered. User uploads are parsed in memory and represented as Qdrant vector payloads. Model files `kokoro-v1.0.onnx` and `voices-v1.0.bin` are local runtime assets referenced by settings.

## Auth/OAuth Integrations
No OAuth, SAML, or OIDC provider integration was discovered. Auth is local email/password plus JWT via `voice_agent_backend/app/core/auth.py:25`, but the auth router is not mounted in `app.main`.

## Environment Variable Completeness
| Var | Defined At | Used At | Default / Example | Risk If Missing |
| --- | --- | --- | --- | --- |
| OLLAMA_BASE | voice_agent_backend/app/core/config.py:58 | docs/intelligence/_generate_docs.py:388, voice_agent_backend/app/services/ollama_service.py:14, voice_agent_backend/app/services/ollama_service.py:60, voice_agent_backend/app/services/ollama_service.py:110, voice_agent_backend/app/services/ollama_service.py:123 | "http://localhost:11434" | feature dependent |
| QDRANT_BASE | voice_agent_backend/app/core/config.py:59 | docs/intelligence/_generate_docs.py:389, voice_agent_backend/app/services/qdrant_service.py:14, voice_agent_backend/app/services/qdrant_service.py:29, voice_agent_backend/app/services/qdrant_service.py:44, voice_agent_backend/app/services/qdrant_service.py:59 | "http://localhost:6333" | feature dependent |
| GROQ_BASE | voice_agent_backend/app/core/config.py:60 | docs/intelligence/_generate_docs.py:387, docs/intelligence/_generate_docs.py:395, voice_agent_backend/app/services/groq_service.py:25, voice_agent_backend/app/services/groq_service.py:87, voice_agent_backend/app/services/groq_service.py:124 | "https://api.groq.com/openai/v1" | feature dependent |
| GROQ_API_KEY | voice_agent_backend/app/core/config.py:61 | docs/intelligence/_generate_docs.py:395, voice_agent_backend/app/services/groq_service.py:27, voice_agent_backend/app/services/groq_service.py:89, voice_agent_backend/app/services/groq_service.py:125, voice_agent_backend/app/services/groq_service.py:140 | "" | high |
| CHAT_MODEL | voice_agent_backend/app/core/config.py:64 | voice_agent_backend/app/api/routes/chat.py:238, voice_agent_backend/app/api/routes/chat.py:395, voice_agent_backend/app/core/nodes/generate_response.py:140, voice_agent_backend/app/core/nodes/handle_early_exit.py:89, voice_agent_backend/plan.md:680 | "llama-3.1-8b-instant" | feature dependent |
| EMBED_MODEL | voice_agent_backend/app/core/config.py:65 | voice_agent_backend/app/api/routes/chat.py:397, voice_agent_backend/app/api/routes/collections.py:31, voice_agent_backend/app/api/routes/ingest.py:347, voice_agent_backend/app/api/routes/ingest.py:352, voice_agent_backend/app/core/langchain_rag.py:314 | "mxbai-embed-large:latest" | feature dependent |
| TRANSLATION_MODEL | voice_agent_backend/app/core/config.py:66 | voice_agent_backend/app/core/translation.py:19, voice_agent_backend/app/core/translation.py:45, voice_agent_backend/plan.md:686 | "llama-3.1-8b-instant" | feature dependent |
| CHAT_PROVIDER | voice_agent_backend/app/core/config.py:68 | voice_agent_backend/app/api/routes/chat.py:239, voice_agent_backend/app/api/routes/chat.py:396, voice_agent_backend/app/core/nodes/generate_response.py:141, voice_agent_backend/app/core/nodes/handle_early_exit.py:90 | "groq"  # "groq" or "ollama" | feature dependent |
| TRANSLATION_PROVIDER | voice_agent_backend/app/core/config.py:69 | voice_agent_backend/app/core/translation.py:20, voice_agent_backend/app/core/translation.py:46 | "groq"  # "groq" or "ollama" | feature dependent |
| DEFAULT_COLLECTION | voice_agent_backend/app/core/config.py:72 | no direct use found | "agent_knowledge" | feature dependent |
| RETRIEVAL_TOP_K | voice_agent_backend/app/core/config.py:73 | voice_agent_backend/app/core/langchain_rag.py:308 | 12  # Increased from 8 for better recall on rare entities | feature dependent |
| SUMMARY_TOP_K | voice_agent_backend/app/core/config.py:74 | voice_agent_backend/app/core/langchain_rag.py:308, voice_agent_backend/app/core/langchain_rag.py:357 | 16 | feature dependent |
| RERANK_TOP_N | voice_agent_backend/app/core/config.py:75 | voice_agent_backend/app/core/langchain_rag.py:354 | 6 | feature dependent |
| SCORE_THRESHOLD | voice_agent_backend/app/core/config.py:76 | voice_agent_backend/app/core/langchain_rag.py:309 | 0.25  # Lowered slightly to capture more candidates for consensus | feature dependent |
| RETRIEVAL_CONFIDENCE_FLOOR | voice_agent_backend/app/core/config.py:77 | voice_agent_backend/app/core/langchain_rag.py:205 | 0.40  # Unified scale for RRF + Vector | feature dependent |
| SUMMARY_CONFIDENCE_FLOOR | voice_agent_backend/app/core/config.py:78 | voice_agent_backend/app/core/langchain_rag.py:205 | 0.35 | feature dependent |
| CHUNK_SIZE | voice_agent_backend/app/core/config.py:81 | voice_agent_backend/app/api/routes/ingest.py:21, voice_agent_backend/scratch/test_chunking.py:29, voice_agent_backend/scratch/test_chunking.py:35 | 1200 | feature dependent |
| CHUNK_OVERLAP | voice_agent_backend/app/core/config.py:82 | voice_agent_backend/app/api/routes/ingest.py:22, voice_agent_backend/scratch/test_chunking.py:45 | 200 | feature dependent |
| MEMORY_PAIRS | voice_agent_backend/app/core/config.py:85 | voice_agent_backend/app/api/routes/chat.py:234 | 10 | feature dependent |
| KOKORO_MODE | voice_agent_backend/app/core/config.py:89 | no direct use found | "native" | feature dependent |
| KOKORO_DOCKER_URL | voice_agent_backend/app/core/config.py:91 | no direct use found | "http://127.0.0.1:8880" | feature dependent |
| KOKORO_MODEL_PATH | voice_agent_backend/app/core/config.py:93 | voice_agent_backend/app/api/routes/models.py:22 | "../kokoro-v1.0.onnx" | feature dependent |
| KOKORO_VOICES_PATH | voice_agent_backend/app/core/config.py:95 | no direct use found | "../voices-v1.0.bin" | feature dependent |
| KOKORO_LANG_CODE | voice_agent_backend/app/core/config.py:97 | no direct use found | "a" | feature dependent |
| TTS_HARDWARE | voice_agent_backend/app/core/config.py:99 | no direct use found | "gpu" | feature dependent |
| TTS_SAMPLE_RATE | voice_agent_backend/app/core/config.py:101 | no direct use found | 24000 | feature dependent |
| CONTEXT_WINDOW_TURNS | voice_agent_backend/app/core/config.py:103 | no direct use found | 3 | feature dependent |
| CORRELATOR_MODEL | voice_agent_backend/app/core/config.py:105 | no direct use found | "meta-llama/llama-4-scout-17b-16e-instruct" | feature dependent |
| CORRELATOR_PROVIDER | voice_agent_backend/app/core/config.py:107 | no direct use found | "groq" | feature dependent |
| BACKCHANNEL_PHRASES | voice_agent_backend/app/core/config.py:110 | no direct use found | ["mm-hmm", "yeah", "I see", "got it", "right"] | feature dependent |
| BACKCHANNEL_COOLDOWN_SECONDS | voice_agent_backend/app/core/config.py:111 | voice_agent_backend/app/api/routes/chat.py:337, voice_agent_backend/app/api/routes/chat.py:424 | 6.0 | feature dependent |
| PREDICTIVE_RAG_TIMEOUT_MS | voice_agent_backend/app/core/config.py:112 | no direct use found | 500 | feature dependent |
| ENABLE_SEARCH | voice_agent_backend/app/core/config.py:115 | no direct use found | True | feature dependent |
| SEARCH_PROVIDER | voice_agent_backend/app/core/config.py:116 | no direct use found | "duckduckgo" # "duckduckgo" or "tavily" | feature dependent |
| TAVILY_API_KEY | voice_agent_backend/app/core/config.py:117 | no direct use found | "" | feature dependent |
| CORS_ORIGINS | voice_agent_backend/app/core/config.py:120 | no direct use found | ["http://localhost:8000", "http://127.0.0.1:8000"] | feature dependent |
| ALLOWED_HOSTS | voice_agent_backend/app/core/config.py:121 | no direct use found | ["localhost", "127.0.0.1"] | feature dependent |
| SECRET_KEY | voice_agent_backend/app/core/config.py:124 | voice_agent_backend/app/core/auth.py:35, voice_agent_backend/app/core/auth.py:57 | [REDACTED fallback secret default] | high |
| ALGORITHM | voice_agent_backend/app/core/config.py:125 | voice_agent_backend/app/core/auth.py:35, voice_agent_backend/app/core/auth.py:57 | "HS256" | feature dependent |
| ACCESS_TOKEN_EXPIRE_MINUTES | voice_agent_backend/app/core/config.py:126 | voice_agent_backend/app/core/auth.py:31 | 60 | feature dependent |
| MAX_FILE_SIZE | voice_agent_backend/app/core/config.py:127 | voice_agent_backend/app/api/routes/ingest.py:410, voice_agent_backend/app/api/routes/ingest.py:413 | 50 * 1024 * 1024  # 50 MB | feature dependent |
| ENABLE_RATE_LIMIT | voice_agent_backend/app/core/config.py:128 | voice_agent_backend/app/core/limiter.py:7 | True | feature dependent |
| HOST | voice_agent_backend/app/core/config.py:148 | no direct use found | "0.0.0.0" | feature dependent |
| PORT | voice_agent_backend/app/core/config.py:149 | no direct use found | 8000 | feature dependent |
| IO_THREAD_POOL_SIZE | voice_agent_backend/app/core/config.py:153 | voice_agent_backend/app/main.py:51, voice_agent_backend/app/main.py:52 | 12 | feature dependent |
| GPU_BATCH_SIZE | voice_agent_backend/app/core/config.py:154 | voice_agent_backend/app/api/routes/ingest.py:356 | 4 | feature dependent |
| ONNX_INTRA_OP_THREADS | voice_agent_backend/app/core/config.py:155 | voice_agent_backend/app/services/speech_service.py:198 | 4 | feature dependent |
| ONNX_INTER_OP_THREADS | voice_agent_backend/app/core/config.py:156 | voice_agent_backend/app/services/speech_service.py:199 | 2 | feature dependent |
| MODELS_TO_CUDA | voice_agent_backend/app/core/config.py:157 | no direct use found | ["kokoro", "embed"] | feature dependent |
| STT_LOCAL_DEVICE | voice_agent_backend/app/core/config.py:158 | no direct use found | "cpu"  # Keep STT on CPU to save 4GB VRAM for RAG/TTS | feature dependent |

## Hardcoded Credentials Found
No raw `.env` values were read. A fallback JWT secret default exists at `voice_agent_backend/app/core/config.py:124` and is redacted here as `[REDACTED]`; this must not be accepted in production. A test placeholder secret exists in `voice_agent_backend/scripts/test_imports.py:10` and is redacted as `[REDACTED]`.

## Current External Checks
Official/current checks performed during this run: Groq API reference for OpenAI-compatible endpoints and speech-to-text, Ollama API and embed docs, Qdrant REST/search docs, Kokoro ONNX package metadata, and Hugging Face model search for `mixedbread-ai/mxbai-embed-large-v1`. These checks confirmed the code is using recognizable provider families, but they do not prove the installed local versions are current because the checkout does not pin exact versions.
