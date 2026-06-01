# Research Sources

## Official Discoverability Sources

| Source | Use |
| --- | --- |
| https://developers.google.com/search/docs/fundamentals/seo-starter-guide | Used for title/snippet, image placement, and alt-text guidance. |
| https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories | Used for GitHub search-surface guidance: names, descriptions, topics, and README qualifiers. |
| https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics | Used for topic-count and topic-quality guidance. |
| https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview | Used for social-preview image size and upload limits. |
| https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories | Used for community-health file expectations. |

## GitHub Search Queries

Executed with GitHub CLI on 2026-06-01:

```text
gh search repos "voice rag assistant" --limit 10 --json fullName,description,stargazersCount,language,url --sort stars
gh search repos "RAG voice assistant" --limit 10 --json fullName,description,stargazersCount,language,url --sort stars
gh search repos "local first voice assistant" --limit 10 --json fullName,description,stargazersCount,language,url --sort stars
gh search repos "document qa voice assistant" --limit 10 --json fullName,description,stargazersCount,language,url --sort stars
```

Observed pattern: the exact phrase family `voice-rag-assistant`, `rag-voice-assistant`, and `VoiceRAG` appears across many small repositories, but descriptions are often empty or generic. That makes precise description, screenshots, and a source-backed README more valuable than a risky rename.
