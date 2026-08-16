from __future__ import annotations

import time

from services.candidate_matching.matcher import match_candidate_to_job
from services.candidate_matching.schemas import (
    CandidateJobMatchPrediction,
    CandidateJobMatchRequest,
)
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "candidate-matching-v1"


def match(req: CandidateJobMatchRequest) -> MLResponse[CandidateJobMatchPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()
    prediction = match_candidate_to_job(req)

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=prediction.confidence,
        evidence=prediction.evidence,
        metadata={
            "job_id": req.job.job_id,
            "candidate_id": req.candidate.candidate_id,
            "note": "Decision-support only. Not a hiring decision.",
        },
    )

    log_inference(
        service="candidate_matching",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=prediction.confidence,
        success=True,
    )
    return response
