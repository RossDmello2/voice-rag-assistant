import asyncio
import sys
from pathlib import Path

# Ensure app is in path
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

async def main():
    try:
        from app.core.voice_graph import get_voice_graph

        graph = get_voice_graph()
        print("Graph compiled successfully!")
        
        # We can also check the graph structure
        nodes = graph.nodes
        print(f"Nodes: {list(nodes.keys())}")
        
    except Exception as e:
        print(f"Error compiling graph: {e}")

if __name__ == "__main__":
    asyncio.run(main())
