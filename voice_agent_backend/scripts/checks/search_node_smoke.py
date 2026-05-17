import asyncio
import logging
from app.core.nodes.search_web import search_web_node
from app.core.graph_state import VoiceAgentState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search():
    print("\n" + "="*50)
    print("TESTING WEB SEARCH NODE")
    print("="*50)
    
    state: VoiceAgentState = {
        "english_query": "What is the current price of Bitcoin?",
        "retrieved_context": {"has_context": False, "context_text": "", "sources": []}
    }
    
    print(f"Query: {state['english_query']}")
    print("Searching...")
    
    result = await search_web_node(state)
    
    context = result.get("retrieved_context", {})
    text = context.get("context_text", "")
    
    if "WEB SEARCH RESULTS:" in text:
        print("SUCCESS: Found search results!")
        print("-" * 30)
        print(text[:500] + "...")
    else:
        print("FAILED: No search results found in context.")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_search())
