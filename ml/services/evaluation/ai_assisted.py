"""
AI-assisted evaluation (master prompt §11): used ONLY for question types
that cannot be scored deterministically — short answers, system design,
communication/approach quality. Never used where deterministic scoring is
possible (MCQ, tests, compilation, etc. — see deterministic.py).

CRITICAL: hidden test cases, reference solutions, and private question
metadata must never be included in a prompt whose output could leak back
to the candidate (master prompt §34). This module only ever grades what
the candidate submitted against a recruiter-authored rubric string.
"""
from __future__ import annotations

import json

from services.evaluation.schemas import EvaluateRequest
from shared.model_router import ModelRouter
from shared.schemas.common import ErrorCode, MLException
from shared.utilities.security import scrub_secrets_and_pii

_SYSTEM_PROMPT = """You are grading a candidate's assessment answer.
Score strictly against the provided rubric only. Do not reward answers
that merely "sound confident" — verify claims against the rubric criteria.
Respond with ONLY a JSON object, no markdown fences, no preamble, in this
exact shape:
{"score": <0-100 integer>, "strengths": [<string>, ...], "weaknesses": [<string>, ...], "reasoning": "<short paragraph>"}
"""


def _build_prompt(req: EvaluateRequest) -> str:
    rubric = "\n".join(f"- {r}" for r in (req.rubric or [])) or "(no rubric provided — grade for correctness, clarity, and completeness)"
    answer = scrub_secrets_and_pii(req.submitted_answer or "")
    prompt_text = scrub_secrets_and_pii(req.prompt or "")
    return f"""Question:
{prompt_text}

Rubric:
{rubric}

Candidate's answer:
{answer}
"""


def grade_with_ai(req: EvaluateRequest, confidence_review_floor: float = 0.65) -> dict:
    if not req.submitted_answer:
        raise MLException(ErrorCode.VALIDATION_ERROR, "submitted_answer is required for AI-assisted grading.")

    router = ModelRouter()
    result = router.complete(
        role="assessment_grading_llm",
        system=_SYSTEM_PROMPT,
        prompt=_build_prompt(req),
        max_tokens=600,
        temperature=0.0,
    )

    try:
        parsed = json.loads(result.text.strip())
        score = float(parsed["score"])
        strengths = list(parsed.get("strengths", []))
        weaknesses = list(parsed.get("weaknesses", []))
        reasoning = str(parsed.get("reasoning", ""))
    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
        raise MLException(
            ErrorCode.INTERNAL_ERROR, f"AI grader returned unparseable output: {e}"
        ) from e

    score = max(0.0, min(100.0, score))
    # Confidence heuristic: shorter/empty rubrics and very short answers are
    # inherently less reliable to auto-grade -> flag for human review.
    has_rubric = bool(req.rubric)
    answer_len_ok = len(req.submitted_answer.strip()) >= 20
    confidence = 0.85 if (has_rubric and answer_len_ok) else 0.55

    return {
        "score": score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "reasoning": reasoning,
        "confidence": confidence,
        "needs_human_review": confidence < confidence_review_floor,
        "model": result.model,
    }
