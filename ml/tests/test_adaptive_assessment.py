from __future__ import annotations

import pytest

from services.adaptive_assessment.schemas import (
    AdaptiveSelectRequest,
    AssessmentHistoryEntry,
    QuestionBlueprintConstraints,
    SkillEstimateInput,
)
from services.adaptive_assessment.service import select_adaptive_question


def _make_request(**overrides):
    base = {
        "candidate_id": "c1",
        "assessment_id": "a1",
        "blueprint": QuestionBlueprintConstraints(
            total_questions=5,
            allowed_skills=["python", "algorithms"],
            allowed_question_types=["mcq", "coding"],
            difficulty_distribution={"easy": 2, "medium": 2, "hard": 1},
            coding_languages=["python"],
        ),
        "skill_profile": {
            "python": SkillEstimateInput(skill="python", estimated_level=0.8, confidence=0.9),
            "algorithms": SkillEstimateInput(skill="algorithms", estimated_level=0.4, confidence=0.7),
        },
        "answered_questions": [],
        "remaining_approved_pool": [
            {"question_id": "q1", "skills": ["python"], "difficulty": 0.8, "question_type": "coding", "language": "python"},
            {"question_id": "q2", "skills": ["algorithms"], "difficulty": 0.3, "question_type": "mcq"},
            {"question_id": "q3", "skills": ["python", "algorithms"], "difficulty": 0.5, "question_type": "mcq"},
        ],
        "target_skills": ["algorithms"],
        "top_k": 1,
    }
    base.update(overrides)
    return AdaptiveSelectRequest(**base)


def test_selects_weak_skill_question():
    req = _make_request()
    resp = select_adaptive_question(req)
    assert resp.prediction.next_question is not None
    assert resp.prediction.next_question.question_id == "q2"
    assert "algorithms" in resp.prediction.next_question.skill_targeted


def test_respects_blueprint_language_restriction():
    pool = [
        {"question_id": "q1", "skills": ["python"], "difficulty": 0.5, "question_type": "coding", "language": "java"},
        {"question_id": "q2", "skills": ["python"], "difficulty": 0.5, "question_type": "mcq"},
    ]
    req = _make_request(remaining_approved_pool=pool)
    resp = select_adaptive_question(req)
    assert resp.prediction.next_question is not None
    assert resp.prediction.next_question.question_id == "q2"


def test_excludes_already_answered():
    pool = [
        {"question_id": "q1", "skills": ["python"], "difficulty": 0.8, "question_type": "coding", "language": "python"},
        {"question_id": "q2", "skills": ["algorithms"], "difficulty": 0.3, "question_type": "mcq"},
    ]
    req = _make_request(
        answered_questions=[AssessmentHistoryEntry(question_id="q2", skill="algorithms", difficulty=0.3, correct=True, question_type="mcq")],
        remaining_approved_pool=pool,
    )
    resp = select_adaptive_question(req)
    assert resp.prediction.next_question is not None
    assert resp.prediction.next_question.question_id == "q1"


def test_empty_pool_returns_none():
    req = _make_request(remaining_approved_pool=[])
    resp = select_adaptive_question(req)
    assert resp.prediction.next_question is None
    assert resp.confidence == 0.2


def test_blueprint_progress_tracked():
    req = _make_request(
        answered_questions=[
            AssessmentHistoryEntry(question_id="q_prev", skill="python", difficulty=0.2, correct=True, question_type="mcq"),
        ],
        remaining_approved_pool=[
            {"question_id": "q2", "skills": ["algorithms"], "difficulty": 0.3, "question_type": "mcq"},
        ],
    )
    resp = select_adaptive_question(req)
    assert resp.prediction.questions_answered == 1
    assert resp.prediction.questions_remaining == 4
    assert "easy" in resp.prediction.blueprint_progress
