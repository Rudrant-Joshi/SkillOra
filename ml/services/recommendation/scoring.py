"""
Question selection scoring (master prompt §10).

Targets the "zone of proximal development": a question whose difficulty is
close to the candidate's current estimated level on its target skill(s) is
most informative (this is the same principle behind IRT-based adaptive
testing, kept here as an explainable heuristic rather than a full IRT
model — appropriate for Phase 1 per §46's "classical ML where sufficient").

Explicitly prevents (master prompt §10):
  - repeated exposure (times_shown_to_candidate / max_reexposure)
  - unauthorized company-private question access (filtered before scoring —
    caller is responsible for only passing an already-authorized pool;
    see gateway/deps.py for the authorization boundary)
"""
from __future__ import annotations

from services.recommendation.schemas import QuestionCandidate

# Weight on "does this target a weak skill" vs "how close is difficulty to level"
_SKILL_GAP_WEIGHT = 0.55
_DIFFICULTY_MATCH_WEIGHT = 0.45


def _candidate_level_for_question(skills_profile: dict[str, float], q_skills: list[str]) -> float:
    relevant = [skills_profile.get(s, 0.5) for s in q_skills]  # unknown skill -> neutral 0.5
    return sum(relevant) / len(relevant) if relevant else 0.5


def score_question(
    question: QuestionCandidate,
    skills_profile: dict[str, float],
    target_skills: list[str],
    max_reexposure: int,
) -> tuple[float, str]:
    if max_reexposure >= 0 and question.times_shown_to_candidate > max_reexposure:
        return -1.0, "excluded: exceeds allowed re-exposure count"

    candidate_level = _candidate_level_for_question(skills_profile, question.skills)
    # Best when question.difficulty ~= candidate_level (informative, not
    # trivially easy or hopelessly hard)
    difficulty_match = 1 - abs(question.difficulty - candidate_level)

    targets_weak_skill = any(s in target_skills for s in question.skills)
    weak_skill_bonus = 1.0 if targets_weak_skill else 0.4

    score = (
        _SKILL_GAP_WEIGHT * weak_skill_bonus
        + _DIFFICULTY_MATCH_WEIGHT * difficulty_match
    )

    reason_parts = []
    if targets_weak_skill:
        matched = [s for s in question.skills if s in target_skills]
        reason_parts.append(f"targets weak skill(s) {matched}")
    reason_parts.append(
        f"difficulty {question.difficulty:.2f} vs candidate level {candidate_level:.2f}"
    )
    reason = "; ".join(reason_parts)

    return round(score, 4), reason
