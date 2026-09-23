"""LangGraph RAG flow with deterministic mock mode."""

from __future__ import annotations

import os
from typing import Literal

from langgraph.graph import END, START, StateGraph

from llm_client import classify_with_llm, generate_with_llm, mock_mode
from models import AnswerResponse, GraphState
from vector_store import retrieve

KEYWORDS = [
    "delivery",
    "return",
    "refund",
    "membership",
    "tracking",
    "cancel",
    "gift card",
    "support hours",
]


def classify_intent(state: GraphState) -> GraphState:
    query = state["query"]
    if mock_mode():
        lowered = query.lower()
        intent = "policy_question" if any(keyword in lowered for keyword in KEYWORDS) else "general_question"
    else:
        intent = classify_with_llm(query)
    return {**state, "intent": intent}


def retrieve_and_answer(state: GraphState) -> GraphState:
    query = state["query"]
    retrieved = retrieve(query, top_k=3)
    documents = retrieved["documents"]
    source_ids = retrieved["ids"]
    if not documents:
        response = AnswerResponse(
            answer="No matching policy context was retrieved.",
            sources=[],
            confidence=0.0,
        )
        return {**state, "retrieved_documents": [], "retrieved_sources": [], "response": response.model_dump()}

    if mock_mode():
        snippet = documents[0][:200].strip()
        response = AnswerResponse(
            answer=f"Based on the retrieved context: {snippet}",
            sources=source_ids,
            confidence=1.0,
        )
    else:
        context = "\n\n".join(
            f"SOURCE {source_id}: {document}" for source_id, document in zip(source_ids, documents)
        )
        generated = generate_with_llm(query, context, source_ids)
        response = AnswerResponse.model_validate(generated)

    return {
        **state,
        "retrieved_documents": documents,
        "retrieved_sources": source_ids,
        "response": response.model_dump(),
    }


def direct_answer(state: GraphState) -> GraphState:
    query = state["query"]
    if mock_mode():
        response = AnswerResponse(
            answer="I can only answer questions about Zepto policies right now.",
            sources=[],
            confidence=1.0,
        )
    else:
        generated = generate_with_llm(query, "", [])
        response = AnswerResponse.model_validate(generated)
    return {**state, "response": response.model_dump()}


def route_after_classification(state: GraphState) -> Literal["retrieve_and_answer", "direct_answer"]:
    return "retrieve_and_answer" if state["intent"] == "policy_question" else "direct_answer"


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_and_answer", retrieve_and_answer)
    graph.add_node("direct_answer", direct_answer)

    graph.add_edge(START, "classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        route_after_classification,
        {
            "retrieve_and_answer": "retrieve_and_answer",
            "direct_answer": "direct_answer",
        },
    )
    graph.add_edge("retrieve_and_answer", END)
    graph.add_edge("direct_answer", END)
    return graph.compile()


APP_GRAPH = build_graph()


def ask(query: str) -> AnswerResponse:
    result = APP_GRAPH.invoke({"query": query})
    return AnswerResponse.model_validate(result["response"])


if __name__ == "__main__":
    print(ask("What is the delivery policy?").model_dump_json(indent=2))
    print(ask("What is 2 + 2?").model_dump_json(indent=2))
