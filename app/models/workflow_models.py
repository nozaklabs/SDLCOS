from typing import Optional, List
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ── Structured outputs per agent ──────────────────────────────────────────────

class EngineeringTask(BaseModel):
    id: str
    title: str
    description: str
    phase: str
    dependencies: List[str] = []
    estimated_complexity: str  # low | medium | high


class PlannerOutput(BaseModel):
    summary: str
    tasks: List[EngineeringTask]
    phases: List[str]
    total_estimated_effort: str
    assumptions: List[str]


class ArchitectOutput(BaseModel):
    architecture_summary: str
    tech_stack: List[str]
    folder_structure: str
    api_contracts: List[str]
    database_schema: Optional[str]
    service_boundaries: List[str]
    key_decisions: List[str]


class CodegenOutput(BaseModel):
    files_generated: List[str]
    code_blocks: List[dict]   # {"filename": str, "language": str, "code": str}
    implementation_notes: List[str]
    next_steps: List[str]


# ── LangGraph shared state ─────────────────────────────────────────────────────

class SDLCOSState(TypedDict):
    # Input
    feature_request: str

    # Agent outputs (populated as graph runs)
    planner_output: Optional[dict]
    architect_output: Optional[dict]
    codegen_output: Optional[dict]

    # Metadata
    errors: List[str]
    agent_logs: List[str]
    run_id: str
