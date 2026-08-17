"""
End-to-end integration test: proves the five new ML services form a working
"connective tissue" — a developer's raw activity flows through skill inference,
auto-profile, feed ranking, difficulty estimation, learning path, and reputation
without any manually authored profile fields.
"""
from datetime import datetime, timezone

from datasets.seed_profiles import build_feed_pool, generate_seed_profiles

from services.activity_feed.schemas import FeedActivityInput, RankFeedRequest
from services.activity_feed.service import rank_feed_service
from services.learning_path.schemas import GeneratePathRequest
from services.learning_path.service import generate_path_service
from services.profile_intelligence.schemas import (
    ActivitySummaryInput,
    GenerateProfileSummaryRequest,
    InferSkillsFromActivityRequest,
)
from services.profile_intelligence.service import (
    generate_profile_summary,
    infer_skills_from_activity,
)
from services.problem_difficulty.schemas import EstimateDifficultyRequest
from services.problem_difficulty.service import estimate_difficulty
from services.reputation.schemas import ComputeReputationRequest, ReputationActivitySummary
from services.reputation.service import compute_reputation_service

VIEWER_ID = "u1"  # alice


def _activity_models(activities):
    return [
        ActivitySummaryInput(
            activity_type=a["activity_type"], title=a["title"],
            description=a.get("description"), language=a.get("language"),
            skills_mentioned=a.get("skills_mentioned", []), created_at=a["created_at"],
        )
        for a in activities
    ]


def _build_users_and_viewer():
    users = generate_seed_profiles()
    viewer = next(u for u in users if u["user_id"] == VIEWER_ID)
    return users, viewer


def test_inferred_skills_are_nonempty_and_contain_language():
    _, viewer = _build_users_and_viewer()
    resp = infer_skills_from_activity(
        InferSkillsFromActivityRequest(
            user_id=viewer["user_id"], activities=_activity_models(viewer["activities"])
        )
    )
    skills = {s.skill for s in resp.prediction.inferred_skills}
    assert len(skills) > 0
    # alice's archetype is a Python backend dev, so Python should be inferred
    assert "Python" in skills
    assert all(0.0 <= s.inferred_level <= 1.0 for s in resp.prediction.inferred_skills)


def test_auto_profile_summary_is_generated_without_manual_skills():
    _, viewer = _build_users_and_viewer()
    resp = generate_profile_summary(
        GenerateProfileSummaryRequest(
            user_id=viewer["user_id"], username=viewer["username"], bio=viewer["bio"],
            activities=_activity_models(viewer["activities"]), current_skills={},
        )
    )
    assert len(resp.prediction.summary) > 20
    assert resp.prediction.suggested_headline
    assert resp.prediction.activity_count == len(viewer["activities"])


def test_feed_ranks_followed_and_relevant_activity_first():
    users, viewer = _build_users_and_viewer()
    pool = build_feed_pool(users, viewer["user_id"])
    pool_models = [
        FeedActivityInput(**{k: p[k] for k in (
            "activity_id", "activity_type", "user_id", "username", "title",
            "description", "language", "skills_mentioned", "created_at", "engagement_count")})
        for p in pool
    ]
    viewer_skills = {s.skill: s.inferred_level for s in
                    infer_skills_from_activity(InferSkillsFromActivityRequest(
                        user_id=viewer["user_id"],
                        activities=_activity_models(viewer["activities"]),
                    )).prediction.inferred_skills}
    resp = rank_feed_service(RankFeedRequest(
        viewer_id=viewer["user_id"], viewer_skills=viewer_skills,
        followed_user_ids=viewer["following"], candidate_pool=pool_models, top_k=5,
    ))
    items = resp.prediction.ranked_items
    assert len(items) > 0
    # all top items should come from people alice follows (social-graph boost)
    assert all(item.user_id in viewer["following"] for item in items[:3])


def test_difficulty_estimate_labels_edit_distance_hard():
    resp = estimate_difficulty(EstimateDifficultyRequest(
        title="Edit Distance", language="cpp",
        description="Compute minimum operations to convert one string to another "
                    "with insert, delete, replace using dynamic programming.",
        topics=["dynamic programming", "string"], test_cases_count=14, constraints_count=4,
    ))
    assert resp.prediction.difficulty_label == "hard"
    assert 0.0 <= resp.prediction.difficulty <= 1.0


def test_learning_path_builds_prerequisite_aware_steps():
    _, viewer = _build_users_and_viewer()
    viewer_skills = {s.skill: s.inferred_level for s in
                    infer_skills_from_activity(InferSkillsFromActivityRequest(
                        user_id=viewer["user_id"],
                        activities=_activity_models(viewer["activities"]),
                    )).prediction.inferred_skills}
    resp = generate_path_service(GeneratePathRequest(
        user_id=viewer["user_id"], current_skills=viewer_skills,
        target_skills=["machine learning", "system design"], max_steps=5,
    ))
    steps = resp.prediction.steps
    assert len(steps) > 0
    skills_in_path = {s.skill.lower() for s in steps}
    # machine learning must appear, and its known prerequisites should precede it
    assert "machine learning" in skills_in_path
    ml_index = next(i for i, s in enumerate(steps) if s.skill.lower() == "machine learning")
    prereq_index = next((i for i, s in enumerate(steps) if s.skill.lower() == "python"), None)
    if prereq_index is not None:
        assert prereq_index < ml_index


def test_reputation_is_explainable_and_in_range():
    _, viewer = _build_users_and_viewer()
    resp = compute_reputation_service(ComputeReputationRequest(
        user_id=viewer["user_id"],
        activity=ReputationActivitySummary(
            snippets_pushed=viewer["snippets_pushed"],
            problems_solved=viewer["problems_solved"],
            problems_attempted=viewer["problems_attempted"],
            followers_count=viewer["followers_count"],
            profile_completeness=90.0,
            avg_code_quality=viewer["avg_code_quality"],
            account_age_days=viewer["account_age_days"],
        ),
        verified_skills=viewer["verified_skills"],
    ))
    assert 0.0 <= resp.prediction.reputation_score <= 100.0
    assert resp.prediction.band in {"newcomer", "contributor", "trusted", "elite"}
    assert len(resp.prediction.factors) == 6
    # every factor is auditable (non-empty detail)
    assert all(f.detail for f in resp.prediction.factors)
