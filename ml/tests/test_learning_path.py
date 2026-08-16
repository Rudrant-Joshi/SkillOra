from services.learning_path.schemas import (
    GeneratePathRequest,
    RecommendNextMilestoneRequest,
)
from services.learning_path.service import (
    generate_path_service,
    recommend_next_milestone_service,
)


def test_generate_path_orders_prerequisites_first():
    req = GeneratePathRequest(
        user_id="u1",
        current_skills={"python": 0.5},
        target_skills=["machine learning"],
        max_steps=5,
    )
    resp = generate_path_service(req)
    skills = [s.skill for s in resp.prediction.steps]
    # prerequisites of ML (data science, statistics, python) should appear first
    assert "machine learning" in skills
    assert "python" in skills
    # python (already known) should come before machine learning
    assert skills.index("python") < skills.index("machine learning")
    assert resp.prediction.total_estimated_hours > 0
    assert resp.prediction.weeks_estimate > 0


def test_generate_path_respects_time_budget_weeks():
    req = GeneratePathRequest(
        user_id="u1",
        current_skills={},
        target_skills=["react", "django"],
        time_budget_weeks=4,
        max_steps=10,
    )
    resp = generate_path_service(req)
    assert resp.prediction.weeks_estimate <= 4.5  # roughly within budget
    assert len(resp.prediction.steps) >= 1


def test_recommend_next_milestone_readiness():
    req = RecommendNextMilestoneRequest(
        user_id="u1",
        current_skills={"python": 0.6, "sql": 0.5},
        completed_milestones=[],
        candidate_skills=["django", "machine learning", "rust"],
    )
    resp = recommend_next_milestone_service(req)
    # django needs python (have) + sql (have) -> higher readiness than ML
    assert resp.prediction.next_skill == "django"
    assert 0.0 <= resp.prediction.readiness_score <= 1.0


def test_recommend_next_milestone_skips_completed():
    req = RecommendNextMilestoneRequest(
        user_id="u1",
        current_skills={"python": 0.6},
        completed_milestones=["django"],
        candidate_skills=["django", "fastapi"],
    )
    resp = recommend_next_milestone_service(req)
    assert resp.prediction.next_skill == "fastapi"
