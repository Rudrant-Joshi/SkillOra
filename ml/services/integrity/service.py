from __future__ import annotations

import time

from services.integrity.rule_engine import evaluate_signals
from services.integrity.risk_model import detect_anomalies
from services.integrity.schemas import (
    AnalyzeIntegrityRequest,
    ASTSimilarityResult,
    IntegrityPrediction,
)
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "integrity-v1"


def _build_ast_similarity(req: AnalyzeIntegrityRequest) -> ASTSimilarityResult | None:
    if req.submitted_code and req.reference_solution and req.language:
        from services.code_similarity.analyzer import compute_ast_similarity
        pct = compute_ast_similarity(req.submitted_code, req.reference_solution, req.language)
        return ASTSimilarityResult(max_similarity_pct=pct, comparison_type="reference_solution")
    return None


def analyze_integrity(req: AnalyzeIntegrityRequest) -> MLResponse[IntegrityPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    ast_sim = _build_ast_similarity(req)
    rule_score, rule_flags, band = evaluate_signals(req.signals)
    anomaly_flags = detect_anomalies(req.signals, ast_sim)
    all_flags = rule_flags + anomaly_flags

    explanation_parts = []
    if rule_score < 100:
        explanation_parts.append(f"Rule penalties brought score to {rule_score}.")
    if anomaly_flags:
        explanation_parts.append(f"Statistical anomalies detected: {[f.type for f in anomaly_flags]}.")
    if ast_sim and ast_sim.max_similarity_pct > 70:
        explanation_parts.append(f"High AST similarity ({ast_sim.max_similarity_pct:.1f}%) with reference solution.")

    explanation = " ".join(explanation_parts) if explanation_parts else "No integrity concerns detected."
    confidence = 0.75 if all_flags else 0.5

    prediction = IntegrityPrediction(
        integrity_score=rule_score,
        band=band,
        flags=all_flags,
        ast_similarity=ast_sim,
        explanation=explanation,
        confidence=confidence,
    )

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=confidence,
        evidence=[f"{f.type}:{f.count}" for f in all_flags[:10]],
        metadata={
            "candidate_id": req.candidate_id,
            "assessment_id": req.assessment_id,
            "note": "Decision-support only. Never auto-reject based on this score.",
        },
    )

    log_inference(
        service="integrity",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=confidence,
        success=True,
    )
    return response
