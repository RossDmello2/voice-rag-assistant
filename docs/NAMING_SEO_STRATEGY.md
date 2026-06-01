# Naming and SEO Strategy

**Date:** 2026-06-01
**Repository:** `RossDmello2/voice-rag-agent`
**Current display name:** VoiceRAG Agent
**Decision:** Keep the current repository slug unless the owner explicitly approves a rename.

## 1. Current Identity Audit

| Surface | Current state | Assessment |
| --- | --- | --- |
| Repository slug | `voice-rag-agent` | Strong. It contains the high-intent keywords `voice`, `rag`, and `agent` in a short kebab-case slug. |
| README title | `VoiceRAG Agent` | Strong. Short, memorable, and maps directly to the repo slug. |
| GitHub description | Local-first voice-to-voice RAG assistant with FastAPI, LangGraph, Qdrant, Ollama embeddings, Groq STT/chat, Kokoro ONNX TTS, and a vanilla JS UI. | Accurate and keyword-rich, but slightly dense. |
| Topics | 20 accurate topics covering language, framework, AI/RAG, voice, storage, and self-hosting. | Strong; GitHub allows up to 20 topics and the repo is already at that limit. |
| README first paragraph | Explains self-hosted document chat, FastAPI UI, Qdrant retrieval, Ollama embeddings, SSE, and Kokoro speech. | Accurate; can be made more direct for non-technical visitors. |
| Visuals | Real screenshots and a deterministic social-preview image. | Strong proof. Add one clearly labeled conceptual workflow visual for faster comprehension. |
| Community files | MIT license, contributing guide, support, security policy, code of conduct, issue templates, PR template, CI, CodeQL, Dependabot. | Credible for open source. |

What is working:

- The name already matches how people search this niche: `voice rag assistant`, `rag voice assistant`, and `voice rag agent`.
- The README has real screenshots near the top, not fake mockups.
- The repo has source-backed setup, test, API, deployment, security, and contribution sections.
- CI, CodeQL, Dependabot, and community files provide professional trust signals.

What was weak before this pass:

- The README status still referred to open CodeQL alerts after those alerts had been fixed.
- The first screen was accurate but could explain the user value faster.
- There was no dedicated naming/SEO decision record for future contributors.
- The repo had a social preview, but no conceptual workflow image explaining voice-to-RAG-to-speech at a glance.

## 2. Source-Backed Project Identity

VoiceRAG Agent is a local-first, self-hosted voice RAG assistant for asking questions over local documents by text or voice.

Source-backed facts:

- FastAPI runtime and frontend mount: `voice_agent_backend/app/main.py:41`, `voice_agent_backend/app/main.py:122`.
- API routers for chat, auth, ingest, STT, collections, health, models, and TTS: `voice_agent_backend/app/main.py:102-109`.
- Qdrant, Ollama, Groq, Kokoro, and SQLite-oriented configuration: `.env.example:14-56`, `voice_agent_backend/app/core/config.py:61-100`, `voice_agent_backend/app/core/config.py:132`.
- Chat, streaming, predictive RAG, and interrupt routes: `voice_agent_backend/app/api/routes/chat.py:52`, `voice_agent_backend/app/api/routes/chat.py:292`, `voice_agent_backend/app/api/routes/chat.py:354`, `voice_agent_backend/app/api/routes/chat.py:489`.
- Protected ingestion and protected collection mutations: `voice_agent_backend/app/api/routes/ingest.py:421-428`, `voice_agent_backend/app/api/routes/collections.py:27-69`.
- Safe Markdown rendering through `renderMarkdownSafe()`: `voice_agent_backend/frontend/script.js:545`, `voice_agent_backend/frontend/script.js:1356-1362`, `voice_agent_backend/frontend/script.js:1816-1834`.

Strongest differentiators:

- Voice-to-voice flow, not only typed document chat.
- Local-first/self-hosted architecture with local Qdrant, Ollama embeddings, SQLite auth, and Kokoro model artifacts.
- Explicit cloud boundary: Groq is used for STT/chat/translation when enabled, so the project is not misrepresented as fully offline.
- Vanilla JavaScript frontend served by FastAPI, which keeps setup and contribution friction lower than a split frontend build stack.
- Real tests and security automation are present.

Boundaries and limitations:

