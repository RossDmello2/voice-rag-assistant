"""
Check interrupt node — uses LangGraph interrupt() for human-in-the-loop.
CRITICAL: interrupt() must NEVER be wrapped in try/except (per LangGraph docs).
"""

import logging
from langgraph.types import interrupt
from langgraph.config import get_stream_writer

from app.core.graph_state import VoiceAgentState

logger = logging.getLogger(__name__)


def check_interrupt_node(state: VoiceAgentState) -> dict:
    """
    Check if the user has requested an interruption.
    
    If interrupt_flag is True in state, we call interrupt() which pauses
    the graph execution until the frontend sends a resume command via
    /chat/interrupt/{thread_id}.
    
    CRITICAL: interrupt() must NEVER be wrapped in try/except.
    """
    writer = get_stream_writer()
    
    if state.get("interrupt_flag", False):
        # Emit interrupt event so frontend knows
        writer({"stage": "interrupted"})
        
        # This pauses the graph. The /chat/interrupt endpoint will
        # resume with Command(resume=<value>).
        # The resumed value replaces the interrupt return.
        resumed_query = interrupt("User requested interruption")
        
        # After resume, update state with new query
        # CRITICAL: Set current_query so translate_input processes the NEW query
        return {
            "interrupt_flag": False,
            "interrupted_query": resumed_query or "",
            "current_query": resumed_query or state.get("current_query", ""),
            "current_stage": "interrupted",
        }
    
    return {"current_stage": "checking"}


def route_after_interrupt(state: VoiceAgentState) -> str:
    """Route after interrupt check: if interrupted with new query, go back to translate."""
    if state.get("interrupted_query"):
        return "translate_input"
    return "classify_intent"