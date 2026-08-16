from __future__ import annotations

import time

from services.recommendation.schemas import (
    RecommendedQuestion,
    RecommendQuestionPrediction,
    RecommendQuestionRequest,
)
from services.recommendation.scoring import score_question
from shared.config.settings import get_thresholds
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "recommendation-v1"


def recommend_questions(req: RecommendQuestionRequest) -> MLResponse[RecommendQuestionPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()
    max_reexposure = get_thresholds()["recommendation"]["max_question_reexposure"]

    scored = []
    for q in req.approved_question_pool:
        if q.question_id in req.exclude_question_ids:
            continue
        score, reason = score_question(
            q, req.candidate_profile.skills, req.target_skills, max_reexposure
        )
        if score < 0:
            continue
        scored.append((q, score, reason))

    scored.sort(key=lambda t: t[1], reverse=True)
    top = scored[: req.top_k]

    recommendations = [
        RecommendedQuestion(question_id=q.question_id, selection_score=score, reason=reason)
        for q, score, reason in top
    ]

    confidence = 0.85 if recommendations else 0.2
    evidence = [f"scored {len(scored)} eligible question(s) from approved pool"]

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=RecommendQuestionPrediction(recommendations=recommendations),
        confidence=confidence,
        evidence=evidence,
        metadata={
            "candidate_id": req.candidate_id,
            "pool_size": len(req.approved_question_pool),
            "note": "Selection is constrained to the caller-supplied approved_question_pool only.",
        },
    )

    log_inference(
        service="recommendation", model_version=SERVICE_VERSION, request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000, confidence=confidence, success=True,
    )
    return response
