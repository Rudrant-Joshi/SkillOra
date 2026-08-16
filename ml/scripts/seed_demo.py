"""
Demo runner — shows the full ML connective tissue working end-to-end on a
deterministic seed graph:

    activity  ->  inferred skills  ->  auto profile
             ->  personalized feed (follows + skills)
    problem   ->  difficulty estimate
    skills    ->  learning path
    activity  ->  reputation

Run:  python scripts/seed_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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

TARGET_USER = "u1"  # alice


def _activities_to_models(activities):
    return [
        ActivitySummaryInput(
            activity_type=a["activity_type"],
            title=a["title"],
            description=a.get("description"),
            language=a.get("language"),
            skills_mentioned=a.get("skills_mentioned", []),
            created_at=a["created_at"],
        )
        for a in activities
    ]


def main() -> None:
    users = generate_seed_profiles()
    viewer = next(u for u in users if u["user_id"] == TARGET_USER)

    print("=" * 72)
    print(f"DEV-CONNECT DEMO  —  profile for @{viewer['username']}")
    print("=" * 72)

    # 1) ACTIVITY -> INFERRED SKILLS
    act_models = _activities_to_models(viewer["activities"])
    infer = infer_skills_from_activity(
        InferSkillsFromActivityRequest(user_id=viewer["user_id"], activities=act_models)
    )
    inferred = [f"{s.skill} ({s.inferred_level:.0%})" for s in infer.prediction.inferred_skills[:6]]
    print("\n[1] Inferred skills from activity (no manual list):")
    print("    " + ", ".join(inferred))

    # 2) ACTIVITY -> AUTO PROFILE
    summary = generate_profile_summary(
        GenerateProfileSummaryRequest(
            user_id=viewer["user_id"], username=viewer["username"], bio=viewer["bio"],
            activities=act_models, current_skills={},
        )
    )
    print("\n[2] Auto-generated profile (connections ARE the profile):")
    print(f'    "{summary.prediction.summary}"')
    print(f"    headline: {summary.prediction.suggested_headline}")

    # 3) FEED — follows + skill overlap drive ranking
    pool = build_feed_pool(users, viewer["user_id"])
    pool_models = [
        FeedActivityInput(**{k: p[k] for k in (
            "activity_id", "activity_type", "user_id", "username",
            "title", "description", "language", "skills_mentioned",
            "created_at", "engagement_count")})
        for p in pool
    ]
    viewer_skills = {s.skill: s.inferred_level for s in infer.prediction.inferred_skills}
    ranked = rank_feed_service(
        RankFeedRequest(
            viewer_id=viewer["user_id"], viewer_skills=viewer_skills,
            followed_user_ids=viewer["following"], candidate_pool=pool_models, top_k=5,
        )
    )
    print("\n[3] Personalized feed (top 5):")
    for item in ranked.prediction.ranked_items:
        owner = next(u["username"] for u in users if u["user_id"] == item.user_id)
        print(f"    - @{owner}: {item.activity_type} — {item.reason}")

    # 4) PROBLEM DIFFICULTY
    diff = estimate_difficulty(EstimateDifficultyRequest(
        title="Edit Distance", language="cpp",
        description="Compute minimum operations to convert one string to another "
                    "with insert, delete, replace using dynamic programming.",
        topics=["dynamic programming", "string"], test_cases_count=14, constraints_count=4,
    ))
    print("\n[4] Problem difficulty estimate:")
    print(f"    Edit Distance -> {diff.prediction.difficulty_label} "
          f"(score {diff.prediction.difficulty:.2f})")

    # 5) LEARNING PATH
    path = generate_path_service(GeneratePathRequest(
        user_id=viewer["user_id"], current_skills=viewer_skills,
        target_skills=["machine learning", "system design"], max_steps=5,
    ))
    print("\n[5] Learning path toward Machine Learning / System Design:")
    for step in path.prediction.steps:
        print(f"    {step.step_number}. {step.skill}  "
              f"({step.current_level:.0%} -> {step.target_level:.0%}, ~{step.estimated_hours}h)")

    # 6) REPUTATION
    rep = compute_reputation_service(ComputeReputationRequest(
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
    print("\n[6] Reputation (explainable trust score):")
    print(f"    {rep.prediction.reputation_score:.0f}/100  band={rep.prediction.band}  "
          f"verification_eligible={rep.prediction.verification_eligible}")

    print("\n" + "=" * 72)
    print("Your work became your profile automatically — no separate resume.")
    print("=" * 72)


if __name__ == "__main__":
    main()
