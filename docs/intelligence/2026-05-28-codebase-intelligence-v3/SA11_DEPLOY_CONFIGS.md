# SA-11: Deployment Config Generation Report

Generated: 2026-05-28 11:20:25 +0530
Project root: <repo-root>
Runtime app root: voice_agent_backend/
Output directory: <repo-root>/docs/intelligence/2026-05-28-codebase-intelligence-v3
Artifact budget: exhaustive
Target platforms: vercel, render, railway
Deployment mode: detect
Secret policy: voice_agent_backend/.env was not read; only path, size, and ignore status were recorded.


## Generated Files
| File | Status | Notes |
| --- | --- | --- |
| .env.example.complete | GENERATED_REVIEW_COPY | Generated under deploy-configs only; review before copying |
| Dockerfile.production | GENERATED_REVIEW_COPY | Generated under deploy-configs only; review before copying |
| render.yaml | GENERATED_REVIEW_COPY | Generated under deploy-configs only; review before copying |
| railway.toml | GENERATED_REVIEW_COPY | Generated under deploy-configs only; review before copying |
| vercel.json | GENERATED_REVIEW_COPY | Generated under deploy-configs only; review before copying |
| .dockerignore | GENERATED_REVIEW_COPY | Generated under deploy-configs only; review before copying |
| .github/workflows/deploy.yml | GENERATED_REVIEW_COPY | Generated under deploy-configs only; review before copying |

## Existing vs Generated Diff
Current live tree had only `voice_agent_backend/Dockerfile` (`voice_agent_backend/Dockerfile:1-12`). Generated review copies add dynamic port binding, non-root user, healthcheck, Render/Railway skeletons, Vercel skeleton, and deploy workflow skeleton.

## Files That Must Be Manually Placed
Copy files from `deploy-configs/` only after choosing the platform and reviewing service roots/secrets.

## Configs Not Generated
Fly.io, Heroku, Netlify, DigitalOcean, AWS, GCP, Azure, Coolify, and CapRover were not selected target platforms.

## Validation Commands
- `docker build -f Dockerfile.production -t voice-agent-prod .` from `voice_agent_backend`.
- `docker run --rm -p 8000:8000 --env-file .env voice-agent-prod`.
- `curl http://127.0.0.1:8000/health`.
