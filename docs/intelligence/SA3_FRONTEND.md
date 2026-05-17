# SA-3: Frontend Report

## Scope
Analyzed `voice_agent_backend/frontend/index.html`, `voice_agent_backend/frontend/style.css`, `voice_agent_backend/frontend/script.js`, and `voice_agent_backend/tests/test_frontend.py`. The frontend syntax check `node --check voice_agent_backend/frontend/script.js` exited successfully during the SA-3 read-only pass.

## UI Architecture
The frontend is a static same-origin SPA. `CONFIG.BACKEND_BASE` is empty at `voice_agent_backend/frontend/script.js:10`, and calls use relative paths. The HTML shell includes service status, orb stage, transcript, text input, control bar, settings panel, document panel, history panel, toast container, and hidden file input.

## Component/Page Inventory
| Component | Evidence | Purpose |
| --- | --- | --- |
| Status bar | voice_agent_backend/frontend/index.html:17 | Ollama/Qdrant/Groq service health |
| Orb stage | voice_agent_backend/frontend/index.html:48 | Voice-state visualization |
| Transcript | voice_agent_backend/frontend/index.html:64 | Conversation rendering |
| Text input/control bar | voice_agent_backend/frontend/index.html:78 | Typed and voice interactions |
| Settings panel | voice_agent_backend/frontend/index.html:148 | Voice/model/provider controls |
| Documents panel | voice_agent_backend/frontend/index.html:297 | Upload and local document list |
| History panel | voice_agent_backend/frontend/index.html:334 | Local conversation sessions |
| Toast container | voice_agent_backend/frontend/index.html:348 | User notifications |

## State Management Map
Global `CONFIG`, `STATE`, and DOM caches live in `voice_agent_backend/frontend/script.js:10`, `voice_agent_backend/frontend/script.js:90`, and `voice_agent_backend/frontend/script.js:513`. Persistent state uses `localStorage` helpers at `voice_agent_backend/frontend/script.js:619` through `voice_agent_backend/frontend/script.js:621` with `ssa_` keys. `loadSettings()` restores settings, local docs, local conversation, sessions, and model choices around `voice_agent_backend/frontend/script.js:1923`.

