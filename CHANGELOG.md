# Changelog

All notable changes to voice-agent are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Added
- GitHub-ready repository metadata, documentation, issue templates, CI workflow, and dependency update configuration.
- Root `.env.example` covering the environment variables used by the FastAPI backend.
- Clear local data directories for Kokoro model artifacts and SQLite runtime state.

### Changed
- Moved architecture, guide, and migration planning documents into root `docs/`.
- Moved frontend tests under `voice_agent_backend/tests/frontend/`.
- Moved developer checks and manual smoke scripts under `voice_agent_backend/scripts/`.
- Updated Kokoro and SQLite default paths to `voice_agent_backend/data/`.

## [1.0.0] - 2026-05-16

### Added
- FastAPI backend serving a vanilla JavaScript voice-agent interface.
- JWT registration/login with local SQLite persistence.
- Qdrant-backed document ingestion and retrieval.
- Groq and Ollama provider integration for chat, embeddings, translation, and STT.
- LangGraph voice pipeline with retrieval, response generation, interruption, and Kokoro TTS support.
