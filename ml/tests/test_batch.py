from __future__ import annotations

import pytest

from services.batch.service import batch_recommend
from services.batch.schemas import BatchRecommendRequest


def test_batch_recommend_returns_results_for_each_candidate():
    req = BatchRecommendRequest(
        candidate_ids=["c1", "c2"],
        approved_question_pool=[
            {"question_id": "q1", "skills": ["python"], "difficulty": 0.5, "question_type": "mcq"},
            {"question_id": "q2", "skills": ["sql"], "difficulty": 0.6, "question_type": "mcq"},
        ],
        top_k=1,
    )
    resp = batch_recommend(req)
    assert resp.prediction.total_candidates == 2
    assert "c1" in resp.prediction.results
    assert "c2" in resp.prediction.results
    assert len(resp.prediction.results["c1"]) <= 1
    assert len(resp.prediction.results["c2"]) <= 1
