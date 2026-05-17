# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| Latest | Yes |
| Older releases | No |

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Email **rossdmello869@gmail.com** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Your suggested fix, if any

You will receive a response within 48 hours acknowledging receipt.

We will work with you to confirm the issue, develop a fix, release a patched version, and credit your discovery unless you prefer to remain anonymous.

## Security Best Practices for Deployment

- Set a strong `SECRET_KEY` in `voice_agent_backend/.env`; do not use the fallback development value in production.
- Keep `GROQ_API_KEY` and `TAVILY_API_KEY` out of source control.
- Do not commit `voice_agent_backend/.env`, local SQLite databases, or model artifacts.
- Serve the app behind HTTPS when exposed outside localhost.
- Protect authenticated routes with bearer tokens and rotate tokens after suspected compromise.
- Do not expose Qdrant, Ollama, or SQLite files directly to the public internet.
- Review CORS origins before deployment; the defaults are for local development.