- Do not claim fully offline operation because Groq-backed features use cloud APIs.
- Do not claim hosted deployment because no live deployment URL exists.
- Do not claim production hardening beyond the verified repo checks; public internet exposure still needs operator-side secrets, CORS/host controls, provider-cost controls, and broader auth decisions.
- Do not claim benchmarked speed, best-in-class retrieval, enterprise security, or one-click deployment.

## 3. Search Intent Matrix

| Persona | Likely query | Relevant keywords | What they need to see quickly | Topic candidates |
| --- | --- | --- | --- | --- |
| Beginner AI builder | `voice rag assistant python` | voice RAG, Python, FastAPI, document QA | What it does, screenshots, quick start, prerequisites | `python`, `fastapi`, `voice-assistant`, `document-qa` |
| RAG developer | `qdrant ollama rag fastapi` | Qdrant, Ollama, LangGraph, RAG | Architecture, providers, API routes, extension points | `qdrant`, `ollama`, `langgraph`, `rag` |
| Self-hosting user | `self hosted voice assistant documents` | self-hosted, local-first, SQLite, Kokoro | Local vs cloud boundary, Docker/deployment caveats | `self-hosted`, `local-first`, `sqlite`, `text-to-speech` |
| Voice AI builder | `speech to text text to speech rag` | STT, TTS, Groq, Kokoro | Voice workflow, provider requirements, cost caveats | `speech-to-text`, `text-to-speech`, `groq`, `kokoro-tts` |
| Professional engineer | `fastapi langgraph rag agent example` | FastAPI, LangGraph, SSE, tests | Source map, tests, security posture, limitations | `fastapi`, `langgraph`, `ai-agent`, `server-sent-events` |
| Recruiter/non-technical evaluator | `AI voice document assistant github` | AI assistant, documents, voice, local-first | Plain-English value, real screenshots, credible status | `voice-agent`, `document-qa`, `voice-assistant` |

## 4. Competitor and Similar-Repo Pattern Scan

GitHub CLI searches on 2026-06-01 found multiple small repositories named around `voice-rag-assistant`, `rag-voice-assistant`, and `VoiceRAG`. Many had empty descriptions or one-line generic descriptions. That suggests the repo should not chase a cute or abstract name; it can stand out by being clearer, better documented, and more visually grounded.

Useful naming patterns:

- `voice-rag-*` and `rag-voice-*` are immediately searchable.
- `assistant`, `agent`, and `document-qa` communicate the use case faster than abstract product names.
- Short, kebab-case repo slugs work better in GitHub search results than long demo titles.

Overused or weak patterns:

- `jarvis` hides the document/RAG use case.
- `chatbot` undersells the voice-to-voice workflow.
- `studio`, `platform`, or `workspace` can imply a product surface larger than this repo proves.
- Acronyms without words such as `VRAG` are harder for beginners to understand and search.

README visual patterns to keep:

- Real screenshots near the top.
- Plain-English value proposition before deep architecture.
- One diagram or conceptual workflow visual only when clearly labeled.

## 5. Candidate Names

Scores are 1-10. Higher is better.

| Candidate | Clarity | Memorability | Searchability | Honesty | Domain Fit | Beginner Appeal | Pro Credibility | Uniqueness | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| VoiceRAG Agent | 9 | 8 | 9 | 10 | 10 | 8 | 9 | 7 | Best balance; keep. |
| Voice RAG Agent | 10 | 7 | 10 | 10 | 10 | 9 | 8 | 6 | Clearer as words, weaker as a brand. |
| VoiceRAG Assistant | 9 | 8 | 9 | 10 | 9 | 9 | 8 | 5 | Very clear, but many similar repos use `assistant`. |
| Local VoiceRAG | 8 | 7 | 8 | 9 | 9 | 8 | 8 | 7 | Good local-first cue, less complete than current. |
| Self-Hosted VoiceRAG | 8 | 6 | 8 | 9 | 9 | 7 | 8 | 7 | Accurate but long and less memorable. |
| DocVoice RAG | 8 | 7 | 7 | 9 | 8 | 8 | 7 | 7 | Good document cue; less standard search wording. |
| VoiceDoc RAG | 8 | 7 | 7 | 9 | 8 | 8 | 7 | 7 | Similar to DocVoice; slightly awkward. |
| TalkDocs RAG | 7 | 8 | 6 | 8 | 8 | 9 | 6 | 7 | Friendly, but sounds more like SaaS branding. |
| SpeakDocs | 7 | 8 | 5 | 7 | 7 | 9 | 6 | 6 | Memorable but hides RAG/agent keywords. |
| SpeechRAG | 7 | 7 | 8 | 8 | 8 | 7 | 7 | 6 | Searchable but sounds like a library, not an app. |
| VoiceQA Local | 8 | 6 | 7 | 8 | 8 | 8 | 7 | 7 | Good query-answering cue; weaker RAG keywording. |
| DocTalk Agent | 7 | 7 | 6 | 8 | 7 | 8 | 7 | 6 | Clear enough but less specific to RAG. |
| RAGVoice Workbench | 7 | 6 | 7 | 7 | 7 | 6 | 8 | 7 | `Workbench` implies broader tooling than source proves. |
| VoiceGraph RAG | 7 | 7 | 6 | 8 | 8 | 6 | 8 | 7 | Useful LangGraph hint, less intuitive to non-technical users. |
| EchoRAG | 5 | 8 | 5 | 6 | 6 | 6 | 5 | 7 | Memorable but too abstract and voice-only sounding. |
| Document Voice Agent | 9 | 5 | 8 | 9 | 8 | 9 | 7 | 4 | Clear phrase, weak brand and too generic. |

