# Contributing to voice-agent

Thank you for your interest in contributing.

## How to Report a Bug

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include what you expected, what happened, exact steps to reproduce, and your environment.

## How to Request a Feature

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md). Describe the problem you are solving, not only the requested implementation.

## How to Submit Code

1. Fork the repository and create a branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Make your changes following the code style below.
3. Write or update tests that cover your change.
4. Run the verification suite:
   ```bash
   node --check voice_agent_backend/frontend/script.js
   cd voice_agent_backend
   python -m pytest tests/frontend -q
   python -m pytest --collect-only -q
   ```
5. Commit using Conventional Commits.
6. Open a pull request against `main` using the PR template.

## Code Style

- Python code uses 4-space indentation, `snake_case` functions and variables, and `PascalCase` Pydantic/SQLAlchemy classes.
- The backend uses async FastAPI route handlers and service functions where network I/O is involved.
- Pydantic models live in `voice_agent_backend/app/models/`.
- Runtime configuration belongs in `voice_agent_backend/app/core/config.py` and environment variables, not hardcoded inside routes.
- Keep manual smoke scripts in `voice_agent_backend/scripts/manual_tests/`; pytest-discovered tests belong in `voice_agent_backend/tests/`.
- There is no formatter configuration in the current tree. Keep changes local and consistent with surrounding files.

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `test:` | Test addition or fix |
| `refactor:` | Code change, no behavior change |
| `chore:` | Maintenance, dependencies, CI, tooling |
| `perf:` | Performance improvement |

## Development Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python -m playwright install chromium
cp .env.example voice_agent_backend/.env
```

Start dependencies:

```bash
docker run -p 6333:6333 qdrant/qdrant
ollama pull mxbai-embed-large
```

Run the app:

```bash
cd voice_agent_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Run a single test file:

```bash
cd voice_agent_backend
python -m pytest tests/frontend/test_frontend.py -q
```

## Questions

Open an issue tagged `question`, or email rossdmello869@gmail.com.
