import json
import logging
from anthropic import Anthropic
from app.core.config import get_settings
from app.models.workflow_models import SDLCOSState

logger = logging.getLogger(__name__)
settings = get_settings()
client = Anthropic(api_key=settings.anthropic_api_key)

ARCHITECT_SYSTEM_PROMPT = """You are the Architect Agent inside SDLCOS, an AI-native SDLC orchestration platform.

Your role: Receive the engineering plan and produce a concrete system architecture.

You must respond ONLY with a valid JSON object — no markdown, no explanation, no preamble.

CRITICAL JSON RULES:
- All string values must be on a single line
- No newlines inside string values — use the literal text \\n only if needed
- No unescaped quotes inside string values
- No code snippets inside string values
- Keep all values short and simple

JSON schema:
{
  "architecture_summary": "one line summary of the architecture",
  "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
  "folder_structure": "app/ agents/ workflows/ api/ models/ core/",
  "api_contracts": ["POST /auth/login returns token and refresh_token", "POST /auth/refresh returns new token"],
  "database_schema": "Users: id email hashed_password role created_at. RefreshTokens: id user_id token expires_at",
  "service_boundaries": ["AuthService", "TokenService", "UserService"],
  "key_decisions": ["Used JWT for stateless auth", "Refresh tokens stored in DB for revocation"]
}

Keep every string value short — one line, no special characters, no code.
"""


def architect_agent(state: SDLCOSState) -> SDLCOSState:
    logger.info("[ArchitectAgent] Starting architecture design")
    logs = state.get("agent_logs", [])
    errors = state.get("errors", [])

    if not state.get("planner_output"):
        error_msg = "[ArchitectAgent] SKIPPED — no planner output available"
        errors.append(error_msg)
        return {**state, "errors": errors, "agent_logs": logs}

    planner_context = json.dumps(state["planner_output"], indent=2)

    try:
        response = client.messages.create(
            model=settings.model_name,
            max_tokens=4096,
            system=ARCHITECT_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Feature Request:\n{state['feature_request']}\n\n"
                        f"Engineering Plan from Planner Agent:\n{planner_context}"
                    )
                }
            ]
        )

        raw = response.content[0].text.strip()
        # Strip markdown fences robustly
        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                if part.startswith("json"):
                    raw = part[4:].strip()
                    break
                elif "{" in part:
                    raw = part.strip()
                    break
        # Extract JSON object directly
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]
        raw = raw.strip()

        architect_output = json.loads(raw)
        logs.append("[ArchitectAgent] ✓ Completed successfully")
        logger.info("[ArchitectAgent] Completed successfully")

        return {
            **state,
            "architect_output": architect_output,
            "agent_logs": logs,
            "errors": errors,
        }

    except Exception as e:
        error_msg = f"[ArchitectAgent] ERROR: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
        return {**state, "errors": errors, "agent_logs": logs}
