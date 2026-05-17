# SA-6: Security and Quality Report

## Authentication/Authorization Audit
| Endpoint | Auth Required | Rate Limit | Risk |
| --- | --- | --- | --- |
| POST /auth/register | no explicit dependency | no | high write/delete risk |
| POST /auth/login | no explicit dependency | no | high write/delete risk |
| POST /chat | no explicit dependency | yes | public or guest path |
| POST /chat/predict | no explicit dependency | no | high write/delete risk |
| POST /chat/backchannel/{session_id} | no explicit dependency | no | high write/delete risk |
| POST /chat/stream | no explicit dependency | yes | public or guest path |
| POST /chat/interrupt/{thread_id} | no explicit dependency | yes | high write/delete risk |
| GET /collections | no explicit dependency | no | public or guest path |
| POST /collections | no explicit dependency | no | high write/delete risk |
| DELETE /collections/{collection_name} | no explicit dependency | no | high write/delete risk |
| GET /collections/{collection_name}/documents | no explicit dependency | no | public or guest path |
| DELETE /collections/{collection_name}/documents/{filename} | no explicit dependency | no | high write/delete risk |
| GET /health | no explicit dependency | no | public or guest path |
| POST /ingest | no explicit dependency | yes | high write/delete risk |
| GET /models | no explicit dependency | no | public or guest path |
| POST /stt | no explicit dependency | no | high write/delete risk |
| POST /tts/generate | no explicit dependency | no | high write/delete risk |

## Injection Vulnerability Report
No direct SQL string interpolation match was found in the SQLAlchemy auth flow. Command/eval usage was not found in the runtime backend routes by the static scan. The main injection-adjacent issue is frontend Markdown rendered through `innerHTML` without sanitization at `voice_agent_backend/frontend/script.js:1195`, which should be treated as XSS risk if LLM/backend output can contain HTML.

## Hardcoded Credentials
| File:Line | Type | Value | Rotation Required |
| --- | --- | --- | --- |
| voice_agent_backend/app/core/config.py:124 | JWT fallback secret | [REDACTED] | yes if ever used outside local dev |
| voice_agent_backend/scripts/test_imports.py:10 | test placeholder secret | [REDACTED] | no, test-only placeholder |

## Dependency Vulnerabilities
The requirements use lower bounds (`>=`) rather than exact pins, so the vulnerability posture depends on the installed environment. High-impact packages to audit before deployment are FastAPI, Uvicorn, python-jose, passlib/bcrypt, SQLAlchemy, httpx, slowapi, onnxruntime-gpu, kokoro-onnx, and duckduckgo-search.

## Test Coverage Report
| Module | Handlers / Files | Tests | Coverage | Gap |
| --- | --- | --- | --- | --- |
| Backend routes | 17 | 0 | 0 route tests discovered | auth, rate limits, provider failures, streaming errors |
| Frontend SPA | 3 | voice_agent_backend/tests/test_frontend.py | partial | default `/chat/stream`, STT/TTS, upload, auth modal |
| Data layer | SQLite/Qdrant helpers | 0 | not covered | migrations, FK, Qdrant write failures |
| Scratch scripts | 6 | manual scripts | manual only | not CI-like validation |

## Logging/Observability Gaps
Audit logging avoids bodies, which is good for secret hygiene, but provider and startup failures are often warnings or transformed into empty/offline states. There is no clear correlation ID across provider calls. Some scripts and frontend code use `print()`/`console.*` style logging instead of structured production logging.

## Concurrency/Race Condition Risks
| Location | Scenario | Severity |
| --- | --- | --- |
| voice_agent_backend/app/core/memory.py:13 | Process-local session state partitions across workers and resets on restart. | medium |
| voice_agent_backend/app/api/routes/chat.py:45 | Predictive RAG cache has TTL but no robust invalidation/consumer path. | medium |
| voice_agent_backend/app/api/routes/chat.py:456 | Graph task exception/cancellation can leave SSE queue waiting. | medium |
| voice_agent_backend/app/services/speech_service.py:35 | Mutable singleton Kokoro/hardware caches reload without an explicit lock. | medium |
| voice_agent_backend/frontend/script.js:331 | Streaming/TTS/interrupt state can race across active turns. | medium |

## MASTER RISK REGISTER
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

## Security Evidence Appendix

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

- `voice_agent_backend/app/core/nodes/generate_response.py:158`: nonlocal tts_error

- `voice_agent_backend/app/core/nodes/generate_response.py:171`: tts_error = tts_err

- `voice_agent_backend/app/core/nodes/generate_response.py:172`: logger.error(f"TTS sentence error: {tts_err}")

- `voice_agent_backend/app/core/nodes/generate_response.py:195`: logger.error(f"LLM streaming error: {e}")

- `voice_agent_backend/app/core/nodes/generate_response.py:196`: error_msg = "Sorry, I encountered an error. Could you try again?"

- `voice_agent_backend/app/core/nodes/generate_response.py:197`: full_response = error_msg

- `voice_agent_backend/app/core/nodes/generate_response.py:198`: writer({"token": error_msg})

- `voice_agent_backend/app/core/nodes/handle_early_exit.py:108`: logger.error(f"General chat LLM call failed: {e}")

- `voice_agent_backend/app/core/nodes/handle_early_exit.py:127`: logger.error(f"Early-exit TTS failed: {tts_err}")

- `voice_agent_backend/app/core/nodes/retrieve_context.py:47`: logger.error(f"Retrieval failed: {e}")

- `voice_agent_backend/app/core/nodes/search_web.py:27`: logger.info(f"Searching web for: {english_query}")

- `voice_agent_backend/app/core/nodes/search_web.py:38`: logger.info(f"Found {len(results)} search results.")

- `voice_agent_backend/app/core/nodes/search_web.py:41`: logger.info("No search results found.")
