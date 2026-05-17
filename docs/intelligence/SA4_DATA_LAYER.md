# SA-4: Data Layer Report

## Scope
Read-only inspection of SQLAlchemy models, Pydantic schemas, SQLite schema, Qdrant vector operations, memory/cache stores, and database/vector query paths. `.env` values were not read. SQLite was inspected schema-only via a read-only connection.

## Schema Inventory
| File:Line | Definition |
| --- | --- |
| docs/intelligence/_generate_docs.py:163 | if re.search(r"class .*BaseModel\|class .*Base\)\|mapped_column\(\|ForeignKey\(\|Base\.metadata\|create_all", line): |
| docs/intelligence/_generate_docs.py:169 | if re.search(r"select\(\|db\.execute\|commit\(\|create_all\|_qdrant_\|search_vectors\|upsert_points\|scroll\|points/delete", line): |
| voice_agent_backend/app/api/routes/auth.py:12 | class UserRegister(BaseModel): |
| voice_agent_backend/app/api/routes/auth.py:16 | class Token(BaseModel): |
| voice_agent_backend/app/api/routes/tts.py:11 | class TTSRequest(BaseModel): |
| voice_agent_backend/app/core/database.py:14 | class Base(DeclarativeBase): |
| voice_agent_backend/app/core/database.py:23 | await conn.run_sync(Base.metadata.create_all) |
| voice_agent_backend/app/models/schemas.py:5 | class ChatRequest(BaseModel): |
| voice_agent_backend/app/models/schemas.py:16 | class STTResponse(BaseModel): |
| voice_agent_backend/app/models/schemas.py:21 | class CollectionCreateRequest(BaseModel): |
| voice_agent_backend/app/models/schemas.py:26 | class DocumentInfo(BaseModel): |
| voice_agent_backend/app/models/schemas.py:32 | class IngestResponse(BaseModel): |
| voice_agent_backend/app/models/schemas.py:41 | class ChatStreamRequest(BaseModel): |
| voice_agent_backend/app/models/schemas.py:61 | class InterruptRequest(BaseModel): |
| voice_agent_backend/app/models/user.py:6 | class User(Base): |
| voice_agent_backend/app/models/user.py:9 | id: Mapped[int] = mapped_column(primary_key=True, index=True) |
| voice_agent_backend/app/models/user.py:10 | email: Mapped[str] = mapped_column(String(255), unique=True, index=True) |
| voice_agent_backend/app/models/user.py:11 | password_hash: Mapped[str] = mapped_column(String(255)) |
| voice_agent_backend/app/models/user.py:12 | is_active: Mapped[bool] = mapped_column(default=True) |
| voice_agent_backend/app/models/user.py:13 | created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow) |
| voice_agent_backend/app/models/user.py:15 | class UserSession(Base): |
| voice_agent_backend/app/models/user.py:18 | id: Mapped[str] = mapped_column(String(128), primary_key=True, index=True) |
| voice_agent_backend/app/models/user.py:19 | user_id: Mapped[int] = mapped_column(ForeignKey("users.id")) |
| voice_agent_backend/app/models/user.py:20 | expires_at: Mapped[datetime] = mapped_column() |
| voice_agent_backend/app/models/user.py:21 | created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow) |

## SQLite Schema
| Type | Name | SQL / Value |
| --- | --- | --- |
| index | ix_user_sessions_id | CREATE INDEX ix_user_sessions_id ON user_sessions (id) |
| index | ix_users_email | CREATE UNIQUE INDEX ix_users_email ON users (email) |
| index | ix_users_id | CREATE INDEX ix_users_id ON users (id) |
| index | sqlite_autoindex_user_sessions_1 | None |
| table | user_sessions | CREATE TABLE user_sessions (<br>	id VARCHAR(128) NOT NULL, <br>	user_id INTEGER NOT NULL, <br>	expires_at DATETIME NOT NULL, <br>	created_at DATETIME NOT NULL, <br>	PRIMARY KEY (id), <br>	FOREIGN KEY(user_id) REFERENCES users (id)<br>) |
| table | users | CREATE TABLE users (<br>	id INTEGER NOT NULL, <br>	email VARCHAR(255) NOT NULL, <br>	password_hash VARCHAR(255) NOT NULL, <br>	is_active BOOLEAN NOT NULL, <br>	created_at DATETIME NOT NULL, <br>	PRIMARY KEY (id)<br>) |
| pragma | foreign_keys | 0 |

## Entity Relationship Map
`users (1) --> (N) user_sessions`. `users.id` is the parent key at `voice_agent_backend/app/models/user.py:9`; `user_sessions.user_id` references it at `voice_agent_backend/app/models/user.py:19`. ORM relationships and cascade policies are not defined.

