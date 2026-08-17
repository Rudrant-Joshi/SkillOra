from __future__ import annotations

import time

from models.optimization.schemas import OptimizationRequest, OptimizationResponse
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "optimization-v1"


def optimize_model(req: OptimizationRequest) -> MLResponse[OptimizationResponse]:
    request_id = new_request_id()
    start = time.perf_counter()

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=OptimizationResponse(
            model_role=req.model_role,
            target_format=req.target_format,
            optimized=False,
            message="ONNX export pipeline is a stub. Implement with torch.onnx.export or equivalent when a trainable model is added.",
        ),
        confidence=1.0,
        evidence=["optimization_stub"],
    )

    log_inference(
        service="optimization",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=1.0,
        success=True,
    )
    return response
