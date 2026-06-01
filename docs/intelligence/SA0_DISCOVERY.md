# SA-0: Discovery Report
Generated: 2026-05-16 20:56:08

## Project Identity
This is a local full-stack voice-to-voice RAG assistant. FastAPI is constructed at `voice_agent_backend/app/main.py:41`, routers are mounted at `voice_agent_backend/app/main.py:102`, and the vanilla frontend is served from `voice_agent_backend/app/main.py:121`. The backend uses SQLite for auth tables, process memory for guest/session state, Qdrant for vectors, Ollama for embeddings/local chat, Groq for cloud chat and STT, and Kokoro ONNX/native or sidecar TTS.

## Tool Inventory
| Tool | Status | Path |
| --- | --- | --- |
| rg | available | <local-rg-path> |
| grep | missing |  |
| find | available (Windows find, not POSIX find) | c:\windows\system32\find.EXE |
| cat | missing |  |
| head | missing |  |
| tail | missing |  |
| wc | missing |  |
| jq | missing |  |
| python3 | available | <local-python-launcher-path> |
| python | available | c:\program files\python312\python.EXE |
| node | available | <local-node-path> |
| git | available | c:\program files\git\cmd\git.EXE |
| pip | available | c:\program files\python312\scripts\pip.EXE |
| pip3 | available | c:\program files\python312\scripts\pip3.EXE |
| npm | available | <local-npm-path> |

## MCP / Plugin Contributions
| Tool | Contribution |
| --- | --- |
| Web search | Used to verify current official provider documentation for Groq, Qdrant, Ollama, and Kokoro package metadata. |
| Hugging Face | Used to validate `mixedbread-ai/mxbai-embed-large-v1` as the model family behind `mxbai-embed-large`. |
| Browser | Available for local frontend checks if a dev server is started; no source mutation required. |
| GitHub/CodeRabbit/Netlify | Not used because no git repository, remote, PR, issue, CI, or deployment target was discoverable. |

