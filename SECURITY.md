# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| Latest | Yes |
| Older releases | No |

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Use GitHub private vulnerability reporting:

https://github.com/RossDmello2/voice-rag-agent/security/advisories/new

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Your suggested fix, if any

The maintainer will review the private advisory, confirm impact where possible, and coordinate a fix before public disclosure. Response timing depends on maintainer availability.

## Security Best Practices for Deployment

- Set a strong `SECRET_KEY` in `voice_agent_backend/.env`; do not use the fallback development value in production.
- Set `APP_ENV=production` for non-local deployments. The app rejects the development fallback secret outside local/dev/test modes.
- Keep `GROQ_API_KEY` and `TAVILY_API_KEY` out of source control.
- Do not commit `voice_agent_backend/.env`, local SQLite databases, or model artifacts.
- Serve the app behind HTTPS when exposed outside localhost.
- `/ingest`, `POST /collections`, collection deletion, and document deletion require JWT bearer tokens.
- Chat, health, model listing, and read-only collection/document listing are local-first public endpoints. Add broader auth before exposing cost-bearing public deployments.
- Assistant Markdown is sanitized client-side before rendering, but model output should still be treated as untrusted.
- Do not expose Qdrant, Ollama, or SQLite files directly to the public internet.
- Review CORS origins before deployment; the defaults are for local development.
