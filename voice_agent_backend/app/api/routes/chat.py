from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest
from app.core.intent import (
    classify_intent,
    detect_prompt_injection,
    map_slang_to_formal,
)
from app.core.langchain_rag import (
    retrieve_context,
    build_contextual_prompt,
    has_sufficient_confidence,
)
from app.core.memory import memory_store
from app.core.config import settings, SYSTEM_PROMPT_BASE, SYSTEM_PROMPT_DOCUMENT
from app.services.llm_router import chat_complete
from app.core.translation import translate_to_english, translate_from_english
from app.core.limiter import limiter
import json
import re
import random
import time
import logging
import asyncio

from app.models.schemas import ChatStreamRequest, InterruptRequest
from app.core.voice_graph import compiled_graph

logger = logging.getLogger(__name__)
router = APIRouter()

NO_INFO_PHRASES = [
    "Hmm I don't really know about that.",
    "I'm not sure I have that information.",
    "That's not something I'm currently aware of.",
    "I don't think I have that info.",
]


# Per-collection document existence cache (60s TTL)
_DOC_EXISTENCE_CACHE = {}
_CACHE_TTL = 60

# Predictive RAG Cache for speculative completion (10s TTL)
_PREDICTIVE_RAG_CACHE = {}
_PREDICTIVE_TTL = 10

# Last backchannel timestamp per session to enforce cooldown
_LAST_BACKCHANNEL_AT = {}


