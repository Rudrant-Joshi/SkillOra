from __future__ import annotations

import time

from services.batch.schemas import BatchRecommendRequest, BatchRecommendResponse
from services.recommendation.service import recommend_questions
from services.recommendation.schemas import RecommendQuestionRequest, CandidateSkillProfile, QuestionCandidate
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "batch-recommendation-v1"


def batch_recommend(req: BatchRecommendRequest) -> MLResponse[BatchRecommendResponse]:
    request_id = new_request_id()
    start = time.perf_counter()

    results: dict[str, list[dict]] = {}
    for candidate_id in req.candidate_ids:
        pool = [
            QuestionCandidate(
                question_id=q["question_id"],
                skills=q.get("skills", []),
                difficulty=float(q.get("difficulty", 0.5)),
                question_type=q.get("question_type", ""),
                times_shown_to_candidate=int(q.get("times_shown_to_candidate", 0)),
            )
            for q in req.approved_question_pool
        ]
        rec_req = RecommendQuestionRequest(
            candidate_id=candidate_id,
            candidate_profile=CandidateSkillProfile(skills={}),
            approved_question_pool=pool,
            top_k=req.top_k,
        )
        rec_resp = recommend_questions(rec_req)
        results[candidate_id] = [
            {"question_id": r.question_id, "selection_score": r.selection_score, "reason": r.reason}
            for r in rec_resp.prediction.recommendations
        ]

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=BatchRecommendResponse(results=results, total_candidates=len(req.candidate_ids)),
        confidence=0.8,
        evidence=[f"batch_recommend:{len(req.candidate_ids)} candidates"],
    )

    log_inference(
        service="batch_recommendation",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=0.8,
        success=True,
    )
    return response
