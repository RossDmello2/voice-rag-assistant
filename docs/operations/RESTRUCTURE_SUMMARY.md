# Project Restructure Summary

**Date:** 2026-05-16  
**Operation:** GitHub Open-Source Standards Restructure

## Changes Made

### Files Moved

| From | To |
|---|---|
| `kokoro-v1.0.onnx` | `voice_agent_backend/data/models/kokoro-v1.0.onnx` |
| `voices-v1.0.bin` | `voice_agent_backend/data/models/voices-v1.0.bin` |
| `voice_agent_backend/voice_agent.db` | `voice_agent_backend/data/sqlite/voice_agent.db` |
| `voice_agent_backend/context.md` | `docs/architecture/context.md` |
| `voice_agent_backend/file_str.md` | `docs/architecture/file_str.md` |
| `voice_agent_backend/HANDOFF_README.md` | `docs/guides/HANDOFF_README.md` |
| `voice_agent_backend/sop(voice_agent).md` | `docs/guides/sop(voice_agent).md` |
| `voice_agent_backend/plan.md` | `docs/specs/langchain_langgraph_migration_plan.md` |
| `voice_agent_backend/tests/test_frontend.py` | `voice_agent_backend/tests/frontend/test_frontend.py` |
| `voice_agent_backend/test_graph.py` | `voice_agent_backend/scripts/manual_tests/graph_smoke.py` plus root wrapper |
| `voice_agent_backend/scratch/benchmark_tts.py` | `voice_agent_backend/scripts/manual_tests/benchmark_tts.py` |
| `voice_agent_backend/scratch/inspect_kokoro.py` | `voice_agent_backend/scripts/manual_tests/inspect_kokoro.py` |
| `voice_agent_backend/scratch/sim_scoring.py` | `voice_agent_backend/scripts/manual_tests/sim_scoring.py` |
| `voice_agent_backend/scratch/test_chunking.py` | `voice_agent_backend/scripts/manual_tests/chunking_smoke.py` |
| `voice_agent_backend/scratch/test_hardware.py` | `voice_agent_backend/scripts/manual_tests/hardware_smoke.py` |
| `voice_agent_backend/scratch/test_normalization.py` | `voice_agent_backend/scripts/manual_tests/tts_normalization_smoke.py` |
| `voice_agent_backend/scratch/test_pipeline.py` | `voice_agent_backend/scripts/manual_tests/pipeline_smoke.py` |
| `voice_agent_backend/scratch/test_rag.py` | `voice_agent_backend/scripts/manual_tests/rag_smoke.py` |
| `voice_agent_backend/scratch/test_speech_norm.py` | `voice_agent_backend/scripts/manual_tests/speech_norm_smoke.py` |
| `voice_agent_backend/scripts/check_backend_health.py` | `voice_agent_backend/scripts/checks/check_backend_health.py` |
| `voice_agent_backend/scripts/verify_kokoro.py` | `voice_agent_backend/scripts/checks/verify_kokoro.py` |
| `voice_agent_backend/scripts/test_imports.py` | `voice_agent_backend/scripts/checks/import_smoke.py` |
| `voice_agent_backend/scripts/test_search_node.py` | `voice_agent_backend/scripts/checks/search_node_smoke.py` |

### Files Created

- `README.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `CHANGELOG.md`
- `SECURITY.md`
- `.gitignore`
- `.env.example`
- `requirements-dev.txt`
- `.github/workflows/ci.yml`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/dependabot.yml`
- `voice_agent_backend/pytest.ini`
- `voice_agent_backend/data/README.md`
- `voice_agent_backend/tests/frontend/__init__.py`
- `voice_agent_backend/test_graph.py`
- `docs/operations/RESTRUCTURE_SUMMARY.md`

### Files Removed

- No deprecated components were removed.
- Original files were removed only after copy and byte-length verification confirmed their destination copies.

### Import and Path Updates

- `voice_agent_backend/app/core/config.py`: Kokoro defaults now point to `data/models/kokoro-v1.0.onnx` and `data/models/voices-v1.0.bin`.
- `voice_agent_backend/app/core/database.py`: SQLite now resolves to `voice_agent_backend/data/sqlite/voice_agent.db`.
- `voice_agent_backend/app/services/speech_service.py`: Kokoro fallback paths now use `data/models/`.
- `voice_agent_backend/scripts/checks/*.py`: backend root path setup updated for the new `scripts/checks/` directory.
- `voice_agent_backend/scripts/manual_tests/*.py`: backend root and Kokoro artifact paths updated for the new `scripts/manual_tests/` directory.
- `voice_agent_backend/tests/frontend/test_frontend.py`: frontend fixture path updated after moving under `tests/frontend/`.
- `voice_agent_backend/start_server.bat` and `voice_agent_backend/start_server.sh`: missing-env guidance now points to root `.env.example`.
- `voice_agent_backend/.env`: only `KOKORO_MODEL_PATH` and `KOKORO_VOICES_PATH` were updated without reading or printing file contents.
- Live docs under `docs/architecture/` and `docs/guides/` were updated for the new data and test/script paths.

### GitHub Standard Files Added

- README, license, contribution guide, code of conduct, changelog, security policy
- GitHub Actions CI workflow
- Bug and feature issue templates
- Pull request template
- Dependabot configuration

## Verification Results

- JavaScript syntax check: PASS (`node --check voice_agent_backend/frontend/script.js`)
- Python syntax check: PASS (`python -m py_compile` over all non-venv Python files)
- Frontend test suite: PASS (`22 passed`)
- Pytest collection: PASS (`tests/frontend/test_frontend.py: 22`)
- App import smoke: PASS (`from app.main import app` returned `Voice Agent API`)
- Internal import smoke: PASS (`ALL 20 IMPORTS PASSED`)
- GitHub standard files: PASS
- Placeholder token scan: PASS
- Moved artifact preservation: PASS for Kokoro model, voices artifact, SQLite DB, docs, tests, and scripts
- Application live startup: NOT RUN as a bound server in this environment; external Qdrant, Ollama, Groq, and TTS warm-up services were not started.

## Known Remaining Items

- This folder is not currently a git repository, so `git status`, GitHub remote metadata lookup, and CodeRabbit review could not be run.
- `voice_agent_backend/.env` exists locally and was not read or printed. It is ignored by `.gitignore`.
- `python voice_agent_backend/test_graph.py` remains a manual diagnostic and reports the pre-existing issue: `get_voice_graph` is not exported from `app.core.voice_graph`.
- `docs/intelligence/` is preserved as historical read-only discovery evidence. It intentionally still contains pre-restructure path references from the original audit snapshot.
