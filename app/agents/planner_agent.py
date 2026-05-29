import json
import logging
from anthropic import Anthropic
from app.core.config import get_settings
from app.models.workflow_models import SDLCOSState

logger = logging.getLogger(__name__)
settings = get_settings()
client = Anthropic(api_key=settings.anthropic_api_key)

PLANNER_SYSTEM_PROMPT = """You are the Planner Agent inside SDLCOS, an AI-native SDLC orchestration platform.

Your role: Analyze a feature request and produce a structured engineering breakdown.

You must respond ONLY with a valid JSON object — no markdown, no explanation, no preamble.

JSON schema:
{
  "summary": "brief summary of what needs to be built",
  "tasks": [
    {
      "id": "T-001",
      "title": "task title",
      "description": "what needs to be done",
      "phase": "phase name",
      "dependencies": [],
      "estimated_complexity": "low | medium | high"
    }
  ],
  "phases": ["Phase 1: ...", "Phase 2: ..."],
  "total_estimated_effort": "e.g. 3-5 days",
  "assumptions": ["assumption 1", "assumption 2"]
}

Rules:
- Think like a senior engineering team lead
- Break features into 4-8 concrete engineering tasks
- Identify logical phases
- Be specific, not vague
- Anticipate integration concerns
"""


def planner_agent(state: SDLCOSState) -> SDLCOSState:
    logger.info("[PlannerAgent] Starting analysis")
    logs = state.get("agent_logs", [])
    errors = state.get("errors", [])

    try:
        response = client.messages.create(
            model=settings.model_name,
            max_tokens=settings.max_tokens,
            system=PLANNER_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Feature Request:\n\n{state['feature_request']}"
                }
            ]
        )

        raw = response.content[0].text.strip()
        # Strip markdown fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        planner_output = json.loads(raw)
        logs.append("[PlannerAgent] ✓ Completed successfully")
        logger.info("[PlannerAgent] Completed successfully")

        return {
            **state,
            "planner_output": planner_output,
            "agent_logs": logs,
            "errors": errors,
        }

    except Exception as e:
        error_msg = f"[PlannerAgent] ERROR: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
        return {**state, "errors": errors, "agent_logs": logs}
