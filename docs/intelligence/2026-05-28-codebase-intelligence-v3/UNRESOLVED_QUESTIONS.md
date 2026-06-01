# Unresolved Questions

Generated: 2026-05-28 11:20:25 +0530
Project root: <repo-root>
Runtime app root: voice_agent_backend/
Output directory: <repo-root>/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


| Question | Why it matters | Evidence | Next inspection |
| --- | --- | --- | --- |
| SQLite disk or managed Postgres? | Controls migrations, disk, backups, scaling | voice_agent_backend/app/core/database.py:8-33 | Choose deploy tier and test DB |
| Hosted Qdrant/Ollama topology? | Localhost defaults fail in cloud | .env.example:25-26 | Choose managed/sidecar services |
| Protect chat/STT/TTS publicly? | Controls cost and abuse | docs/deployment.md:49 | Define public/private auth mode |
| Enable Kokoro native hosted? | Requires artifacts and compute | .env.example:52-55 | Run container smoke |
| Can pip-audit finish? | Dependency vulnerability state unknown | verification timeout | Re-run with more time |
