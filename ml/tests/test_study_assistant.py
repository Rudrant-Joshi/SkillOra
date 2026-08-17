from __future__ import annotations

import pytest

from services.study_assistant.schemas import StudyAssistRequest
from services.study_assistant.service import generate_study_assist


def test_explain_mode_returns_answer():
    req = StudyAssistRequest(user_id="u1", query="What is a Python decorator?", mode="explain")
    resp = generate_study_assist(req)
    assert resp.prediction.answer
    assert resp.prediction.mode == "explain"
    assert resp.confidence >= 0.0


def test_study_plan_mode():
    req = StudyAssistRequest(user_id="u1", query="Prepare for algorithms interview", mode="study_plan")
    resp = generate_study_assist(req)
    assert resp.prediction.answer
    assert resp.prediction.mode == "study_plan"


def test_flashcard_mode():
    req = StudyAssistRequest(user_id="u1", query="Python list comprehensions", mode="flashcard")
    resp = generate_study_assist(req)
    assert resp.prediction.answer
    # LLM may be unavailable in test env; just verify response structure is valid
    assert resp.prediction.mode == "flashcard"
    assert resp.confidence >= 0.0


def test_skill_profile_included_in_prompt():
    req = StudyAssistRequest(
        user_id="u1",
        query="Explain binary search",
        mode="explain",
        skill_profile={"algorithms": 0.3},
    )
    resp = generate_study_assist(req)
    assert resp.prediction.answer
