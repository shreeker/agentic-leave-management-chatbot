# Agentic Leave Management System

A genuinely agentic leave-management reference implementation using:

- Python 3.11+
- LangGraph for durable state
- LangChain tools
- Any OpenAI-compatible LLM HTTP endpoint via `ChatOpenAI`
- RAG over HR policies
- Dynamic tool selection
- Dynamic planning/re-planning
- Human-in-the-loop approval
- Persistent leave data in SQLite
- Audit events
- FastAPI API
- LangSmith tracing/evaluation hooks

## What makes this agentic?

There is intentionally NO fixed business sequence such as:

`balance -> policy -> calendar -> manager -> create`

The agent receives a goal, decides what information/actions it needs, chooses tools dynamically, observes tool results, and can change its plan.

The only hard control loop is the generic agent loop:

`reason -> tool -> observe -> reason -> ... -> final`

Safety-sensitive writes are guarded by deterministic authorization checks and human approval.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Set LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL

python -m app.seed
uvicorn app.api:app --reload
```

Then:

```bash
curl -X POST http://localhost:8000/chat \
  -H 'content-type: application/json' \
  -d '{"employee_id":"E1001","message":"I want to take vacation from 2026-10-12 to 2026-10-20 for a family trip."}'
```

## Important production note

This is a complete runnable reference implementation, but real enterprise deployment should replace the SQLite/calendar/approval adapters with your HRIS, corporate calendar, IAM/authentication, and approval systems.
