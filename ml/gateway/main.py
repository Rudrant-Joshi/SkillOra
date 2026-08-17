"""
ML Gateway — FastAPI app implementing the ML Service API Contract (§25).

Thin HTTP shell: every route validates input via Pydantic, calls a plain
service function, and returns MLResponse or MLErrorResponse. No business
logic lives here — see services/*.
"""
from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from gateway.deps import get_auth_context
from services.adaptive_assessment.schemas import AdaptiveSelectRequest
from services.adaptive_assessment.service import select_adaptive_question
from services.activity_feed.schemas import (
    DetectTrendingRequest,
    RankFeedRequest,
    SuggestConnectionsRequest,
)
from services.activity_feed.service import (
    detect_trending_service,
    rank_feed_service,
    suggest_connections_service,
)
from services.analytics.schemas import AnalyticsQuery
from services.analytics.service import summarize_analytics
from services.batch.schemas import BatchRecommendRequest
from services.batch.service import batch_recommend
from services.candidate_matching.schemas import CandidateJobMatchRequest
from services.candidate_matching.service import match
from services.code_intelligence.schemas import CodeAnalysisRequest
from services.code_intelligence.service import analyze_code
from services.code_similarity.schemas import CodeSimilarityRequest
from services.code_similarity.service import compute_similarity
from services.content_generation.schemas import GenerateQuestionRequest
from services.content_generation.service import create_question
from services.evaluation.schemas import EvaluateRequest
from services.evaluation.scorecard import ScorecardRequest, build_scorecard
from services.evaluation.service import evaluate
from services.feedback.schemas import FeedbackLogRequest
from services.feedback.service import log_feedback
from services.integrity.schemas import AnalyzeIntegrityRequest
from services.integrity.service import analyze_integrity
from services.learning_path.schemas import (
    GeneratePathRequest,
    RecommendNextMilestoneRequest,
)
from services.learning_path.service import (
    generate_path_service,
    recommend_next_milestone_service,
)
from services.problem_difficulty.schemas import (
    CalibrateDifficultyRequest,
    EstimateDifficultyRequest,
)
from services.problem_difficulty.service import (
    calibrate_difficulty_service,
    estimate_difficulty,
)
from services.profile_intelligence.schemas import (
    GenerateProfileSummaryRequest,
    InferSkillsFromActivityRequest,
    ScoreProfileCompletenessRequest,
)
from services.profile_intelligence.service import (
    generate_profile_summary,
    infer_skills_from_activity,
    score_profile_completeness,
)
from services.rag.schemas import RagQueryRequest
from services.rag.service import query_rag
from services.rag.vector_store import InMemoryVectorStore
from services.recommendation.schemas import RecommendQuestionRequest
from services.recommendation.service import recommend_questions
from services.reputation.schemas import (
    ComputeActivityQualityRequest,
    ComputeReputationRequest,
)
from services.reputation.service import (
    compute_activity_quality_service,
    compute_reputation_service,
)
from services.skill_engine.schemas import BatchSkillEstimateRequest, SkillEstimateRequest
from services.skill_engine.service import estimate, estimate_batch
from services.study_assistant.schemas import StudyAssistRequest
from services.study_assistant.service import generate_study_assist
from shared.schemas.common import AuthContext, MLErrorResponse, MLException

app = FastAPI(
    title="Skillora ML Gateway",
    version="1.0.0",
    description="ML/AI intelligence layer — Phase 1 MVP. See README.md and docs/API.md.",
)

# Process-lifetime in-memory vector store for Phase 1 / local dev.
# A real deployment binds this to the platform vector database instead —
# see services/rag/vector_store.py for the swap point.
_vector_store = InMemoryVectorStore()


