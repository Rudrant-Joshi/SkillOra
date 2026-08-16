from datetime import datetime, timezone

from services.profile_intelligence.schemas import (
    ActivitySummaryInput,
    GenerateProfileSummaryRequest,
    InferSkillsFromActivityRequest,
    ScoreProfileCompletenessRequest,
)
from services.profile_intelligence.service import (
    generate_profile_summary,
    infer_skills_from_activity,
    score_profile_completeness,
)


def _activity(activity_type, title, language=None, skills=None, days_ago=0):
    return ActivitySummaryInput(
        activity_type=activity_type,
        title=title,
        language=language,
        skills_mentioned=skills or [],
        created_at=(datetime.now(timezone.utc).replace(microsecond=0)).isoformat(),
    )


def test_infer_skills_from_python_snippets():
    req = InferSkillsFromActivityRequest(
        user_id="u1",
        activities=[
            _activity("snippet", "My flask app", "python", ["Flask"]),
            _activity("submission", "Two sum problem", "python", []),
        ],
    )
    resp = infer_skills_from_activity(req)
    skills = {s.skill for s in resp.prediction.inferred_skills}
    assert "Python" in skills or "Flask" in skills
    assert resp.confidence > 0.3
    assert resp.prediction.inferred_skills[0].inferred_level >= 0.0


def test_infer_skills_detects_problem_topics():
    req = InferSkillsFromActivityRequest(
        user_id="u1",
        activities=[_activity("submission", "Dynamic programming knapsack", "python", [])],
    )
    resp = infer_skills_from_activity(req)
    skills_lower = {s.skill.lower() for s in resp.prediction.inferred_skills}
    assert any("dynamic programming" in s for s in skills_lower) or any("algorithms" in s for s in skills_lower)


def test_generate_summary_with_activity():
    req = GenerateProfileSummaryRequest(
        user_id="u1",
        username="alice",
        bio="Backend developer",
        activities=[
            _activity("snippet", "Django REST API", "python", ["Django"]),
            _activity("submission", "Graph BFS", "python", []),
        ],
        current_skills={"Python": 0.7},
    )
    resp = generate_profile_summary(req)
    assert resp.prediction.activity_count == 2
    assert resp.prediction.suggested_headline
    assert resp.prediction.profile_strength in {"emerging", "active", "established"}


def test_generate_summary_empty_profile():
    req = GenerateProfileSummaryRequest(
        user_id="u1",
        username="newbie",
        activities=[],
    )
    resp = generate_profile_summary(req)
    assert resp.prediction.activity_count == 0
    assert resp.prediction.profile_strength == "empty"


def test_completeness_score_reflects_activity():
    req = ScoreProfileCompletenessRequest(
        user_id="u1",
        username="bob",
        bio="I build things",
        activities=[
            _activity("snippet", "React app", "javascript", ["React"]),
            _activity("submission", "Array problem", "javascript", []),
            _activity("follow", "Followed carol", None, []),
        ],
        current_skills={"JavaScript": 0.6},
    )
    resp = score_profile_completeness(req)
    assert resp.prediction.completeness_score > 60
    assert resp.prediction.band in {"partial", "complete", "verified"}


def test_completeness_empty():
    req = ScoreProfileCompletenessRequest(
        user_id="u1",
        username="x",
        activities=[],
    )
    resp = score_profile_completeness(req)
    assert resp.prediction.completeness_score == 0.0
    assert resp.prediction.band == "empty"
