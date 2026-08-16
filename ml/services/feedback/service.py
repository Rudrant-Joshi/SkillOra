from __future__ import annotations

import time
import uuid

from services.feedback.schemas import FeedbackLogRequest, FeedbackLogResponse
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "feedback-v1"


def log_feedback(req: FeedbackLogRequest) -> MLResponse[FeedbackLogResponse]:
    request_id = new_request_id()
    start = time.perf_counter()

    feedback_id = f"fb_{uuid.uuid4().hex[:8]}"

    log_inference(
        service="feedback",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=None,
        success=True,
        extra={
            "feedback_id": feedback_id,
            "original_request_id": req.request_id,
            "service": req.service,
            "has_actual_outcome": req.actual_outcome is not None,
            "user_feedback": req.user_feedback,
        },
    )

    return MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=FeedbackLogResponse(logged=True, feedback_id=feedback_id),
        confidence=1.0,
        evidence=[f"feedback_logged:{feedback_id}"],
        metadata={"original_request_id": req.request_id},
    )
