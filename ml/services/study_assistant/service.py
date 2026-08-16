"""
AI Study Assistant (master prompt §6).

Provides:
  - Personalized explanations
  - Study plans
  - Flashcard generation

Uses the ModelRouter for LLM calls. Returns `grounded=false` when
no retrieval context is available, so the caller knows the answer
is generated from general knowledge rather than retrieved material.
"""
from __future__ import annotations

import time

from services.study_assistant.schemas import StudyAssistPrediction, StudyAssistRequest
from shared.model_router import ModelRouter
from shared.schemas.common import MLException
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "study-assistant-v1"

_EXPLAIN_SYSTEM = """You are an expert tutor. Provide a clear, concise
explanation tailored to the learner's current skill level. If a skill
profile is provided, adapt depth accordingly. Do not invent facts."""

_PLAN_SYSTEM = """You are a learning designer. Create a focused study plan
with 3-5 concrete steps, ordered by priority. Each step should include a
specific resource type (practice problems, reading, project) and an
estimated time. Do not invent URLs."""

_FLASHCARD_SYSTEM = """You are a flashcard author. Generate exactly 3 Q&A
flashcards. Format each as:
Q: <question>
A: <answer>
Keep questions specific and answers concise."""


def _build_skill_context(skill_profile: dict[str, float] | None) -> str:
    if not skill_profile:
        return ""
    lines = [f"- {skill}: level {level:.2f}" for skill, level in sorted(skill_profile.items())]
    return "Learner skill profile:\n" + "\n".join(lines)


def _call_llm(system: str, prompt: str, max_tokens: int = 800) -> tuple[str, str]:
    router = ModelRouter()
    result = router.complete(role="study_assistant_llm", system=system, prompt=prompt, max_tokens=max_tokens)
    return result.text.strip(), result.model


def generate_study_assist(req: StudyAssistRequest) -> MLResponse[StudyAssistPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()
    skill_ctx = _build_skill_context(req.skill_profile)
    user_prompt = req.query
    if skill_ctx:
        user_prompt = f"{skill_ctx}\n\nQuestion: {user_prompt}"
    if req.context:
        user_prompt = f"Context:\n{req.context}\n\n{user_prompt}"

    mode = req.mode.lower()
    if mode == "study_plan":
        system = _PLAN_SYSTEM
        max_tokens = 600
    elif mode == "flashcard":
        system = _FLASHCARD_SYSTEM
        max_tokens = 500
    else:
        system = _EXPLAIN_SYSTEM
        max_tokens = 800

    try:
        answer, model = _call_llm(system, user_prompt, max_tokens=max_tokens)
        confidence = 0.75
        grounded = bool(req.context)
        evidence = [f"llm:{model}"]
        if not grounded:
            answer += "\n\n(Note: this explanation is generated without retrieved learning material — verify against authoritative sources.)"
    except MLException:
        answer = "Study assistant is temporarily unavailable. Please try again later."
        confidence = 0.2
        grounded = False
        evidence = ["llm_unavailable"]

    prediction = StudyAssistPrediction(
        answer=answer,
        mode=mode,
        grounded=grounded,
        sources=["llm_generation"],
        confidence=confidence,
    )

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=confidence,
        evidence=evidence,
        metadata={"user_id": req.user_id, "mode": mode},
    )

    log_inference(
        service="study_assistant",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=confidence,
        success=True,
    )
    return response
