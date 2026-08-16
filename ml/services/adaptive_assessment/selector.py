"""
Adaptive question selector (master prompt §8).

Critical rules:
  - The ML model must NOT change duration, number of questions, allowed skills,
    question types, difficulty distribution, scoring rules, or coding language
    restrictions.
  - It selects ONLY among approved questions supplied by the caller.
  - It does NOT redefine the examination.

This module is deterministic: no LLM calls. It uses skill-estimate-weighted
scoring similar to the question recommendation engine, plus blueprint-progress
tracking to ensure the adaptive path stays inside the recruiter-approved
blueprint constraints.
"""
from __future__ import annotations

from collections import defaultdict

from services.adaptive_assessment.schemas import (
    AssessmentHistoryEntry,
    QuestionBlueprintConstraints,
    RecommendedAdaptiveQuestion,
    SkillEstimateInput,
)


_SKILL_GAP_WEIGHT = 0.55
_DIFFICULTY_MATCH_WEIGHT = 0.45


def _candidate_level(skill_profile: dict[str, SkillEstimateInput], skills: list[str]) -> float:
    relevant = [skill_profile.get(s, SkillEstimateInput(skill=s, estimated_level=0.5, confidence=0.0)).estimated_level for s in skills]
    return sum(relevant) / len(relevant) if relevant else 0.5


def _difficulty_bucket(difficulty: float) -> str:
    if difficulty <= 0.33:
        return "easy"
    if difficulty <= 0.66:
        return "medium"
    return "hard"


def _blueprint_progress(blueprint: QuestionBlueprintConstraints, history: list[AssessmentHistoryEntry]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for entry in history:
        bucket = _difficulty_bucket(entry.difficulty)
        counts[bucket] += 1
    return dict(counts)


def _is_question_allowed(question: dict, blueprint: QuestionBlueprintConstraints) -> bool:
    q_type = question.get("question_type", "")
    q_lang = question.get("language", "")
    q_skills = [s.lower() for s in question.get("skills", [])]
    if blueprint.allowed_question_types and q_type not in blueprint.allowed_question_types:
        return False
    if q_type in ("coding", "sql") and blueprint.coding_languages:
        if q_lang and q_lang.lower() not in [l.lower() for l in blueprint.coding_languages]:
            return False
    if blueprint.allowed_skills:
        if not any(s in [a.lower() for a in blueprint.allowed_skills] for s in q_skills):
            return False
    return True


def select_next_question(
    blueprint: QuestionBlueprintConstraints,
    skill_profile: dict[str, SkillEstimateInput],
    target_skills: list[str],
    answered: list[AssessmentHistoryEntry],
    remaining_pool: list[dict],
) -> RecommendedAdaptiveQuestion | None:
    answered_ids = {e.question_id for e in answered}
    eligible = [
        q for q in remaining_pool
        if q.get("question_id") not in answered_ids and _is_question_allowed(q, blueprint)
    ]

    if not eligible:
        return None

    progress = _blueprint_progress(blueprint, answered)
    total_answered = len(answered)

    def score_question(q: dict) -> tuple[float, str]:
        q_skills = [s.lower() for s in q.get("skills", [])]
        difficulty = float(q.get("difficulty", 0.5))
        candidate_level = _candidate_level(skill_profile, q_skills)

        difficulty_match = 1.0 - abs(difficulty - candidate_level)
        targets_weak = any(s in [t.lower() for t in target_skills] for s in q_skills) if target_skills else False
        weak_skill_bonus = 1.0 if targets_weak else 0.4

        selection_score = _SKILL_GAP_WEIGHT * weak_skill_bonus + _DIFFICULTY_MATCH_WEIGHT * difficulty_match

        bucket = _difficulty_bucket(difficulty)
        bucket_reason = f"difficulty bucket '{bucket}' count so far: {progress.get(bucket, 0)}/{blueprint.total_questions}"
        target_reason = f"targets weak skill(s) {[s for s in q_skills if s in [t.lower() for t in target_skills]]}" if targets_weak else "exploration"
        reason = f"{target_reason}; {bucket_reason}"

        return selection_score, reason

    scored = [(q, *score_question(q)) for q in eligible]
    scored.sort(key=lambda t: t[1], reverse=True)
    best_q, best_score, best_reason = scored[0]

    q_skills = [s.lower() for s in best_q.get("skills", [])]
    primary_skill = q_skills[0] if q_skills else "unknown"
    difficulty = float(best_q.get("difficulty", 0.5))
    bucket = _difficulty_bucket(difficulty)

    return RecommendedAdaptiveQuestion(
        question_id=best_q["question_id"],
        selection_score=round(best_score, 4),
        reason=best_reason,
        skill_targeted=primary_skill,
        estimated_difficulty=difficulty,
        blueprint_alignment={
            "difficulty_bucket": bucket,
            "bucket_count_so_far": str(progress.get(bucket, 0)),
            "total_answered": str(total_answered),
            "within_allowed_skills": str(_is_question_allowed(best_q, blueprint)),
        },
    )
