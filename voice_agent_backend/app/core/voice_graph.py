"""
LangGraph StateGraph assembly for the voice agent pipeline.

Graph topology:
  START -> translate_input -> check_interrupt -> classify_intent
    classify_intent -> "retrieve" -> retrieve_context -> check_confidence
    classify_intent -> "search" -> search_web -> generate_response
    classify_intent -> "early_exit" -> handle_early_exit
    check_confidence -> "generate" -> generate_response
    check_confidence -> "search" -> search_web
    check_confidence -> "early_exit" -> handle_early_exit
    generate_response -> update_context -> END
    handle_early_exit -> update_context -> END
"""

import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.graph_state import VoiceAgentState
from app.core.nodes.translate_input import translate_input_node
from app.core.nodes.check_interrupt import check_interrupt_node, route_after_interrupt
from app.core.agents.supervisor import supervisor_node, route_after_supervisor
from app.core.agents.ultrathink_critic import ultrathink_critic_node
from app.core.nodes.retrieve_context import retrieve_context_node
from app.core.nodes.check_confidence import check_confidence_node, route_after_confidence
from app.core.nodes.generate_response import generate_response_node
from app.core.nodes.update_context import update_context_node
from app.core.nodes.handle_early_exit import handle_early_exit_node
from app.core.nodes.search_web import search_web_node

logger = logging.getLogger(__name__)


def build_voice_graph() -> StateGraph:
    """Build and compile the voice agent LangGraph pipeline."""

    graph = StateGraph(VoiceAgentState)

    # -- Add nodes --------------------------------------------------
    graph.add_node("translate_input", translate_input_node)
    graph.add_node("check_interrupt", check_interrupt_node)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("ultrathink_critic", ultrathink_critic_node)
    graph.add_node("retrieve_context", retrieve_context_node)
    graph.add_node("check_confidence", check_confidence_node)
    graph.add_node("generate_response", generate_response_node)
    graph.add_node("update_context", update_context_node)
    graph.add_node("handle_early_exit", handle_early_exit_node)
    graph.add_node("search_web", search_web_node)

    # -- Set entry point --------------------------------------------
    graph.set_entry_point("translate_input")

    # -- Add edges --------------------------------------------------
    # translate_input -> check_interrupt
    graph.add_edge("translate_input", "check_interrupt")

    # check_interrupt -> Fork to Parallel Paths
    # check_interrupt -> supervisor
    graph.add_conditional_edges(
        "check_interrupt",
        route_after_interrupt,
        {
            "translate_input": "translate_input",
            "classify_intent": "supervisor",  # map old label to new node for now
        },
    )

    # supervisor -> retrieve_context OR ultrathink_critic OR handle_early_exit
    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "retrieve_context": "retrieve_context",
            "search_web": "search_web",
            "ultrathink_critic": "ultrathink_critic",
            "generate_response": "generate_response",
            "handle_early_exit": "handle_early_exit",
        },
    )

    # retrieve_context -> check_confidence
    graph.add_edge("retrieve_context", "check_confidence")

    # check_confidence -> generate_response OR handle_early_exit OR ultrathink_critic
    graph.add_conditional_edges(
        "check_confidence",
        route_after_confidence,
        {
            "generate_response": "generate_response",
            "search_web": "search_web",
            "ultrathink_critic": "ultrathink_critic",
            "handle_early_exit": "handle_early_exit",
        },
    )

    # search_web -> generate_response
    graph.add_edge("search_web", "generate_response")

    # ultrathink_critic -> generate_response
    graph.add_edge("ultrathink_critic", "generate_response")

    # generate_response -> update_context (Immediate handover)
    # Synthesis is handled internally by generate_response_node for low latency.
    graph.add_edge("generate_response", "update_context")

    # handle_early_exit -> update_context
    graph.add_edge("handle_early_exit", "update_context")

    # update_context -> END
    graph.add_edge("update_context", END)

    # -- Compile with MemorySaver checkpointer ----------------------
    checkpointer = MemorySaver()

    compiled = graph.compile(
        checkpointer=checkpointer,
    )

    logger.info("Voice agent graph compiled successfully.")
    return compiled


# -- Compiled graph singleton (lazy) ---------------------------------
_compiled_graph = None


def get_compiled_graph():
    """Lazy-init the compiled graph. Safe to call after settings are loaded."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_voice_graph()
    return _compiled_graph


class _GraphProxy:
    """Lazy proxy that delegates all attribute access to the real compiled graph."""
    def __getattr__(self, name):
        return getattr(get_compiled_graph(), name)
    
    def __call__(self, *args, **kwargs):
        return get_compiled_graph()(*args, **kwargs)


compiled_graph = _GraphProxy()