@app.exception_handler(MLException)
async def ml_exception_handler(request, exc: MLException):
    status_map = {
        "VALIDATION_ERROR": 422,
        "UNAUTHORIZED_SCOPE": 403,
        "NOT_FOUND": 404,
        "RATE_LIMITED": 429,
        "MODEL_UNAVAILABLE": 503,
        "UNSUPPORTED_LANGUAGE": 422,
        "CONTENT_POLICY": 422,
        "INTERNAL_ERROR": 500,
    }
    from shared.schemas.common import new_request_id

    body = MLErrorResponse(
        request_id=new_request_id(), error={"code": exc.code, "message": exc.message}
    )
    return JSONResponse(status_code=status_map.get(exc.code.value, 500), content=body.model_dump())


@app.get("/health")
def health():
    return {"status": "ok"}


# ---- Code Intelligence -----------------------------------------------------

@app.post("/ml/code/analyze")
def code_analyze(req: CodeAnalysisRequest, auth: AuthContext = Depends(get_auth_context)):
    return analyze_code(req)


@app.post("/ml/code/explain")
def code_explain(req: CodeAnalysisRequest, auth: AuthContext = Depends(get_auth_context)):
    req.task = "explain"
    return analyze_code(req)


@app.post("/ml/code/review")
def code_review(req: CodeAnalysisRequest, auth: AuthContext = Depends(get_auth_context)):
    req.task = "review"
    return analyze_code(req)


# ---- Assessment Evaluation --------------------------------------------------

@app.post("/ml/assessment/evaluate")
def assessment_evaluate(req: EvaluateRequest, auth: AuthContext = Depends(get_auth_context)):
    return evaluate(req)


@app.post("/ml/assessment/select-question")
def assessment_select_question(
    req: RecommendQuestionRequest, auth: AuthContext = Depends(get_auth_context)
):
    return recommend_questions(req)


@app.post("/ml/assessment/scorecard")
def assessment_scorecard(req: ScorecardRequest, auth: AuthContext = Depends(get_auth_context)):
    return build_scorecard(req)


# ---- Skill Estimation --------------------------------------------------------

@app.post("/ml/skill/estimate")
def skill_estimate(req: SkillEstimateRequest, auth: AuthContext = Depends(get_auth_context)):
    return estimate(req)


@app.post("/ml/skill/estimate-batch")
def skill_estimate_batch(
    req: BatchSkillEstimateRequest, auth: AuthContext = Depends(get_auth_context)
):
    return estimate_batch(req)


# ---- Recommendations ---------------------------------------------------------

@app.post("/ml/recommendations")
def recommendations(req: RecommendQuestionRequest, auth: AuthContext = Depends(get_auth_context)):
    return recommend_questions(req)


# ---- RAG ----------------------------------------------------------------------

@app.post("/ml/rag/query")
def rag_query(req: RagQueryRequest, auth: AuthContext = Depends(get_auth_context)):
    return query_rag(req, store=_vector_store)


# ---- Adaptive Assessment (Phase 2) --------------------------------------------

@app.post("/ml/assessment/adaptive/select-question")
def adaptive_select_question(req: AdaptiveSelectRequest, auth: AuthContext = Depends(get_auth_context)):
    return select_adaptive_question(req)


# ---- Candidate-Job Matching (Phase 2) -----------------------------------------

@app.post("/ml/candidate/match")
def candidate_match(req: CandidateJobMatchRequest, auth: AuthContext = Depends(get_auth_context)):
    return match(req)


# ---- Integrity (Phase 3) -------------------------------------------------------

@app.post("/ml/integrity/analyze")
def integrity_analyze(req: AnalyzeIntegrityRequest, auth: AuthContext = Depends(get_auth_context)):
    return analyze_integrity(req)


# ---- Code Similarity (Phase 3) -------------------------------------------------

@app.post("/ml/code/similarity")
def code_similarity(req: CodeSimilarityRequest, auth: AuthContext = Depends(get_auth_context)):
    return compute_similarity(req)


# ---- Study Assistant (Phase 3) -------------------------------------------------