@router.post("/chat")
@limiter.limit("20/minute")
async def chat_endpoint(
    request: Request, req: ChatRequest
):
    """
    Main chat endpoint with SSE streaming.
    Full orchestration: translate input → classify intent → RAG retrieval → LLM stream → translate output
    """
    session = memory_store.get_or_create(req.session_id)
    last_retrieval = memory_store.get_last_retrieval(req.session_id)
    history = memory_store.get_history(req.session_id)
    last_intent_was_document = bool(
        last_retrieval.get("resolvedQuery") or last_retrieval.get("answer")
    )

    # Translate non-English input to English first
    start_time = time.time()
    english_message = req.message
    if req.language != "en":
        english_message = await translate_to_english(req.message, req.language)
        print(f"LATENCY: Translation took {time.time() - start_time:.2f}s", flush=True)

    # Normalize slang (e.g., 'u' -> 'you') for better processing
    english_message = map_slang_to_formal(english_message)

    # Prompt injection guard
    if detect_prompt_injection(english_message):

        async def blocked_generate():
            answer = "I can only help with questions about uploaded documents and general conversation."
            yield f"data: {json.dumps({'token': answer})}\n\n"
            yield "data: [DONE]\n\n"
            memory_store.append_turn(req.session_id, req.message, answer)

        return StreamingResponse(blocked_generate(), media_type="text/event-stream")

    # Check if documents exist in collection (with 60s cache)
    from app.services.qdrant_service import list_documents

    cache_key = req.collection
    now = time.time()
    
    if cache_key in _DOC_EXISTENCE_CACHE and (now - _DOC_EXISTENCE_CACHE[cache_key]["time"]) < _CACHE_TTL:
        has_documents = _DOC_EXISTENCE_CACHE[cache_key]["exists"]
    else:
        has_documents = False
        try:
            docs = await list_documents(req.collection)
            has_documents = len(docs) > 0
            _DOC_EXISTENCE_CACHE[cache_key] = {"exists": has_documents, "time": now}
        except Exception:
            has_documents = False

    # Intent classification (Run in parallel with speculative retrieval)
    intent_start = time.time()

    # We fire off both at once.
    # Note: retrieval_task starts as a 'speculative' search before we know the intent.
    intent_task = asyncio.create_task(
        classify_intent(
            text=english_message,
            has_documents=has_documents,
            last_intent_was_document=last_intent_was_document,
        )
    )

    # We only fire retrieval if documents exist
    retrieval_task = None
    if has_documents:
        # Default flags for speculative pre-fetch
        speculative_flags = {"isSummary": False, "isFollowUp": False}
        retrieval_task = asyncio.create_task(
            retrieve_context(
                query=english_message,
                collection=req.collection,
                flags=speculative_flags,
                last_retrieval=last_retrieval if last_intent_was_document else None,
                embed_model=req.embed_model,
            )
        )

    async def generate():
        nonlocal last_retrieval
        gen_start = time.time()

        # 1. Wait for intent
        intent, flags = await intent_task
        print(
            f"LATENCY: Intent classification took {time.time() - intent_start:.2f}s",
            flush=True,
        )

        # 2. Early handle intents that don't need RAG
        if intent == "STOP_COMMAND":
            answer = "Okay, stopping."
            yield f"data: {json.dumps({'token': answer})}\n\n"
            yield "data: [DONE]\n\n"
            memory_store.append_turn(req.session_id, req.message, answer)
            if retrieval_task:
                retrieval_task.cancel()
            return

        if intent == "UPLOAD_INTENT":
            answer = "You can upload a document through the Documents panel. Just click the folder icon and select your file."
            yield f"data: {json.dumps({'token': answer})}\n\n"
            yield "data: [DONE]\n\n"
            memory_store.append_turn(req.session_id, req.message, answer)
            if retrieval_task:
                retrieval_task.cancel()
            return

        system_prompt = SYSTEM_PROMPT_BASE
        context_prompt = english_message
        sources = []

        # 3. Handle DOCUMENT_QUERY (Wait for parallel retrieval if needed)
        if intent == "DOCUMENT_QUERY" and retrieval_task:
            context = await retrieval_task
            print(
                f"LATENCY: Document retrieval took {time.time() - intent_start:.2f}s (Total from start)",
                flush=True,
            )

            if not context.get("has_context") or not has_sufficient_confidence(
                [
                    {
                        "combined_score": context.get("top_score", 0),
                        "score": context.get("top_score", 0),
                    }
                ],
                flags.get("isSummary", False),
            ):
                answer = random.choice(NO_INFO_PHRASES)
                if req.language != "en":
                    answer = await translate_from_english(answer, req.language)
                yield f"data: {json.dumps({'token': answer})}\n\n"
                yield "data: [DONE]\n\n"
                memory_store.append_turn(req.session_id, req.message, answer)
                return

            last_answer = (
                last_retrieval.get("answer", "") if last_intent_was_document else ""
            )
            context_prompt = build_contextual_prompt(
                english_message, context, flags, last_answer
            )
            sources = context.get("sources", [])
            system_prompt = SYSTEM_PROMPT_DOCUMENT

            # Save retrieval state
            memory_store.set_last_retrieval(
                req.session_id,
                {
                    "query": english_message,
                    "resolvedQuery": english_message,
                    "answer": "",
                    "sources": sources,
                    **{
                        k: context[k]
                        for k in ["context_text", "pages", "result_count", "top_score"]
                        if k in context
                    },
                },
            )

        elif intent == "IDENTITY_QUERY":
            if retrieval_task:
                retrieval_task.cancel()
            context_prompt = (
                "KNOWLEDGE ABOUT ME:\n"
                "- I am your helpful and professional voice assistant.\n"
                "- I speak naturally, use contractions, and keep things simple.\n\n"
                f"User asked: {english_message}"
            )
        else:
            # GENERAL_CHAT or other: cancel speculative retrieval
            if retrieval_task:
                retrieval_task.cancel()

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-settings.MEMORY_PAIRS * 2 :])
        messages.append({"role": "user", "content": context_prompt})

        # Determine which model and provider to use (respect client override)
        chat_model = req.chat_model or settings.CHAT_MODEL
        chat_provider = req.chat_provider or settings.CHAT_PROVIDER

        # Stream LLM response
        print(
            f"LATENCY: Pre-LLM orchestration took {time.time() - gen_start:.2f}s",
            flush=True,
        )
        full_response = ""
        ttft_logged = False
        try:
            async for token in chat_complete(
                messages, chat_model, provider=chat_provider, stream=True
            ):
                if not ttft_logged:
                    print(
                        f"LATENCY: TTFT (from generate start) took {time.time() - gen_start:.2f}s",
                        flush=True,
                    )
                    ttft_logged = True
                full_response += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception:
            logger.exception("Chat completion stream failed")
            error_msg = "Sorry, I encountered an error while generating a response."
            yield f"data: {json.dumps({'token': error_msg})}\n\n"
            full_response = error_msg

        # Strip inline citations from final response
        clean_response = re.sub(
            r"【[^】]+】|\[\s*Source:[^\]]+\]|\(\s*Source:[^)]+\)", "", full_response
        ).strip()

        # Translate response back if non-English
        display_response = clean_response
        if req.language != "en":
            display_response = await translate_from_english(
                clean_response, req.language
            )
            yield f"data: {json.dumps({'translated': display_response})}\n\n"

        yield f"data: {json.dumps({'sources': sources, 'intent': intent})}\n\n"
        yield "data: [DONE]\n\n"

        # Commit turn to memory
        memory_store.append_turn(req.session_id, req.message, clean_response)
        if intent == "DOCUMENT_QUERY":
            lr = memory_store.get_last_retrieval(req.session_id)
            lr["answer"] = clean_response
            memory_store.set_last_retrieval(req.session_id, lr)

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/chat/predict")
async def chat_predict_endpoint(req: ChatStreamRequest):
    """
    Speculative RAG endpoint. Frontend triggers this when user is 'FINISHING_LIKELY'.
    Warms up the cache for a specific session/query.
    """
    if not req.message or len(req.message.split()) < 3:
        return {"status": "skipped", "reason": "too_short"}

    cache_key = f"{req.session_id}:{req.message}"
    
    # Check if already cached
    now = time.time()
    if cache_key in _PREDICTIVE_RAG_CACHE:
        if (now - _PREDICTIVE_RAG_CACHE[cache_key]["time"]) < _PREDICTIVE_TTL:
            return {"status": "cached"}

    try:
        # Fire retrieval
        context = await retrieve_context(
            query=req.message,
            collection=req.collection,
            flags={"isSummary": False, "isFollowUp": False},
            last_retrieval=None, # Predictive doesn't need prev context yet
            embed_model=req.embed_model,
        )
        
        _PREDICTIVE_RAG_CACHE[cache_key] = {
            "context": context,
            "time": now
        }
        return {"status": "success"}
    except Exception:
        logger.exception("Predictive RAG failed")
        return {"status": "error", "detail": "Predictive RAG failed"}


