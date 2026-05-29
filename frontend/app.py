import streamlit as st
import requests
import json
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SDLCOS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

.stApp {
    background: #0a0a0f;
    color: #e2e8f0;
}

.main-header {
    text-align: center;
    padding: 2.5rem 0 1rem 0;
}

.main-header h1 {
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 50%, #00d4ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}

.main-header .tagline {
    color: #64748b;
    font-size: 0.95rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.5rem;
    font-weight: 500;
}

.agent-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}

.agent-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00d4ff, #7c3aed);
}

.agent-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.agent-badge {
    background: #1e1e2e;
    border: 1px solid #2d2d4e;
    border-radius: 6px;
    padding: 0.25rem 0.6rem;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    color: #00d4ff;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.agent-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #f1f5f9;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
}

.status-running { background: #f59e0b; animation: pulse 1s infinite; }
.status-done { background: #10b981; }
.status-error { background: #ef4444; }
.status-idle { background: #374151; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.pipeline-banner {
    background: linear-gradient(135deg, #0f0f1a 0%, #111118 100%);
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.metric-chip {
    background: #0a0a0f;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    text-align: center;
    min-width: 100px;
}

.metric-chip .value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #00d4ff;
    font-family: 'JetBrains Mono', monospace;
}

.metric-chip .label {
    font-size: 0.65rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.code-block {
    background: #0d0d14;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #a5b4fc;
    white-space: pre-wrap;
    overflow-x: auto;
    max-height: 400px;
    overflow-y: auto;
    line-height: 1.6;
}

.task-row {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    background: #0d0d14;
    border: 1px solid #1a1a2e;
}

.task-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #7c3aed;
    min-width: 52px;
    margin-top: 2px;
}

.task-complexity {
    font-size: 0.65rem;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    margin-left: auto;
    white-space: nowrap;
    margin-top: 2px;
}

.complexity-low { background: #064e3b; color: #6ee7b7; }
.complexity-medium { background: #78350f; color: #fcd34d; }
.complexity-high { background: #7f1d1d; color: #fca5a5; }

.log-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #475569;
    padding: 0.2rem 0;
    border-bottom: 1px solid #111118;
}

.log-line.success { color: #10b981; }
.log-line.error { color: #ef4444; }

div[data-testid="stTextArea"] textarea {
    background: #111118 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.95rem !important;
}

div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #00d4ff, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    transition: opacity 0.2s !important;
}
</style>
""", unsafe_allow_html=True)

API_BASE = "http://localhost:8000"

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>⚡ SDLCOS</h1>
    <p class="tagline">AI-Native Software Development Lifecycle Orchestration System</p>
</div>
""", unsafe_allow_html=True)

# ── Example requests ──────────────────────────────────────────────────────────
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

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
feature_request = st.text_area(
    "Feature Request",
    value=st.session_state.get("feature_input", ""),
    placeholder="Describe the feature you want SDLCOS to engineer...\n\nExample: Build JWT authentication for a FastAPI app with refresh tokens and role-based access control",
    height=120,
    label_visibility="collapsed",
)

run_btn = st.button("⚡ RUN PIPELINE", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Pipeline execution ────────────────────────────────────────────────────────
if run_btn and feature_request.strip():
    start_time = time.time()

    # Status placeholders
    status_area = st.empty()
    results_area = st.container()

    with status_area:
        st.markdown("""
        <div class="pipeline-banner">
            <span class="status-dot status-running"></span>
            <span style="color:#94a3b8; font-size:0.9rem;">Pipeline running — 3 agents initializing...</span>
        </div>
        """, unsafe_allow_html=True)

    try:
        response = requests.post(
            f"{API_BASE}/workflow/run",
            json={"feature_request": feature_request},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        elapsed = round(time.time() - start_time, 1)

        status_area.empty()

        # ── Pipeline summary banner ────────────────────────────────────────
        error_count = len(data.get("errors", []))
        agents_done = sum([
            1 for k in ["planner_output", "architect_output", "codegen_output"]
            if data.get(k)
        ])

        st.markdown(f"""
        <div class="pipeline-banner">
            <span class="status-dot status-done"></span>
            <span style="color:#10b981; font-weight:600; font-size:0.95rem;">Pipeline Complete</span>
            <span style="color:#374151; margin: 0 0.5rem;">|</span>
            <div style="display:flex; gap:1rem; flex-wrap:wrap;">
                <div class="metric-chip">
                    <div class="value">{elapsed}s</div>
                    <div class="label">Duration</div>
                </div>
                <div class="metric-chip">
                    <div class="value">{agents_done}/3</div>
                    <div class="label">Agents</div>
                </div>
                <div class="metric-chip">
                    <div class="value">{data.get("run_id", "—")}</div>
                    <div class="label">Run ID</div>
                </div>
                <div class="metric-chip">
                    <div class="value" style="color:{'#ef4444' if error_count else '#10b981'}">{error_count}</div>
                    <div class="label">Errors</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Agent output tabs ──────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs([
            "🧠 Planner Agent",
            "🏗️ Architect Agent",
            "⚙️ Codegen Agent",
            "📋 Pipeline Logs",
        ])

        # Planner
        with tab1:
            planner = data.get("planner_output")
            if planner:
                st.markdown(f"""
                <div class="agent-card">
                    <div class="agent-header">
                        <span class="agent-badge">agent-01</span>
                        <span class="agent-name">Planner Agent</span>
                        <span class="status-dot status-done" style="margin-left:auto;"></span>
                    </div>
                    <p style="color:#94a3b8; margin:0 0 1rem 0;">{planner.get("summary", "")}</p>
                </div>
                """, unsafe_allow_html=True)

                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown("**Engineering Tasks**")
                    for task in planner.get("tasks", []):
                        complexity = task.get("estimated_complexity", "medium")
                        st.markdown(f"""
                        <div class="task-row">
                            <span class="task-id">{task.get("id", "")}</span>
                            <div style="flex:1;">
                                <div style="font-weight:600; color:#f1f5f9; font-size:0.9rem;">{task.get("title", "")}</div>
                                <div style="color:#64748b; font-size:0.8rem; margin-top:2px;">{task.get("description", "")}</div>
                                <div style="color:#475569; font-size:0.72rem; margin-top:4px;">Phase: {task.get("phase", "")} · Deps: {", ".join(task.get("dependencies", [])) or "none"}</div>
                            </div>
                            <span class="task-complexity complexity-{complexity}">{complexity}</span>
                        </div>
                        """, unsafe_allow_html=True)

                with col_b:
                    st.markdown("**Phases**")
                    for phase in planner.get("phases", []):
                        st.markdown(f"<div style='color:#94a3b8; font-size:0.85rem; padding:0.4rem 0; border-bottom:1px solid #1e1e2e;'>→ {phase}</div>", unsafe_allow_html=True)

                    st.markdown("<br>**Effort Estimate**", unsafe_allow_html=True)
                    st.markdown(f"<div style='color:#00d4ff; font-size:1.1rem; font-weight:600; font-family:JetBrains Mono,monospace;'>{planner.get('total_estimated_effort', '—')}</div>", unsafe_allow_html=True)

                    if planner.get("assumptions"):
                        st.markdown("<br>**Assumptions**", unsafe_allow_html=True)
                        for a in planner.get("assumptions", []):
                            st.markdown(f"<div style='color:#64748b; font-size:0.8rem; padding:0.25rem 0;'>• {a}</div>", unsafe_allow_html=True)
            else:
                st.error("Planner agent did not produce output.")

        # Architect
        with tab2:
            arch = data.get("architect_output")
            if arch:
                st.markdown(f"""
                <div class="agent-card">
                    <div class="agent-header">
                        <span class="agent-badge">agent-02</span>
                        <span class="agent-name">Architect Agent</span>
                        <span class="status-dot status-done" style="margin-left:auto;"></span>
                    </div>
                    <p style="color:#94a3b8; margin:0;">{arch.get("architecture_summary", "")}</p>
                </div>
                """, unsafe_allow_html=True)

                col_a, col_b = st.columns([1, 1])
                with col_a:
                    st.markdown("**Folder Structure**")
                    st.markdown(f'<div class="code-block">{arch.get("folder_structure", "")}</div>', unsafe_allow_html=True)

                    st.markdown("<br>**Tech Stack**", unsafe_allow_html=True)
                    stack_html = "".join([
                        f'<span style="background:#1e1e2e; border:1px solid #2d2d4e; border-radius:4px; padding:0.2rem 0.6rem; font-size:0.78rem; color:#a5b4fc; margin:0.2rem; display:inline-block;">{t}</span>'
                        for t in arch.get("tech_stack", [])
                    ])
                    st.markdown(stack_html, unsafe_allow_html=True)

                with col_b:
                    st.markdown("**API Contracts**")
                    for contract in arch.get("api_contracts", []):
                        st.markdown(f'<div class="code-block" style="margin-bottom:0.5rem; padding:0.6rem 1rem;">{contract}</div>', unsafe_allow_html=True)

                    st.markdown("<br>**Service Boundaries**", unsafe_allow_html=True)
                    for svc in arch.get("service_boundaries", []):
                        st.markdown(f"<div style='color:#7c3aed; font-family:JetBrains Mono,monospace; font-size:0.82rem; padding:0.3rem 0; border-bottom:1px solid #1a1a2e;'>◆ {svc}</div>", unsafe_allow_html=True)

                if arch.get("key_decisions"):
                    st.markdown("<br>**Key Architectural Decisions**", unsafe_allow_html=True)
                    for d in arch.get("key_decisions", []):
                        st.markdown(f"<div style='color:#94a3b8; font-size:0.85rem; padding:0.35rem 0; border-bottom:1px solid #111118;'>→ {d}</div>", unsafe_allow_html=True)

                if arch.get("database_schema"):
                    st.markdown("<br>**Database Schema**", unsafe_allow_html=True)
                    st.markdown(f'<div class="code-block">{arch.get("database_schema", "")}</div>', unsafe_allow_html=True)
            else:
                st.error("Architect agent did not produce output.")

        # Codegen
        with tab3:
            codegen = data.get("codegen_output")
            if codegen:
                st.markdown(f"""
                <div class="agent-card">
                    <div class="agent-header">
                        <span class="agent-badge">agent-03</span>
                        <span class="agent-name">Code Generation Agent</span>
                        <span class="status-dot status-done" style="margin-left:auto;"></span>
                    </div>
                    <p style="color:#94a3b8; margin:0;">{len(codegen.get("files_generated", []))} files generated</p>
                </div>
                """, unsafe_allow_html=True)

                # File list
                st.markdown("**Generated Files**")
                files_html = "".join([
                    f'<span style="background:#0d0d14; border:1px solid #1e1e2e; border-radius:4px; padding:0.2rem 0.7rem; font-size:0.78rem; color:#00d4ff; font-family:JetBrains Mono,monospace; margin:0.2rem; display:inline-block;">📄 {f}</span>'
                    for f in codegen.get("files_generated", [])
                ])
                st.markdown(files_html, unsafe_allow_html=True)

                st.markdown("<br>**Code**", unsafe_allow_html=True)
                for block in codegen.get("code_blocks", []):
                    with st.expander(f"📄 {block.get('filename', 'file')}"):
                        st.code(block.get("code", ""), language=block.get("language", "python"))

                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if codegen.get("implementation_notes"):
                        st.markdown("**Implementation Notes**")
                        for note in codegen.get("implementation_notes", []):
                            st.markdown(f"<div style='color:#94a3b8; font-size:0.85rem; padding:0.35rem 0; border-bottom:1px solid #111118;'>→ {note}</div>", unsafe_allow_html=True)
                with col_b:
                    if codegen.get("next_steps"):
                        st.markdown("**Next Steps**")
                        for step in codegen.get("next_steps", []):
                            st.markdown(f"<div style='color:#7c3aed; font-size:0.85rem; padding:0.35rem 0; border-bottom:1px solid #111118;'>◆ {step}</div>", unsafe_allow_html=True)
            else:
                st.error("Codegen agent did not produce output.")

        # Logs
        with tab4:
            st.markdown("**Pipeline Execution Log**")
            for log in data.get("agent_logs", []):
                css_class = "success" if "✓" in log else ("error" if "ERROR" in log else "")
                st.markdown(f'<div class="log-line {css_class}">{log}</div>', unsafe_allow_html=True)

            if data.get("errors"):
                st.markdown("<br>**Errors**", unsafe_allow_html=True)
                for err in data.get("errors", []):
                    st.markdown(f'<div class="log-line error">✗ {err}</div>', unsafe_allow_html=True)

    except requests.exceptions.ConnectionError:
        status_area.empty()
        st.error("⚠️ Cannot connect to SDLCOS API. Make sure FastAPI is running: `uvicorn app.main:app --reload`")
    except Exception as e:
        status_area.empty()
        st.error(f"Pipeline error: {str(e)}")

elif run_btn and not feature_request.strip():
    st.warning("Please enter a feature request before running the pipeline.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#1e1e2e; font-size:0.75rem; font-family:JetBrains Mono,monospace; letter-spacing:0.1em;">
    SDLCOS v0.1.0 · NozakLabs · AI-Native Engineering Infrastructure
</div>
""", unsafe_allow_html=True)
