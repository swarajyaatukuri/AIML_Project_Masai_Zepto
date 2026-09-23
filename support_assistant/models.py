"""Pydantic request/response models and LangGraph TypedDict state."""

from __future__ import annotations

from typing import Literal, TypedDict

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class GraphState(TypedDict, total=False):
    query: str
    intent: Literal["policy_question", "general_question"]
    retrieved_documents: list[str]
    retrieved_sources: list[str]
    answer: str
    response: dict
    confidence: float
    error: str
