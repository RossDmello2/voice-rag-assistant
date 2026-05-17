# Open Source Landscape

**Date:** 2026-05-17  
**Depth:** standard

## Sources Reviewed

| Source | Why Comparable | Applied Pattern | Not Copied |
|---|---|---|---|
| GitHub security features: https://docs.github.com/en/code-security/getting-started/github-security-features | Open-source security baseline. | Security policy, Dependabot, secret scanning, push protection, and code scanning are the expected GitHub posture. | Paid/enterprise-only enforcement is documented, not assumed. |
| GitHub Dependabot options: https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference | Dependency update automation. | Keep weekly pip and GitHub Actions updates. | No npm schedule because the repo has no `package.json`. |
| GitHub CodeQL docs: https://docs.github.com/en/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql | SAST baseline. | Add a Python/JavaScript CodeQL workflow if it can run with least privilege. | Do not treat CodeQL as a replacement for tests. |
| OpenSSF Scorecard action: https://github.com/ossf/scorecard-action | Supply-chain posture. | Use least-privilege workflow permissions and document Scorecard follow-up. | Publishing Scorecard results is deferred until the repository exists on GitHub. |
| OpenSSF Scorecard checks: https://github.com/ossf/scorecard | Open-source readiness signals. | CI tests, dependency update tooling, security policy, SAST, token permissions, and binary-artifact policy are relevant. | Binaries are preserved locally but excluded from git rather than forced into the repo. |
| SLSA specification: https://slsa.dev/spec/v1.1/ | Build provenance posture. | Document Docker build provenance and future artifact attestation steps. | Full SLSA release automation is out of scope until there is a public release path. |
| OWASP ASVS authentication: https://github.com/OWASP/ASVS/blob/master/4.0/en/0x11-V2-Authentication.md | Auth/access-control risk framing. | Require bearer auth for mutating operations and avoid fallback secrets in production mode. | MFA/session hardening is documented as future work for multi-user deployment. |
| OWASP File Upload Cheat Sheet: https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/File_Upload_Cheat_Sheet.md | Upload security. | Enforce extension and size checks, sanitize filenames, and avoid trusting raw upload names. | Antivirus scanning is documented as future deployment hardening. |
| FastAPI OAuth2/JWT tutorial: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ | Local FastAPI auth pattern. | Use OAuth2 bearer dependency and JWT validation for protected endpoints. | Refresh-token and role-based scopes are deferred. |
| DOMPurify: https://github.com/cure53/DOMPurify | Frontend XSS mitigation for Markdown output. | Sanitize Markdown HTML before assigning to `innerHTML`. | No Node build pipeline is introduced only to bundle it. |
| LangGraph: https://github.com/langchain-ai/langgraph | Agent graph runtime. | Preserve the existing graph as the core production surface and test imports. | No framework migration is attempted. |
| Open WebUI: https://github.com/open-webui/open-webui | Self-hosted AI UI pattern. | Model/provider settings, health state, and local deployment documentation are useful. | Its full multi-user platform architecture is too large for this app. |
| LibreChat: https://github.com/danny-avila/LibreChat | AI chat app with auth/provider configuration. | Authenticated settings and provider separation inform this pass. | Plugin/agent marketplace features are not copied. |
| run-llama/chat-ui: https://github.com/run-llama/chat-ui | LLM chat/source UI pattern. | Source visibility and chat ergonomics are relevant to future UI passes. | Component-library migration is not needed for this vanilla UI. |

## Decisions

- Keep the product local-first, but protect destructive/cost-bearing write flows.
- Preserve local model/data artifacts, exclude them from git, and document how to restore them.
- Add security automation that works without requiring paid GitHub features.
- Do not introduce a frontend framework, Expo app, or package publishing flow in this pass.
