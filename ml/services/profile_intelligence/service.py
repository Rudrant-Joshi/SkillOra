"""
Profile Intelligence service — the "your activity IS your profile" connective
tissue from the DevConnect pitch.

Three capabilities:
  - infer_skills_from_activity: detect skills from snippets/submissions, not
    from a self-reported list
  - generate_profile_summary: auto-generated profile text + headline
  - score_profile_completeness: how complete/verifyable the profile is

All run deterministically; the summary uses the LLM only when available and
degrades gracefully to a templated summary otherwise.
"""
from __future__ import annotations

import time

from models.profile_intelligence import (
    build_profile_summary,
    classify_profile_strength,
    infer_skills_from_activities,
    score_profile_completeness as score_profile_completeness_model,
    suggest_headline,
)
from services.profile_intelligence.schemas import (
    GenerateProfileSummaryRequest,
    InferSkillsFromActivityRequest,
    InferredSkillsPrediction,
    ProfileSummaryPrediction,
)
from shared.logging.logger import log_inference
from shared.model_router import ModelRouter
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "profile-intelligence-v1"

_SUMMARY_SYSTEM_PROMPT = """You write concise, professional developer profile
summaries (2-3 sentences). Use ONLY the provided facts: skills, activity
counts, and bio. Do not invent achievements, projects, or metrics. Be
specific and concrete. Write in third person."""


def infer_skills_from_activity(req: InferSkillsFromActivityRequest) -> MLResponse[InferredSkillsPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    results = infer_skills_from_activities(
        [a.model_dump() for a in req.activities], current_skills=req.current_skills
    )
    new_skills = [r.skill for r in results if r.skill.lower() not in (s.lower() for s in req.current_skills)]
    confidence = max((r.confidence for r in results), default=0.3)

    prediction = InferredSkillsPrediction(
        inferred_skills=[
            {
                "skill": r.skill,
                "inferred_level": round(r.inferred_level, 4),
                "confidence": round(r.confidence, 4),
                "evidence": r.evidence,
            }
            for r in results[:20]
        ],
        new_skills_detected=new_skills[:10],
        confidence=round(confidence, 4),
    )

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=round(confidence, 4),
        evidence=[f"inferred {len(results)} skill(s) from {len(req.activities)} activities"],
        metadata={"user_id": req.user_id},
    )
    log_inference(
        service="profile_intelligence",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=response.confidence,
        success=True,
    )
    return response


def generate_profile_summary(req: GenerateProfileSummaryRequest) -> MLResponse[ProfileSummaryPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()
    success = True

    infer_result = infer_skills_from_activities(
        [a.model_dump() for a in req.activities], current_skills=req.current_skills
    )
    top_skills = [r.skill for r in infer_result[:8]]

    completeness = score_profile_completeness_model(
        req.user_id, req.username, req.bio, [a.model_dump() for a in req.activities], req.current_skills
    )
    profile_strength = classify_profile_strength(completeness.score)
    headline = suggest_headline(req.username, top_skills, len(req.activities))

    summary = build_profile_summary(
        req.username, top_skills, len(req.activities), profile_strength, req.bio
    )
    confidence = 0.8

    try:
        if top_skills or req.activities:
            router = ModelRouter()
            try:
                facts = (
                    f"Username: {req.username}\n"
                    f"Bio: {req.bio or '(none)'}\n"
                    f"Top skills: {', '.join(top_skills)}\n"
                    f"Activity count: {len(req.activities)}\n"
                    f"Profile strength: {profile_strength}\n"
                )
                result = router.complete(
                    role="profile_summary_llm",
                    system=_SUMMARY_SYSTEM_PROMPT,
                    prompt=f"Write a 2-3 sentence profile summary from these facts:\n\n{facts}",
                    max_tokens=200,
                )
                if result.text and len(result.text.strip()) > 20:
                    summary = result.text.strip()
                    confidence = 0.85
            except Exception:
                # LLM is best-effort; deterministic summary already computed.
                pass
    except Exception:
        success = False
        raise

    prediction = ProfileSummaryPrediction(
        summary=summary,
        top_skills=top_skills,
        suggested_headline=headline,
        activity_count=len(req.activities),
        profile_strength=profile_strength,  # type: ignore[arg-type]
    )

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=confidence,
        evidence=[f"profile_strength={profile_strength}", f"top_skills={len(top_skills)}"],
        metadata={"user_id": req.user_id},
    )
    log_inference(
        service="profile_intelligence",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=confidence,
        success=success,
    )
    return response


def score_profile_completeness(req: "ScoreProfileCompletenessRequest") -> MLResponse["ProfileCompletenessPrediction"]:
    from services.profile_intelligence.schemas import (
        ProfileCompletenessPrediction,
        ScoreProfileCompletenessRequest,
    )

    request_id = new_request_id()
    start = time.perf_counter()
    completeness = score_profile_completeness_model(
        req.user_id, req.username, req.bio,
        [a.model_dump() for a in req.activities], req.current_skills
    )
    verified = completeness.score >= 80
    prediction = ProfileCompletenessPrediction(
        completeness_score=round(completeness.score, 2),
        band=completeness.band,  # type: ignore[arg-type]
        missing_fields=[],
        suggestions=["Push code, solve problems, and fill your bio to improve this score."],
        verification_eligible=verified,
    )
    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=0.9,
        evidence=[f"completeness={completeness.score:.1f}"],
        metadata={"user_id": req.user_id},
    )
    log_inference(
        service="profile_intelligence",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=0.9,
        success=True,
    )
    return response