@router.post("/chat/backchannel/{session_id}")
async def chat_backchannel_endpoint(session_id: str):
    """
    Manual backchannel trigger for the listening phase.
    Triggered by frontend when user pauses mid-thought.
    """
    now = time.time()
    last_at = _LAST_BACKCHANNEL_AT.get(session_id, 0)
    
    if (now - last_at) < settings.BACKCHANNEL_COOLDOWN_SECONDS:
        return {"status": "skipped", "reason": "cooldown"}

    from app.services.speech_service import speech_service
    b64_audio = speech_service.get_backchannel()
    if b64_audio:
        _LAST_BACKCHANNEL_AT[session_id] = now
        return {"status": "success", "audio": b64_audio}
    
    return {"status": "error", "reason": "no_audio"}


# ═══════════════════════════════════════════════════════════════════
# NEW: LangGraph voice pipeline endpoints
# ═══════════════════════════════════════════════════════════════════

@router.post("/chat/stream")
@limiter.limit("20/minute")
async def chat_stream_endpoint(
    request: Request, req: ChatStreamRequest
):
    """
    LangGraph-powered voice pipeline with SSE streaming.
    Invokes compiled_graph.astream() with stream_mode=["custom"],
    yielding SSE events for tokens, stages, audio chunks, etc.
    """
    session_id = req.session_id or req.thread_id or f"session_{int(time.time() * 1000)}"
    thread_id = req.thread_id or session_id  # Fallback to session_id for guest users

    session = memory_store.get_or_create(session_id)
    last_retrieval = memory_store.get_last_retrieval(session_id)
    history = memory_store.get_history(session_id)
    # Convert history pairs to context_window format [ {q:..., a:...}, ... ]
    context_window = []
    # history stores full role/content pairs. We group them.
    for i in range(0, len(history), 2):
        if i + 1 < len(history):
            context_window.append({"q": history[i]["content"], "a": history[i+1]["content"]})

    # Build initial state for the graph
    initial_state = {
        "messages": [],
        "context_window": context_window,
        "current_query": req.message,
        "english_query": "",
        "intent": None,
        "intent_flags": {"isSummary": False, "isFollowUp": False},
        "has_documents": req.has_documents,
        "last_intent_was_document": req.last_intent_was_document,
        "is_injection": False,
        "retrieved_context": None,
        "generated_response": "",
        "clean_response": "",
        "display_response": "",
        "interrupt_flag": False,
        "interrupted_query": "",
        "thread_id": thread_id,
        "session_id": session_id, # Pass session_id to save back to memory_store later
        "chat_model": req.chat_model or settings.CHAT_MODEL,
        "chat_provider": req.chat_provider or settings.CHAT_PROVIDER,
        "embed_model": req.embed_model or settings.EMBED_MODEL,
        "collection": req.collection,
        "language": req.language,
        "tts_voice": req.tts_voice,
        "tts_speed": req.tts_speed,
        "hardware": req.hardware,
        "sources": [],
        "last_retrieval": last_retrieval,
        "current_stage": "",
    }

    config = {
        "configurable": {"thread_id": thread_id},
    }

    # Unified transmission queue for both LangGraph events and side-car backchannels
    sse_queue = asyncio.Queue()

    async def side_car_backchannel_listener(request_body: ChatStreamRequest):
        """
        Side-car task that can emit backchannels independently of LangGraph.
        """
        sid = request_body.session_id
        now = time.time()
        last_at = _LAST_BACKCHANNEL_AT.get(sid, 0)
        
        # Check cooldown
        if (now - last_at) < settings.BACKCHANNEL_COOLDOWN_SECONDS:
            return

        from app.services.speech_service import speech_service
        b64_audio = speech_service.get_backchannel()
        if b64_audio:
            _LAST_BACKCHANNEL_AT[sid] = now
            # Push directly to SSE queue
            await sse_queue.put({"audio": b64_audio})

    async def stream_graph():
        """Stream LangGraph events as SSE."""
        # 1. Start side-car if requested (or based on heuristics)
        # For now, we can trigger a processing backchannel immediately if we expect long RAG
        if req.has_documents:
            asyncio.create_task(side_car_backchannel_listener(req))

        try:
            # Wrap graph execution in a task
            async def run_graph():
                async for event in compiled_graph.astream(
                    initial_state,
                    config=config,
                    stream_mode=["custom"],
                ):
                    if isinstance(event, tuple) and len(event) == 2:
                        _, data = event
                    else:
                        data = event
                    await sse_queue.put(data)
                await sse_queue.put("[DONE]")

            graph_task = asyncio.create_task(run_graph())

            while True:
                data = await sse_queue.get()
                if data == "[DONE]":
                    yield "data: [DONE]\n\n"
                    break
                
                if isinstance(data, dict):
                    # Signal backchannel emission to frontend if we wanted
                    # existing logic:
                    if "token" in data:
                        yield f"data: {json.dumps({'token': data['token']})}\n\n"
                    if "stage" in data:
                        yield f"data: {json.dumps({'stage': data['stage']})}\n\n"
                    if "audio" in data:
                        yield f"data: {json.dumps({'audio': data['audio']})}\n\n"
                    if data.get("audio_done"):
                        yield f"data: {json.dumps({'audio_done': True})}\n\n"
                    if "translated" in data:
                        yield f"data: {json.dumps({'translated': data['translated']})}\n\n"
                    if "sources" in data and "stage" not in data:
                        yield f"data: {json.dumps({'sources': data['sources']})}\n\n"

        except Exception as e:
            logger.error(f"Graph streaming error: {e}", exc_info=True)
            yield f"data: {json.dumps({'token': 'Sorry, something went wrong.'})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream_graph(), media_type="text/event-stream")


