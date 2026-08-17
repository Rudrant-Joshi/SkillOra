from __future__ import annotations

import time

from services.adaptive_assessment.schemas import (
    AdaptiveSelectPrediction,
    AdaptiveSelectRequest,
    RecommendedAdaptiveQuestion,
)
from shared.config.settings import get_thresholds
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id
from services.adaptive_assessment.selector import select_next_question

SERVICE_VERSION = "adaptive-assessment-v1"


def select_adaptive_question(req: AdaptiveSelectRequest) -> MLResponse[AdaptiveSelectPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()
    thresholds = get_thresholds().get("adaptive_assessment", {})

    next_q = select_next_question(
        blueprint=req.blueprint,
        skill_profile=req.skill_profile,
        target_skills=req.target_skills,
        answered=req.answered_questions,
        remaining_pool=req.remaining_approved_pool,
    )

    current_estimates = {s: v.estimated_level for s, v in req.skill_profile.items()}
    current_confidence = {s: v.confidence for s, v in req.skill_profile.items()}
    progress = {}
    if next_q:
        bucket = "easy" if next_q.estimated_difficulty <= 0.33 else "medium" if next_q.estimated_difficulty <= 0.66 else "hard"
        progress = {bucket: 1}

    prediction = AdaptiveSelectPrediction(
        next_question=next_q,
        current_skill_estimates=current_estimates,
        updated_confidence=current_confidence,
        questions_answered=len(req.answered_questions),
        questions_remaining=req.blueprint.total_questions - len(req.answered_questions),
        blueprint_progress=progress,
    )

    evidence = [
        f"adaptive_select: pool_size={len(req.remaining_approved_pool)}",
        f"answered={len(req.answered_questions)}",
        f"blueprint_total={req.blueprint.total_questions}",
    ]
    confidence = 0.9 if next_q else 0.2
    if not next_q:
        evidence.append("no eligible question remaining in approved pool")

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=confidence,
        evidence=evidence,
        metadata={
            "candidate_id": req.candidate_id,
            "assessment_id": req.assessment_id,
            "note": "Selection is constrained to the caller-supplied approved pool and blueprint. No blueprint rules are modified.",
        },
    )

    log_inference(
        service="adaptive_assessment",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=confidence,
        success=True,
    )
    return response
