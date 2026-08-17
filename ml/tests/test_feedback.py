from __future__ import annotations

import pytest

from services.feedback.service import log_feedback
from services.feedback.schemas import FeedbackLogRequest


def test_feedback_log_returns_logged_true():
    req = FeedbackLogRequest(
        request_id="req_abc",
        service="evaluation",
        model_version="evaluation-v1",
        prediction={"score": 85},
        actual_outcome={"score": 90},
    )
    resp = log_feedback(req)
    assert resp.prediction.logged is True
    assert resp.prediction.feedback_id


def test_feedback_log_without_actual_outcome():
    req = FeedbackLogRequest(
        request_id="req_def",
        service="skill_engine",
        model_version="skill-v1",
        prediction={"estimated_level": 0.8},
    )
    resp = log_feedback(req)
    assert resp.prediction.logged is True
