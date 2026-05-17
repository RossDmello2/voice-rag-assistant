import asyncio
import json
import base64
import sys
import os
from pathlib import Path

# Add backend root to path to reach app module.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(BACKEND_ROOT))

from app.core.voice_graph import compiled_graph
from app.core.graph_state import VoiceAgentState

async def test_streaming_answer():
    print("--- Starting End-to-End Pipeline Test ---")
    
    # Mocking the state
    initial_state = {
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
        "language": "en",
        "collection": "voice_agent_migration",
        "tts_voice": "af_heart",
        "tts_speed": 1.0,
        "hardware": "gpu",
        "has_documents": False
    }
    
    config = {"configurable": {"thread_id": "test_thread"}}
    
    received_tokens = []
    has_audio = False
    
    print("Streaming events...")
    async for event in compiled_graph.astream(
        initial_state,
        config=config,
        stream_mode=["custom"]
    ):
        if isinstance(event, tuple):
            _, data = event
        else:
            data = event
            
        if "token" in data:
            token = data["token"]
            received_tokens.append(token)
            print(token, end="", flush=True)
            
        if "audio" in data:
            has_audio = True
            # Just print the length, don't flood console with base64
            print(f"\n[Audio Chunk Received: {len(data['audio'])} bytes]")
            
        if "stage" in data:
            print(f"\n[Stage: {data['stage']}]")

    print("\n\n--- Test Summary ---")
    print(f"Full Response: {''.join(received_tokens)}")
    print(f"Audio Generated: {has_audio}")
    
    if len(received_tokens) > 0 and has_audio:
        print("SUCCESS: Pipeline is answering properly with text and audio.")
    else:
        print("FAILURE: Pipeline failed to generate response or audio.")

if __name__ == "__main__":
    asyncio.run(test_streaming_answer())
