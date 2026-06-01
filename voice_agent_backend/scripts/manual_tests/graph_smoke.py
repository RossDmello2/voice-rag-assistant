import asyncio
import sys
from pathlib import Path

# Ensure app is in path
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

async def main():
    try:
        from app.core.voice_graph import get_compiled_graph

        graph = get_compiled_graph()
        print("Graph compiled successfully!")
        structure = graph.get_graph()
        print(f"Nodes: {list(structure.nodes.keys())}")
        
    except Exception as e:
        print(f"Error compiling graph: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
