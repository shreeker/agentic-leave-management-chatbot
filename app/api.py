from fastapi import FastAPI
from .models import ChatRequest, ChatResponse
from .agent import Agent
from .db import init_db

app = FastAPI(title="Agentic Leave Management API")
agent = Agent()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = agent.run(
        employee_id=request.employee_id,
        user_message=request.message,
    )
    return ChatResponse(
        thread_id=request.employee_id,
        response=response,
    )