## SQL Query Audit
| File:Line | Query / Storage Operation |
| --- | --- |
| docs/intelligence/_generate_docs.py:163 | if re.search(r"class .*BaseModel\|class .*Base\)\|mapped_column\(\|ForeignKey\(\|Base\.metadata\|create_all", line): |
| docs/intelligence/_generate_docs.py:169 | if re.search(r"select\(\|db\.execute\|commit\(\|create_all\|_qdrant_\|search_vectors\|upsert_points\|scroll\|points/delete", line): |
| voice_agent_backend/app/api/routes/auth.py:23 | result = await db.execute(select(User).where(User.email == user_data.email)) |
| voice_agent_backend/app/api/routes/auth.py:33 | await db.commit() |
| voice_agent_backend/app/api/routes/auth.py:41 | result = await db.execute(select(User).where(User.email == form_data.username)) |
| voice_agent_backend/app/api/routes/ingest.py:4 | from app.services.qdrant_service import create_collection, upsert_points |
| voice_agent_backend/app/api/routes/ingest.py:391 | await upsert_points(collection, points) |
| voice_agent_backend/app/core/auth.py:65 | result = await db.execute(select(User).where(User.email == email)) |
| voice_agent_backend/app/core/database.py:23 | await conn.run_sync(Base.metadata.create_all) |
| voice_agent_backend/app/core/langchain_rag.py:9 | from app.services.qdrant_service import search_vectors |
| voice_agent_backend/app/core/langchain_rag.py:322 | search_vectors(collection, emb, fetch_k, score_threshold) |
| voice_agent_backend/app/services/qdrant_service.py:13 | async def _qdrant_get(path: str, timeout: float = 10.0) -> dict: |
| voice_agent_backend/app/services/qdrant_service.py:28 | async def _qdrant_post(path: str, payload: dict, timeout: float = 30.0) -> dict: |
| voice_agent_backend/app/services/qdrant_service.py:43 | async def _qdrant_put(path: str, payload: dict, timeout: float = 30.0) -> dict: |
| voice_agent_backend/app/services/qdrant_service.py:58 | async def _qdrant_delete(path: str, timeout: float = 10.0) -> dict: |
| voice_agent_backend/app/services/qdrant_service.py:78 | data = await _qdrant_get("/collections") |
| voice_agent_backend/app/services/qdrant_service.py:98 | return await _qdrant_put(f"/collections/{name}", payload) |
| voice_agent_backend/app/services/qdrant_service.py:104 | return await _qdrant_delete(f"/collections/{name}") |
| voice_agent_backend/app/services/qdrant_service.py:140 | data = await _qdrant_post( |
| voice_agent_backend/app/services/qdrant_service.py:141 | f"/collections/{collection}/points/scroll", payload |
| voice_agent_backend/app/services/qdrant_service.py:175 | return await _qdrant_post( |
| voice_agent_backend/app/services/qdrant_service.py:176 | f"/collections/{collection}/points/delete", payload |
| voice_agent_backend/app/services/qdrant_service.py:183 | async def upsert_points(collection: str, points: list[dict]) -> dict: |
| voice_agent_backend/app/services/qdrant_service.py:196 | return await _qdrant_put( |
| voice_agent_backend/app/services/qdrant_service.py:201 | async def search_vectors( |
| voice_agent_backend/app/services/qdrant_service.py:217 | data = await _qdrant_post( |

## Vector Store Analysis
Qdrant access is raw REST through shared `httpx`; default base URL is `voice_agent_backend/app/core/config.py:59`. Collection creation uses Cosine vectors sized by `get_embed_dim()` in `voice_agent_backend/app/core/config.py:36` and Qdrant service creation logic. Ingest extracts/chunks, creates a collection if missing, embeds with Ollama, and upserts UUID points. Payload fields include text, source, chunk_index, page, section, subsection, section_chunk_index, chunk_type, and has_table.

## Cache And Memory Analysis
Backend memory is process-local dict state guarded by a `threading.Lock` in `voice_agent_backend/app/core/memory.py:12`. Each session stores messages, last retrieval, active collection, language, and timestamps. LangGraph checkpointing uses in-memory `MemorySaver`. Client localStorage persists per-collection docs/conversation/retrieval/sessions/session id under `ssa_` keys.

## Data Integrity Risks
1. HIGH: Qdrant helpers swallow connection/HTTP errors and return empty results.
2. HIGH: Ingest does not verify Qdrant upsert response before returning success.
3. HIGH: Existing collection vector dimensions are not checked before ingest with a selected embed model.
4. MEDIUM: `safe_filename` is computed but raw upload filename remains in payload/source behavior.
5. MEDIUM: `/ingest` collection is raw Form input while only JSON body schemas enforce collection regex.
6. MEDIUM: Re-ingesting the same file creates duplicate UUID points; no manifest/checksum/idempotency exists.
7. MEDIUM: Document-existence cache is not invalidated after ingest/delete.
8. MEDIUM: Memory/session/checkpoint state is not durable or multi-worker safe.
9. MEDIUM: SQLite FK enforcement is not enabled by app code despite declared FK.
10. LOW: SQL auth tables exist, but auth routes are not mounted.

## Recommended Follow-Up
Make Qdrant write/search helpers raise typed failures, validate and encode collection names consistently, add a durable document manifest, enable SQLite FK PRAGMA if SQLite remains part of the app, and replace process-local state if restart continuity or multi-worker deployment matters.

## Data Layer Evidence Appendix

- `docs/intelligence/_generate_docs.py:163`: if re.search(r"class .*BaseModel|class .*Base\)|mapped_column\(|ForeignKey\(|Base\.metadata|create_all", line):

- `docs/intelligence/_generate_docs.py:169`: if re.search(r"select\(|db\.execute|commit\(|create_all|_qdrant_|search_vectors|upsert_points|scroll|points/delete", line):

- `voice_agent_backend/app/api/routes/auth.py:23`: result = await db.execute(select(User).where(User.email == user_data.email))

- `voice_agent_backend/app/api/routes/auth.py:33`: await db.commit()

- `voice_agent_backend/app/api/routes/auth.py:41`: result = await db.execute(select(User).where(User.email == form_data.username))

- `voice_agent_backend/app/api/routes/ingest.py:4`: from app.services.qdrant_service import create_collection, upsert_points

- `voice_agent_backend/app/api/routes/ingest.py:391`: await upsert_points(collection, points)

- `voice_agent_backend/app/core/auth.py:65`: result = await db.execute(select(User).where(User.email == email))

- `voice_agent_backend/app/core/database.py:23`: await conn.run_sync(Base.metadata.create_all)

- `voice_agent_backend/app/core/langchain_rag.py:9`: from app.services.qdrant_service import search_vectors

- `voice_agent_backend/app/core/langchain_rag.py:322`: search_vectors(collection, emb, fetch_k, score_threshold)

- `voice_agent_backend/app/services/qdrant_service.py:13`: async def _qdrant_get(path: str, timeout: float = 10.0) -> dict:

- `voice_agent_backend/app/services/qdrant_service.py:28`: async def _qdrant_post(path: str, payload: dict, timeout: float = 30.0) -> dict:

- `voice_agent_backend/app/services/qdrant_service.py:43`: async def _qdrant_put(path: str, payload: dict, timeout: float = 30.0) -> dict:

- `voice_agent_backend/app/services/qdrant_service.py:58`: async def _qdrant_delete(path: str, timeout: float = 10.0) -> dict:

- `voice_agent_backend/app/services/qdrant_service.py:78`: data = await _qdrant_get("/collections")

- `voice_agent_backend/app/services/qdrant_service.py:98`: return await _qdrant_put(f"/collections/{name}", payload)

- `voice_agent_backend/app/services/qdrant_service.py:104`: return await _qdrant_delete(f"/collections/{name}")

- `voice_agent_backend/app/services/qdrant_service.py:140`: data = await _qdrant_post(

- `voice_agent_backend/app/services/qdrant_service.py:141`: f"/collections/{collection}/points/scroll", payload

- `voice_agent_backend/app/services/qdrant_service.py:175`: return await _qdrant_post(

- `voice_agent_backend/app/services/qdrant_service.py:176`: f"/collections/{collection}/points/delete", payload

- `voice_agent_backend/app/services/qdrant_service.py:183`: async def upsert_points(collection: str, points: list[dict]) -> dict:

- `voice_agent_backend/app/services/qdrant_service.py:196`: return await _qdrant_put(

- `voice_agent_backend/app/services/qdrant_service.py:201`: async def search_vectors(

- `voice_agent_backend/app/services/qdrant_service.py:217`: data = await _qdrant_post(

- `docs/intelligence/_generate_docs.py:163`: if re.search(r"class .*BaseModel|class .*Base\)|mapped_column\(|ForeignKey\(|Base\.metadata|create_all", line):

- `docs/intelligence/_generate_docs.py:169`: if re.search(r"select\(|db\.execute|commit\(|create_all|_qdrant_|search_vectors|upsert_points|scroll|points/delete", line):

- `voice_agent_backend/app/api/routes/auth.py:12`: class UserRegister(BaseModel):

- `voice_agent_backend/app/api/routes/auth.py:16`: class Token(BaseModel):

- `voice_agent_backend/app/api/routes/tts.py:11`: class TTSRequest(BaseModel):

- `voice_agent_backend/app/core/database.py:14`: class Base(DeclarativeBase):

- `voice_agent_backend/app/core/database.py:23`: await conn.run_sync(Base.metadata.create_all)

- `voice_agent_backend/app/models/schemas.py:5`: class ChatRequest(BaseModel):

- `voice_agent_backend/app/models/schemas.py:16`: class STTResponse(BaseModel):

- `voice_agent_backend/app/models/schemas.py:21`: class CollectionCreateRequest(BaseModel):

- `voice_agent_backend/app/models/schemas.py:26`: class DocumentInfo(BaseModel):
