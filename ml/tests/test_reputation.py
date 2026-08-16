from services.reputation.schemas import (
    ComputeActivityQualityRequest,
    ComputeReputationRequest,
    ReputationActivitySummary,
)
from services.reputation.service import (
    compute_activity_quality_service,
    compute_reputation_service,
)


def test_reputation_elite_for_strong_profile():
    req = ComputeReputationRequest(
        user_id="u1",
        activity=ReputationActivitySummary(
            snippets_pushed=20,
            problems_solved=50,
            problems_attempted=60,
            followers_count=100,
            profile_completeness=95.0,
            avg_code_quality=85.0,
            account_age_days=400,
        ),
        verified_skills=["Python", "React"],
    )
    resp = compute_reputation_service(req)
    assert resp.prediction.reputation_score >= 80
    assert resp.prediction.band in {"trusted", "elite"}
    assert resp.prediction.verification_eligible is True
    assert len(resp.prediction.factors) == 6


def test_reputation_newcomer_for_empty():
    req = ComputeReputationRequest(
        user_id="u1",
        activity=ReputationActivitySummary(
            snippets_pushed=0,
            problems_solved=0,
            problems_attempted=0,
            followers_count=0,
            profile_completeness=10.0,
            avg_code_quality=0.0,
            account_age_days=2,
        ),
        verified_skills=[],
    )
    resp = compute_reputation_service(req)
    assert resp.prediction.band == "newcomer"
    assert resp.prediction.reputation_score < 30


def test_reputation_factors_are_explainable():
    req = ComputeReputationRequest(
        user_id="u1",
        activity=ReputationActivitySummary(
            snippets_pushed=5, problems_solved=10, problems_attempted=12,
            followers_count=3, profile_completeness=70, avg_code_quality=60,
            account_age_days=50,
        ),
        verified_skills=["Go"],
    )
    resp = compute_reputation_service(req)
    names = {f.name for f in resp.prediction.factors}
    assert {"activity_volume", "problem_solving", "code_quality", "network",
            "profile_completeness", "verified_skills"} <= names


def test_activity_quality_excellent_for_strong_submission():
    req = ComputeActivityQualityRequest(
        activity_type="submission",
        code_quality_score=90.0,
        test_pass_rate=1.0,
        has_description=True,
        engagement_count=8,
        novelty_score=0.8,
    )
    resp = compute_activity_quality_service(req)
    assert resp.prediction.quality_score >= 80
    assert resp.prediction.quality_band in {"good", "excellent"}
    assert "high code quality" in resp.prediction.strengths


def test_activity_quality_low_for_poor_submission():
    req = ComputeActivityQualityRequest(
        activity_type="submission",
        code_quality_score=20.0,
        test_pass_rate=0.2,
        has_description=False,
        engagement_count=0,
        novelty_score=0.1,
    )
    resp = compute_activity_quality_service(req)
    assert resp.prediction.quality_score < 50
    assert "missing description" in resp.prediction.weaknesses


def test_activity_quality_follow_is_low_information():
    req = ComputeActivityQualityRequest(activity_type="follow")
    resp = compute_activity_quality_service(req)
    assert resp.prediction.quality_band in {"low", "fair"}
