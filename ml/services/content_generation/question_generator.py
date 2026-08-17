"""
AI Question Generation (master prompt §20, §21).

Generates draft questions from skill/topic/difficulty specifications.
All generated questions are marked as `requires_human_review=true` and
must be validated + approved by a recruiter before publishing.

For coding questions, the draft includes starter_code, visible_tests,
hidden_tests, and constraints. The actual execution validation happens
in the backend sandbox — this module only produces the draft.
"""
from __future__ import annotations

import uuid

from services.content_generation.schemas import (
    GenerateQuestionPrediction,
    GenerateQuestionRequest,
    GeneratedQuestionDraft,
)
from shared.model_router import ModelRouter
from shared.schemas.common import MLException

SERVICE_VERSION = "question-generation-v1"

_MCQ_SYSTEM = """You are an assessment author. Generate a single clear MCQ
question for the given skill, topic, and difficulty (0..1). Output strict JSON:
{"title": "...", "prompt": "...", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "..."}
Do not include markdown fences."""

_CODING_SYSTEM = """You are an assessment author. Generate a coding problem
draft for the given skill, topic, and language. Output strict JSON:
{"title": "...", "prompt": "...", "starter_code": "...", "visible_tests": ["..."], "hidden_tests": ["..."], "constraints": ["..."], "explanation": "..."}
Do not include markdown fences."""


def _generate_with_llm(system: str, user_prompt: str, max_tokens: int = 600) -> dict:
    import json
    import re

    router = ModelRouter()
    result = router.complete(role="study_assistant_llm", system=system, prompt=user_prompt, max_tokens=max_tokens)
    text = result.text.strip()
    # Strip markdown fences if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


def _validate_mcq(data: dict) -> list[str]:
    flags: list[str] = []
    if len(data.get("options", [])) < 2:
        flags.append("mcq_insufficient_options")
    if not data.get("correct_answer"):
        flags.append("mcq_missing_correct_answer")
    if len(data.get("prompt", "")) < 20:
        flags.append("prompt_too_short")
    return flags


def _validate_coding(data: dict) -> list[str]:
    flags: list[str] = []
    if not data.get("starter_code"):
        flags.append("coding_missing_starter_code")
    if len(data.get("visible_tests", [])) < 1:
        flags.append("coding_missing_visible_tests")
    if len(data.get("hidden_tests", [])) < 1:
        flags.append("coding_missing_hidden_tests")
    return flags


def generate_question(req: GenerateQuestionRequest) -> GenerateQuestionPrediction:
    draft_id = f"draft_{uuid.uuid4().hex[:8]}"
    difficulty_label = "easy" if req.difficulty <= 0.33 else "medium" if req.difficulty <= 0.66 else "hard"
    base_prompt = f"Skill: {req.skill}\nTopic: {req.topic}\nDifficulty: {difficulty_label} ({req.difficulty:.2f})\nLanguage: {req.language or 'N/A'}\nType: {req.question_type}"

    try:
        if req.question_type == "coding":
            system = _CODING_SYSTEM
            data = _generate_with_llm(system, base_prompt, max_tokens=700)
            flags = _validate_coding(data)
            draft = GeneratedQuestionDraft(
                draft_id=draft_id,
                skill=req.skill,
                topic=req.topic,
                difficulty=req.difficulty,
                question_type=req.question_type,
                title=data.get("title", ""),
                prompt=data.get("prompt", ""),
                starter_code=data.get("starter_code"),
                visible_tests=data.get("visible_tests", []),
                hidden_tests=data.get("hidden_tests", []),
                constraints=data.get("constraints", []),
                explanation=data.get("explanation", ""),
                validation_flags=flags,
                requires_human_review=True,
            )
        else:
            system = _MCQ_SYSTEM
            data = _generate_with_llm(system, base_prompt, max_tokens=500)
            flags = _validate_mcq(data)
            draft = GeneratedQuestionDraft(
                draft_id=draft_id,
                skill=req.skill,
                topic=req.topic,
                difficulty=req.difficulty,
                question_type=req.question_type,
                title=data.get("title", ""),
                prompt=data.get("prompt", ""),
                options=data.get("options", []),
                correct_answer=data.get("correct_answer"),
                explanation=data.get("explanation", ""),
                validation_flags=flags,
                requires_human_review=True,
            )
        confidence = 0.6 if not flags else 0.4
    except MLException:
        draft = GeneratedQuestionDraft(
            draft_id=draft_id,
            skill=req.skill,
            topic=req.topic,
            difficulty=req.difficulty,
            question_type=req.question_type,
            title="",
            prompt="",
            validation_flags=["llm_unavailable"],
            requires_human_review=True,
        )
        confidence = 0.2

    return GenerateQuestionPrediction(draft=draft, confidence=confidence)