@app.post("/ml/study/assist")
def study_assist(req: StudyAssistRequest, auth: AuthContext = Depends(get_auth_context)):
    return generate_study_assist(req)


# ---- Content Generation (Phase 3) ----------------------------------------------

@app.post("/ml/assessment/generate")
def assessment_generate(req: GenerateQuestionRequest, auth: AuthContext = Depends(get_auth_context)):
    return create_question(req)


# ---- Feedback / Continuous Learning (Phase 4) ----------------------------------

@app.post("/ml/feedback/log")
def feedback_log(req: FeedbackLogRequest, auth: AuthContext = Depends(get_auth_context)):
    return log_feedback(req)


# ---- Analytics (Phase 4) -------------------------------------------------------

@app.post("/ml/analytics/summary")
def analytics_summary(req: AnalyticsQuery, auth: AuthContext = Depends(get_auth_context)):
    return summarize_analytics(req)


# ---- Batch Recommendation (Phase 4) --------------------------------------------

@app.post("/ml/batch/recommend")
def batch_recommend(req: BatchRecommendRequest, auth: AuthContext = Depends(get_auth_context)):
    return batch_recommend(req)


# ===== New in Phase 1.5 — DevConnect connective-tissue ML ======================


# ---- Profile Intelligence ------------------------------------------------------

@app.post("/ml/profile/summary")
def profile_summary(req: GenerateProfileSummaryRequest, auth: AuthContext = Depends(get_auth_context)):
    return generate_profile_summary(req)


@app.post("/ml/profile/infer-skills")
def profile_infer_skills(req: InferSkillsFromActivityRequest, auth: AuthContext = Depends(get_auth_context)):
    return infer_skills_from_activity(req)


@app.post("/ml/profile/completeness")
def profile_completeness(req: ScoreProfileCompletenessRequest, auth: AuthContext = Depends(get_auth_context)):
    return score_profile_completeness(req)


# ---- Activity Feed ------------------------------------------------------------

@app.post("/ml/feed/rank")
def feed_rank(req: RankFeedRequest, auth: AuthContext = Depends(get_auth_context)):
    return rank_feed_service(req)


@app.post("/ml/feed/trending")
def feed_trending(req: DetectTrendingRequest, auth: AuthContext = Depends(get_auth_context)):
    return detect_trending_service(req)


@app.post("/ml/connections/suggest")
def connections_suggest(req: SuggestConnectionsRequest, auth: AuthContext = Depends(get_auth_context)):
    return suggest_connections_service(req)


# ---- Problem Difficulty (Judge) ------------------------------------------------

@app.post("/ml/problem/difficulty/estimate")
def problem_difficulty_estimate(req: EstimateDifficultyRequest, auth: AuthContext = Depends(get_auth_context)):
    return estimate_difficulty(req)


@app.post("/ml/problem/difficulty/calibrate")
def problem_difficulty_calibrate(req: CalibrateDifficultyRequest, auth: AuthContext = Depends(get_auth_context)):
    return calibrate_difficulty_service(req)


# ---- Learning Path ------------------------------------------------------------

@app.post("/ml/learning/path")
def learning_path(req: GeneratePathRequest, auth: AuthContext = Depends(get_auth_context)):
    return generate_path_service(req)


@app.post("/ml/learning/next-milestone")
def learning_next_milestone(req: RecommendNextMilestoneRequest, auth: AuthContext = Depends(get_auth_context)):
    return recommend_next_milestone_service(req)


# ---- Developer Reputation ------------------------------------------------------

@app.post("/ml/reputation/compute")
def reputation_compute(req: ComputeReputationRequest, auth: AuthContext = Depends(get_auth_context)):
    return compute_reputation_service(req)


@app.post("/ml/reputation/activity-quality")
def reputation_activity_quality(req: ComputeActivityQualityRequest, auth: AuthContext = Depends(get_auth_context)):
    return compute_activity_quality_service(req)
