"""FastAPI application for the Zepto policy support assistant."""

from __future__ import annotations

from fastapi import FastAPI

from graph import ask
from models import AnswerResponse, AskRequest

app = FastAPI(
    title="Zepto Policy Support Assistant",
    version="1.0.0",
    description="A local RAG support assistant with deterministic MOCK_LLM mode.",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "zepto-support-assistant", "status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
def ask_endpoint(request: AskRequest) -> AnswerResponse:
    return ask(request.query)
