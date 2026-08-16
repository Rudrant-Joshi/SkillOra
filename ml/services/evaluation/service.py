from __future__ import annotations

import time

from services.evaluation.ai_assisted import grade_with_ai
from services.evaluation.deterministic import DETERMINISTIC_EVALUATORS, is_deterministic
from services.evaluation.schemas import EvaluateRequest, EvaluationPrediction
from shared.config.settings import get_thresholds
from shared.logging.logger import log_inference
from shared.schemas.common import ErrorCode, MLException, MLResponse, new_request_id

SERVICE_VERSION = "evaluation-v1"


def evaluate(req: EvaluateRequest) -> MLResponse[EvaluationPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()
    thresholds = get_thresholds()["evaluation"]
    success = True
    error_code = None

    try:
        if is_deterministic(req.question_type):
            evaluator = DETERMINISTIC_EVALUATORS[req.question_type]
            score, reasoning = evaluator(req)
            prediction = EvaluationPrediction(
                score=score,
                evaluation_method="deterministic",
                reasoning=reasoning,
                needs_human_review=False,
            )
            confidence = 1.0
            evidence = ["deterministic_scoring"]

        elif req.question_type in ("short_answer", "system_design"):
            ai_result = grade_with_ai(
                req, confidence_review_floor=thresholds["needs_human_review_confidence_below"]
            )
            prediction = EvaluationPrediction(
                score=ai_result["score"],
                evaluation_method="ai_assisted",
                strengths=ai_result["strengths"],
                weaknesses=ai_result["weaknesses"],
                reasoning=ai_result["reasoning"],
                needs_human_review=ai_result["needs_human_review"],
            )
            confidence = ai_result["confidence"]
            evidence = [f"ai_assisted:{ai_result['model']}"]

        else:
            raise MLException(
                ErrorCode.VALIDATION_ERROR,
                f"Unsupported question_type '{req.question_type}' for evaluation.",
            )

        return MLResponse(
            request_id=request_id,
            model_version=SERVICE_VERSION,
            prediction=prediction,
            confidence=confidence,
            evidence=evidence,
            metadata={"question_id": req.question_id, "question_type": req.question_type},
        )
    except MLException as e:
        success = False
        error_code = e.code.value
        raise
    finally:
        log_inference(
            service="evaluation", model_version=SERVICE_VERSION, request_id=request_id,
            latency_ms=(time.perf_counter() - start) * 1000, confidence=None,
            success=success, error_code=error_code,
        )
