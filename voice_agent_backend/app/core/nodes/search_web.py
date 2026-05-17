"""
Search web node — provides real-time search capabilities to the voice agent.
Uses DuckDuckGo search by default (no API key required).
"""

import logging
from duckduckgo_search import DDGS
from langgraph.config import get_stream_writer

from app.core.graph_state import VoiceAgentState
from app.core.config import settings

logger = logging.getLogger(__name__)


async def search_web_node(state: VoiceAgentState) -> dict:
    """
    Search the web for the user's query and add results to the state.
    """
    writer = get_stream_writer()
    writer({"stage": "searching"})

    english_query = state.get("english_query", "")
    if not english_query:
        return {"current_stage": "searching"}

    logger.info(f"Searching web for: {english_query}")
    
    search_results = ""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(english_query, max_results=5)
            if results:
                formatted_results = []
                for i, r in enumerate(results, 1):
                    formatted_results.append(f"[{i}] {r['title']}: {r['body']}\nSource: {r['href']}")
                search_results = "\n\n".join(formatted_results)
                logger.info(f"Found {len(results)} search results.")
            else:
                search_results = "No relevant search results found."
                logger.info("No search results found.")
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        search_results = f"Web search is currently unavailable: {e}"

    # We store search results in retrieved_context to be used by the generate_response node
    # or we can create a specific field for it. 
    # To keep it simple and compatible with existing prompts, we'll append it or set it.
    
    current_context = state.get("retrieved_context", {})
    if not current_context:
        current_context = {"has_context": True, "context_text": "", "sources": []}
    
    current_context["context_text"] = f"DEBUG: WEB SEARCH RESULTS DETECTED\n{search_results}\n\n{current_context.get('context_text', '')}"
    current_context["has_context"] = True
    current_context["source_type"] = "web"
    
    return {
        "retrieved_context": current_context,
        "current_stage": "searching",
        "intent": "WEB_SEARCH" # Update intent so generator knows to use search prompt
    }
