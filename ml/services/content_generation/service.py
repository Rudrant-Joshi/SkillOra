from __future__ import annotations

import time

from services.content_generation.question_generator import generate_question
from services.content_generation.schemas import GenerateQuestionPrediction, GenerateQuestionRequest
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "content-generation-v1"


def create_question(req: GenerateQuestionRequest) -> MLResponse[GenerateQuestionPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()
    result = generate_question(req)

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=result,
        confidence=result.confidence,
        evidence=["llm_draft", f"type={req.question_type}"],
        metadata={
            "draft_id": result.draft.draft_id,
            "note": "This is an AI-generated draft. It requires recruiter review and approval before publishing.",
        },
    )

    log_inference(
        service="content_generation",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=result.confidence,
        success=True,
    )
    return response
