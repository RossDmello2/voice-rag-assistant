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

- Confirm GitHub recognizes `README.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, issue forms, and PR template.
- Keep security reports out of public issues and route them through GitHub private vulnerability reporting.
- Enable Discussions only if there is a maintainer ready to respond.

## Security Settings

- Enable Dependabot alerts and security updates.
- Enable private vulnerability reporting.
- Keep secret scanning and push protection enabled when available for the account/repository.
- Require CI and CodeQL before merging once the first branch-protection rule is configured.
- Review open code-scanning alerts before marking a hosted public deployment as hardened.
- Keep GitHub Actions permissions least-privilege by default.

## Verification

Run the README verification commands before pushing a release tag. Hosted/provider smoke tests still require Qdrant, Ollama, Kokoro artifacts, and valid Groq credentials.
