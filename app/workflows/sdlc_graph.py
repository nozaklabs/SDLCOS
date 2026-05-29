import uuid
import logging
from langgraph.graph import StateGraph, END
from app.models.workflow_models import SDLCOSState
from app.agents.planner_agent import planner_agent
from app.agents.architect_agent import architect_agent
from app.agents.codegen_agent import codegen_agent

logger = logging.getLogger(__name__)


def build_sdlcos_graph() -> StateGraph:
    """
    Constructs the SDLCOS LangGraph pipeline.

    Flow: Planner → Architect → Codegen → END

    Each node receives the full shared state and returns
    an updated state dict. LangGraph merges the updates.
    """
    graph = StateGraph(SDLCOSState)

    # Register agent nodes
    graph.add_node("planner", planner_agent)
    graph.add_node("architect", architect_agent)
    graph.add_node("codegen", codegen_agent)

    # Wire the pipeline
    graph.set_entry_point("planner")
    graph.add_edge("planner", "architect")
    graph.add_edge("architect", "codegen")
    graph.add_edge("codegen", END)

    return graph.compile()


# Compiled graph — singleton for the app lifetime
sdlcos_graph = build_sdlcos_graph()


def run_sdlcos_pipeline(feature_request: str) -> SDLCOSState:
    """
    Entry point for running the full SDLCOS pipeline.

    Args:
        feature_request: The raw engineering request from the user.

    Returns:
        Final SDLCOSState with all agent outputs populated.
    """
    run_id = str(uuid.uuid4())[:8]
    logger.info(f"[SDLCOS] Starting pipeline run {run_id}")

    initial_state: SDLCOSState = {
        "feature_request": feature_request,
        "planner_output": None,
        "architect_output": None,
        "codegen_output": None,
        "errors": [],
        "agent_logs": [f"[SDLCOS] Pipeline started — run_id: {run_id}"],
        "run_id": run_id,
    }

    result = sdlcos_graph.invoke(initial_state)
    logger.info(f"[SDLCOS] Pipeline run {run_id} complete")
    return result
