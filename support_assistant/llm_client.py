"""Optional real-LLM client. Required grading path remains MOCK_LLM=1/default."""

from __future__ import annotations

import json
import os

import requests

from prompt_template import CLASSIFY_PROMPT, DIRECT_PROMPT, PROMPT_TEMPLATE


def mock_mode() -> bool:
    return os.getenv("MOCK_LLM", "1") != "0"


def call_real_llm(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("MOCK_LLM=0 requires GROQ_API_KEY for the optional real-LLM path.")
    endpoint = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    response = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"]


def classify_with_llm(query: str) -> str:
    prompt = CLASSIFY_PROMPT.replace("{query}", query)
    raw = call_real_llm(prompt)
    try:
        parsed = json.loads(raw)
        intent = str(parsed["intent"])
        if intent in {"policy_question", "general_question"}:
            return intent
    except Exception:
        pass
    # Conservative fallback for optional path.
    lowered = raw.lower()
    return "policy_question" if "policy_question" in lowered else "general_question"


def generate_with_llm(query: str, context: str, source_ids: list[str]) -> dict:
    prompt = PROMPT_TEMPLATE.format(context=context, query=query)
    last_error = None
    for attempt in range(3):
        corrective = ""
        if attempt > 0:
            corrective = (
                "\nCORRECTION: Your previous output failed schema validation. "
                "Return only a JSON object with answer (string), sources (list), and confidence (0..1)."
            )
        try:
            raw = call_real_llm(prompt + corrective)
            parsed = json.loads(raw)
            answer = str(parsed["answer"])
            sources = list(parsed.get("sources", source_ids))
            confidence = float(parsed.get("confidence", 0.0))
            if not 0 <= confidence <= 1:
                raise ValueError("confidence must be between 0 and 1")
            return {"answer": answer, "sources": sources, "confidence": confidence}
        except Exception as exc:  # noqa: BLE001 - optional retry path
            last_error = exc
    return {
        "answer": f"ERROR: unable to validate real-LLM response after 3 attempts: {last_error}",
        "sources": [],
        "confidence": 0.0,
    }