Rejected naming directions:

- `Jarvis`, `Friday`, or assistant-persona names: memorable but too generic and do not communicate document RAG.
- `Enterprise VoiceRAG`: unsupported overclaim.
- `Offline VoiceRAG`: misleading because Groq-backed features use cloud APIs.
- `VoiceRAG Platform`: implies a broader product platform than the source proves.

## 6. Top 3 Recommendations

### 1. Keep: VoiceRAG Agent

- Display name: `VoiceRAG Agent`
- Repo slug: `voice-rag-agent`
- Tagline: `Talk to your documents with a local-first voice RAG assistant.`
- GitHub description: `Local-first voice RAG assistant for talking to documents with FastAPI, LangGraph, Qdrant, Ollama embeddings, Groq STT/chat, Kokoro TTS, and vanilla JS.`
- Risk/tradeoff: `VoiceRAG` is not unique across GitHub, but the current slug is clear and searchable.

### 2. Alternative: VoiceRAG Assistant

- Display name: `VoiceRAG Assistant`
- Repo slug: `voice-rag-assistant`
- Tagline: `Ask your documents questions by voice, then hear grounded answers back.`
- GitHub description: `Self-hosted voice RAG assistant for document Q&A with FastAPI, Qdrant, Ollama embeddings, Groq STT/chat, Kokoro TTS, and vanilla JS.`
- Risk/tradeoff: Strong beginner clarity, but the slug collides with many similarly named repos and would require explicit owner approval.

### 3. Alternative: Local VoiceRAG

- Display name: `Local VoiceRAG`
- Repo slug: `local-voice-rag`
- Tagline: `A local-first document QA assistant for speech-to-speech RAG workflows.`
- GitHub description: `Local-first document voice RAG assistant using FastAPI, LangGraph, Qdrant, Ollama embeddings, Groq STT/chat, Kokoro TTS, and SQLite auth.`
- Risk/tradeoff: Strong local-first cue, but less memorable than the current display name.

## 7. Recommended Topics

Keep 20 topics and prefer domain/use-case topics over low-intent implementation details:

```text
ai-agent
document-qa
fastapi
groq
kokoro-tts
langgraph
local-first
ollama
python
qdrant
rag
retrieval-augmented-generation
self-hosted
speech-to-text
sqlite
text-to-speech
vanilla-javascript
vector-database
voice-agent
voice-assistant
```

Recommended change: replace `server-sent-events` with `vector-database`. SSE is true, but `vector-database` is more likely to match RAG/search intent and is still accurate because the repo uses Qdrant.

## 8. README Opening Recommendation

Recommended opening paragraph:

> VoiceRAG Agent is a local-first voice RAG assistant for talking to your documents. Upload files, ask questions by text or voice, stream grounded answers from a FastAPI backend, and optionally hear responses through Kokoro ONNX text-to-speech.

Follow immediately with:

> It is self-hosted by design, but not fully offline by default: Groq-backed STT, translation, and chat use cloud APIs when enabled.

## 9. Final Recommendation

Keep the actual GitHub repository slug as `voice-rag-agent`.

Do not rename the repository without explicit owner approval. A rename would affect clone URLs, badges, README links, existing search signals, and downstream references. The current slug is already one of the strongest honest keyword combinations for this project.

If the owner later approves a rename, the only serious alternative is `voice-rag-assistant`, but the improvement is not large enough to justify URL churn right now.