## Full Directory Tree
```
docs/intelligence/_generate_docs.py
kokoro-v1.0.onnx [binary/artifact]
voice_agent_backend/.env [exists; contents skipped]
voice_agent_backend/app/__init__.py
voice_agent_backend/app/api/__init__.py
voice_agent_backend/app/api/routes/__init__.py
voice_agent_backend/app/api/routes/auth.py
voice_agent_backend/app/api/routes/chat.py
voice_agent_backend/app/api/routes/collections.py
voice_agent_backend/app/api/routes/health.py
voice_agent_backend/app/api/routes/ingest.py
voice_agent_backend/app/api/routes/models.py
voice_agent_backend/app/api/routes/stt.py
voice_agent_backend/app/api/routes/tts.py
voice_agent_backend/app/core/__init__.py
voice_agent_backend/app/core/agents/supervisor.py
voice_agent_backend/app/core/agents/ultrathink_critic.py
voice_agent_backend/app/core/auth.py
voice_agent_backend/app/core/config.py
voice_agent_backend/app/core/correlator.py
voice_agent_backend/app/core/database.py
voice_agent_backend/app/core/graph_state.py
voice_agent_backend/app/core/intent.py
voice_agent_backend/app/core/langchain_rag.py
voice_agent_backend/app/core/limiter.py
voice_agent_backend/app/core/memory.py
voice_agent_backend/app/core/nodes/__init__.py
voice_agent_backend/app/core/nodes/check_confidence.py
voice_agent_backend/app/core/nodes/check_interrupt.py
voice_agent_backend/app/core/nodes/classify_intent.py
voice_agent_backend/app/core/nodes/generate_response.py
voice_agent_backend/app/core/nodes/handle_early_exit.py
voice_agent_backend/app/core/nodes/retrieve_context.py
voice_agent_backend/app/core/nodes/search_web.py
voice_agent_backend/app/core/nodes/synthesize_speech.py
voice_agent_backend/app/core/nodes/translate_input.py
voice_agent_backend/app/core/nodes/update_context.py
voice_agent_backend/app/core/onnx_runtime.py
voice_agent_backend/app/core/translation.py
voice_agent_backend/app/core/voice_graph.py
voice_agent_backend/app/main.py
voice_agent_backend/app/middleware/logging.py
voice_agent_backend/app/models/__init__.py
voice_agent_backend/app/models/schemas.py
voice_agent_backend/app/models/user.py
voice_agent_backend/app/services/__init__.py
voice_agent_backend/app/services/groq_service.py
voice_agent_backend/app/services/http_client.py
voice_agent_backend/app/services/llm_router.py
voice_agent_backend/app/services/ollama_service.py
voice_agent_backend/app/services/qdrant_service.py
voice_agent_backend/app/services/speech_service.py
voice_agent_backend/context.md
voice_agent_backend/Dockerfile
voice_agent_backend/file_str.md
voice_agent_backend/frontend/index.html
voice_agent_backend/frontend/script.js
voice_agent_backend/frontend/style.css
voice_agent_backend/HANDOFF_README.md
voice_agent_backend/plan.md
voice_agent_backend/requirements.txt
voice_agent_backend/scratch/benchmark_tts.py
voice_agent_backend/scratch/inspect_kokoro.py
voice_agent_backend/scratch/sim_scoring.py
voice_agent_backend/scratch/test_chunking.py
voice_agent_backend/scratch/test_hardware.py
voice_agent_backend/scratch/test_normalization.py
voice_agent_backend/scratch/test_pipeline.py
voice_agent_backend/scratch/test_rag.py
voice_agent_backend/scratch/test_speech_norm.py
voice_agent_backend/scripts/check_backend_health.py
voice_agent_backend/scripts/test_imports.py
voice_agent_backend/scripts/test_search_node.py
voice_agent_backend/scripts/verify_kokoro.py
voice_agent_backend/sop(voice_agent).md
voice_agent_backend/start_server.bat
voice_agent_backend/start_server.sh
voice_agent_backend/test_graph.py
voice_agent_backend/tests/__init__.py
voice_agent_backend/tests/test_frontend.py
voice_agent_backend/voice_agent.db [binary/artifact]
voices-v1.0.bin [binary/artifact]
```

