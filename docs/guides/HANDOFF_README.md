# Voice Agent — Production Setup Guide
## (Handoff Document — readable by humans AND local LLMs)

---

## WHAT THIS IS

A full-stack voice agent web application with:
- **Frontend**: Vanilla JavaScript, served by FastAPI at http://localhost:8000
- **Backend**: Python 3.10+ / FastAPI (async)
- **Database**: SQLite (user auth only) — auto-created on first run
- **Vector DB**: Qdrant (required — run separately)
- **LLM**: Groq API (cloud) or Ollama (local)
- **Embeddings**: Ollama (local)
- **STT**: Groq Whisper API
- **TTS**: Browser Web Speech API (built-in, no setup needed)

---

## QUICK START (5 steps)

### Step 1 — Prerequisites
Install these before anything else:
```
Python 3.10 or higher
pip (Python package manager)
Qdrant vector database (see Step 2)
```

### Step 2 — Start Qdrant
Qdrant is REQUIRED for document storage. Run it with Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant
```
Or download from https://qdrant.tech/documentation/quick-start/

### Step 3 — Configure environment
Copy the root `.env.example` file to `voice_agent_backend/.env`, then set your Groq API key:
```
GROQ_API_KEY=
```
Get a free Groq key at https://console.groq.com

### Step 4 — Install Python dependencies
```bash
cd voice_agent_backend
pip install -r requirements.txt
```

### Step 5 — Start the server
**Windows:**
```
Double-click start_server.bat
```
Or from terminal:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Linux / macOS:**
```bash
bash start_server.sh
```

### Step 6 — Open the app
Go to: http://localhost:8000

You will see a **Sign In** screen. Click **Register** to create your account (stored locally in SQLite). Then sign in.

---

## ARCHITECTURE OVERVIEW

```
Browser (http://localhost:8000)
    ↓  GET /           → FastAPI serves index.html (frontend)
    ↓  POST /auth/login → FastAPI verifies user, returns JWT token
    ↓  POST /chat      → FastAPI → Groq LLM (streaming SSE)
    ↓  POST /ingest    → FastAPI → Qdrant (document upload)
    ↓  POST /stt       → FastAPI → Groq Whisper (audio)
    ↓  GET  /health    → FastAPI → checks Qdrant + Groq + Ollama
```

Current repository layout note: the public `.env.example` now lives at the repository root. Runtime-local artifacts live under `voice_agent_backend/data/`: Kokoro files are in `data/models/`, and SQLite is in `data/sqlite/`. Frontend tests live in `voice_agent_backend/tests/frontend/`, developer checks live in `voice_agent_backend/scripts/checks/`, and manual smoke scripts live in `voice_agent_backend/scripts/manual_tests/`.

---

## FILE STRUCTURE

```
voice_agent_backend/
├── .env                    ← YOUR CONFIG (edit GROQ_API_KEY here)
├── .env.example            ← Template for .env
├── requirements.txt        ← Python dependencies
├── start_server.bat        ← Windows startup script
├── start_server.sh         ← Linux/macOS startup script
├── app/
│   ├── main.py             ← FastAPI app, middleware, routes
│   ├── core/
│   │   ├── config.py       ← Settings (reads .env)
│   │   ├── auth.py         ← JWT token logic
│   │   ├── database.py     ← SQLite async engine
│   │   ├── intent.py       ← Intent classifier (regex + LLM)
│   │   ├── langchain_rag.py← RAG pipeline (embed, search, rerank)
│   │   ├── memory.py       ← In-memory session store
│   │   ├── voice_graph.py  ← LangGraph pipeline (optional)
│   │   └── nodes/          ← LangGraph node functions
│   ├── api/routes/
│   │   ├── auth.py         ← POST /auth/login, /auth/register
│   │   ├── chat.py         ← POST /chat (SSE streaming)
│   │   ├── collections.py  ← GET/POST/DELETE /collections
│   │   ├── health.py       ← GET /health
│   │   ├── ingest.py       ← POST /ingest (file upload)
│   │   ├── models.py       ← GET /models
│   │   └── stt.py          ← POST /stt (audio)
│   ├── models/
│   │   ├── user.py         ← SQLAlchemy User model
│   │   └── schemas.py      ← Pydantic request/response models
│   └── services/
│       ├── groq_service.py ← Groq API (chat + STT)
│       ├── ollama_service.py← Ollama (embeddings + chat)
│       ├── qdrant_service.py← Qdrant vector DB operations
│       ├── llm_router.py   ← Routes to Groq or Ollama
│       └── speech_service.py← Kokoro TTS (optional)
└── frontend/
    ├── index.html          ← Single-page app HTML
    ├── style.css           ← All styles
    └── script.js           ← All frontend JavaScript
```

---

## CONFIGURATION (.env keys)

| Key | Default | Description |
|-----|---------|-------------|
| GROQ_API_KEY | (empty) | **REQUIRED** — Get from console.groq.com |
| GROQ_BASE | https://api.groq.com/openai/v1 | Groq API base URL |
| CHAT_MODEL | llama-3.1-8b-instant | Groq model for chat |
| CHAT_PROVIDER | groq | "groq" or "ollama" |
| OLLAMA_BASE | http://localhost:11434 | Ollama URL (only if using Ollama) |
| EMBED_MODEL | mxbai-embed-large:latest | Ollama embedding model |
| QDRANT_BASE | http://localhost:6333 | Qdrant URL |
| SECRET_KEY | (set in .env) | JWT signing key — change this! |
| PORT | 8000 | Server port |
| KOKORO_MODE | disabled | TTS: "disabled", "native", or "docker" |
| KOKORO_MODEL_PATH | data/models/kokoro-v1.0.onnx | Kokoro ONNX model file |
| KOKORO_VOICES_PATH | data/models/voices-v1.0.bin | Kokoro voice artifact file |

---

## BUGS FIXED IN THIS VERSION

1. **[CRITICAL] Frontend had zero auth** — No login/register UI, no token storage, all protected API endpoints returned 401. Fixed by:
   - Adding full login/register modal in `index.html`
   - Adding `AUTH` module in `script.js` (token in localStorage)
   - Adding `window.fetch` interceptor that auto-injects `Authorization: Bearer <token>` on every same-origin request
   - `init()` now shows auth modal if not logged in

2. **[CRITICAL] `ingest.py` dead temp file code** — File was saved to disk but `ingest_document()` re-read from the UploadFile object. Removed dead code; now passes `file_content` bytes directly.

3. **[CRITICAL] `qdrant_service.py` delete_collection bad API** — Called Qdrant points/delete with invalid filter format before collection delete. Fixed to directly call `DELETE /collections/{name}` which removes everything.

4. **[HIGH] CORS missing DELETE/PUT methods** — Frontend calls DELETE to remove documents/collections, POST to create. CORS now allows all needed methods.

5. **[HIGH] `requirements.txt` included `kokoro`** — Kokoro TTS library is hard to install and only needed if `KOKORO_MODE=native`. Made optional (commented out). `KOKORO_MODE=disabled` by default.

6. **[HIGH] `start_server.bat` hardcoded personal path** — Changed to use `%~dp0` (directory of the script). Added Linux `start_server.sh`.

7. **[MEDIUM] HSTS header breaks `http://localhost`** — Removed Strict-Transport-Security header (only valid for HTTPS production).

8. **[MEDIUM] VoicePipeline `result.data`** — `ReadableStreamReadResult` has `.value`, not `.data`. Fixed to `result.value`.

9. **[LOW] `speech_service.py` numpy top-level import** — Made safe with try/except so import failure doesn't crash the whole server.

---

## HOW AUTH WORKS

1. User opens `http://localhost:8000` → sees login modal
2. User registers (first time) or logs in
3. Backend creates/validates user in SQLite, returns JWT token
4. Frontend stores token in `localStorage` as `ssa_auth_token`
5. `window.fetch` is patched — all API calls auto-include `Authorization: Bearer <token>`
6. On page reload, token is loaded from localStorage → user stays logged in
7. Logout clears the token from localStorage and shows the modal again

---

## HOW RAG (DOCUMENT Q&A) WORKS

1. User uploads PDF/DOCX/TXT/CSV via Documents panel
2. Backend (`/ingest`):
   - Extracts text from file
   - Chunks text with section/heading awareness
   - Sends each chunk to Ollama for embedding
   - Stores vectors + metadata in Qdrant
3. User asks a question
4. Backend (`/chat`):
   - Classifies intent (document query vs general chat)
   - Generates multiple query variants
   - Embeds queries via Ollama
   - Searches Qdrant for similar chunks
   - Re-ranks results using BM25 + vector hybrid scoring
   - Passes top chunks to Groq LLM as context
   - Streams response back via SSE

---

## SERVICES STATUS CHECK

When you open the app, the status bar shows:
- **Ollama**: Green = embedding models ready. Red = Ollama not running (OK if using Groq for chat)
- **Qdrant**: Green = vector DB ready. Red = Qdrant not running (documents won't work)
- **Groq**: Green = API key valid. Red = invalid key or no internet

---

## COMMON ISSUES

**"Backend connection failed"**
→ Server isn't running. Run `start_server.bat` or `python -m uvicorn app.main:app --port 8000`

**Groq shows red / chat doesn't work**
→ Edit `.env` and set a real `GROQ_API_KEY`

**Documents can't be uploaded / "Ingest failed"**
→ Qdrant isn't running. Start it: `docker run -p 6333:6333 qdrant/qdrant`

**"All chunks failed to embed"**
→ Ollama isn't running or embedding model not pulled.
→ Run: `ollama pull mxbai-embed-large`

**Login modal keeps showing after login**
→ Check browser console for errors. May be CORS or server not running.

**Page loads but is blank**
→ Check browser console. CDN scripts (marked.js) need internet access.

---

## RUNNING WITHOUT OLLAMA (Groq-only mode)

If you don't want to run Ollama locally:
1. You won't be able to upload documents (embedding requires Ollama)
2. Chat will still work for general conversation
3. Set `CHAT_PROVIDER=groq` in `.env` (already default)

---

## FOR LOCAL LLM (HANDOFF CONTEXT)

If you are a local LLM helping to debug this project, here are the key facts:

- **Entry point**: `app/main.py` → FastAPI application
- **Auth**: JWT tokens, created in `app/core/auth.py`, validated via `Depends(get_current_user)` on protected routes
- **Protected routes**: `/chat`, `/chat/stream`, `/chat/interrupt/*`, `/ingest`, `GET /collections`, `POST /collections`, `DELETE /collections/*`, `DELETE /collections/*/documents/*`
- **Public routes**: `/health`, `/models`, `/stt`, `/auth/login`, `/auth/register`, `GET /collections/*/documents`
- **Frontend token**: Stored in `localStorage.ssa_auth_token`, injected into all fetch() calls via patched `window.fetch`
- **LLM streaming**: SSE (Server-Sent Events) — `data: {"token": "..."}\n\n` format, ends with `data: [DONE]\n\n`
- **Vector search**: Qdrant at `http://localhost:6333` — collection name defaults to `agent_knowledge`
- **Embedding**: Ollama `/api/embed` endpoint — model `mxbai-embed-large:latest` (1024 dimensions)
- **Session memory**: In-memory Python dict in `app/core/memory.py` (resets on server restart)
- **Database**: SQLite file `data/sqlite/voice_agent.db` under `voice_agent_backend` (auto-created if missing)

---

## PORTS USED

| Port | Service |
|------|---------|
| 8000 | Voice Agent (FastAPI — this app) |
| 6333 | Qdrant vector DB |
| 11434 | Ollama (local LLM/embeddings) |
