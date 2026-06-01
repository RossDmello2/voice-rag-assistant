# SA-4: Data Layer Report

Generated: 2026-05-28 11:20:25 +0530
Project root: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent
Runtime app root: voice_agent_backend/
Output directory: C:/Users/rossd/OneDrive/Desktop/logic/voice_agent/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


Line-count note: this report is concise because the persistent schema is small; required sections are present.

## Schema Inventory
| Entity | Evidence | Notes |
| --- | --- | --- |
| User | voice_agent_backend/app/models/user.py:6-13 | id, email, password_hash, is_active, created_at |
| UserSession | voice_agent_backend/app/models/user.py:15-20 | id, user_id, expires_at, created_at |
| ChatRequest | voice_agent_backend/app/models/schemas.py:5-14 | chat/session/collection/language/model fields |
| IngestResponse | voice_agent_backend/app/models/schemas.py:32-36 | filename, chunks, collection, status |
| ChatStreamRequest | voice_agent_backend/app/models/schemas.py:41-58 | graph streaming request |

## Migration History Summary
No Alembic or migration directory was found. Startup creates tables with `Base.metadata.create_all` (`voice_agent_backend/app/core/database.py:31-33`).

## Query Audit
| Operation | Evidence | Assessment |
| --- | --- | --- |
| register user check/insert | voice_agent_backend/app/api/routes/auth.py:23-34 | SQLAlchemy parameterized; hashes password |
| login lookup | voice_agent_backend/app/api/routes/auth.py:41-44 | SQLAlchemy parameterized; bcrypt verify |
| current user lookup | voice_agent_backend/app/core/auth.py:65-68 | token subject to email lookup |
| Qdrant create/upsert/delete | voice_agent_backend/app/services/qdrant_service.py:105-225 | requires write acknowledgement |
| Qdrant vector search | voice_agent_backend/app/services/qdrant_service.py:228-255 | score threshold and payload returned |

## Vector Store Analysis
Ingest extracts PDF/DOCX/TXT/CSV, chunks with metadata, embeds via Ollama, and writes Qdrant points containing text/source/chunk/page/section fields (`voice_agent_backend/app/api/routes/ingest.py:249-418`).

## Database Hosting Compatibility (v3)
| Store | Status | Evidence | Action |
| --- | --- | --- | --- |
| SQLite local | READY for private single instance | voice_agent_backend/app/core/database.py:8-10 | mount persistent disk |
| Postgres | NEEDS CHANGES | DATABASE_URL exists at voice_agent_backend/app/core/config.py:132 | add driver, migrations, tests |
| Qdrant hosted/container | NEEDS CONFIG | .env.example:26 | set QDRANT_BASE |
| Ollama hosted/sidecar | NEEDS CONFIG | .env.example:25 | set OLLAMA_BASE or use cloud embeddings |
