# Authoritative Environment Variable Manifest

Generated: 2026-05-28 11:20:25 +0530
Project root: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent
Runtime app root: voice_agent_backend/
Output directory: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


## Complete Variable Table
| Variable | Secret | Template default | Evidence |
| --- | --- | --- | --- |
| APP_ENV | no | local | .env.example:8 |
| HOST | no | 0.0.0.0 | .env.example:9 |
| PORT | no | 8000 | .env.example:10 |
| CORS_ORIGINS | no | ["http://localhost:8000","http://127.0.0.1:8000"] | .env.example:11 |
| ALLOWED_HOSTS | no | ["localhost","127.0.0.1"] | .env.example:12 |
| ENABLE_RATE_LIMIT | no | true | .env.example:13 |
| DATABASE_URL | conditional | (blank) | .env.example:14 |
| SECRET_KEY | yes | (blank) | .env.example:17 |
| ALGORITHM | no | HS256 | .env.example:18 |
| ACCESS_TOKEN_EXPIRE_MINUTES | no | 60 | .env.example:19 |
| MAX_FILE_SIZE | no | 52428800 | .env.example:20 |
| GROQ_BASE | no | https://api.groq.com/openai/v1 | .env.example:23 |
| GROQ_API_KEY | yes | (blank) | .env.example:24 |
| OLLAMA_BASE | no | http://localhost:11434 | .env.example:25 |
| QDRANT_BASE | no | http://localhost:6333 | .env.example:26 |
| CHAT_PROVIDER | no | groq | .env.example:29 |
| CHAT_MODEL | no | llama-3.1-8b-instant | .env.example:30 |
| TRANSLATION_PROVIDER | no | groq | .env.example:31 |
| TRANSLATION_MODEL | no | llama-3.1-8b-instant | .env.example:32 |
| EMBED_MODEL | no | mxbai-embed-large:latest | .env.example:33 |
| CORRELATOR_PROVIDER | no | groq | .env.example:34 |
| CORRELATOR_MODEL | no | meta-llama/llama-4-scout-17b-16e-instruct | .env.example:35 |
| DEFAULT_COLLECTION | no | agent_knowledge | .env.example:38 |
| RETRIEVAL_TOP_K | no | 12 | .env.example:39 |
| SUMMARY_TOP_K | no | 16 | .env.example:40 |
| RERANK_TOP_N | no | 6 | .env.example:41 |
| SCORE_THRESHOLD | no | 0.25 | .env.example:42 |
| RETRIEVAL_CONFIDENCE_FLOOR | no | 0.40 | .env.example:43 |
| SUMMARY_CONFIDENCE_FLOOR | no | 0.35 | .env.example:44 |
| CHUNK_SIZE | no | 1200 | .env.example:45 |
| CHUNK_OVERLAP | no | 200 | .env.example:46 |
| MEMORY_PAIRS | no | 10 | .env.example:47 |
| CONTEXT_WINDOW_TURNS | no | 3 | .env.example:48 |
| PREDICTIVE_RAG_TIMEOUT_MS | no | 500 | .env.example:49 |
| KOKORO_MODE | no | native | .env.example:52 |
| KOKORO_DOCKER_URL | no | http://127.0.0.1:8880 | .env.example:53 |
| KOKORO_MODEL_PATH | no | data/models/kokoro-v1.0.onnx | .env.example:54 |
| KOKORO_VOICES_PATH | no | data/models/voices-v1.0.bin | .env.example:55 |
| KOKORO_LANG_CODE | no | a | .env.example:56 |
| TTS_HARDWARE | no | gpu | .env.example:57 |
| TTS_SAMPLE_RATE | no | 24000 | .env.example:58 |
| BACKCHANNEL_PHRASES | no | ["mm-hmm","yeah","I see","got it","right"] | .env.example:59 |
| BACKCHANNEL_COOLDOWN_SECONDS | no | 6.0 | .env.example:60 |
| ENABLE_SEARCH | no | true | .env.example:63 |
| SEARCH_PROVIDER | no | duckduckgo | .env.example:64 |
| TAVILY_API_KEY | yes | (blank) | .env.example:65 |
| IO_THREAD_POOL_SIZE | no | 12 | .env.example:68 |
| GPU_BATCH_SIZE | no | 4 | .env.example:69 |
| ONNX_INTRA_OP_THREADS | no | 4 | .env.example:70 |
| ONNX_INTER_OP_THREADS | no | 2 | .env.example:71 |
| MODELS_TO_CUDA | no | ["kokoro","embed"] | .env.example:72 |
| STT_LOCAL_DEVICE | no | cpu | .env.example:73 |

## Variables Missing from .env.example
None detected among deployment-relevant `Settings` fields during this pass.

## Variables Hardcoded in Source
No real secrets found. Local service defaults and fallback local `SECRET_KEY` exist; production validator rejects the fallback outside local/test (`voice_agent_backend/app/core/config.py:127-145`).