@router.post("/chat/interrupt/{thread_id}")
@limiter.limit("30/minute")
async def interrupt_endpoint(
    request: Request,
    thread_id: str,
    req: InterruptRequest,
):
    """
    Resume a paused LangGraph execution for a thread.
    The graph was paused by interrupt() in check_interrupt_node.
    This endpoint resumes it with Command(resume=<new_query>) and
    streams the resumed graph output as SSE events.
    """
    from langgraph.types import Command

    config = {
        "configurable": {"thread_id": thread_id},
    }

    resume_value = req.new_query or ""

    async def stream_resume():
        """Stream resumed graph events as SSE."""
        try:
            async for event in compiled_graph.astream(
                Command(resume=resume_value),
                config=config,
                stream_mode=["custom"],
            ):
                if isinstance(event, tuple) and len(event) == 2:
                    _, data = event
                else:
                    data = event

                if isinstance(data, dict):
                    if "token" in data:
                        yield f"data: {json.dumps({'token': data['token']})}\n\n"
                    if "stage" in data:
                        yield f"data: {json.dumps({'stage': data['stage']})}\n\n"
                    if "audio" in data:
                        yield f"data: {json.dumps({'audio': data['audio']})}\n\n"
                    if data.get("audio_done"):
                        yield f"data: {json.dumps({'audio_done': True})}\n\n"
                    if "translated" in data:
                        yield f"data: {json.dumps({'translated': data['translated']})}\n\n"
                    if "sources" in data and "stage" not in data:
                        yield f"data: {json.dumps({'sources': data['sources']})}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Interrupt resume failed: {e}", exc_info=True)
            yield f"data: {json.dumps({'token': 'Sorry, something went wrong resuming.'})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream_resume(), media_type="text/event-stream")
