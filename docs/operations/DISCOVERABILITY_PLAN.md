# Discoverability Plan

Date: 2026-06-01
Project identity: VoiceRAG Agent
Repository slug: `RossDmello2/voice-rag-agent`

## Positioning

VoiceRAG Agent should be described consistently as:

> Local-first voice RAG assistant for talking to documents with FastAPI, vanilla JavaScript, LangGraph, Qdrant, Ollama embeddings, Groq STT/chat, Kokoro ONNX TTS, and SQLite auth.

This is intentionally precise. The project is not a generic agent framework, a hosted SaaS, or a fully offline assistant when Groq is enabled.

## Search Surfaces

GitHub repository discovery depends heavily on the repository name, description, topics, and README. Google can use page titles, headings, snippets, meta descriptions, and nearby image context. The project therefore optimizes the surfaces it controls:

- Repository name: `voice-rag-agent`
- Display name: `VoiceRAG Agent`
- README H1, tagline, feature language, and quickstart
- GitHub description and topics
- Screenshot and social preview assets
- Frontend `<title>`, description, Open Graph, and Twitter card metadata

No change can guarantee top placement in GitHub or Google search. The goal is accurate, useful, and consistent signals.

## GitHub Metadata

Description:

```text
Local-first voice RAG assistant for talking to documents with FastAPI, LangGraph, Qdrant, Ollama embeddings, Groq STT/chat, Kokoro TTS, and vanilla JS.
```

Topics:

```text
ai-agent, document-qa, fastapi, groq, kokoro-tts, langgraph, local-first,
ollama, python, qdrant, rag, retrieval-augmented-generation, self-hosted,
speech-to-text, sqlite, text-to-speech, vanilla-javascript, vector-database,
voice-agent, voice-assistant
```

## Assets

- `docs/assets/screenshots/home.png`: primary README screenshot.
- `docs/assets/screenshots/auth-documents.png`: auth and document-management screenshot.
- `docs/assets/brand/workflow-visual.png`: generated conceptual workflow visual; label as conceptual, not product evidence.
- `docs/assets/social-preview.png`: GitHub social preview source image.

If a hosted public app or docs site is added later, update the frontend canonical URL and Open Graph URL from the GitHub repository URL to the public site URL.

## Source References

- Google SEO Starter Guide: https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- GitHub repository search qualifiers: https://github.com/github/docs/blob/main/content/search-github/searching-on-github/searching-for-repositories.md
- GitHub repository topics: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics
- GitHub social preview: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview
- GitHub community profile: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories
