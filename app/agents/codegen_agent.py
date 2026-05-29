import json
import logging
from anthropic import Anthropic
from app.core.config import get_settings
from app.models.workflow_models import SDLCOSState

logger = logging.getLogger(__name__)
settings = get_settings()
client = Anthropic(api_key=settings.anthropic_api_key)

CODEGEN_SYSTEM_PROMPT = """You are the Code Generation Agent inside SDLCOS, an AI-native SDLC orchestration platform.

Your role: Receive the architecture plan and describe the implementation plan for core components.

You must respond ONLY with a valid JSON object — no markdown, no explanation, no preamble.

CRITICAL JSON RULES:
- All string values must be short and on a single line
- No newlines inside string values
- No quotes inside string values
- No actual code inside string values — describe what the code does instead

JSON schema:
{
  "files_generated": ["app/models/user.py", "app/services/auth_service.py", "app/api/routes/auth.py"],
  "code_blocks": [
    {
      "filename": "app/models/user.py",
      "language": "python",
      "code": "SQLAlchemy User model with id, email, hashed_password, role, and created_at fields"
    },
    {
      "filename": "app/services/auth_service.py",
      "language": "python",
      "code": "AuthService class with login, logout, refresh_token, and verify_token methods using JWT"
    }
  ],
  "implementation_notes": ["Passwords hashed with bcrypt before storage", "JWT tokens expire in 15 minutes"],
  "next_steps": ["Add rate limiting to auth endpoints", "Set up refresh token rotation policy"]
}

Keep every string value short and clean — describe code intent, do not write actual code.
"""


def codegen_agent(state: SDLCOSState) -> SDLCOSState:
    logger.info("[CodegenAgent] Starting code generation")
    logs = state.get("agent_logs", [])
    errors = state.get("errors", [])

    if not state.get("architect_output"):
        error_msg = "[CodegenAgent] SKIPPED — no architect output available"
        errors.append(error_msg)
        return {**state, "errors": errors, "agent_logs": logs}

    planner_context = json.dumps(state.get("planner_output", {}), indent=2)
    architect_context = json.dumps(state["architect_output"], indent=2)

    try:
        response = client.messages.create(
            model=settings.model_name,
            max_tokens=2048,
            system=CODEGEN_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Feature Request:\n{state['feature_request']}\n\n"
                        f"Engineering Plan:\n{planner_context}\n\n"
                        f"Architecture Design:\n{architect_context}\n\n"
                        "Generate the core implementation files."
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

        codegen_output = json.loads(raw)
        logs.append("[CodegenAgent] ✓ Completed successfully")
        logger.info("[CodegenAgent] Completed successfully")

        return {
            **state,
            "codegen_output": codegen_output,
            "agent_logs": logs,
            "errors": errors,
        }

    except Exception as e:
        error_msg = f"[CodegenAgent] ERROR: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
        return {**state, "errors": errors, "agent_logs": logs}
