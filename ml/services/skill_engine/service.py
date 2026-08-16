from __future__ import annotations

import time

from models.skill_estimation.estimator import SkillEvidence, estimate_skill
from services.skill_engine.schemas import (
    BatchSkillEstimateRequest,
    SkillEstimatePrediction,
    SkillEstimateRequest,
)
from shared.config.settings import get_thresholds
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "skill-v1"


def _to_domain_evidence(items) -> list[SkillEvidence]:
    return [
        SkillEvidence(
            source=i.source,
            observed_value=i.observed_value,
            timestamp=i.timestamp,
            weight_override=i.weight_override,
            detail=i.detail or "",
        )
        for i in items
    ]


def estimate(req: SkillEstimateRequest) -> MLResponse[SkillEstimatePrediction]:
    request_id = new_request_id()
    start = time.perf_counter()
    thresholds = get_thresholds()["skill_engine"]

    result = estimate_skill(
        req.skill,
        _to_domain_evidence(req.evidence),
        half_life_days=thresholds["decay_half_life_days"],
        min_evidence_for_high_confidence=thresholds["min_evidence_for_high_confidence"],
        low_confidence_floor=thresholds["low_confidence_floor"],
    )

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=SkillEstimatePrediction(
            skill=result.skill,
            estimated_level=result.estimated_level,
            confidence=result.confidence,
            evidence_count=result.evidence_count,
        ),
        confidence=result.confidence,
        evidence=result.evidence,
        metadata={"user_id": req.user_id, "note": "estimated_level is a probabilistic estimate, not ground truth"},
    )

    log_inference(
        service="skill_engine", model_version=SERVICE_VERSION, request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000, confidence=result.confidence,
        success=True,
    )
    return response


def estimate_batch(req: BatchSkillEstimateRequest) -> dict[str, MLResponse[SkillEstimatePrediction]]:
    """Convenience for building a full learner skill profile in one call."""
    out = {}
    for skill, evidence in req.skills.items():
        out[skill] = estimate(SkillEstimateRequest(user_id=req.user_id, skill=skill, evidence=evidence))
    return out
