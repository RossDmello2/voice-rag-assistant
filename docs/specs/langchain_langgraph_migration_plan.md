# Voice Agent — LangChain/LangGraph Migration & Security Hardening Plan

## Document Purpose

This is the implementation blueprint for evolving the Voice Agent backend from custom HTTP client code to LangChain/LangGraph, while simultaneously hardening it into a production-secure web application. No changes are made to the current codebase until each phase is explicitly started and verified.

---

## Table of Contents

1. [Current State Audit](#1-current-state-audit)
2. [Security Audit — Current Vulnerabilities](#2-security-audit--current-vulnerabilities)
3. [Migration Principles & Non-Negotiables](#3-migration-principles--non-negotiables)
4. [Phase 0: Security Hardening (Pre-Migration)](#4-phase-0-security-hardening-pre-migration)
5. [Phase 1: Replace Document Loaders](#5-phase-1-replace-document-loaders)
6. [Phase 2: Replace Embeddings Interface](#6-phase-2-replace-embeddings-interface)
7. [Phase 3: Replace Vector Store](#7-phase-3-replace-vector-store)
8. [Phase 4: Replace Chat LLM Interface](#8-phase-4-replace-chat-llm-interface)
9. [Phase 5: Integrate Custom Reranker into LangChain Retrieval](#9-phase-5-integrate-custom-reranker-into-langchain-retrieval)
10. [Phase 6: LangGraph Agent Orchestrator](#10-phase-6-langgraph-agent-orchestrator)
11. [Phase 7: Observability, Evaluation & Memory](#11-phase-7-observability-evaluation--memory)
12. [Phase 8: Advanced Security & Compliance](#12-phase-8-advanced-security--compliance)
13. [Risk Registry](#13-risk-registry)
14. [Dependency Map](#14-dependency-map)
15. [Verification Checklist Per Phase](#15-verification-checklist-per-phase)

---

## 1. Current State Audit

### Files and Their Current Roles

| File | Lines | Current Role | LangChain Equivalent | Migration Priority |
|------|-------|-------------|---------------------|-------------------|
| `app/services/ollama_service.py` | 54 | Raw httpx calls to Ollama `/api/embed` | `langchain_ollama.OllamaEmbeddings` | Phase 2 |
| `app/services/qdrant_service.py` | 215 | Raw httpx REST calls to Qdrant API | `langchain_qdrant.QdrantVectorStore` | Phase 3 |
| `app/services/groq_service.py` | 128 | Raw httpx calls to Groq chat + Whisper | `langchain_groq.ChatGroq` | Phase 4 |
| `app/core/langchain_rag.py` | 281 | Custom RAG: query variants, embed, search, rerank, format | `langchain` retriever + custom reranker | Phase 5 |
| `app/core/intent.py` | 238 | Two-tier intent classification (regex + LLM) | LangGraph router node | Phase 6 |
| `app/core/memory.py` | 74 | In-memory dict with threading.Lock | LangGraph checkpointing + persistent store | Phase 7 |
| `app/core/translation.py` | 53 | Groq LLM for translate to/from English | `langchain_groq.ChatGroq` chain | Phase 4 |
| `app/core/config.py` | 78 | Pydantic settings, system prompts, embed dims | Keep + extend | No change |
| `app/models/schemas.py` | 33 | Pydantic request/response models | Keep + extend for security | Phase 0 |
| `app/api/routes/chat.py` | 168 | SSE orchestration: translate → intent → RAG → stream | LangGraph graph invocation | Phase 6 |
| `app/api/routes/ingest.py` | 382 | Document extraction, chunking, embedding, upsert | LangChain loaders + text splitters | Phase 1 |
| `app/api/routes/stt.py` | 27 | Groq Whisper proxy | Keep (no LangChain equivalent) | No change |
| `app/api/routes/collections.py` | 65 | Qdrant collection CRUD via REST | `langchain_qdrant` management | Phase 3 |
| `app/api/routes/health.py` | 34 | Service health pings | Keep | No change |
| `app/main.py` | 25 | FastAPI app + static mount | Keep + add security middleware | Phase 0 |

### What Works Well (Do Not Break)

1. **Custom hybrid reranker** (`langchain_rag.py:66-114`) — Domain-optimized with number bonus, proper noun bonus, section bonus, table bonus. This produces measurably better results for document Q&A than generic rerankers. **Preserve until Phase 5 where it integrates as a LangChain `BaseDocumentCompressor`.**

2. **Section-aware chunking** (`ingest.py:101-190`) — Heading detection, table detection, section/subsection tracking, semantic overlap. No LangChain text splitter replicates this exactly. **Preserve as a custom `TextSplitter` subclass in Phase 1.**

3. **Two-tier intent classification** (`intent.py`) — Regex fast path (0ms, 0 cost) catches 80%+ of intents. LLM fallback only fires when ambiguous. **Preserve the regex tier; wrap the LLM tier in LangChain in Phase 4.**

4. **SSE streaming contract** — Frontend `script.js` expects exact `data: {"token":"..."}\n\n` format. **All phases must maintain this SSE contract.**

5. **Frontend** — `script.js`, `index.html`, `style.css` are not touched in any phase.

---

## 2. Security Audit — Current Vulnerabilities

### Critical

| ID | Vulnerability | Location | Risk | Phase Fix |
|----|--------------|----------|------|-----------|
| S-01 | **No authentication** — anyone with network access can use all endpoints | `main.py` | Data exfiltration, unauthorized document access, API key abuse | Phase 0 |
| S-02 | **No rate limiting** — unlimited requests to Groq/Ollama/Qdrant | All routes | API cost abuse, DoS | Phase 0 |
| S-03 | **No file upload validation** — only extension check, no content-type verification, no malware scan, no size limit enforced server-side | `ingest.py:352-381` | Malicious file upload, server compromise | Phase 0 |
| S-04 | **API key in .env with no rotation** — single static Groq key, no vault | `.env`, `config.py` | Key leakage via logs/errors/git | Phase 0+8 |
| S-05 | **No input length limit** — message field unbounded | `ChatRequest.message` | Token cost abuse, context window overflow | Phase 0 |
| S-06 | **Session IDs client-generated** — no server validation, can impersonate sessions | `script.js:70` | Session hijacking, data access | Phase 0 |

### High

| ID | Vulnerability | Location | Risk | Phase Fix |
|----|--------------|----------|------|-----------|
| S-07 | **No HTTPS enforcement** — HTTP by default | `main.py` | MITM, credential sniffing | Phase 0 |
| S-08 | **No CORS restriction** — `allow_origins=["*"]` | `main.py` | Cross-origin attacks | Phase 0 |
| S-09 | **In-memory session store** — lost on restart, no persistence | `memory.py` | Data loss, no audit trail | Phase 7 |
| S-10 | **No request logging** — no audit trail for who accessed what | All routes | Forensic blindness | Phase 0 |
| S-11 | **Prompt injection detection is trivial** — only substring matching | `intent.py:87-99` | Bypass with encoding/obfuscation | Phase 8 |
| S-12 | **No output filtering** — LLM responses not scanned for PII/leaks | `chat.py:136-143` | Data leakage through LLM | Phase 8 |

### Medium

| ID | Vulnerability | Location | Risk | Phase Fix |
|----|--------------|----------|------|-----------|
| S-13 | **No security headers** — no CSP, HSTS, X-Frame-Options | `main.py` | Clickjacking, XSS vectors | Phase 0 |
| S-14 | **Error messages expose internals** — stack traces in HTTP 500 | `ingest.py:381`, `chat.py:140` | Information disclosure | Phase 0 |
| S-15 | **No document access control** — any session can query any collection | `chat.py`, `collections.py` | Cross-tenant data access | Phase 8 |
| S-16 | **Qdrant has no auth** — direct REST access open | `qdrant_service.py` | Unauthorized vector DB access | Phase 8 |
| S-17 | **No content-type validation on upload** — trust client extension | `ingest.py:266-274` | Content-type spoofing | Phase 0 |

---

## 3. Migration Principles & Non-Negotiables

### Non-Negotiable Rules

1. **Every phase must leave the application fully functional.** No broken states between phases.
2. **The SSE streaming contract is sacred.** `data: {"token":"..."}\n\n` → `data: [DONE]\n\n` must work identically.
3. **The frontend never changes.** All migration is backend-only.
4. **The custom reranker is preserved until Phase 5.** Then it becomes a `BaseDocumentCompressor`, not replaced.
5. **The section-aware chunker is preserved.** It becomes a custom `TextSplitter` subclass.
6. **The regex intent tier is preserved.** It remains the fast path; only the LLM tier gets LangChain'd.
7. **Every new dependency must be pinned in `requirements.txt`.**
8. **Security hardening in Phase 0 happens before any LangChain migration.**
9. **Each phase has a verification gate.** Do not proceed until all checks pass.
10. **No `pip install langchain` blanket.** Install only needed subpackages: `langchain-core`, `langchain-ollama`, `langchain-qdrant`, `langchain-groq`, `langgraph`.

### Migration Strategy: Strangler Fig Pattern

Each custom service file is replaced by a LangChain adapter that exposes the same function signatures. The route files import from the adapter layer, not the LangChain classes directly. This allows:

- Swapping implementations without touching route logic
- Falling back to the old implementation if a phase fails
- Testing both implementations side-by-side

```
Current:  route.py → custom_service.py → httpx → external API
Target:   route.py → adapter_layer.py → langchain_component → external API
```

---

## 4. Phase 0: Security Hardening (Pre-Migration)

**Goal**: Make the application safe to expose on the internet before adding LangChain complexity.

### 0A. Input Validation & Request Limits

**File**: `app/models/schemas.py`

Add constraints to all Pydantic models:

```python
# ChatRequest — add field constraints
session_id: str = Field(..., min_length=1, max_length=128, pattern=r'^[a-zA-Z0-9_-]+$')
message: str = Field(..., min_length=1, max_length=4000)
collection: str = Field(..., min_length=1, max_length=128, pattern=r'^[a-zA-Z0-9_-]+$')
language: str = Field(..., min_length=2, max_length=3, pattern=r'^[a-z]{2,3}$')

# CollectionCreateRequest
name: str = Field(..., min_length=1, max_length=128, pattern=r'^[a-zA-Z0-9_-]+$')

# IngestRequest — add file size limit (handled at route level)
```

**File**: `app/api/routes/ingest.py`

Add server-side file validation:

```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/csv',
}
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.csv'}

# In ingest_endpoint():
# 1. Check file size before reading full content
# 2. Validate content-type header matches extension
# 3. Validate magic bytes (PDF starts with %PDF-, DOCX is a ZIP with specific structure)
# 4. Sanitize filename (remove path traversal attempts)
```

### 0B. Authentication & Session Management

**New file**: `app/core/auth.py`

Implement JWT-based authentication:

```python
# Dependencies: python-jose[cryptography], passlib[bcrypt]

# What to implement:
# - POST /auth/register — create user account (email + password, bcrypt hash)
# - POST /auth/login — validate credentials, return JWT access + refresh tokens
# - POST /auth/refresh — rotate refresh token, issue new access token
# - get_current_user() dependency — validate JWT from Authorization header
# - Session IDs now server-generated, tied to authenticated user
# - All existing routes get `current_user: User = Depends(get_current_user)` dependency
```

**New file**: `app/api/routes/auth.py`

```python
# Register auth routes in main.py
# Users can only access their own sessions and collections
# Collection names prefixed with user_id: f"{user_id}_{collection_name}"
```

**Database**: Add SQLite (or PostgreSQL) for user accounts:

```python
# New file: app/core/database.py
# SQLAlchemy async session
# Tables: users, sessions, api_keys (encrypted)
# Users table: id, email, password_hash, created_at, is_active
# Sessions table: id, user_id, session_token, created_at, expires_at
```

### 0C. Rate Limiting

**New file**: `app/middleware/rate_limit.py`

```python
# Dependencies: slowapi or custom Redis-backed limiter

# Rate limits:
# - POST /chat: 20 requests/minute per user
# - POST /ingest: 5 requests/minute per user
# - POST /stt: 30 requests/minute per user
# - GET /health: 60 requests/minute per user
# - All other: 60 requests/minute per user

# Implementation:
# - Use slowapi with in-memory storage (upgrade to Redis in Phase 8)
# - Attach to FastAPI app with @limiter.limit() decorator per route
# - Return 429 Too Many Requests with Retry-After header
```

### 0D. Security Headers & CORS

**File**: `app/main.py`

```python
# Add security middleware:
# - Strict-Transport-Security: max-age=31536000; includeSubDomains
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
# - Content-Security-Policy: default-src 'self'; script-src 'self' cdnjs.cloudflare.com cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'
# - X-XSS-Protection: 1; mode=block
# - Referrer-Policy: strict-origin-when-cross-origin

# Restrict CORS:
# - Remove allow_origins=["*"]
# - Add ALLOWED_ORIGINS to .env (comma-separated list of frontend domains)
# - For same-origin deployment: allow_origins=["http://localhost:8000"]
```

### 0E. Request Logging & Error Sanitization

**New file**: `app/middleware/logging.py`

```python
# Structured request logging:
# - Log: timestamp, method, path, status_code, latency_ms, user_id, session_id
# - Do NOT log: request bodies (may contain PII), API keys, passwords
# - Use Python logging with JSON formatter for production

# Error sanitization:
# - Never return raw exception messages to client
# - Log full traceback server-side, return generic message to client
# - Add custom exception handler in main.py
```

### 0F. Session ID Server-Side Generation

**File**: `app/api/routes/chat.py`

```python
# Change: session_id is no longer accepted from client in ChatRequest
# Instead: session_id comes from the authenticated user's session
# Client still sends session_id for per-collection state, but it's validated:
#   - Must match a session owned by the authenticated user
#   - Generated server-side with secrets.token_urlsafe()
#   - Frontend gets session_id from /auth/login or /sessions/create response
```

### Phase 0 Verification Gate

- [ ] All Pydantic models enforce field constraints
- [ ] File uploads validate content-type, magic bytes, size limit
- [ ] JWT authentication works on all routes
- [ ] Rate limiting returns 429 when exceeded
- [ ] Security headers present on all responses
- [ ] CORS restricted to configured origins
- [ ] Request logging captures method/path/status/latency
- [ ] Error responses never include stack traces
- [ ] Session IDs are server-generated
- [ ] Application still starts and all endpoints work with valid auth

---

## 5. Phase 1: Replace Document Loaders

**Goal**: Replace custom `extract_text_from_pdf/docx/txt` functions with LangChain document loaders while preserving section-aware chunking.

### Current Implementation

`app/api/routes/ingest.py` lines 193-250: Three functions that extract raw text from files using `pypdf` and `python-docx`, returning `[{pageNum, lines, text}]`.

### Target Implementation

**New file**: `app/core/document_loaders.py`

```python
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.documents import Document
from typing import BinaryIO

class VoiceAgentDocumentLoader:
    """
    Wraps LangChain loaders to produce the same output format
    as the current extract_text_from_* functions.

    Key differences from current:
    - PyPDFLoader provides page-level metadata natively
    - Docx2txtLoader handles DOCX properly
    - Both return LangChain Document objects with page_content + metadata

    Output format preserved: [{pageNum, lines, text}]
    so that chunk_structured_lines() continues to work unchanged.
    """

    @staticmethod
    async def load_pdf(file_bytes: bytes) -> list[dict]:
        """Replace extract_text_from_pdf()."""
        # Write bytes to temp file (PyPDFLoader needs a file path)
        # Load with PyPDFLoader
        # Convert Document objects to {pageNum, lines, text} format
        # Return same structure as current

    @staticmethod
    async def load_docx(file_bytes: bytes) -> list[dict]:
        """Replace extract_text_from_docx()."""
        # Same pattern as load_pdf

    @staticmethod
    async def load_txt(file_bytes: bytes) -> list[dict]:
        """Replace extract_text_from_txt()."""
        # Use TextLoader or simple decode (already simple)
```

### Section-Aware Chunker as LangChain TextSplitter

**New file**: `app/core/text_splitters.py`

```python
from langchain_core.text_splitters import TextSplitter
from langchain_core.documents import Document

class SectionAwareTextSplitter(TextSplitter):
    """
    Custom TextSplitter that preserves the exact chunking logic from
    ingest.py: is_heading_line(), is_table_line(), chunk_structured_lines().

    This is NOT replaced by RecursiveCharacterTextSplitter because:
    - The heading detection (uppercase ratio, numbered patterns) is domain-specific
    - The table detection (tab count, multi-space gaps) preserves table data integrity
    - Section/subsection metadata must be tracked in chunk payload
    - Semantic overlap uses sentence-boundary-aware tail extraction

    Implementation:
    - Move is_heading_line(), is_table_line(), chunk_text_simple(), chunk_structured_lines()
      from ingest.py into this class
    - The create_documents() method produces Document objects with metadata:
      {page, section, subsection, chunk_type, section_chunk_index, source}
    - The split_text() method is not used (we override create_documents directly)
    """

    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200, **kwargs):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs)
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def create_documents(
        self, texts: list[str], metadatas: list[dict] | None = None
    ) -> list[Document]:
        # For each text (one page), run chunk_structured_lines()
        # Return Document(page_content=chunk_text, metadata={page, section, subsection, ...})
        # Add section context prefix and semantic overlap (ingest.py lines 295-307)
        pass
```

### Changes to `ingest.py`

```python
# Replace:
#   from app.core.document_loaders import VoiceAgentDocumentLoader (NEW)
#   from app.core.text_splitters import SectionAwareTextSplitter (NEW)
#   Remove: extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
#   Remove: is_heading_line, is_table_line, chunk_text_simple, chunk_structured_lines
#   Keep: ingest_document() and ingest_endpoint() (modified to use new imports)

# In ingest_document():
#   1. Use VoiceAgentDocumentLoader.load_pdf/docx/txt instead of extract_*
#   2. Use SectionAwareTextSplitter.create_documents() instead of chunk_structured_lines()
#   3. Embedding + upsert logic unchanged (still uses ollama_service + qdrant_service)
```

### New Dependencies

```
langchain-community>=0.3.0
langchain-core>=0.3.0
```

### Phase 1 Verification Gate

- [ ] `pip install langchain-community langchain-core` succeeds
- [ ] PDF extraction produces same page count and text as before
- [ ] DOCX extraction produces same text as before
- [ ] TXT/CSV extraction unchanged
- [ ] Section-aware chunking produces identical chunk metadata (section, subsection, chunk_type, page)
- [ ] Ingest endpoint still returns `{filename, chunks_created, collection, status}`
- [ ] Frontend document upload + delete still works
- [ ] Custom heading detection and table detection still function

---

## 6. Phase 2: Replace Embeddings Interface

**Goal**: Replace `ollama_service.generate_embedding()` with `langchain_ollama.OllamaEmbeddings`.

### Current Implementation

`app/services/ollama_service.py`: Single function `generate_embedding(text, model) -> list[float]` that calls `POST {OLLAMA_BASE}/api/embed` via httpx.

### Target Implementation

**New file**: `app/services/embedding_adapter.py`

```python
from langchain_ollama import OllamaEmbeddings
from app.core.config import settings

class EmbeddingAdapter:
    """
    Wraps LangChain OllamaEmbeddings to expose the same interface
    as ollama_service.generate_embedding().

    This adapter allows:
    - Swapping embedding models without changing callers
    - Using LangChain's built-in batching and retry logic
    - Future: swapping to OpenAI embeddings or other providers
    """

    def __init__(self):
        self._embeddings = OllamaEmbeddings(
            model=settings.EMBED_MODEL,
            base_url=settings.OLLAMA_BASE,
        )

    async def embed_query(self, text: str) -> list[float]:
        """Single text embedding — replaces generate_embedding()."""
        return await self._embeddings.aembed_query(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Batch embedding — more efficient for ingestion."""
        return await self._embeddings.aembed_documents(texts)

# Singleton
embedding_adapter = EmbeddingAdapter()
```

### Changes Required

- `app/core/langchain_rag.py`: Replace `from app.services.ollama_service import generate_embedding` with `from app.services.embedding_adapter import embedding_adapter`; change `await generate_embedding(v, model)` to `await embedding_adapter.embed_query(v)`
- `app/api/routes/ingest.py`: Same replacement; also consider using `embed_documents()` for batch embedding of all chunks (significant performance improvement for large documents)
- `app/services/ollama_service.py`: Keep file but mark functions as deprecated; remove after Phase 2 verification passes

### Batch Embedding Optimization (Ingest)

Current: embed each chunk sequentially (slow for large documents).

```python
# Current (ingest.py lines 320-341):
for idx, chunk in enumerate(all_chunks):
    embedding = await generate_embedding(chunk['text'], settings.EMBED_MODEL)

# Target:
texts = [chunk['text'] for chunk in all_chunks]
embeddings = await embedding_adapter.embed_documents(texts)  # Batch!
points = [
    {"id": str(uuid.uuid4()), "vector": emb, "payload": {...}}
    for emb, chunk in zip(embeddings, all_chunks)
]
```

### New Dependencies

```
langchain-ollama>=0.2.0
```

### Phase 2 Verification Gate

- [ ] `pip install langchain-ollama` succeeds
- [ ] `embedding_adapter.embed_query("test")` returns same-dimension vector as old `generate_embedding()`
- [ ] `embedding_adapter.embed_documents(["a", "b"])` returns list of same vectors
- [ ] RAG retrieval with new embeddings produces same quality results (manual test with known query)
- [ ] Document ingestion with batch embedding works
- [ ] `ollama_service.py` functions still available as fallback
- [ ] All frontend features still work (chat, upload, collections)

---

## 7. Phase 3: Replace Vector Store

**Goal**: Replace `qdrant_service.py` raw REST calls with `langchain_qdrant.QdrantVectorStore`.

### Current Implementation

`app/services/qdrant_service.py`: 215 lines of raw httpx REST calls for collection CRUD, point upsert, vector search, document listing, and deletion.

### Target Implementation

**New file**: `app/services/vectorstore_adapter.py`

```python
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from app.core.config import settings
from app.services.embedding_adapter import embedding_adapter

class VectorStoreAdapter:
    """
    Wraps LangChain QdrantVectorStore to provide the same interface
    as qdrant_service.py functions.

    Key considerations:
    - QdrantVectorStore handles embedding automatically when using
      add_documents() / similarity_search()
    - But our custom reranker needs raw score + payload access,
      which requires using similarity_search_with_score()
    - Collection management still needs qdrant_client directly
      (LangChain doesn't expose all Qdrant admin operations)
    """

    def __init__(self):
        self._client = QdrantClient(url=settings.QDRANT_BASE)
        self._embeddings = embedding_adapter._embeddings

    def get_store(self, collection_name: str) -> QdrantVectorStore:
        """Get a QdrantVectorStore instance for a collection."""
        return QdrantVectorStore(
            client=self._client,
            collection_name=collection_name,
            embedding=self._embeddings,
        )

    async def list_collections(self) -> list[str]:
        """Replace qdrant_service.list_collections()."""
        return [c.name for c in self._client.get_collections().collections]

    async def create_collection(self, name: str, vector_size: int) -> dict:
        """Replace qdrant_service.create_collection()."""
        # Use qdrant_client directly for collection creation
        # QdrantVectorStore.from_documents() can auto-create, but we need control
        pass

    async def upsert_documents(
        self, collection: str, documents: list, ids: list[str] | None = None
    ) -> dict:
        """Replace qdrant_service.upsert_points() — now takes Document objects."""
        store = self.get_store(collection)
        store.add_documents(documents=documents, ids=ids)
        pass

    async def search(
        self, collection: str, query: str, limit: int = 8, score_threshold: float = 0.30
    ) -> list[dict]:
        """
        Replace qdrant_service.search_vectors().
        Returns format compatible with our custom reranker:
        [{id, score, payload}]
        """
        store = self.get_store(collection)
        results = store.similarity_search_with_score(query, k=limit, score_threshold=score_threshold)
        # Convert (Document, score) tuples to {id, score, payload} dicts
        pass

    async def delete_collection(self, name: str) -> dict: ...
    async def list_documents(self, collection: str) -> list[dict]: ...
    async def delete_document_vectors(self, collection: str, filename: str) -> dict: ...
    async def health_check(self) -> bool: ...

# Singleton
vectorstore_adapter = VectorStoreAdapter()
```

### Important: RAG Pipeline Search Still Uses Raw Vectors

The current `langchain_rag.py` does multi-variant search:

```python
# Current: embed each variant, search with raw vectors, merge results
embeddings = await asyncio.gather(*[generate_embedding(v, model) for v in variants])
all_results = await asyncio.gather(*[search_vectors(collection, emb, k, threshold) for emb in embeddings])
```

With `QdrantVectorStore`, we can use `similarity_search_with_score()` which handles embedding internally. But our multi-variant approach requires searching with pre-computed embeddings from different variant texts. We have two options:

**Option A (Recommended)**: Use `QdrantVectorStore.similarity_search_with_score()` per variant (lets LangChain handle embedding each variant). Simpler but slightly more API calls.

**Option B**: Use `qdrant_client` directly for the raw vector search in the retrieval pipeline, while using `QdrantVectorStore` for everything else (ingestion, collection management). Preserves exact current behavior.

Choose Option A for LangChain consistency. The extra embedding calls are negligible since Ollama is local.

### New Dependencies

```
langchain-qdrant>=0.2.0
qdrant-client>=1.9.0
```

### Phase 3 Verification Gate

- [ ] `pip install langchain-qdrant qdrant-client` succeeds
- [ ] Collection CRUD (create, list, delete) works via adapter
- [ ] Document upsert via `add_documents()` works with section metadata
- [ ] `similarity_search_with_score()` returns results with scores and payloads
- [ ] Document listing (scroll points) still works
- [ ] Document deletion by source filename still works
- [ ] All frontend features still work (chat, upload, collections, clear knowledge)
- [ ] Old `qdrant_service.py` functions still available as fallback

---

## 8. Phase 4: Replace Chat LLM Interface

**Goal**: Replace `groq_service.chat_complete()` with `langchain_groq.ChatGroq`, and `groq_service.transcribe_audio()` stays as-is (no LangChain equivalent).

### Current Implementation

`app/services/groq_service.py`:
- `chat_complete()` — Dual-mode function: returns async generator (stream) or coroutine (non-stream)
- `transcribe_audio()` — httpx multipart upload to Groq Whisper
- `health_check()` — GET /models

### Target Implementation

**New file**: `app/services/llm_adapter.py`

```python
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import AsyncCallbackHandler
from app.core.config import settings
from typing import AsyncGenerator

class StreamingCallbackHandler(AsyncCallbackHandler):
    """
    Custom callback that captures streaming tokens.
    This is how LangChain streaming integrates with our SSE format.

    The callback's on_llm_new_token() method is called for each token.
    We store tokens in a queue that the SSE generator reads from.
    """
    async def on_llm_new_token(self, token: str, **kwargs):
        # Push token to async queue for SSE consumption
        pass


class LLMAdapter:
    """
    Wraps LangChain ChatGroq to provide the same interface as
    groq_service.chat_complete().

    Critical: The SSE streaming contract must be preserved.
    LangChain streams via callbacks, not async generators.
    We bridge this with StreamingCallbackHandler.
    """

    def __init__(self):
        self._chat = ChatGroq(
            model=settings.CHAT_MODEL,
            temperature=0.7,
            max_tokens=1024,
            groq_api_key=settings.GROQ_API_KEY,
        )
        self._translation_chat = ChatGroq(
            model=settings.TRANSLATION_MODEL,
            temperature=0,
            max_tokens=512,
            groq_api_key=settings.GROQ_API_KEY,
        )
        self._intent_chat = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=20,
            groq_api_key=settings.GROQ_API_KEY,
        )

    async def stream_chat(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        """
        Replace chat_complete(messages, stream=True).
        Yields tokens one at a time via LangChain streaming.
        """
        lc_messages = self._convert_messages(messages)
        async for chunk in self._chat.astream(lc_messages):
            if chunk.content:
                yield chunk.content

    async def complete_chat(self, messages: list[dict], **kwargs) -> str:
        """Replace chat_complete(messages, stream=False)."""
        lc_messages = self._convert_messages(messages)
        # Apply overrides (temperature, max_tokens) for intent/translation
        chat = self._get_chat_for_purpose(**kwargs)
        response = await chat.ainvoke(lc_messages)
        return response.content

    async def translate(self, text: str, direction: str, language: str) -> str:
        """Replace translation.py functions."""
        if direction == "to_english":
            prompt = f"Translate the following {language} text to English. Return ONLY the English translation, no explanation:\n{text}"
        else:
            prompt = f"Translate the following English text to {language}. Return ONLY the translation, no explanation, no markdown:\n{text}"
        messages = [HumanMessage(content=prompt)]
        response = await self._translation_chat.ainvoke(messages)
        return response.content.strip()

    async def classify_intent(self, text: str) -> str:
        """Replace intent.py classify_intent_llm()."""
        prompt = INTENT_PROMPT.replace('{MESSAGE}', text)
        messages = [HumanMessage(content=prompt)]
        response = await self._intent_chat.ainvoke(messages)
        raw = response.content.strip().upper()
        for intent in VALID_INTENTS:
            if intent in raw:
                return intent
        return 'GENERAL_CHAT'

    def _convert_messages(self, messages: list[dict]) -> list:
        """Convert [{role, content}] to LangChain message objects."""
        result = []
        for m in messages:
            if m['role'] == 'system':
                result.append(SystemMessage(content=m['content']))
            elif m['role'] == 'user':
                result.append(HumanMessage(content=m['content']))
            elif m['role'] == 'assistant':
                result.append(AIMessage(content=m['content']))
        return result

# Singleton
llm_adapter = LLMAdapter()
```

### Changes Required

- `app/api/routes/chat.py`: Replace `from app.services.groq_service import chat_complete` with `from app.services.llm_adapter import llm_adapter`; change `async for token in chat_complete(messages, model, stream=True)` to `async for token in llm_adapter.stream_chat(messages)`
- `app/core/intent.py`: Replace `classify_intent_llm()` to use `llm_adapter.classify_intent()`
- `app/core/translation.py`: Replace both functions to use `llm_adapter.translate()`
- `app/api/routes/stt.py`: Keep `groq_service.transcribe_audio()` — no LangChain equivalent
- `app/api/routes/health.py`: Keep `groq_service.health_check()` for now (or add to adapter)

### New Dependencies

```
langchain-groq>=0.2.0
```

### Phase 4 Verification Gate

- [ ] `pip install langchain-groq` succeeds
- [ ] `llm_adapter.stream_chat()` produces tokens in same format as `chat_complete(stream=True)`
- [ ] `llm_adapter.complete_chat()` returns same quality responses as `chat_complete(stream=False)`
- [ ] Translation produces same results
- [ ] Intent classification LLM tier produces same results
- [ ] SSE streaming from `/chat` still works end-to-end in browser
- [ ] STT still works (unchanged)
- [ ] Health check still works

---

## 9. Phase 5: Integrate Custom Reranker into LangChain Retrieval

**Goal**: Build a LangChain retriever that uses our custom hybrid reranker as a `BaseDocumentCompressor`, preserving the domain-optimized scoring logic.

### Current Implementation

`app/core/langchain_rag.py` — 281 lines of custom RAG pipeline:
1. `build_query_variants()` — generates multiple search queries
2. `retrieve_context()` — embed variants, search Qdrant, merge, rerank, confidence check
3. `rerank_results()` — hybrid BM25+vector scoring (THE CROWN JEWEL)
4. `diversify_for_summary()` — source/section diversity for summary queries
5. `has_sufficient_confidence()` — confidence floor check
6. `format_context()` — format results for prompt injection
7. `build_contextual_prompt()` — construct prompt with context

### Target Implementation

**New file**: `app/core/retriever.py`

```python
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetriever
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from app.services.vectorstore_adapter import vectorstore_adapter
from app.services.embedding_adapter import embedding_adapter
from app.core.config import settings

class HybridReranker(BaseDocumentCompressor):
    """
    LangChain BaseDocumentCompressor that wraps our custom rerank_results().

    This is NOT replaced — it is INTEGRATED into LangChain's retrieval pipeline.
    The scoring formula is preserved exactly:
      combined = vector_score * 0.55
               + keyword_score * 0.25
               + number_bonus (max 0.30)
               + noun_bonus (max 0.20)
               + section_bonus (max 0.15)
               + table_bonus (0.10)

    The reranker operates on LangChain Document objects instead of raw dicts.
    Document.metadata carries: source, page, section, subsection, chunk_type, has_table
    Document.page_content carries: chunk text

    compress_documents() is the LangChain entry point.
    """

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Callbacks = None,
        **kwargs,
    ) -> Sequence[Document]:
        # Convert Document → {payload, score} format
        # Run rerank_results() logic
        # Convert back to Document list (sorted by combined_score)
        pass


class MultiQueryRetriever(BaseRetriever):
    """
    Custom retriever that implements multi-variant search + reranking.

    Replaces retrieve_context() from langchain_rag.py.

    Flow:
    1. Build query variants (same logic as build_query_variants())
    2. Search Qdrant for each variant via vectorstore_adapter
    3. Merge results (deduplicate by source + chunk_index)
    4. Rerank via HybridReranker
    5. Apply confidence floor (same as has_sufficient_confidence())
    6. Apply diversity for summary queries (same as diversify_for_summary())
    7. Return formatted context (same as format_context())
    """

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun, **kwargs
    ) -> list[Document]:
        # flags, last_retrieval passed via kwargs
        # Full pipeline: variants → search → merge → rerank → confidence → diversity
        pass
```

### What Changes vs What Stays

| Function | Action | Reason |
|----------|--------|--------|
| `build_query_variants()` | **Keep as-is** | Pure string manipulation, no LangChain benefit |
| `retrieve_context()` | **Replace** with `MultiQueryRetriever._get_relevant_documents()` | LangChain retriever interface |
| `rerank_results()` | **Preserve as `HybridReranker.compress_documents()`** | Domain-optimized scoring, just format conversion |
| `diversify_for_summary()` | **Keep as-is** | Pure list filtering, no LangChain benefit |
| `has_sufficient_confidence()` | **Keep as-is** | Simple threshold check |
| `format_context()` | **Keep as-is** | String formatting for prompt |
| `build_contextual_prompt()` | **Keep as-is** | Prompt template construction |
| `tokenize()` | **Keep as-is** | Used by reranker and query variants |

### Changes to `chat.py`

```python
# Replace:
#   from app.core.langchain_rag import retrieve_context, build_contextual_prompt, has_sufficient_confidence
# With:
#   from app.core.retriever import MultiQueryRetriever
#   from app.core.langchain_rag import build_contextual_prompt, has_sufficient_confidence, format_context

# In the generate() function:
#   retriever = MultiQueryRetriever(collection=req.collection, ...)
#   documents = retriever.invoke(english_message, config={"flags": flags, "last_retrieval": ...})
#   context = format_from_documents(documents)  # Convert Document list to context dict
```

### Phase 5 Verification Gate

- [ ] `HybridReranker.compress_documents()` produces same ranking as `rerank_results()`
- [ ] Number bonus, noun bonus, section bonus, table bonus all preserved
- [ ] Multi-variant search merges results correctly (dedup by source+chunk_index)
- [ ] Confidence floor still triggers "I don't know" responses
- [ ] Summary diversity still works
- [ ] Document Q&A produces same quality results as before
- [ ] Follow-up queries still carry last_retrieval context
- [ ] SSE streaming still works end-to-end

---

## 10. Phase 6: LangGraph Agent Orchestrator

**Goal**: Replace the monolithic `chat.py` generate() function with a LangGraph state machine that models the conversation flow as a graph.

### Current Flow (Procedural in chat.py)

```
translate → injection_check → check_documents → classify_intent →
  if STOP → return
  if UPLOAD → return
  if DOCUMENT_QUERY → retrieve → confidence_check → build_prompt
  if IDENTITY_QUERY → build_identity_prompt
  if GENERAL_CHAT → use_base_prompt
→ stream_llm → strip_citations → translate_back → send_sources → done
```

### Target Flow (LangGraph State Machine)

**New file**: `app/core/graph.py`

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage

class ConversationState(TypedDict):
    """State that flows through the graph."""
    session_id: str
    user_message: str           # Original user message (possibly non-English)
    english_message: str        # Translated to English (if needed)
    language: str                # Source language code
    collection: str              # Qdrant collection name
    intent: str                  # Classified intent
    intent_flags: dict           # isSummary, isFollowUp
    has_documents: bool          # Whether collection has documents
    context: dict | None         # RAG retrieval result
    system_prompt: str           # Selected system prompt
    context_prompt: str          # User message with context
    sources: list[str]           # Source filenames
    full_response: str           # Complete LLM response
    clean_response: str          # After citation stripping
    display_response: str        # After back-translation
    last_retrieval: dict         # For follow-up context
    is_blocked: bool             # Prompt injection detected
    is_short_circuit: bool       # STOP/UPLOAD/NO_INFO shortcut

# Define graph nodes:
def translate_input(state: ConversationState) -> ConversationState: ...
def check_injection(state: ConversationState) -> ConversationState: ...
def check_documents(state: ConversationState) -> ConversationState: ...
def classify_intent_node(state: ConversationState) -> ConversationState: ...
def handle_stop(state: ConversationState) -> ConversationState: ...
def handle_upload(state: ConversationState) -> ConversationState: ...
def retrieve_context(state: ConversationState) -> ConversationState: ...
def check_confidence(state: ConversationState) -> ConversationState: ...
def build_prompt(state: ConversationState) -> ConversationState: ...
def stream_llm(state: ConversationState) -> ConversationState: ...
def post_process(state: ConversationState) -> ConversationState: ...

# Build the graph
graph = StateGraph(ConversationState)

# Add nodes
graph.add_node("translate_input", translate_input)
graph.add_node("check_injection", check_injection)
graph.add_node("check_documents", check_documents)
graph.add_node("classify_intent", classify_intent_node)
graph.add_node("retrieve_context", retrieve_context)
graph.add_node("build_prompt", build_prompt)
graph.add_node("stream_llm", stream_llm)
graph.add_node("post_process", post_process)

# Add edges (conditional routing)
graph.set_entry_point("translate_input")
graph.add_edge("translate_input", "check_injection")
graph.add_conditional_edges("check_injection", lambda s: END if s["is_blocked"] else "check_documents")
graph.add_edge("check_documents", "classify_intent")
graph.add_conditional_edges("classify_intent", route_by_intent)
graph.add_edge("retrieve_context", "build_prompt")
graph.add_edge("build_prompt", "stream_llm")
graph.add_edge("stream_llm", "post_process")
graph.add_edge("post_process", END)

# Compile
app_graph = graph.compile()
```

### SSE Streaming Challenge with LangGraph

LangGraph graphs execute synchronously (or async) but our SSE generator needs to yield tokens as they arrive. Solution:

```python
# In chat.py:
@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # Run the graph up to the LLM streaming step
    # The graph prepares everything (translate, intent, retrieval, prompt)
    # Then we take over with our SSE generator for the streaming part

    # Option A: Run graph with interrupt before stream_llm, then stream manually
    # Option B: Use graph.stream() with custom event handling

    # Recommended: Option A
    # 1. Run graph.invoke() up to build_prompt node
    # 2. Extract prepared state (messages, system prompt)
    # 3. Use llm_adapter.stream_chat() in our SSE generator
    # 4. Run post-processing after streaming completes

    # This preserves the SSE contract while getting LangGraph's
    # routing, observability, and state management benefits.
```

### Future Enhancement: Agent Capabilities

With LangGraph in place, adding agent behavior becomes trivial:

```python
# Future: Tool-using agent
from langgraph.prebuilt import create_react_agent

tools = [
    search_documents_tool,
    list_collections_tool,
    get_document_summary_tool,
    translate_tool,
]

# Agent decides when to search, when to ask follow-up, when to summarize
agent = create_react_agent(llm, tools, checkpointer=checkpointer)
```

### New Dependencies

```
langgraph>=0.2.0
```

### Phase 6 Verification Gate

- [ ] `pip install langgraph` succeeds
- [ ] Graph compiles and all nodes execute
- [ ] Intent routing works (STOP, UPLOAD, DOCUMENT_QUERY, GENERAL_CHAT, IDENTITY_QUERY)
- [ ] SSE streaming preserved with same token-by-token format
- [ ] Sources sent after stream completes
- [ ] Prompt injection still blocks
- [ ] Translation still works for non-English
- [ ] All frontend features still work

---

## 11. Phase 7: Observability, Evaluation & Memory

### 7A. LangSmith Observability

**Goal**: Trace every LLM call, retrieval, and tool use through LangSmith.

```python
# In .env:
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_sk_...
LANGCHAIN_PROJECT=voicerag-agent-prod

# In config.py:
LANGCHAIN_TRACING_V2: bool = False
LANGCHAIN_API_KEY: str = ""
LANGCHAIN_PROJECT: str = "voicerag-agent"

# All LangChain components automatically trace when these are set.
# No code changes needed beyond adding env vars.
# Traces will show:
# - Full prompt sent to LLM
# - Token counts and latency
# - Retrieval queries and scores
# - Intent classification result
# - End-to-end latency per conversation turn
```

### 7B. Persistent Memory

**Goal**: Replace `memory.py`'s in-memory dict with LangGraph checkpointing + database.

**Current**: `SessionMemory` stores everything in a Python dict. Lost on restart. No cross-session persistence. Thread-safe with Lock but not process-safe.

**Target**:

```python
# Replace with LangGraph's SqliteSaver or PostgresSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
# or for production:
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# In graph.py:
checkpointer = AsyncSqliteSaver.from_conn_string("checkpoints.db")
# or
checkpointer = AsyncPostgresSaver.from_conn_string(DATABASE_URL)

app_graph = graph.compile(checkpointer=checkpointer)

# Conversation history now persists across:
# - Server restarts
# - Multiple worker processes
# - Can be queried for analytics

# Also add conversation store for listing/resuming sessions:
# New table: conversations
#   - user_id, session_id, title, created_at, updated_at, message_count
#   - Enables /sessions endpoint to list past conversations
```

### 7C. RAG Evaluation Pipeline

**New file**: `app/eval/rag_eval.py`

```python
from langchain.evaluation import QAEvalChain
from langsmith import Client

# Define evaluation datasets:
# - Set of (question, expected_answer, collection) tuples
# - Automatically run retrieval + generation
# - Score on: faithfulness, relevance, completeness

# Key metrics:
# 1. Retrieval recall: Did the right chunks get retrieved?
# 2. Answer faithfulness: Is the answer grounded in retrieved context?
# 3. Answer correctness: Does it match expected answer?
# 4. Latency: End-to-end response time
# 5. Token usage: Input + output tokens per turn

# Run as: python -m app.eval.rag_eval --dataset qa_test_set.json
```

### New Dependencies

```
langsmith>=0.1.0
langgraph-checkpoint-sqlite>=0.1.0
# For production:
# langgraph-checkpoint-postgres>=0.1.0
```

### Phase 7 Verification Gate

- [ ] LangSmith traces appear in dashboard for every chat turn
- [ ] Checkpoints persist to SQLite/Postgres
- [ ] Server restart does not lose conversation history
- [ ] Evaluation pipeline runs and produces scores
- [ ] Frontend still works identically

---

## 12. Phase 8: Advanced Security & Compliance

### 8A. PII Detection & Redaction

**New file**: `app/core/pii_guard.py`

```python
# Before sending user input to LLM: scan for PII
# After receiving LLM response: scan for PII leakage

# PII types to detect:
# - Email addresses
# - Phone numbers
# - Social security numbers
# - Credit card numbers
# - IP addresses
# - Names (using NER model)

# Options:
# A. Regex-based (fast, low accuracy): presidio-anonymizer
# B. NER-based (slower, high accuracy): GLiNER or presidio with spaCy
# C. LLM-based (slowest, most accurate): Ask LLM to check for PII

# Recommended: Option A + B combined
# - Fast regex pre-scan catches obvious patterns
# - NER scan for names and addresses
# - Redact before sending to LLM
# - Log PII detection events (without the PII itself)
```

### 8B. Advanced Prompt Injection Defense

**Current**: Substring matching against 16 patterns.

**Target**: Multi-layer defense:

```python
# Layer 1: Current regex patterns (keep, fast)
# Layer 2: LLM-as-judge (ask a small model if input is injection)
# Layer 3: Input/output embedding similarity check
#   - If output embedding is very similar to system prompt embedding,
#     the user may have extracted the prompt

# New file: app/core/injection_guard.py
class InjectionGuard:
    async def check(self, text: str) -> tuple[bool, str]:
        """
        Returns (is_safe, reason).
        Runs all three layers; any trigger blocks the request.
        """
        # Layer 1: Regex (0ms)
        if detect_prompt_injection(text):
            return False, "regex_pattern_match"

        # Layer 2: LLM judge (~200ms, only if Layer 1 passes)
        judge_result = await self._llm_judge(text)
        if not judge_result.is_safe:
            return False, "llm_judge_rejection"

        # Layer 3: Output monitoring (post-generation)
        # Checked after response, logged if suspicious
        return True, ""
```

### 8C. Document Access Control

```python
# Collections are namespaced by user_id
# Collection name format: "{user_id}__{collection_name}"
# User can only access their own collections
# Admin can access all collections

# In every route that takes collection_name:
# 1. Verify collection belongs to current user
# 2. Strip user_id prefix before Qdrant operations
# 3. Re-add prefix after Qdrant operations
# 4. Never expose user_id prefix to frontend
```

### 8D. API Key Vault

```python
# Replace .env-based API keys with encrypted storage
# New table: api_keys (id, user_id, provider, encrypted_key, key_hint, created_at)
# Encryption: Fernet symmetric encryption with server master key
# Master key: stored in hardware security module or environment variable

# Users can add their own API keys via settings panel
# System falls back to default key if user hasn't provided one
# Keys are never logged, never returned to client
```

### 8E. Audit Logging

```python
# Log every significant action to database:
# - User login/logout
# - Document upload (filename, size, collection)
# - Chat message (redacted content, intent, token count)
# - Document deletion
# - Collection creation/deletion
# - API key changes
# - Failed auth attempts
# - PII detection events
# - Prompt injection blocks

# New table: audit_logs
#   (timestamp, user_id, action, resource_type, resource_id, metadata_json)
```

### Phase 8 Verification Gate

- [ ] PII is detected and redacted in user inputs
- [ ] LLM responses are scanned for PII leakage
- [ ] Prompt injection defense catches encoded/obfuscated attacks
- [ ] Users can only access their own collections
- [ ] API keys are stored encrypted, never in logs
- [ ] Audit log captures all significant actions
- [ ] All frontend features still work

---

## 13. Risk Registry

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| LangChain breaking changes between phases | Medium | High | Pin all dependency versions in requirements.txt |
| SSE streaming breaks during LLM adapter swap | High | Critical | Test streaming in browser after every change; keep fallback |
| Custom reranker produces different results after conversion | Medium | High | Write comparison tests before starting Phase 5 |
| Section-aware chunking produces different chunks | Medium | High | Write golden test: given same PDF, output identical chunks |
| LangGraph streaming incompatible with SSE format | Medium | Critical | Use interrupt pattern: graph prepares, manual SSE streams |
| Phase 0 auth breaks existing frontend flow | High | Critical | Frontend needs login UI; add auth routes before requiring auth |
| Ollama API format differs from LangChain expectations | Low | Medium | Test embedding dimensions match after Phase 2 |
| Qdrant payload format changes with LangChain adapter | Medium | High | Verify metadata round-trip: ingest → search → payload intact |
| Performance regression from LangChain abstraction overhead | Low | Medium | Benchmark each phase; keep custom fallback if >20% slower |
| Memory store migration loses conversation history | Medium | Medium | Export existing sessions before migrating; import into new store |

---

## 14. Dependency Map

### Phase 0 (Security — no LangChain deps)
```
python-jose[cryptography]   # JWT auth
passlib[bcrypt]             # Password hashing
slowapi                     # Rate limiting
sqlalchemy[asyncio]         # User database
aiosqlite                   # Async SQLite driver
```

### Phase 1 (Document Loaders)
```
langchain-core>=0.3.0
langchain-community>=0.3.0
```

### Phase 2 (Embeddings)
```
langchain-ollama>=0.2.0
```

### Phase 3 (Vector Store)
```
langchain-qdrant>=0.2.0
qdrant-client>=1.9.0
```

### Phase 4 (Chat LLM)
```
langchain-groq>=0.2.0
```

### Phase 5 (Retriever — no new deps)
```
# Uses langchain-core BaseRetriever + BaseDocumentCompressor
```

### Phase 6 (LangGraph)
```
langgraph>=0.2.0
```

### Phase 7 (Observability)
```
langsmith>=0.1.0
langgraph-checkpoint-sqlite>=0.1.0
```

### Phase 8 (Security)
```
presidio-anonymizer         # PII detection
presidio-analyzer           # PII analysis
cryptography                # API key encryption
```

### Final requirements.txt (all phases)
```
# Existing
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
httpx>=0.25.0
python-multipart>=0.0.6
pypdf>=3.17.0
python-docx>=1.0.0

# Phase 0: Security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
slowapi>=0.1.9
sqlalchemy[asyncio]>=2.0.0
aiosqlite>=0.19.0

# Phases 1-4: LangChain
langchain-core>=0.3.0
langchain-community>=0.3.0
langchain-ollama>=0.2.0
langchain-qdrant>=0.2.0
langchain-groq>=0.2.0
qdrant-client>=1.9.0

# Phase 6: LangGraph
langgraph>=0.2.0

# Phase 7: Observability
langsmith>=0.1.0
langgraph-checkpoint-sqlite>=0.1.0

# Phase 8: Security
presidio-anonymizer>=2.2.0
presidio-analyzer>=2.2.0
```

---

## 15. Verification Checklist Per Phase

Every phase must pass ALL checks before proceeding to the next.

### Universal Checks (Apply to Every Phase)

- [ ] `pip install -r requirements.txt` succeeds with no conflicts
- [ ] `python -m uvicorn app.main:app --port 8000` starts without errors
- [ ] `GET /health` returns 200 with service statuses
- [ ] `POST /chat` with valid ChatRequest returns SSE stream with tokens + [DONE]
- [ ] `POST /ingest` with a PDF returns `{filename, chunks_created, status: "success"}`
- [ ] `GET /collections` returns list of collections
- [ ] Frontend at `http://localhost:8000` loads, shows orb, can type messages
- [ ] Voice input (browser STT) captures speech and submits
- [ ] TTS speaks the agent's response
- [ ] Document upload shows in document list
- [ ] Collection switching works
- [ ] New chat clears conversation
- [ ] Settings persist across page reload

### Phase-Specific Critical Checks

**Phase 0**: JWT login required; rate limit triggers 429; security headers present; file upload rejects oversized/wrong-type files; no stack traces in error responses

**Phase 1**: PDF upload produces same chunk count as before; section metadata preserved; heading/table detection unchanged

**Phase 2**: Embedding dimensions match old output; RAG retrieval quality same; batch embedding faster than sequential

**Phase 3**: Search results have same scores and payloads; document listing works; collection CRUD works

**Phase 4**: SSE streaming token-by-token; translation quality same; intent classification same; latency not worse

**Phase 5**: Reranker produces same ranking order; confidence thresholds same; summary diversity same; document Q&A quality same or better

**Phase 6**: All intent paths work (STOP, UPLOAD, DOC_QUERY, GENERAL_CHAT); SSE preserved; graph compiles without errors

**Phase 7**: LangSmith traces visible; conversations survive server restart; eval pipeline produces scores

**Phase 8**: PII detected in test inputs; injection defense catches obfuscated attacks; cross-user collection access denied; audit log populated

---

## Execution Order Summary

```
Phase 0 ── Security Hardening (MUST BE FIRST)
  │
  ├─ 0A: Input validation
  ├─ 0B: JWT authentication
  ├─ 0C: Rate limiting
  ├─ 0D: Security headers + CORS
  ├─ 0E: Request logging + error sanitization
  └─ 0F: Server-side session IDs

Phase 1 ── Document Loaders (lowest risk, highest maintenance reduction)
  │
  ├─ LangChain PyPDFLoader, Docx2txtLoader
  └─ SectionAwareTextSplitter (custom TextSplitter subclass)

Phase 2 ── Embeddings Interface
  │
  ├─ OllamaEmbeddings adapter
  └─ Batch embedding optimization

Phase 3 ── Vector Store
  │
  ├─ QdrantVectorStore adapter
  └─ Collection/document management via qdrant_client

Phase 4 ── Chat LLM Interface
  │
  ├─ ChatGroq adapter with streaming
  ├─ Translation via ChatGroq
  └─ Intent LLM tier via ChatGroq

Phase 5 ── Custom Reranker Integration (HIGHEST CARE)
  │
  ├─ HybridReranker as BaseDocumentCompressor
  ├─ MultiQueryRetriever wrapping full pipeline
  └─ Preserve ALL scoring logic exactly

Phase 6 ── LangGraph Agent
  │
  ├─ ConversationState graph
  ├─ Conditional routing by intent
  └─ SSE streaming bridge

Phase 7 ── Observability & Memory
  │
  ├─ LangSmith tracing
  ├─ Persistent checkpointing
  └─ RAG evaluation pipeline

Phase 8 ── Advanced Security
  │
  ├─ PII detection/redaction
  ├─ Multi-layer injection defense
  ├─ Document access control
  ├─ API key vault
  └─ Audit logging
```

Each phase depends on the previous. Do not skip. Do not parallelize. Verify each gate before proceeding.
