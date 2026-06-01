# Productionization Gap Analysis

**Date:** 2026-05-17

> Status: Historical gap snapshot. Several gaps below have since been addressed, including auth mounting, protected mutating routes, backend tests, CodeQL, CI permissions, deployment docs, and `AGENTS.md`. For current truth, use `docs/operations/PRODUCTIONIZATION_SUMMARY.md`, `docs/operations/VERIFICATION_MATRIX.md`, and `docs/operations/CONTRIBUTION_READINESS_AUDIT.md`.

## Runtime Gaps

- `/auth/register` and `/auth/login` exist but are not mounted in `app.main`.
- Mutating routes for ingestion and collection/document deletion do not require authentication.
- Qdrant helper failures can be converted into empty results, and ingest does not validate upsert success.
- `safe_filename` is computed but the raw upload filename is still stored and returned.
- SQLite location is hardcoded instead of configurable through `.env.example`.

## Product Usability Gaps

- The frontend has CSS for auth, but no auth modal markup or working token flow.
- Existing frontend 401 branches reference missing functions (`AUTH`, `isAuthError`, `showAuthModal`, `setAuthError`).
- Read-only local-first flows should remain usable, but write/delete flows need a sign-in path.

## Security Gaps

- The JWT secret has a fallback value that should not be accepted outside local mode.
- Assistant Markdown is parsed into `innerHTML` without a sanitizer.
- GitHub CI lacks explicit top-level `permissions: contents: read`.
- No CodeQL workflow exists yet.
- `.env` exists locally and must remain ignored and never printed.

## Test Gaps

- Existing tests are frontend-only and mock backend APIs.
- No backend tests cover mounted auth, JWT validation, protected mutations, ingest failure handling, or config validation.
- Frontend tests do not cover auth modal behavior, authorized write calls, or XSS sanitization.

## Documentation Gaps

- Phase 0 productionization docs are missing for v2.
- README claims some auth-protected endpoints before live auth is mounted.
- `docs/intelligence/` is historical and intentionally stale after restructure; current operation docs must record the updated truth.
- `AGENTS.md` is missing.

## Deployment Gaps

- Docker docs exist only minimally through `voice_agent_backend/Dockerfile`.
- No `docs/deployment.md` exists for Qdrant/Ollama/Groq/Kokoro setup boundaries.
- CI does not run backend tests because none exist yet.

## External Blockers To Document If Still Present

- Full provider smoke depends on local Qdrant/Ollama and a valid Groq key.
- CodeRabbit depends on git plus CodeRabbit CLI/auth.
- `pip-audit` and `gitleaks` depend on local tool availability.
