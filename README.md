# voice-agent

[![CI](https://github.com/RossDmello2/voice-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/RossDmello2/voice-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg)](https://fastapi.tiangolo.com/)

> Local voice-to-voice RAG assistant with FastAPI, vanilla JavaScript, LangGraph, Qdrant, Ollama, Groq, Kokoro ONNX TTS, and SQLite auth.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Features

- Serves a vanilla JavaScript voice-agent UI directly from FastAPI.
- Streams chat responses over Server-Sent Events through `/chat` and `/chat/stream`.
- Supports JWT registration and login backed by local SQLite.
- Ingests PDF, DOCX, TXT, and CSV documents into Qdrant for retrieval-augmented answers.
- Uses Ollama embeddings and optional Ollama chat fallback for local model workflows.
- Uses Groq for cloud chat, translation, and Whisper speech-to-text.
- Runs a LangGraph voice pipeline with stages for translation, intent detection, retrieval, response generation, and speech synthesis.
- Supports Kokoro ONNX TTS with local model artifacts stored under `voice_agent_backend/data/models/`.
- Exposes dependency health checks for Qdrant, Ollama, and Groq.
- Includes Playwright tests for the browser UI.

## Architecture

The runtime application lives in `voice_agent_backend/app`. FastAPI mounts the frontend, registers API routers, initializes the SQLite database, and warms the speech pipeline on startup. The chat path combines intent classification, session memory, Qdrant retrieval, Groq or Ollama generation, and optional Kokoro audio output.

```text
Browser -> FastAPI routes -> LangGraph/RAG services -> Qdrant/Ollama/Groq -> SSE/audio response
```

Full architecture notes are in [docs/architecture](docs/architecture/). Historical discovery notes are preserved in [docs/intelligence](docs/intelligence/).

## Quick Start

### Prerequisites

- Python 3.10 or newer; Python 3.11 is recommended.
- Node.js for `node --check` and Playwright tooling.
- Qdrant running on port `6333` for document search.
- Ollama running on port `11434` with `mxbai-embed-large:latest` for embeddings.
- A Groq API key for cloud chat, translation, and STT.
- Optional: CUDA-compatible ONNX Runtime setup for Kokoro GPU TTS.

### Installation

```bash
git clone https://github.com/RossDmello2/voice-agent.git
cd voice-agent
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r voice_agent_backend/requirements.txt
cp .env.example voice_agent_backend/.env
# Edit voice_agent_backend/.env before starting the app.
```

### Running

Start Qdrant:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Start the backend and frontend:

```bash
cd voice_agent_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000`.

## Configuration

All runtime configuration is read from `voice_agent_backend/.env`. Copy `.env.example` from the repository root and fill in the required values.

| Variable | Required | Default | Description |
|---|---|---|---|
| `OLLAMA_BASE` | No | `http://localhost:11434` | Ollama API base URL for embeddings and optional chat. |
| `QDRANT_BASE` | No | `http://localhost:6333` | Qdrant API base URL. |
| `GROQ_BASE` | No | `https://api.groq.com/openai/v1` | Groq OpenAI-compatible API base URL. |
| `GROQ_API_KEY` | Yes for Groq/STT | none | Groq API key. |
| `CHAT_MODEL` | No | `llama-3.1-8b-instant` | Default chat model. |
| `EMBED_MODEL` | No | `mxbai-embed-large:latest` | Default Ollama embedding model. |
| `TRANSLATION_MODEL` | No | `llama-3.1-8b-instant` | Translation model. |
| `CHAT_PROVIDER` | No | `groq` | Chat provider: `groq` or `ollama`. |
| `TRANSLATION_PROVIDER` | No | `groq` | Translation provider. |
| `DEFAULT_COLLECTION` | No | `agent_knowledge` | Default Qdrant collection. |
| `RETRIEVAL_TOP_K` | No | `12` | Number of retrieval candidates. |
| `SUMMARY_TOP_K` | No | `16` | Number of summary candidates. |
| `RERANK_TOP_N` | No | `6` | Number of reranked chunks retained. |
| `SCORE_THRESHOLD` | No | `0.25` | Baseline retrieval threshold. |
| `RETRIEVAL_CONFIDENCE_FLOOR` | No | `0.40` | Confidence floor for document answers. |
| `SUMMARY_CONFIDENCE_FLOOR` | No | `0.35` | Confidence floor for summaries. |
| `CHUNK_SIZE` | No | `1200` | Text chunk size for ingestion. |
| `CHUNK_OVERLAP` | No | `200` | Text chunk overlap for ingestion. |
| `MEMORY_PAIRS` | No | `10` | Number of conversation pairs included in context. |
| `KOKORO_MODE` | No | `native` | TTS mode: `native`, `docker`, or `disabled`. |
| `KOKORO_DOCKER_URL` | No | `http://127.0.0.1:8880` | Kokoro sidecar URL. |
| `KOKORO_MODEL_PATH` | No | `data/models/kokoro-v1.0.onnx` | Kokoro ONNX model path relative to `voice_agent_backend`. |
| `KOKORO_VOICES_PATH` | No | `data/models/voices-v1.0.bin` | Kokoro voice artifact path relative to `voice_agent_backend`. |
| `KOKORO_LANG_CODE` | No | `a` | Kokoro language code. |
| `TTS_HARDWARE` | No | `gpu` | Preferred TTS hardware: `gpu` or `cpu`. |
| `TTS_SAMPLE_RATE` | No | `24000` | TTS sample rate in Hz. |
| `CONTEXT_WINDOW_TURNS` | No | `3` | LangGraph context window size. |
| `CORRELATOR_MODEL` | No | `meta-llama/llama-4-scout-17b-16e-instruct` | Follow-up correlation model. |
| `CORRELATOR_PROVIDER` | No | `groq` | Follow-up correlation provider. |
| `BACKCHANNEL_PHRASES` | No | JSON list | Short phrases precomputed for voice backchannels. |
| `BACKCHANNEL_COOLDOWN_SECONDS` | No | `6.0` | Minimum seconds between backchannels. |
| `PREDICTIVE_RAG_TIMEOUT_MS` | No | `500` | Predictive RAG timeout budget. |
| `ENABLE_SEARCH` | No | `true` | Enables web search node. |
| `SEARCH_PROVIDER` | No | `duckduckgo` | Search provider: `duckduckgo` or `tavily`. |
| `TAVILY_API_KEY` | No | none | Tavily API key if using Tavily. |
| `CORS_ORIGINS` | No | local app URLs | Allowed CORS origins. |
| `ALLOWED_HOSTS` | No | local hosts | Allowed hostnames. |
| `SECRET_KEY` | Yes | none in template | JWT signing key. |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | JWT expiry time. |
| `MAX_FILE_SIZE` | No | `52428800` | Upload size limit in bytes. |
| `ENABLE_RATE_LIMIT` | No | `true` | Enables API rate limits. |
| `HOST` | No | `0.0.0.0` | Server bind host. |
| `PORT` | No | `8000` | Server port. |
| `IO_THREAD_POOL_SIZE` | No | `12` | Default executor worker count. |
| `GPU_BATCH_SIZE` | No | `4` | GPU batch size. |
| `ONNX_INTRA_OP_THREADS` | No | `4` | ONNX intra-op thread count. |
| `ONNX_INTER_OP_THREADS` | No | `2` | ONNX inter-op thread count. |
| `MODELS_TO_CUDA` | No | JSON list | Models preferred on CUDA. |
| `STT_LOCAL_DEVICE` | No | `cpu` | Local STT device preference. |

## Project Structure

```text
voice-agent/
├── docs/                         Documentation and architecture notes
│   ├── architecture/             Current architecture docs
│   ├── guides/                   Handoff and operation guides
│   ├── intelligence/             Historical discovery/audit notes
│   └── specs/                    Migration and technical plans
├── voice_agent_backend/          Runtime backend and served frontend
│   ├── app/                      FastAPI application code
│   ├── data/                     Local models and SQLite data
│   ├── frontend/                 Vanilla JavaScript UI
│   ├── scripts/checks/           Developer checks
│   ├── scripts/manual_tests/     Manual smoke scripts
│   └── tests/frontend/           Playwright frontend tests
└── .github/                      GitHub workflows and templates
```

## Running Tests

```bash
# JavaScript syntax check
node --check voice_agent_backend/frontend/script.js

# Frontend test suite
cd voice_agent_backend
python -m pytest tests/frontend -q

# Python syntax check
python -m py_compile $(find . -name "*.py" -not -path "*/.venv/*" -not -path "*/venv/*" -not -path "*/__pycache__/*")

# Collection check
python -m pytest --collect-only -q
```

## API Reference

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/auth/register` | Register a local user and return a bearer token. | No |
| `POST` | `/auth/login` | Login with OAuth2 form credentials and return a bearer token. | No |
| `POST` | `/chat` | Stream legacy chat/RAG responses over SSE. | Yes |
| `POST` | `/chat/predict` | Warm predictive RAG cache for an in-progress query. | No |
| `POST` | `/chat/backchannel/{session_id}` | Emit a precomputed voice backchannel. | No |
| `POST` | `/chat/stream` | Stream the LangGraph voice pipeline over SSE. | No |
| `POST` | `/chat/interrupt/{thread_id}` | Resume an interrupted LangGraph thread. | No |
| `POST` | `/ingest` | Upload and index a PDF, DOCX, TXT, or CSV file. | Yes |
| `POST` | `/stt` | Transcribe uploaded audio with Groq Whisper. | No |
| `POST` | `/tts/generate` | Stream Kokoro TTS audio for text. | No |
| `GET` | `/collections` | List Qdrant collections. | Yes |
| `POST` | `/collections` | Create a Qdrant collection. | Yes |
| `DELETE` | `/collections/{collection_name}` | Delete a Qdrant collection. | Yes |
| `GET` | `/collections/{collection_name}/documents` | List indexed documents in a collection. | No |
| `DELETE` | `/collections/{collection_name}/documents/{filename}` | Delete one document from a collection. | Yes |
| `GET` | `/health` | Check Qdrant, Ollama, Groq, and model availability. | No |
| `GET` | `/models` | List available chat, embedding, and TTS model options. | No |

Non-trivial request models are defined in [voice_agent_backend/app/models/schemas.py](voice_agent_backend/app/models/schemas.py). Authentication helpers are in [voice_agent_backend/app/core/auth.py](voice_agent_backend/app/core/auth.py).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, style, and pull request guidelines.

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE).
