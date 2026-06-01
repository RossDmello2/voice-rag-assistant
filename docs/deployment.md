# Deployment

This project is a local-first FastAPI app that serves its vanilla JavaScript UI from the same origin.

## Local Runtime

1. Copy `.env.example` to `voice_agent_backend/.env`.
2. Set `SECRET_KEY` to a strong random value.
3. Set `GROQ_API_KEY` if using Groq chat, translation, or STT.
4. Start Qdrant on `http://localhost:6333`.
5. Start Ollama on `http://localhost:11434` and install the configured embedding model when using local embeddings.
6. Place Kokoro artifacts at:
   - `voice_agent_backend/data/models/kokoro-v1.0.onnx`
   - `voice_agent_backend/data/models/voices-v1.0.bin`
7. Start the app:

```bash
cd voice_agent_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`.

## Docker

Build from the backend directory:

```bash
cd voice_agent_backend
docker build -t voice-rag-agent .
```

Run with a mounted `.env` file and local data directory:

```bash
docker run --rm -p 8000:8000 --env-file .env -v "%cd%/data:/app/data" voice-rag-agent
```

The image starts Uvicorn with `${PORT:-8000}`, so hosted platforms that inject `PORT` can bind the expected port without editing the Dockerfile. The container expects Qdrant, Ollama, and any Kokoro sidecar to be reachable from inside Docker. Use host-network equivalents or service names when composing multiple containers.

## Public Exposure Checklist

- Set `APP_ENV=production`.
- Use a strong `SECRET_KEY`; the fallback local secret is rejected in production mode.
- Serve behind HTTPS.
- Restrict `CORS_ORIGINS`.
- `ALLOWED_HOSTS` is currently configuration only; add host enforcement middleware before relying on it as a deployment control.
- Do not expose Qdrant, Ollama, SQLite, `.env`, or model files directly.
- Keep Groq/Tavily keys server-side only.
- Add broader auth to chat/STT/TTS before hosting an open public endpoint with cost-bearing providers.

## Artifact Policy

The local `.env`, SQLite database, and Kokoro model files are intentionally ignored by git. Restore them from local backups or documented model sources after cloning.
