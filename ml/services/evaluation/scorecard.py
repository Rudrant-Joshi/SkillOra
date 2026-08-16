"""
Candidate Score Engine (master prompt §12): aggregates per-question
evaluation results into a multi-dimensional scorecard. Pure aggregation
over already-computed evaluation scores — no new modeling needed, so this
stays deterministic and explainable by construction.

This produces decision-support output only. It does not recommend
hire/no-hire (that's §13 Hiring Recommendation Engine — Phase 2 scope,
not built here) and it must never be treated as an automatic accept/reject
signal (master prompt §40, §31).
"""
from __future__ import annotations

import time
from collections import defaultdict

from pydantic import BaseModel, Field

from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "scorecard-v1"


class DimensionScoreInput(BaseModel):
    dimension: str  # e.g. "algorithms", "backend", "system_design"
    score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)
    question_id: str


class ScorecardRequest(BaseModel):
    candidate_id: str
    assessment_id: str
    dimension_scores: list[DimensionScoreInput]


class ScorecardPrediction(BaseModel):
    overall_score: float
    dimensions: dict[str, float]
    dimension_confidence: dict[str, float]


def build_scorecard(req: ScorecardRequest) -> MLResponse[ScorecardPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    by_dim: dict[str, list[DimensionScoreInput]] = defaultdict(list)
    for item in req.dimension_scores:
        by_dim[item.dimension].append(item)

    dimensions: dict[str, float] = {}
    dimension_confidence: dict[str, float] = {}
    evidence: list[str] = []

    for dim, items in by_dim.items():
        # confidence-weighted average within a dimension
        total_w = sum(i.confidence for i in items) or 1.0
        dimensions[dim] = round(sum(i.score * i.confidence for i in items) / total_w, 2)
        dimension_confidence[dim] = round(sum(i.confidence for i in items) / len(items), 4)
        evidence.append(f"{dim}: {len(items)} question(s) contributed")

    overall_score = round(sum(dimensions.values()) / len(dimensions), 2) if dimensions else 0.0
    overall_confidence = (
        round(sum(dimension_confidence.values()) / len(dimension_confidence), 4)
        if dimension_confidence else 0.0
    )

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=ScorecardPrediction(
            overall_score=overall_score,
            dimensions=dimensions,
            dimension_confidence=dimension_confidence,
        ),
        confidence=overall_confidence,
        evidence=evidence,
        metadata={
            "candidate_id": req.candidate_id,
            "assessment_id": req.assessment_id,
            "note": "Decision-support only. Not a hiring decision.",
        },
    )

    log_inference(
        service="scorecard", model_version=SERVICE_VERSION, request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000, confidence=overall_confidence,
        success=True,
    )
    return response
