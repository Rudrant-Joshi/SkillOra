from __future__ import annotations

import pytest

from services.content_generation.schemas import GenerateQuestionRequest
from services.content_generation.service import create_question


def test_generate_mcq_draft():
    req = GenerateQuestionRequest(skill="python", topic="data types", difficulty=0.5, question_type="mcq")
    resp = create_question(req)
    assert resp.prediction.draft.draft_id
    assert resp.prediction.draft.question_type == "mcq"
    assert resp.prediction.draft.requires_human_review is True
    assert "draft" in resp.metadata.get("note", "").lower()


def test_generate_coding_draft():
    req = GenerateQuestionRequest(skill="python", topic="arrays", difficulty=0.6, question_type="coding", language="python")
    resp = create_question(req)
    assert resp.prediction.draft.question_type == "coding"
    assert resp.prediction.draft.visible_tests or resp.prediction.draft.validation_flags


def test_generated_draft_has_skill_and_topic():
    req = GenerateQuestionRequest(skill="sql", topic="joins", difficulty=0.4, question_type="mcq")
    resp = create_question(req)
    assert resp.prediction.draft.skill == "sql"
    assert resp.prediction.draft.topic == "joins"