## Technology Stack
| Layer | Detected | Evidence |
| --- | --- | --- |
| Python | yes | voice_agent_backend/requirements.txt and app/*.py |
| FastAPI | yes | voice_agent_backend/app/main.py:4 and voice_agent_backend/app/main.py:41 |
| Vanilla JS frontend | yes | voice_agent_backend/frontend/script.js |
| React/Next/Vue | no | no package.json or framework source found |
| SQLite | yes | voice_agent_backend/app/core/database.py:8 and voice_agent_backend/voice_agent.db |
| SQLAlchemy | yes | voice_agent_backend/app/core/database.py:1 and voice_agent_backend/app/models/user.py:1 |
| Qdrant | yes | voice_agent_backend/app/services/qdrant_service.py:13 |
| Ollama | yes | voice_agent_backend/app/services/ollama_service.py:14 |
| Groq | yes | voice_agent_backend/app/services/groq_service.py:25 |
| LangGraph | yes | voice_agent_backend/app/core/voice_graph.py:17 |
| Kokoro ONNX | yes | voice_agent_backend/app/services/speech_service.py:218 |
| Docker | yes | voice_agent_backend/Dockerfile:1 |

## Entry Points
| Path | Evidence | Summary |
| --- | --- | --- |
| voice_agent_backend/app/main.py | voice_agent_backend/app/main.py:41 | FastAPI app, middleware, startup, router inclusion, static frontend mount. |
| voice_agent_backend/Dockerfile | voice_agent_backend/Dockerfile:12 | Docker runs uvicorn app.main:app on port 8000. |
| voice_agent_backend/start_server.bat | voice_agent_backend/start_server.bat:17 | Windows launcher for uvicorn with NVIDIA DLL PATH additions. |
| voice_agent_backend/start_server.sh | voice_agent_backend/start_server.sh:14 | Unix launcher for uvicorn. |
| voice_agent_backend/frontend/index.html | voice_agent_backend/app/main.py:121 | Static SPA served by FastAPI. |
| voice_agent_backend/test_graph.py | voice_agent_backend/test_graph.py:1 | Manual graph smoke script. |

## Configuration Files
| Path | Role | Read Status |
| --- | --- | --- |
| voice_agent_backend/requirements.txt | Python dependency manifest | read fully |
| voice_agent_backend/Dockerfile | Container runtime | read fully |
| voice_agent_backend/start_server.bat | Windows launcher | read fully |
| voice_agent_backend/start_server.sh | Unix launcher | read fully |
| voice_agent_backend/.env | Local secret/config file | exists; contents intentionally skipped |

## Priority Read Targets
| Rank | LOC | Path |
| --- | --- | --- |
| 1 | 2253 | voice_agent_backend/frontend/script.js |
| 2 | 1495 | voice_agent_backend/plan.md |
| 3 | 1494 | voice_agent_backend/frontend/style.css |
| 4 | 543 | voice_agent_backend/app/api/routes/chat.py |
| 5 | 538 | docs/intelligence/_generate_docs.py |
| 6 | 464 | voice_agent_backend/app/services/speech_service.py |
| 7 | 446 | voice_agent_backend/app/api/routes/ingest.py |
| 8 | 427 | voice_agent_backend/tests/test_frontend.py |
| 9 | 366 | voice_agent_backend/frontend/index.html |
| 10 | 361 | voice_agent_backend/app/core/langchain_rag.py |

## Dependency Catalog
| Dependency | Category |
| --- | --- |
| fastapi, uvicorn, pydantic, pydantic-settings | Core API/runtime/config |
| httpx, python-multipart | HTTP and upload handling |
| pypdf, python-docx | Document extraction |
| slowapi | Rate limiting |
| python-jose, passlib, email-validator | JWT/password/auth utilities |
| sqlalchemy, aiosqlite | SQLite async data layer |
| langgraph, langchain-core | Voice graph orchestration |
| numpy, kokoro-onnx, onnxruntime-gpu, misaki, soundfile | Voice/TTS inference |
| duckduckgo-search | Web search integration |

## Git Context
Git metadata is unavailable. `git rev-parse --show-toplevel` failed at both project root and backend root; branch, log, status, blame, and history are not available from this checkout.

## Test Infrastructure
| Test File | LOC | Coverage Notes |
| --- | --- | --- |
| voice_agent_backend/scratch/test_chunking.py | 66 | frontend/static or scratch/manual check |
| voice_agent_backend/scratch/test_hardware.py | 39 | frontend/static or scratch/manual check |
| voice_agent_backend/scratch/test_normalization.py | 68 | frontend/static or scratch/manual check |
| voice_agent_backend/scratch/test_pipeline.py | 66 | frontend/static or scratch/manual check |
| voice_agent_backend/scratch/test_rag.py | 32 | frontend/static or scratch/manual check |
| voice_agent_backend/scratch/test_speech_norm.py | 39 | frontend/static or scratch/manual check |
| voice_agent_backend/scripts/test_imports.py | 74 | frontend/static or scratch/manual check |
| voice_agent_backend/scripts/test_search_node.py | 37 | frontend/static or scratch/manual check |
| voice_agent_backend/test_graph.py | 23 | frontend/static or scratch/manual check |
| voice_agent_backend/tests/__init__.py | 0 | frontend/static or scratch/manual check |
| voice_agent_backend/tests/test_frontend.py | 427 | frontend/static or scratch/manual check |

## Flags For Subsequent Agents
- `auth.router` is imported but not included in `voice_agent_backend/app/main.py:102` through `voice_agent_backend/app/main.py:108`.
- No `.env.example` exists although startup scripts reference one at `voice_agent_backend/start_server.bat:8` and `voice_agent_backend/start_server.sh:8`.
- Large model files at root are required by Kokoro settings defaults in `voice_agent_backend/app/core/config.py:93` and `voice_agent_backend/app/core/config.py:95`.
- The repo is not a git checkout, so change provenance cannot be audited locally.
