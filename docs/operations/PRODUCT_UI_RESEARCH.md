# Product UI Research

**Date:** 2026-05-17  
**UI relevance:** high, because the browser UI is the primary human workflow.

## Relevant Patterns

- Self-hosted AI products such as Open WebUI and LibreChat put provider/model settings in the app but keep secrets server-managed. This matches the current Groq key hint and should remain the rule.
- AI chat interfaces need clear health state, source visibility, loading states, and recovery paths. The existing UI already has service health, transcript, document panel, and settings panel; the productionization pass should harden those rather than redesigning the UI.
- Auth should appear only when required for protected actions or when the user chooses to sign in. Local read/chat workflows remain low-friction.
- Markdown from model output must be sanitized before rendering. DOMPurify is the right browser-side fit because it is designed to clean HTML before `innerHTML`.
- Upload workflows should use sanitized display filenames and should not trust raw browser filenames for storage or vector metadata.

## Applied To This Repo

- Add a compact auth modal using the existing `.auth-*` styles.
- Add a logout control in the status bar and persist only JWT plus email metadata in localStorage.
- Attach bearer tokens through a small fetch wrapper for protected writes only.
- Keep same-origin relative `fetch()` calls. There is no Expo runtime, no `EXPO_PUBLIC_*` environment surface, and no axios dependency.
- Add frontend tests for auth state, 401 recovery, authorized write calls, and malicious Markdown sanitization.

## Deferred UI Work

- A full design-system or component-library migration is out of scope.
- Mobile/desktop visual polish is limited to making the auth surface usable and non-overlapping.
- Durable backend document list reconciliation is deferred unless required by tests.
