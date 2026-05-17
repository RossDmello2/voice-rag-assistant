"""
Retrieve context node — async wrapper around langchain_rag retrieve_context().
MUST be async because retrieve_context() is async (Finding 4).
"""

import logging
from langgraph.config import get_stream_writer

from app.core.langchain_rag import retrieve_context
from app.core.graph_state import VoiceAgentState

logger = logging.getLogger(__name__)


async def retrieve_context_node(state: VoiceAgentState) -> dict:
    """
    Retrieve relevant context from Qdrant using RAG pipeline.
    MUST be async because retrieve_context() is async (Finding 4).
    """
    writer = get_stream_writer()
    writer({"stage": "retrieving"})

    english_query = state.get("english_query", "")
    collection = state.get("collection", "agent_knowledge")
    flags = state.get("intent_flags", {"isSummary": False, "isFollowUp": False})
    last_retrieval = state.get("last_retrieval")
    embed_model = state.get("embed_model")

    try:
        context = await retrieve_context(
            query=english_query,
            collection=collection,
            flags=flags,
            last_retrieval=last_retrieval,
            embed_model=embed_model,
        )

        sources = context.get("sources", [])
        writer({"sources": sources})

        return {
            "retrieved_context": context,
            "sources": sources,
            "current_stage": "retrieving",
        }
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return {
            "retrieved_context": {"has_context": False, "context_text": "", "sources": []},
            "sources": [],
            "current_stage": "retrieving",
        }