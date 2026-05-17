"""
ULTRATHINK Critic Agent: Performs System 2 (Chain of Thought) reasoning.
It evaluates complex queries, formulates a logical answer based on context,
and saves the reasoning to the scratchpad before final TTS generation.
"""

import logging
from langgraph.config import get_stream_writer
from app.core.graph_state import VoiceAgentState
from app.services.groq_service import chat_complete
from app.core.config import settings

logger = logging.getLogger(__name__)

async def ultrathink_critic_node(state: VoiceAgentState) -> dict:
    """
    Executes a multi-step reasoning prompt using Groq (non-streaming).
    Populates the 'scratchpad' and 'ultrathink_logs' for the generate node to use.
    """
    writer = get_stream_writer()
    writer({"stage": "ultrathinking"})

    query = state.get("english_query", "")
    context_data = state.get("retrieved_context", {})
    context_text = context_data.get("text", "")
    
    logger.info("ULTRATHINK process initiated. Simulating deep thought...")

    system_prompt = (
        "You are the internal 'ULTRATHINK' reasoning engine for an advanced Voice Agent.\n"
        "Your goal is to carefully analyze the user's query and any provided document context.\n"
        "Think step-by-step. Do not format your response for speech, format it as a logical, factual breakdown.\n"
        "You MUST output your thought process first, followed by a 'FINAL DRAFT' section.\n"
        "The FINAL DRAFT will be used by the Speech Agent to synthesize the spoken response.\n"
        "Context provided:\n"
        f"{context_text}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    try:
        # Use a high-capability model for reasoning if available, otherwise fallback
        # In a real setup, you might hardcode a specific reasoning model like llama3-70b-8192
        model_to_use = "llama-3.3-70b-versatile"
        
        response_text = await chat_complete(
            messages=messages,
            model=model_to_use,
            temperature=0.2, # Low temp for logical reasoning
            max_tokens=2048,
            stream=False # Wait for the full thought process
        )

        logger.info("ULTRATHINK process completed.")
        
        return {
            "current_stage": "ultrathinking",
            "ultrathink_logs": [response_text],
            "scratchpad": [{"role": "system", "content": "ULTRATHINK Reasoning Output:\n" + response_text}]
        }

    except Exception as e:
        logger.error(f"ULTRATHINK failed: {e}")
        return {
            "current_stage": "ultrathinking",
            "ultrathink_logs": [f"Error during reasoning: {str(e)}"],
        }