## API Call Inventory
| File:Line | Endpoint | Evidence |
| --- | --- | --- |
| voice_agent_backend/frontend/script.js:331 | /chat/stream | fetch('/chat/stream', { |
| voice_agent_backend/frontend/script.js:462 | /chat/interrupt/ | fetch('/chat/interrupt/' + this.activeThreadId, { |
| voice_agent_backend/frontend/script.js:605 | dynamic/wrapped | return fetch(url, merged).then(function (resp) { |
| voice_agent_backend/frontend/script.js:1311 | /chat/backchannel/ | fetch('/chat/backchannel/' + getOrCreateSessionId(), { method: 'POST' }) |
| voice_agent_backend/frontend/script.js:1329 | /chat/predict | fetch('/chat/predict', { |
| voice_agent_backend/frontend/script.js:1407 | /stt | fetch('/stt', { method: 'POST', body: formData }).then(function (r) { if (!r.ok) throw new Error('STT error ' + r.status); return r.json();  |
| voice_agent_backend/frontend/script.js:1704 | /chat | fetch('/chat', { |
| voice_agent_backend/frontend/script.js:1785 | /ingest | fetch('/ingest', { method: 'POST', body: formData }).then(function (r) { |
| voice_agent_backend/frontend/script.js:1823 | /collections/ | fetch('/collections/' + getActiveCollection() + '/documents/' + encodeURIComponent(doc.filename), { method: 'DELETE' }).then(function (r) {  |
| voice_agent_backend/frontend/script.js:1982 | /models | return fetch('/models').then(function (r) { if (!r.ok) throw new Error('Models error'); return r.json(); }).then(function (data) { |
| voice_agent_backend/frontend/script.js:2051 | /collections | return fetch('/collections').then(function (r) { if (!r.ok) throw new Error('Collections error'); return r.json(); }).then(function (data) { |
| voice_agent_backend/frontend/script.js:2065 | /collections | return fetch('/collections', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: col }) }).then( |
| voice_agent_backend/frontend/script.js:2085 | /collections | fetch('/collections', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name }) }).then(functi |
| voice_agent_backend/frontend/script.js:2096 | /health | return fetch('/health').then(function (r) { if (!r.ok) throw new Error('Health check failed'); return r.json(); }).then(function (data) { |
| voice_agent_backend/frontend/script.js:2192 | /collections/ | fetch('/collections/' + col, { method: 'DELETE' }).then(function () { |

## Client-Side Route Map
There is no framework router. Screen changes are panel open/close and class toggles. API paths are same-origin: `/health`, `/models`, `/collections`, `/ingest`, `/stt`, `/chat`, `/chat/stream`, `/chat/predict`, `/chat/backchannel/{session}`, and `/chat/interrupt/{thread}`.

## Auth And LocalStorage
The script has an auth-module heading at `voice_agent_backend/frontend/script.js:51`, but no implemented AUTH object, login form logic, fetch interceptor, or `Authorization` header path was found. Error branches reference undefined symbols `isAuthError`, `AUTH.clear`, `showAuthModal`, and `setAuthError` around `voice_agent_backend/frontend/script.js:438` and `voice_agent_backend/frontend/script.js:2119`. CSS contains auth modal/logout styles, but the HTML lacks matching auth modal markup.

## Form Analysis
The UI includes textarea/chat controls, STT provider controls, model/provider selects, collection/document upload controls, and a Groq key input. The Groq key input exists at `voice_agent_backend/frontend/index.html:264`, but its change handler only shows a toast saying server `.env` manages keys at `voice_agent_backend/frontend/script.js:2199`.

## UI Bugs Found
1. HIGH: Auth handling is broken if a 401 path is reached because catch blocks reference undefined auth functions.
2. MEDIUM: Default chat route is `/chat/stream`, but tests mainly mock `/chat`, so the default streaming path is weakly covered.
3. MEDIUM: Fallback `/chat` SSE parser lacks carryover buffering for split chunks.
4. MEDIUM: Fallback `/chat` can call finalization twice, once on `[DONE]` and again when reader ends.
5. HIGH: Markdown from assistant output is rendered through `marked.parse` and assigned to `innerHTML` without sanitizer at `voice_agent_backend/frontend/script.js:1185` and `voice_agent_backend/frontend/script.js:1195`.
6. LOW: Backend PCM audio can continue after UI phase returns to idle.
7. LOW: New collection row exists hidden but no visible trigger was found.
8. MEDIUM: Document list persistence is local-only after upload; boot does not fetch backend documents.

## Accessibility And UX Correctness
Positive: `html lang` exists, key control buttons have `aria-label`, focus-visible styles are defined, and reduced-motion preferences are respected. Gaps: slide panels are plain `div`s without dialog roles/focus traps, textarea has placeholder but no clear label, the drop zone is a clickable `div` without keyboard button semantics, and the handsfree checkbox label appears weak.

## Test Coverage
The Playwright suite serves static frontend files and mocks APIs, so it does not require FastAPI/Qdrant/Ollama/Groq. It covers load smoke checks, panel open/close, basic textarea behavior, status items, shortcuts, button labels, no JS page errors on normal mocked load, and `html[lang]`. It does not assert the real `/chat/stream` success path, STT/TTS, ingestion flow, collection creation trigger, localStorage persistence, or auth modal behavior.

## Frontend Evidence Appendix

- `voice_agent_backend/frontend/script.js:331`: /chat/stream | fetch('/chat/stream', {

- `voice_agent_backend/frontend/script.js:462`: /chat/interrupt/ | fetch('/chat/interrupt/' + this.activeThreadId, {

- `voice_agent_backend/frontend/script.js:605`: dynamic/wrapped | return fetch(url, merged).then(function (resp) {

- `voice_agent_backend/frontend/script.js:1311`: /chat/backchannel/ | fetch('/chat/backchannel/' + getOrCreateSessionId(), { method: 'POST' })

- `voice_agent_backend/frontend/script.js:1329`: /chat/predict | fetch('/chat/predict', {

- `voice_agent_backend/frontend/script.js:1407`: /stt | fetch('/stt', { method: 'POST', body: formData }).then(function (r) { if (!r.ok) throw new Error('STT error ' + r.status); return r.json();

- `voice_agent_backend/frontend/script.js:1704`: /chat | fetch('/chat', {

- `voice_agent_backend/frontend/script.js:1785`: /ingest | fetch('/ingest', { method: 'POST', body: formData }).then(function (r) {

- `voice_agent_backend/frontend/script.js:1823`: /collections/ | fetch('/collections/' + getActiveCollection() + '/documents/' + encodeURIComponent(doc.filename), { method: 'DELETE' }).then(function (r) {

- `voice_agent_backend/frontend/script.js:1982`: /models | return fetch('/models').then(function (r) { if (!r.ok) throw new Error('Models error'); return r.json(); }).then(function (data) {

- `voice_agent_backend/frontend/script.js:2051`: /collections | return fetch('/collections').then(function (r) { if (!r.ok) throw new Error('Collections error'); return r.json(); }).then(function (data) {

- `voice_agent_backend/frontend/script.js:2065`: /collections | return fetch('/collections', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: col }) }).then(

- `voice_agent_backend/frontend/script.js:2085`: /collections | fetch('/collections', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name }) }).then(functi

- `voice_agent_backend/frontend/script.js:2096`: /health | return fetch('/health').then(function (r) { if (!r.ok) throw new Error('Health check failed'); return r.json(); }).then(function (data) {

- `voice_agent_backend/frontend/script.js:2192`: /collections/ | fetch('/collections/' + col, { method: 'DELETE' }).then(function () {

- `docs/intelligence/_generate_docs.py:50`: return path.read_text(encoding="utf-8", errors="replace").splitlines()

- `docs/intelligence/_generate_docs.py:59`: p = subprocess.run(args, cwd=str(cwd), text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=45)

- `docs/intelligence/_generate_docs.py:181`: if re.search(r"logger\.|print\(|console\.|warning|error", line):

- `docs/intelligence/_generate_docs.py:197`: sqlite_rows.append(("error", "sqlite", repr(exc)))

- `docs/intelligence/_generate_docs.py:334`: "## Error Handling Report\nQdrant helpers often convert connection/status errors into empty dictionaries, for example helper exception paths in `voice_agent_backend/app/services/qd

- `docs/intelligence/_generate_docs.py:338`: "## Test Coverage\nThe only `voice_agent_backend/tests` file is frontend-focused and mocks API responses. Backend tests are missing for auth mounting, rate limits, collection delet

- `docs/intelligence/_generate_docs.py:364`: "## Test Coverage\nThe Playwright suite serves static frontend files and mocks APIs, so it does not require FastAPI/Qdrant/Ollama/Groq. It covers load smoke checks, panel open/clos

- `docs/intelligence/_generate_docs.py:378`: "## Data Integrity Risks\n1. HIGH: Qdrant helpers swallow connection/HTTP errors and return empty results.\n2. HIGH: Ingest does not verify Qdrant upsert response before returning

- `docs/intelligence/_generate_docs.py:388`: ("Ollama", "`settings.OLLAMA_BASE`, default `http://localhost:11434`", "none/local", "httpx call-level/shared client", "no central retry found", "empty model list/offline health/er

- `docs/intelligence/_generate_docs.py:389`: ("Qdrant", "`settings.QDRANT_BASE`, default `http://localhost:6333`", "none observed", "10-30 second helper timeouts", "no central retry found", "empty dict/results or route error"

- `docs/intelligence/_generate_docs.py:390`: ("Kokoro native ONNX", "`KOKORO_MODEL_PATH`, `KOKORO_VOICES_PATH`", "local file assets", "startup/runtime load time", "fallback depends on mode", "TTS warning/degradation"),

- `docs/intelligence/_generate_docs.py:391`: ("Kokoro Docker sidecar", "`KOKORO_DOCKER_URL`", "none/local", "httpx/service specific", "no central retry found", "TTS error/degradation"),

- `docs/intelligence/_generate_docs.py:392`: ("DuckDuckGo/Tavily", "`SEARCH_PROVIDER`, `TAVILY_API_KEY`", "Tavily API key if used", "provider specific", "not centrally observed", "search node fallback/error"),

- `docs/intelligence/_generate_docs.py:417`: ("Backend routes", len(routes), 0, "0 route tests discovered", "auth, rate limits, provider failures, streaming errors"),

- `docs/intelligence/_generate_docs.py:422`: "## Logging/Observability Gaps\nAudit logging avoids bodies, which is good for secret hygiene, but provider and startup failures are often warnings or transformed into empty/offlin

- `docs/intelligence/_generate_docs.py:444`: "## 5. What Can Go Wrong?\nThe biggest issues are disconnected auth router, unauthenticated mutating routes, fallback JWT secret, hidden Qdrant write failures, graph streaming task

- `docs/intelligence/_generate_docs.py:461`: ("Ollama", "none/local", "empty models/offline/errors", "no central retry found"),

- `docs/intelligence/_generate_docs.py:462`: ("Qdrant", "none observed", "empty result/dict or route error", "no central retry found"),

- `docs/intelligence/_generate_docs.py:463`: ("Kokoro native/Docker", "local files or local sidecar", "TTS degradation/warning", "no central retry found"),

- `docs/intelligence/_generate_docs.py:464`: ("DuckDuckGo/Tavily", "TAVILY_API_KEY if Tavily selected", "search degradation/error", "not centrally determined"),

- `docs/intelligence/_generate_docs.py:472`: line_counts = {p.name: len(p.read_text(encoding="utf-8", errors="replace").splitlines()) for p in sorted(OUT.glob("SA*.md"))}

- `docs/intelligence/_generate_docs.py:538`: print(json.dumps({p.name: len(p.read_text(encoding='utf-8', errors='replace').splitlines()) for p in sorted(OUT.glob('*.md'))}, indent=2))

- `voice_agent_backend/app/api/routes/chat.py:73`: print(f"LATENCY: Translation took {time.time() - start_time:.2f}s", flush=True)

- `voice_agent_backend/app/api/routes/chat.py:140`: print(

- `voice_agent_backend/app/api/routes/chat.py:171`: print(

- `voice_agent_backend/app/api/routes/chat.py:242`: print(

- `voice_agent_backend/app/api/routes/chat.py:253`: print(

- `voice_agent_backend/app/api/routes/chat.py:261`: error_msg = f"Sorry, I encountered an error: {str(e)}"

- `voice_agent_backend/app/api/routes/chat.py:262`: yield f"data: {json.dumps({'token': error_msg})}\n\n"

- `voice_agent_backend/app/api/routes/chat.py:263`: full_response = error_msg

- `voice_agent_backend/app/api/routes/chat.py:324`: logger.error(f"Predictive RAG failed: {e}")

- `voice_agent_backend/app/api/routes/chat.py:325`: return {"status": "error", "detail": str(e)}

- `voice_agent_backend/app/api/routes/chat.py:346`: return {"status": "error", "reason": "no_audio"}

- `voice_agent_backend/app/api/routes/chat.py:481`: logger.error(f"Graph streaming error: {e}", exc_info=True)

- `voice_agent_backend/app/api/routes/chat.py:539`: logger.error(f"Interrupt resume failed: {e}", exc_info=True)

- `voice_agent_backend/app/api/routes/health.py:23`: "error": str(ollama_ok) if isinstance(ollama_ok, Exception) else None

- `voice_agent_backend/app/api/routes/health.py:27`: "error": str(qdrant_ok) if isinstance(qdrant_ok, Exception) else None

- `voice_agent_backend/app/api/routes/health.py:31`: "error": str(groq_ok) if isinstance(groq_ok, Exception) else None

- `voice_agent_backend/app/api/routes/ingest.py:269`: text = file_bytes.decode("utf-8", errors="ignore")

- `voice_agent_backend/app/api/routes/ingest.py:384`: logger.warning(f"Batch embedding failed for chunks {i}-{i+batch_size}: {e}")

- `voice_agent_backend/app/core/agents/supervisor.py:44`: logger.info(f"Supervisor promoting intent {intent} to ULTRATHINK.")

- `voice_agent_backend/app/core/agents/supervisor.py:48`: logger.info(f"Supervisor finalized intent: {intent} (flags={flags})")

- `voice_agent_backend/app/core/agents/ultrathink_critic.py:27`: logger.info("ULTRATHINK process initiated. Simulating deep thought...")

- `voice_agent_backend/app/core/agents/ultrathink_critic.py:57`: logger.info("ULTRATHINK process completed.")

- `voice_agent_backend/app/core/agents/ultrathink_critic.py:66`: logger.error(f"ULTRATHINK failed: {e}")

- `voice_agent_backend/app/core/auth.py:14`: oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

- `voice_agent_backend/app/core/correlator.py:28`: Falls back to "new" on any error.

- `voice_agent_backend/app/core/correlator.py:52`: logger.warning(f"Correlator failed, defaulting to 'new': {e}")

- `voice_agent_backend/app/core/nodes/check_confidence.py:32`: logger.info(f"Intent {intent} does not require confidence check. Synchronized.")

- `voice_agent_backend/app/core/nodes/check_confidence.py:42`: logger.info(f"Low confidence (top_score={top_score:.3f}). Routing to early exit.")

- `voice_agent_backend/app/core/nodes/check_confidence.py:44`: logger.info(f"Sufficient confidence (top_score={top_score:.3f}). Proceeding to generate.")

- `voice_agent_backend/app/core/nodes/classify_intent.py:38`: logger.info(f"Fast intent match: {intent}. Proceeding.")

- `voice_agent_backend/app/core/nodes/classify_intent.py:47`: logger.info(f"Intent classified: {intent} (flags={flags})")

- `voice_agent_backend/app/core/nodes/generate_response.py:154`: tts_error = None
