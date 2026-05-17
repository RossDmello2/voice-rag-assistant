"""
Synthesize speech node — Kokoro TTS streaming via speech_service.
Emits audio chunks as base64-encoded PCM via get_stream_writer().
"""

import base64
import logging
from langgraph.config import get_stream_writer

from app.services.speech_service import speech_service
from app.core.graph_state import VoiceAgentState

logger = logging.getLogger(__name__)


async def synthesize_speech_node(state: VoiceAgentState) -> dict:
    """
    Synthesize speech from the clean response text using Kokoro TTS.
    Streams int16 PCM audio chunks at 24kHz as base64-encoded SSE events.
    """
    writer = get_stream_writer()
    writer({"stage": "speaking"})

    clean_response = state.get("clean_response", "")
    if not clean_response:
        writer({"audio_done": True})
        return {"current_stage": "speaking"}

    tts_voice = state.get("tts_voice", "af_heart")
    tts_speed = state.get("tts_speed", 1.0)
    hardware = state.get("hardware", "gpu")

    # Stream audio chunks from Kokoro
    chunk_count = 0
    try:
        async for pcm_bytes in speech_service.synthesize_stream(
            clean_response, 
            voice=tts_voice, 
            speed=tts_speed,
            hardware=hardware
        ):

            # Encode PCM bytes as base64 for SSE transport
            audio_b64 = base64.b64encode(pcm_bytes).decode("ascii")
            writer({"audio": audio_b64})
            chunk_count += 1
    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")

    writer({"audio_done": True})
    logger.info(f"TTS synthesized {chunk_count} chunks")

    return {"current_stage": "speaking"}