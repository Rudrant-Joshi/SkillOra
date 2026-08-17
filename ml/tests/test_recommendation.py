from services.recommendation.schemas import (
    CandidateSkillProfile,
    QuestionCandidate,
    RecommendQuestionRequest,
)
from services.recommendation.service import recommend_questions


def _pool():
    return [
        QuestionCandidate(question_id="q_easy_sql", skills=["sql"], difficulty=0.2, question_type="sql"),
        QuestionCandidate(question_id="q_hard_sql", skills=["sql"], difficulty=0.9, question_type="sql"),
        QuestionCandidate(question_id="q_mid_sql", skills=["sql"], difficulty=0.55, question_type="sql"),
        QuestionCandidate(question_id="q_python", skills=["python"], difficulty=0.5, question_type="coding"),
    ]


def test_recommends_within_approved_pool_only():
    req = RecommendQuestionRequest(
        candidate_id="c1",
        candidate_profile=CandidateSkillProfile(skills={"sql": 0.6, "python": 0.8}),
        approved_question_pool=_pool(),
        target_skills=["sql"],
        top_k=1,
    )
    resp = recommend_questions(req)
    assert len(resp.prediction.recommendations) == 1
    assert resp.prediction.recommendations[0].question_id in {q.question_id for q in _pool()}


def test_prefers_difficulty_near_candidate_level():
    req = RecommendQuestionRequest(
        candidate_id="c1",
        candidate_profile=CandidateSkillProfile(skills={"sql": 0.55}),
        approved_question_pool=_pool(),
        target_skills=["sql"],
        top_k=1,
    )
    resp = recommend_questions(req)
    assert resp.prediction.recommendations[0].question_id == "q_mid_sql"


def test_excludes_previously_shown_questions():
    req = RecommendQuestionRequest(
        candidate_id="c1",
        candidate_profile=CandidateSkillProfile(skills={"sql": 0.55}),
        approved_question_pool=_pool(),
        target_skills=["sql"],
        exclude_question_ids=["q_mid_sql"],
        top_k=1,
    )
    resp = recommend_questions(req)
    assert resp.prediction.recommendations[0].question_id != "q_mid_sql"


def test_respects_reexposure_limit():
    pool = [
        QuestionCandidate(
            question_id="q_seen", skills=["sql"], difficulty=0.5, question_type="sql",
            times_shown_to_candidate=5,
        )
    ]
    req = RecommendQuestionRequest(
        candidate_id="c1",
        candidate_profile=CandidateSkillProfile(skills={"sql": 0.5}),
        approved_question_pool=pool,
        target_skills=["sql"],
        top_k=1,
    )
    resp = recommend_questions(req)
    assert len(resp.prediction.recommendations) == 0
