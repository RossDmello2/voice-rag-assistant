# Verification Matrix

**Date:** 2026-06-01
**Project:** VoiceRAG Agent

| Gate | Command/Evidence | Result | Notes |
| --- | --- | --- | --- |
| Branch created | `git branch --show-current` | PASS | Working branch for this docs/metadata pass: `codex/github-identity-seo`. |
| GitHub repository created | `gh repo view RossDmello2/voice-rag-agent --json nameWithOwner,visibility,description,url` | PASS | Repository is public and `origin` points to `https://github.com/RossDmello2/voice-rag-agent.git`. |
| GitHub topics configured | `gh repo view RossDmello2/voice-rag-agent --json repositoryTopics` | PASS | All 20 planned topics are configured. |
| Branch protection | `gh api repos/RossDmello2/voice-rag-agent/branches/main/protection` | PASS | `main` requires `lint`, `test (3.11)`, `Analyze (python)`, and `Analyze (javascript-typescript)`; force pushes and deletions are disabled. |
| GitHub security automation | `gh api .../vulnerability-alerts`; `gh api .../automated-security-fixes` | PASS | Dependabot vulnerability alerts and automated security fixes are enabled or already enabled. |
| Remote CI | `gh run list --repo RossDmello2/voice-rag-agent --branch main` | PASS | Latest `CI` run for the current `main` commit completed successfully. |
| Remote CodeQL | `gh run list --repo RossDmello2/voice-rag-agent --branch main` | PASS | Latest `CodeQL` run for the current `main` commit completed successfully. |
| Code scanning alerts | `gh api 'repos/RossDmello2/voice-rag-agent/code-scanning/alerts?state=open&per_page=100' --jq 'length'` | PASS | GitHub reports `0` open code-scanning alerts after the 2026-06-01 CodeQL fix and rescan. |
| Private vulnerability reporting | `gh api repos/RossDmello2/voice-rag-agent/private-vulnerability-reporting` | PASS | Enabled for private security reports through GitHub Security Advisories. |
| Issue forms | PyYAML parse of `.github/ISSUE_TEMPLATE/*.yml` | PASS | `bug_report.yml`, `feature_request.yml`, and `config.yml` parse successfully. |
| Local artifact ignore | `git check-ignore voice_agent_backend/.env voice_agent_backend/data/models/kokoro-v1.0.onnx voice_agent_backend/data/sqlite/voice_agent.db` | PASS | `.env`, Kokoro ONNX, and SQLite DB are ignored. |
| No tracked secrets/artifacts | `git ls-files \| rg "(^|/)\\.env$|\\.onnx$|\\.bin$|voice_agent_backend/data/sqlite/.*\\.(db|sqlite|sqlite3)$"` | PASS | No tracked `.env`, model binary, or runtime DB artifacts. |
| Public path/contact scan | `rg` over README, `.github`, and docs for personal contact/local path markers | PASS | No remaining personal email, mail contact links, machine-local path links, or cloud-drive workspace references in public docs/templates. |
| JavaScript syntax | `node --check voice_agent_backend/frontend/script.js` | PASS | Exit 0. |
| Python compile | `cd voice_agent_backend; python -m compileall app scripts tests` | PASS | Exit 0. |
| Automated tests | `cd voice_agent_backend; python -m pytest tests/backend tests/frontend -q` | PASS | 33 passed. |
| Pytest collection | `cd voice_agent_backend; python -m pytest --collect-only -q` | PASS | 7 backend tests and 26 frontend tests collected. |
| Import smoke | `cd voice_agent_backend; python scripts/checks/import_smoke.py` | PASS | `ALL 20 IMPORTS PASSED`. |
| App import | `cd voice_agent_backend; python -c "from app.main import app; print(app.title)"` | PASS | Printed `Voice Agent API`. |
| Dependency audit | `cd voice_agent_backend; python -m pip_audit -r requirements.txt` | PASS | No known vulnerabilities found. |
| Markdown local links | Inline Python local Markdown link checker | PASS | All local Markdown links resolve inside the repository. |
| Browser smoke | Temporary Uvicorn on `http://127.0.0.1:8023` plus Playwright DOM/auth check | PASS | Page title was `VoiceRAG Agent | Local Voice-to-Voice RAG Assistant`; auth modal opened; no page errors. |
| Screenshot and visual assets | Playwright screenshots, social preview source image, and conceptual workflow visual | PASS | Existing real screenshots remain under `docs/assets/screenshots/`; `docs/assets/social-preview.png` is the deterministic GitHub preview source; `docs/assets/brand/workflow-visual.png` is generated conceptual artwork and is labeled as non-screenshot context. |
| Git diff whitespace | `git diff --check` | PASS | Exit 0; Git only emitted Windows CRLF conversion warnings. |

## Known External Limits

- GitHub social preview upload is available in repository settings, but `gh repo edit` does not expose a supported image-upload flag. The source image is committed at `docs/assets/social-preview.png` and the upload step is documented in `docs/guides/GITHUB_PUBLISHING_CHECKLIST.md`.
- Full provider smoke depends on local Qdrant, Ollama, Kokoro artifacts, and valid Groq credentials.
- GitHub Actions currently reports upcoming Node.js 20 action-runtime deprecation warnings for upstream actions; CI and CodeQL still pass.
- FastAPI `on_event` and SQLAlchemy `datetime.utcnow()` deprecation warnings remain pre-existing follow-up items.
