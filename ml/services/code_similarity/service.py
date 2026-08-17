from __future__ import annotations

import time

from services.code_similarity.analyzer import compute_ast_similarity
from services.code_similarity.schemas import CodeSimilarityPrediction, CodeSimilarityRequest
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "code-similarity-v1"


def compute_similarity(req: CodeSimilarityRequest) -> MLResponse[CodeSimilarityPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    similarity = compute_ast_similarity(
        candidate_code=req.candidate_code,
        reference_code=req.reference_code or "",
        language=req.language,
    )

    confidence = 0.8 if req.reference_code else 0.3
    evidence = [f"ast+token_similarity={similarity:.4f}"]

    prediction = CodeSimilarityPrediction(
        similarity=round(similarity, 4),
        method="ast+embedding",
        comparison=req.comparison_type,
        confidence=confidence,
    )

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=confidence,
        evidence=evidence,
        metadata={"language": req.language},
    )

    log_inference(
        service="code_similarity",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=confidence,
        success=True,
    )
    return response
