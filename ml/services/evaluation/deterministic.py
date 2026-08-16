"""
Deterministic evaluation (master prompt §11): MCQ correctness, multiple-select,
SQL execution results, unit/hidden test results, compilation, time/memory
limits. Never replaced by an LLM where these are computable exactly
(master prompt §40: "Do not replace deterministic evaluation with an LLM").

NOTE: actual code execution / SQL execution happens in a secure sandbox
that is NOT part of the ML layer (backend/DevOps own the sandbox per team
boundaries in §1). This module scores the *results* the sandbox returns.
"""
from __future__ import annotations

from services.evaluation.schemas import EvaluateRequest


def evaluate_mcq(req: EvaluateRequest) -> tuple[float, str]:
    correct = set(req.correct_options or [])
    submitted = set(req.submitted_options or [])
    if not correct:
        return 0.0, "No correct options configured for this question."
    is_correct = correct == submitted
    score = 100.0 if is_correct else 0.0
    reasoning = "Exact match against correct option set." if is_correct else \
        "Submitted options do not match the correct option set."
    return score, reasoning


def evaluate_multi_select(req: EvaluateRequest) -> tuple[float, str]:
    """Partial credit: fraction of correct options selected minus penalty for wrong picks."""
    correct = set(req.correct_options or [])
    submitted = set(req.submitted_options or [])
    if not correct:
        return 0.0, "No correct options configured for this question."

    true_positives = len(correct & submitted)
    false_positives = len(submitted - correct)
    score = max(0.0, (true_positives - false_positives) / len(correct)) * 100
    reasoning = (
        f"{true_positives}/{len(correct)} correct options selected, "
        f"{false_positives} incorrect option(s) selected."
    )
    return round(score, 2), reasoning


def evaluate_tests(req: EvaluateRequest) -> tuple[float, str]:
    """Coding/SQL: score = fraction of tests passed, gated by compile/limits."""
    if req.compiled is False:
        return 0.0, "Submission did not compile/parse."
    if req.time_limit_exceeded:
        return 0.0, "Submission exceeded the time limit."
    if req.memory_limit_exceeded:
        return 0.0, "Submission exceeded the memory limit."

    tests = req.test_results or []
    if not tests:
        return 0.0, "No test results available to evaluate."

    passed = sum(1 for t in tests if t.passed)
    score = (passed / len(tests)) * 100
    visible_passed = sum(1 for t in tests if t.passed and not t.hidden)
    hidden_passed = sum(1 for t in tests if t.passed and t.hidden)
    visible_total = sum(1 for t in tests if not t.hidden)
    hidden_total = sum(1 for t in tests if t.hidden)
    reasoning = (
        f"{passed}/{len(tests)} tests passed "
        f"({visible_passed}/{visible_total} visible, {hidden_passed}/{hidden_total} hidden)."
    )
    return round(score, 2), reasoning


DETERMINISTIC_EVALUATORS = {
    "mcq": evaluate_mcq,
    "multi_select": evaluate_multi_select,
    "coding": evaluate_tests,
    "sql": evaluate_tests,
}


def is_deterministic(question_type: str) -> bool:
    return question_type in DETERMINISTIC_EVALUATORS
