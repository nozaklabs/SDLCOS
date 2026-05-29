# ⚡ SDLCOS — AI-Native SDLC Orchestration System

> An AI-native multi-agent platform that automates software engineering workflows through coordinated autonomous agents.

Built by [NozakLabs](https://github.com/nozaklabs)

---

## What It Does

SDLCOS takes a feature request and runs it through a coordinated pipeline of specialized AI agents:

```
Feature Request → Planner Agent → Architect Agent → Codegen Agent → Structured Output
```

| Agent | Role |
|---|---|
| 🧠 Planner | Breaks down the request into engineering tasks, phases, and effort estimates |
| 🏗️ Architect | Designs system architecture, folder structure, API contracts, and DB schema |
| ⚙️ Codegen | Generates production-ready implementation files |

---

## Stack

- **Orchestration**: LangGraph
- **AI**: LLM API
- **Backend**: Python + FastAPI
- **Frontend**: Streamlit
- **Infra**: Docker

---

## Quickstart

### 1. Clone & configure

```bash
git clone https://github.com/nozaklabs/sdlcos
cd sdlcos
cp .env.example .env
# Add your LLM API key to .env
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the API

```bash
uvicorn app.main:app --reload
```

### 4. Run the UI (new terminal)

```bash
cd frontend
streamlit run app.py
```

Open `http://localhost:8501` and run your first pipeline.

---

## API

```
POST /workflow/run
{
  "feature_request": "Build JWT auth for a FastAPI app with refresh tokens"
}
```

Response includes structured outputs from all three agents.

---

## Roadmap

- [ ] Testing Agent
- [ ] Security Agent
- [ ] Reviewer Agent
- [ ] DevOps Agent
- [ ] Agent memory system
- [ ] Evaluation framework
- [ ] GitHub integration
- [ ] Observability dashboard

---

## License

MIT
