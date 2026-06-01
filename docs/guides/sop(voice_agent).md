# Local Operating Guide: VoiceRAG Agent

This guide is for running VoiceRAG Agent locally from a cloned repository. It replaces older machine-specific instructions that referenced private local paths.

## What VoiceRAG Agent Is

VoiceRAG Agent is a local-first voice-to-voice RAG assistant. It serves a browser UI from FastAPI, accepts text or voice input, can ingest documents into Qdrant, retrieves document context with Ollama embeddings, generates responses through Groq or Ollama, and can speak responses through Kokoro ONNX TTS.

Groq-backed STT/chat/translation use cloud APIs. Keep provider keys in `voice_agent_backend/.env`; never paste secrets into issues, screenshots, or docs.

## Start The App

From the repository root:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r voice_agent_backend\requirements.txt
Copy-Item .env.example voice_agent_backend\.env
```

Edit `voice_agent_backend\.env`, then start the dependencies you need:

```powershell
docker run -p 6333:6333 qdrant/qdrant
ollama pull mxbai-embed-large
```

Start the app:

```powershell
Set-Location voice_agent_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://127.0.0.1:8000`.

## Use The UI

- Use the text box for typed questions.
- Use the microphone button for voice input when browser speech capture is available.
- Sign in before uploading documents or creating/deleting collections.
- Keep read-only chat and health checks local-first unless you intentionally add broader deployment auth.

## Stop The App

Press `Ctrl+C` in the terminal that is running Uvicorn.

## Useful Checks

```powershell
git check-ignore voice_agent_backend/.env voice_agent_backend/data/models/kokoro-v1.0.onnx voice_agent_backend/data/sqlite/voice_agent.db
node --check voice_agent_backend/frontend/script.js
Set-Location voice_agent_backend
python -m compileall app scripts tests
python -m pytest tests/backend tests/frontend -q
python scripts/checks/import_smoke.py
python -c "from app.main import app; print(app.title)"
```

Provider-level smoke checks need configured Qdrant, Ollama, Kokoro model artifacts, and Groq credentials.
