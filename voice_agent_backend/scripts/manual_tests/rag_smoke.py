import asyncio
import logging
import os
import sys
from pathlib import Path

# Add backend to path - adjusting for the nested structure.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(BACKEND_ROOT))

from app.core.langchain_rag import retrieve_context
from app.core.config import settings

async def main():
    logging.basicConfig(level=logging.INFO)
    query = "for customer service do u have an emeial"
    collection = "agent_knowledge" # Assuming this is the default
    flags = {"isSummary": False, "isFollowUp": False}
    
    print(f"Testing Query: {query}")
    print("-" * 50)
    
    context = await retrieve_context(query, collection, flags)
    
    if context["has_context"]:
        print(f"Context Found (Score: {context['top_score']:.3f}):")
        print(context["context_text"])
        print("-" * 50)
        print(f"Sources: {context['sources']}")
    else:
        print("NO CONTEXT FOUND")

if __name__ == "__main__":
    asyncio.run(main())
