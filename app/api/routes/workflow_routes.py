from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.workflows.sdlc_graph import run_sdlcos_pipeline
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workflow", tags=["workflow"])


class WorkflowRequest(BaseModel):
    feature_request: str


class WorkflowResponse(BaseModel):
    run_id: str
    feature_request: str
    planner_output: dict | None
    architect_output: dict | None
    codegen_output: dict | None
    agent_logs: list[str]
    errors: list[str]
    status: str


@router.post("/run", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest):
    if not request.feature_request.strip():
        raise HTTPException(status_code=400, detail="feature_request cannot be empty")

    try:
        result = run_sdlcos_pipeline(request.feature_request)
        status = "completed" if not result.get("errors") else "completed_with_errors"

        return WorkflowResponse(
            run_id=result.get("run_id", "unknown"),
            feature_request=result["feature_request"],
            planner_output=result.get("planner_output"),
            architect_output=result.get("architect_output"),
            codegen_output=result.get("codegen_output"),
            agent_logs=result.get("agent_logs", []),
            errors=result.get("errors", []),
            status=status,
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
