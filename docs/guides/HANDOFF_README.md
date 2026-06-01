# VoiceRAG Agent Handoff Guide

This guide is a short operational handoff for maintainers and local coding agents. It reflects the current repository layout and should be read alongside:

- [../../README.md](../../README.md)
- [../README.md](../README.md)
- [../architecture/README.md](../architecture/README.md)
- [../features/README.md](../features/README.md)

## What This Project Is

VoiceRAG Agent is a local-first voice-to-voice RAG assistant. FastAPI serves a vanilla JavaScript frontend, handles API routes, stores local users in SQLite, sends document vectors to Qdrant, uses Ollama for embeddings and optional chat, uses Groq for cloud chat/STT/translation when configured, and uses Kokoro ONNX for local TTS when model artifacts are present.

It is self-hosted, but not fully offline by default because Groq-backed features call cloud APIs when enabled.

## Runtime Roots

```text
voice-rag-agent/
|-- README.md
|-- .env.example
|-- docs/
`-- voice_agent_backend/
    |-- app/          FastAPI backend
    |-- frontend/     Vanilla JavaScript UI served by FastAPI
    |-- data/         Local model and SQLite paths; runtime artifacts are ignored
    |-- scripts/      Checks and manual smoke scripts
    `-- tests/        Backend and frontend tests
```

The app reads runtime configuration from `voice_agent_backend/.env`. Do not commit that file.

## Local Setup

```bash
git clone https://github.com/RossDmello2/voice-rag-agent.git
cd voice-rag-agent
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r voice_agent_backend/requirements.txt
pip install -r requirements-dev.txt
python -m playwright install chromium
cp .env.example voice_agent_backend/.env
```

Edit `voice_agent_backend/.env` before starting the app.

Minimum local dependencies for document RAG:

- Qdrant at `http://localhost:6333`
- Ollama at `http://localhost:11434`
- Ollama embedding model `mxbai-embed-large:latest`

Groq-backed chat/STT/translation requires `GROQ_API_KEY`. Kokoro native TTS requires local model artifacts:

- `voice_agent_backend/data/models/kokoro-v1.0.onnx`
- `voice_agent_backend/data/models/voices-v1.0.bin`

## Run Commands

Start Qdrant:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Start the app:

```bash
cd voice_agent_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000`.

## API Boundary

Public/local-first endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `POST /chat`
- `POST /chat/predict`
- `POST /chat/backchannel/{session_id}`
- `POST /chat/stream`
- `POST /chat/interrupt/{thread_id}`
- `POST /stt`
- `POST /tts/generate`
- `GET /collections`
- `GET /collections/{collection_name}/documents`
- `GET /health`
- `GET /models`

Bearer-token protected write endpoints:

- `POST /ingest`
- `POST /collections`
- `DELETE /collections/{collection_name}`
- `DELETE /collections/{collection_name}/documents/{filename}`

Do not describe chat, read-only collection listing, or health/model endpoints as protected unless the source changes.

## Configuration Notes

Important variables:

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | Runtime mode; production rejects fallback secrets. |
| `SECRET_KEY` | JWT signing key. Set a strong value outside local tests. |
| `DATABASE_URL` | Optional SQLAlchemy URL; defaults to local SQLite. |
| `GROQ_API_KEY` | Groq cloud chat/STT/translation key. |
| `OLLAMA_BASE` | Ollama API base URL. |
| `QDRANT_BASE` | Qdrant API base URL. |
| `KOKORO_MODE` | `native`, `docker`, or `disabled`. |
| `KOKORO_MODEL_PATH` | Kokoro ONNX path relative to `voice_agent_backend`. |
| `KOKORO_VOICES_PATH` | Kokoro voice artifact path relative to `voice_agent_backend`. |

`ALLOWED_HOSTS` exists in configuration but is not enforced by middleware in the current source. Do not rely on it as a deployment security control until host enforcement is implemented.

## Verification Commands

```bash
git check-ignore voice_agent_backend/.env voice_agent_backend/data/models/kokoro-v1.0.onnx voice_agent_backend/data/sqlite/voice_agent.db
node --check voice_agent_backend/frontend/script.js
cd voice_agent_backend
python -m compileall app scripts tests
python -m pytest tests/backend tests/frontend -q
python -m pytest --collect-only -q
python scripts/checks/import_smoke.py
python -c "from app.main import app; print(app.title)"
```

Use browser smoke testing after frontend changes.

## Security Notes

- Do not read, print, or commit `voice_agent_backend/.env`.
- Do not commit SQLite DBs or Kokoro model artifacts.
- Keep provider keys server-side only.
- Assistant Markdown must pass through `renderMarkdownSafe()` before DOM insertion.
- Add broader auth before exposing cost-bearing chat/STT/TTS endpoints publicly.
- Report vulnerabilities through GitHub private vulnerability reporting, not public issues.

## Known Gaps

- Full provider smoke requires Qdrant, Ollama, Kokoro artifacts, and Groq credentials.
- CodeQL is enabled and passing, but open code-scanning alerts remain until core-code fixes are approved.
- The GitHub social preview source image is committed, but uploading it to repository settings is an owner-side manual step.
