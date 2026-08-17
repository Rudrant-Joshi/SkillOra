"""
Learning Path service — turns skill gaps into an ordered, time-aware learning
plan and recommends the next milestone. Deterministic (master prompt §46).
"""
from __future__ import annotations

import time

from models.learning_path import generate_path, recommend_next_milestone
from services.learning_path.schemas import (
    GeneratePathRequest,
    LearningPathPrediction,
    LearningStep,
    MilestonePrediction,
    RecommendNextMilestoneRequest,
)
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "learning-path-v1"


def generate_path_service(req: GeneratePathRequest) -> MLResponse[LearningPathPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    result = generate_path(
        req.current_skills,
        req.target_skills,
        req.max_steps,
        req.time_budget_weeks,
    )

    steps = [
        LearningStep(
            step_number=i + 1,
            skill=s.skill,
            current_level=round(s.current_level, 4),
            target_level=round(s.target_level, 4),
            difficulty=s.difficulty,
            estimated_hours=s.estimated_hours,
            reason=s.reason,
            prerequisites=s.prerequisites,
        )
        for i, s in enumerate(result["steps"])
    ]

    prediction = LearningPathPrediction(
        steps=steps,
        total_estimated_hours=result["total_estimated_hours"],
        weeks_estimate=result["weeks_estimate"],
        confidence=0.75,
        prerequisites_warning=result["prerequisites_warning"],
    )
    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=0.75,
        evidence=[f"{len(steps)} step(s) planned to {len(req.target_skills)} target skill(s)"],
        metadata={"user_id": req.user_id},
    )
    log_inference(
        service="learning_path",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=0.75,
        success=True,
    )
    return response


def recommend_next_milestone_service(req: RecommendNextMilestoneRequest) -> MLResponse[MilestonePrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    best = recommend_next_milestone(
        req.current_skills, req.completed_milestones, req.candidate_skills
    )
    prediction = MilestonePrediction(**best)
    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=round(prediction.readiness_score, 4),
        evidence=[f"next_skill={prediction.next_skill}"],
        metadata={"user_id": req.user_id},
    )
    log_inference(
        service="learning_path",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=response.confidence,
        success=True,
    )
    return response
