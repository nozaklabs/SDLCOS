import streamlit as st
import anthropic
import json
import os
import time
import uuid

st.set_page_config(page_title="SDLCOS", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #0a0a0f; color: #e2e8f0; }
.main-header { text-align: center; padding: 2.5rem 0 1rem 0; }
.main-header h1 { font-size: 3.2rem; font-weight: 700; letter-spacing: -0.04em; background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 50%, #00d4ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; }
.main-header .tagline { color: #64748b; font-size: 0.95rem; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 0.5rem; font-weight: 500; }
.agent-card { background: #111118; border: 1px solid #1e1e2e; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; position: relative; overflow: hidden; }
.agent-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #00d4ff, #7c3aed); }
.agent-badge { background: #1e1e2e; border: 1px solid #2d2d4e; border-radius: 6px; padding: 0.25rem 0.6rem; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; color: #00d4ff; letter-spacing: 0.1em; text-transform: uppercase; }
.pipeline-banner { background: linear-gradient(135deg, #0f0f1a 0%, #111118 100%); border: 1px solid #1e1e2e; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; }
.metric-chip { background: #0a0a0f; border: 1px solid #1e1e2e; border-radius: 8px; padding: 0.5rem 1rem; text-align: center; min-width: 100px; display: inline-block; margin: 0.25rem; }
.metric-chip .value { font-size: 1.4rem; font-weight: 700; color: #00d4ff; font-family: 'JetBrains Mono', monospace; }
.metric-chip .label { font-size: 0.65rem; color: #475569; text-transform: uppercase; letter-spacing: 0.1em; }
.code-block { background: #0d0d14; border: 1px solid #1e1e2e; border-radius: 8px; padding: 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #a5b4fc; white-space: pre-wrap; overflow-x: auto; max-height: 300px; overflow-y: auto; line-height: 1.6; }
.task-row { display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; background: #0d0d14; border: 1px solid #1a1a2e; }
.task-id { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #7c3aed; min-width: 52px; margin-top: 2px; }
.task-complexity { font-size: 0.65rem; padding: 0.15rem 0.5rem; border-radius: 4px; margin-left: auto; white-space: nowrap; margin-top: 2px; }
.complexity-low { background: #064e3b; color: #6ee7b7; }
.complexity-medium { background: #78350f; color: #fcd34d; }
.complexity-high { background: #7f1d1d; color: #fca5a5; }
.log-line { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #475569; padding: 0.2rem 0; border-bottom: 1px solid #111118; }
.log-line.success { color: #10b981; }
.log-line.error { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

PLANNER_PROMPT = """You are the Planner Agent inside SDLCOS, an AI-native SDLC orchestration platform.
Analyze a feature request and produce a structured engineering breakdown.
Respond ONLY with valid JSON — no markdown, no preamble.
JSON schema:
{
  "summary": "brief summary",
  "tasks": [{"id": "T-001", "title": "...", "description": "...", "phase": "...", "dependencies": [], "estimated_complexity": "low|medium|high"}],
  "phases": ["Phase 1: ...", "Phase 2: ..."],
  "total_estimated_effort": "e.g. 3-5 days",
  "assumptions": ["assumption 1"]
}
Rules: Break into 4-8 tasks. Be specific. Identify phases and dependencies."""

ARCHITECT_PROMPT = """You are the Architect Agent inside SDLCOS, an AI-native SDLC orchestration platform.
Receive the engineering plan and produce a concrete system architecture.
Respond ONLY with valid JSON — no markdown, no preamble.
CRITICAL: All string values must be short and on a single line. No newlines or quotes inside strings.
JSON schema:
{
  "architecture_summary": "one line summary",
  "tech_stack": ["Python", "FastAPI"],
  "folder_structure": "app/ agents/ workflows/ api/ models/ core/ services/",
  "api_contracts": ["POST /auth/login returns access_token and refresh_token"],
  "database_schema": "Users: id email hashed_password role created_at",
  "service_boundaries": ["AuthService", "TokenService"],
  "key_decisions": ["Used JWT for stateless auth"]
}"""

CODEGEN_PROMPT = """You are the Code Generation Agent inside SDLCOS, an AI-native SDLC orchestration platform.
Receive the architecture plan and describe the implementation.
Respond ONLY with valid JSON — no markdown, no preamble.
CRITICAL: All string values must be short and on a single line. No actual code — describe what each file does.
JSON schema:
{
  "files_generated": ["app/models/user.py", "app/services/auth_service.py"],
  "code_blocks": [{"filename": "app/models/user.py", "language": "python", "code": "SQLAlchemy User model with id, email, hashed_password, role, created_at fields"}],
  "implementation_notes": ["Passwords hashed with bcrypt", "JWT tokens expire in 15 minutes"],
  "next_steps": ["Add rate limiting", "Set up token rotation"]
}"""


def parse_json(raw):
    raw = raw.strip()
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            if part.startswith("json"):
                raw = part[4:].strip()
                break
            elif "{" in part:
                raw = part.strip()
                break
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    return json.loads(raw)


def run_agent(client, system_prompt, user_message):
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return parse_json(response.content[0].text)


def run_pipeline(api_key, feature_request):
    client = anthropic.Anthropic(api_key=api_key)
    run_id = str(uuid.uuid4())[:8]
    logs = [f"[SDLCOS] Pipeline started — run_id: {run_id}"]
    errors = []
    planner_output = architect_output = codegen_output = None

    try:
        planner_output = run_agent(client, PLANNER_PROMPT, f"Feature Request:\n\n{feature_request}")
        logs.append("[PlannerAgent] ✓ Completed successfully")
    except Exception as e:
        errors.append(f"[PlannerAgent] ERROR: {str(e)}")

    if planner_output:
        try:
            architect_output = run_agent(client, ARCHITECT_PROMPT, f"Feature Request:\n{feature_request}\n\nEngineering Plan:\n{json.dumps(planner_output, indent=2)}")
            logs.append("[ArchitectAgent] ✓ Completed successfully")
        except Exception as e:
            errors.append(f"[ArchitectAgent] ERROR: {str(e)}")
    else:
        errors.append("[ArchitectAgent] SKIPPED — no planner output")

    if architect_output:
        try:
            codegen_output = run_agent(client, CODEGEN_PROMPT, f"Feature Request:\n{feature_request}\n\nArchitecture:\n{json.dumps(architect_output, indent=2)}")
            logs.append("[CodegenAgent] ✓ Completed successfully")
        except Exception as e:
            errors.append(f"[CodegenAgent] ERROR: {str(e)}")
    else:
        errors.append("[CodegenAgent] SKIPPED — no architect output")

    return {"run_id": run_id, "planner_output": planner_output, "architect_output": architect_output, "codegen_output": codegen_output, "agent_logs": logs, "errors": errors}


st.markdown('<div class="main-header"><h1>⚡ SDLCOS</h1><p class="tagline">AI-Native Software Development Lifecycle Orchestration System</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    st.markdown("**SDLCOS v0.1.0**")
    st.markdown("NozakLabs · AI-Native Engineering")

try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    st.error("API key not configured. Please add ANTHROPIC_API_KEY to Streamlit secrets.")
    st.stop()

st.markdown("##### Try an example or write your own:")
examples = [
    "Build JWT authentication for a FastAPI app with refresh tokens and role-based access control",
    "Build a real-time notification system using WebSockets and Redis pub/sub",
    "Create a multi-tenant SaaS billing system with Stripe integration and usage metering",
]
cols = st.columns(3)
for i, (col, ex) in enumerate(zip(cols, examples)):
    with col:
        if st.button(f"📋 Example {i+1}", key=f"ex_{i}", use_container_width=True):
            st.session_state["feature_input"] = ex

st.markdown("<br>", unsafe_allow_html=True)
feature_request = st.text_area("Feature Request", value=st.session_state.get("feature_input", ""), placeholder="Describe the feature you want SDLCOS to engineer...", height=120, label_visibility="collapsed")
run_btn = st.button("⚡ RUN PIPELINE", use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

if run_btn and feature_request.strip():
    start_time = time.time()
    status = st.empty()
    status.markdown('<div class="pipeline-banner"><span style="color:#f59e0b;">⟳ Pipeline running — 3 agents initializing...</span></div>', unsafe_allow_html=True)
    data = run_pipeline(api_key, feature_request)
    elapsed = round(time.time() - start_time, 1)
    status.empty()

    error_count = len(data.get("errors", []))
    agents_done = sum([1 for k in ["planner_output", "architect_output", "codegen_output"] if data.get(k)])

    st.markdown(f'<div class="pipeline-banner"><span style="color:#10b981;font-weight:600;">● Pipeline Complete</span> &nbsp;|&nbsp;<div style="display:inline-flex;gap:1rem;flex-wrap:wrap;margin-top:0.5rem;"><div class="metric-chip"><div class="value">{elapsed}s</div><div class="label">Duration</div></div><div class="metric-chip"><div class="value">{agents_done}/3</div><div class="label">Agents</div></div><div class="metric-chip"><div class="value">{data.get("run_id","—")}</div><div class="label">Run ID</div></div><div class="metric-chip"><div class="value" style="color:{"#ef4444" if error_count else "#10b981"}">{error_count}</div><div class="label">Errors</div></div></div></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🧠 Planner Agent", "🏗️ Architect Agent", "⚙️ Codegen Agent", "📋 Pipeline Logs"])

    with tab1:
        planner = data.get("planner_output")
        if planner:
            st.markdown(f'<div class="agent-card"><div><span class="agent-badge">agent-01</span> <strong>Planner Agent</strong></div><p style="color:#94a3b8;margin-top:0.75rem;">{planner.get("summary","")}</p></div>', unsafe_allow_html=True)
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown("**Engineering Tasks**")
                for task in planner.get("tasks", []):
                    c = task.get("estimated_complexity", "medium")
                    st.markdown(f'<div class="task-row"><span class="task-id">{task.get("id","")}</span><div style="flex:1;"><div style="font-weight:600;color:#f1f5f9;font-size:0.9rem;">{task.get("title","")}</div><div style="color:#64748b;font-size:0.8rem;margin-top:2px;">{task.get("description","")}</div></div><span class="task-complexity complexity-{c}">{c}</span></div>', unsafe_allow_html=True)
            with col_b:
                st.markdown("**Phases**")
                for phase in planner.get("phases", []):
                    st.markdown(f"<div style='color:#94a3b8;font-size:0.85rem;padding:0.4rem 0;border-bottom:1px solid #1e1e2e;'>→ {phase}</div>", unsafe_allow_html=True)
                st.markdown(f"<br><div style='color:#00d4ff;font-size:1.1rem;font-weight:600;font-family:JetBrains Mono,monospace;'>{planner.get('total_estimated_effort','—')}</div>", unsafe_allow_html=True)
        else:
            st.error("Planner agent did not produce output.")

    with tab2:
        arch = data.get("architect_output")
        if arch:
            st.markdown(f'<div class="agent-card"><div><span class="agent-badge">agent-02</span> <strong>Architect Agent</strong></div><p style="color:#94a3b8;margin-top:0.75rem;">{arch.get("architecture_summary","")}</p></div>', unsafe_allow_html=True)
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.markdown("**Folder Structure**")
                st.markdown(f'<div class="code-block">{arch.get("folder_structure","")}</div>', unsafe_allow_html=True)
                st.markdown("<br>**Tech Stack**", unsafe_allow_html=True)
                stack_html = "".join([f'<span style="background:#1e1e2e;border:1px solid #2d2d4e;border-radius:4px;padding:0.2rem 0.6rem;font-size:0.78rem;color:#a5b4fc;margin:0.2rem;display:inline-block;">{t}</span>' for t in arch.get("tech_stack", [])])
                st.markdown(stack_html, unsafe_allow_html=True)
            with col_b:
                st.markdown("**API Contracts**")
                for contract in arch.get("api_contracts", []):
                    st.markdown(f'<div class="code-block" style="margin-bottom:0.5rem;padding:0.6rem 1rem;">{contract}</div>', unsafe_allow_html=True)
                st.markdown("<br>**Service Boundaries**", unsafe_allow_html=True)
                for svc in arch.get("service_boundaries", []):
                    st.markdown(f"<div style='color:#7c3aed;font-family:JetBrains Mono,monospace;font-size:0.82rem;padding:0.3rem 0;border-bottom:1px solid #1a1a2e;'>◆ {svc}</div>", unsafe_allow_html=True)
        else:
            st.error("Architect agent did not produce output.")

    with tab3:
        codegen = data.get("codegen_output")
        if codegen:
            st.markdown(f'<div class="agent-card"><div><span class="agent-badge">agent-03</span> <strong>Code Generation Agent</strong></div><p style="color:#94a3b8;margin-top:0.75rem;">{len(codegen.get("files_generated",[]))} files generated</p></div>', unsafe_allow_html=True)
            files_html = "".join([f'<span style="background:#0d0d14;border:1px solid #1e1e2e;border-radius:4px;padding:0.2rem 0.7rem;font-size:0.78rem;color:#00d4ff;font-family:JetBrains Mono,monospace;margin:0.2rem;display:inline-block;">📄 {f}</span>' for f in codegen.get("files_generated", [])])
            st.markdown(files_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            for block in codegen.get("code_blocks", []):
                with st.expander(f"📄 {block.get('filename','file')}"):
                    st.code(block.get("code",""), language=block.get("language","python"))
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.markdown("**Implementation Notes**")
                for note in codegen.get("implementation_notes", []):
                    st.markdown(f"<div style='color:#94a3b8;font-size:0.85rem;padding:0.35rem 0;border-bottom:1px solid #111118;'>→ {note}</div>", unsafe_allow_html=True)
            with col_b:
                st.markdown("**Next Steps**")
                for step in codegen.get("next_steps", []):
                    st.markdown(f"<div style='color:#7c3aed;font-size:0.85rem;padding:0.35rem 0;border-bottom:1px solid #111118;'>◆ {step}</div>", unsafe_allow_html=True)
        else:
            st.error("Codegen agent did not produce output.")

    with tab4:
        st.markdown("**Pipeline Execution Log**")
        for log in data.get("agent_logs", []):
            css = "success" if "✓" in log else ("error" if "ERROR" in log else "")
            st.markdown(f'<div class="log-line {css}">{log}</div>', unsafe_allow_html=True)
        if data.get("errors"):
            st.markdown("<br>**Errors**", unsafe_allow_html=True)
            for err in data.get("errors", []):
                st.markdown(f'<div class="log-line error">✗ {err}</div>', unsafe_allow_html=True)

elif run_btn:
    st.warning("Please enter a feature request.")

st.markdown("<br><br><div style='text-align:center;color:#1e1e2e;font-size:0.75rem;font-family:JetBrains Mono,monospace;'>SDLCOS v0.1.0 · NozakLabs · AI-Native Engineering Infrastructure</div>", unsafe_allow_html=True)
