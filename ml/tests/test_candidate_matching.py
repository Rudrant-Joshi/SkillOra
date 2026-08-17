from __future__ import annotations

import pytest

from services.candidate_matching.schemas import (
    CandidateJobMatchPrediction,
    CandidateJobMatchRequest,
    CandidateProfile,
    JobRequirement,
)
from services.candidate_matching.service import match


def _make_request(**overrides):
    base = {
        "job": JobRequirement(
            job_id="j1",
            title="Backend Engineer",
            required_skills=["python", "fastapi", "sql"],
            preferred_skills=["docker", "redis"],
            min_experience_years=3.0,
        ),
        "candidate": CandidateProfile(
            candidate_id="c1",
            skills={"python": 0.9, "fastapi": 0.85, "sql": 0.7, "docker": 0.4},
            experience_years=4.0,
        ),
        "assessment_results": {"overall": 88},
        "shared_repository_ids": ["repo_1"],
        "shared_project_ids": [],
    }
    base.update(overrides)
    return CandidateJobMatchRequest(**base)


def test_strong_match_high_score():
    req = _make_request()
    resp = match(req)
    assert resp.prediction.match_score >= 0.7
    assert resp.confidence >= 0.6
    matched_skills = [e.skill for e in resp.prediction.matched_skills]
    assert "python" in matched_skills
    assert "fastapi" in matched_skills


def test_missing_skills_detected():
    req = _make_request()
    resp = match(req)
    missing_skills = [e.skill for e in resp.prediction.missing_skills]
    assert "redis" in missing_skills


def test_below_experience_penalized():
    req = _make_request(candidate=CandidateProfile(candidate_id="c1", skills={"python": 0.9, "fastapi": 0.85, "sql": 0.7}, experience_years=1.0))
    resp = match(req)
    assert any("experience_below_min" in e for e in resp.prediction.evidence)


def test_no_sensitive_characteristics_used():
    req = _make_request()
    resp = match(req)
    for e in resp.prediction.evidence:
        assert "gender" not in e.lower()
        assert "race" not in e.lower()
        assert "religion" not in e.lower()


def test_decision_support_only_in_metadata():
    req = _make_request()
    resp = match(req)
    assert "Decision-support only" in resp.metadata.get("note", "")
