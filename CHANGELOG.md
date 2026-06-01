# Changelog

All notable changes to VoiceRAG Agent are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Added
- GitHub-ready repository metadata, documentation, issue templates, CI workflow, and dependency update configuration.
- Root `.env.example` covering the environment variables used by the FastAPI backend.
- Clear local data directories for Kokoro model artifacts and SQLite runtime state.
- Strict productionization operation docs, file ledger, product-shape decision, gap analysis, and research notes.
- Backend tests for mounted auth, protected mutating routes, ingest filename sanitization, Qdrant write failure handling, and config validation.
- Frontend tests for auth modal behavior, token persistence, authorized write calls, and Markdown sanitization.
- CodeQL workflow and backend import smoke in CI.
- Project-specific `AGENTS.md` and deployment documentation.
- Current architecture guide, feature catalog, and contribution-readiness audit for open-source contributors.
- VoiceRAG Agent public identity, GitHub publishing checklist, documentation index, discoverability plan, and repository asset guidance.

### Changed
- Moved architecture, guide, and migration planning documents into root `docs/`.
- Moved frontend tests under `voice_agent_backend/tests/frontend/`.
- Moved developer checks and manual smoke scripts under `voice_agent_backend/scripts/`.
- Updated Kokoro and SQLite default paths to `voice_agent_backend/data/`.
- Mounted auth routes and protected document/collection write operations with JWT bearer auth.
- Sanitized assistant Markdown rendering before assigning HTML to the DOM.
- Made ingest use sanitized filenames and fail when Qdrant does not acknowledge vector writes.
- Added `APP_ENV` and optional `DATABASE_URL` runtime configuration.
- Updated contributor and pull request guidance to require backend/frontend verification and feature ownership review.
- Updated public repository links and naming from `voice-agent` to `voice-rag-agent`.

## [1.0.0] - 2026-05-16

### Added
- FastAPI backend serving a vanilla JavaScript voice-agent interface.
- JWT registration/login with local SQLite persistence.
- Qdrant-backed document ingestion and retrieval.
- Groq and Ollama provider integration for chat, embeddings, translation, and STT.
- LangGraph voice pipeline with retrieval, response generation, interruption, and Kokoro TTS support.
