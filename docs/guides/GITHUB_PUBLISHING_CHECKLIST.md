# GitHub Publishing Checklist

Use this checklist when publishing VoiceRAG Agent to `RossDmello2/voice-rag-agent`.

## Repository Setup

- Create a public GitHub repository named `voice-rag-agent`.
- Add `origin` to the local repository.
- Push `main` and the active contribution branch.
- Set the repository description from `docs/operations/DISCOVERABILITY_PLAN.md`.
- Add all 20 GitHub topics from the discoverability plan.
- Upload `docs/assets/social-preview.png` as the repository social preview.

## Community Profile

- Confirm GitHub recognizes `README.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue templates, and PR template.
- Keep security reports out of public issues and route them through `SECURITY.md`.
- Enable Discussions only if there is a maintainer ready to respond.

## Security Settings

- Enable Dependabot alerts and security updates.
- Keep secret scanning and push protection enabled when available for the account/repository.
- Require CI and CodeQL before merging once the first branch-protection rule is configured.
- Keep GitHub Actions permissions least-privilege by default.

## Verification

Run the README verification commands before pushing a release tag. Hosted/provider smoke tests still require Qdrant, Ollama, Kokoro artifacts, and valid Groq credentials.

