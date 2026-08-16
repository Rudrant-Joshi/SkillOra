"""
Developer Reputation service — an explainable trust/quality score for the
platform's public profiles, plus per-activity quality scoring. Deterministic
(master prompt §46: classical ML sufficient; explainability required since
reputation substitutes for a resume).
"""
from __future__ import annotations

import time

from models.reputation import compute_activity_quality, compute_reputation
from services.reputation.schemas import (
    ActivityQualityPrediction,
    ComputeActivityQualityRequest,
    ComputeReputationRequest,
    ReputationFactor,
    ReputationPrediction,
)
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "reputation-v1"


def compute_reputation_service(req: ComputeReputationRequest) -> MLResponse[ReputationPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    result = compute_reputation(req.activity.model_dump(), req.verified_skills)

    factors = [
        ReputationFactor(name=f["name"], contribution=f["contribution"], detail=f["detail"])
        for f in result.factors
    ]

    prediction = ReputationPrediction(
        reputation_score=result.score,
        band=result.band,  # type: ignore[arg-type]
        factors=factors,
        confidence=result.confidence,
        verification_eligible=result.verification_eligible,
    )
    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=result.confidence,
        evidence=[f"band={result.band}", f"score={result.score:.1f}"],
        metadata={"user_id": req.user_id},
    )
    log_inference(
        service="reputation",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=result.confidence,
        success=True,
    )
    return response


def compute_activity_quality_service(req: ComputeActivityQualityRequest) -> MLResponse[ActivityQualityPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    result = compute_activity_quality(
        req.activity_type,
        req.code_quality_score,
        req.test_pass_rate,
        req.has_description,
        req.engagement_count,
        req.novelty_score,
    )

    prediction = ActivityQualityPrediction(
        quality_score=result["quality_score"],
        quality_band=result["quality_band"],  # type: ignore[arg-type]
        strengths=result["strengths"],
        weaknesses=result["weaknesses"],
    )
    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=0.85,
        evidence=[f"band={result['quality_band']}"],
        metadata={"activity_type": req.activity_type},
    )
    log_inference(
        service="reputation",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=0.85,
        success=True,
    )
    return response
