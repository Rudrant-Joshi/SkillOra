"""
Problem Difficulty service — estimates and calibrates difficulty for the judge
problem bank. Deterministic; no LLM required (master prompt §46).
"""
from __future__ import annotations

import time

from models.problem_difficulty import (
    calibrate_difficulty,
    estimate_difficulty_heuristic,
)
from services.problem_difficulty.schemas import (
    CalibrateDifficultyRequest,
    CalibratedDifficultyPrediction,
    EstimateDifficultyRequest,
    DifficultyPrediction,
)
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "problem-difficulty-v1"


def estimate_difficulty(req: EstimateDifficultyRequest) -> MLResponse[DifficultyPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    est = estimate_difficulty_heuristic(
        req.title,
        req.description,
        req.starter_code,
        req.test_cases_count,
        req.constraints_count,
        req.topics,
    )

    prediction = DifficultyPrediction(
        difficulty=est.difficulty,
        difficulty_label=est.label,
        confidence=est.confidence,
        reasoning=est.reasoning,
        signal_scores=est.signal_scores,
    )
    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=est.confidence,
        evidence=[f"heuristic:{est.label}"],
        metadata={"title": req.title},
    )
    log_inference(
        service="problem_difficulty",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=est.confidence,
        success=True,
    )
    return response


def calibrate_difficulty_service(req: CalibrateDifficultyRequest) -> MLResponse[CalibratedDifficultyPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    outcomes = [o.model_dump() for o in req.submission_outcomes]
    est = calibrate_difficulty(outcomes, req.prior_difficulty)

    prediction = CalibratedDifficultyPrediction(
        calibrated_difficulty=est.difficulty,
        difficulty_label=est.label,
        confidence=est.confidence,
        sample_size=len(outcomes),
        pass_rate=est.signal_scores.get("pass_rate", 0.0),
        reasoning=est.reasoning,
    )
    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=est.confidence,
        evidence=[f"calibrated:{est.label}", f"n={len(outcomes)}"],
        metadata={"problem_id": req.problem_id},
    )
    log_inference(
        service="problem_difficulty",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=est.confidence,
        success=True,
    )
    return response
