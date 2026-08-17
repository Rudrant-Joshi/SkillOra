"""
Learning Path model (master prompt §8, §46).

Generates a personalized learning path from a learner's current skill levels
to a set of target skills, ordered so prerequisites come first and each step
builds on existing strength (zone of proximal development: pick the next
skill that is just beyond current ability). Deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LearningStepResult:
    skill: str
    current_level: float
    target_level: float
    difficulty: float
    estimated_hours: int
    reason: str
    prerequisites: list[str] = field(default_factory=list)


# Rough prerequisite graph (skill -> list of skills that help).
_PREREQS: dict[str, list[str]] = {
    "algorithms": ["data structures"],
    "dynamic programming": ["algorithms", "data structures"],
    "graph theory": ["algorithms", "data structures"],
    "system design": ["algorithms", "databases", "networking"],
    "react": ["javascript", "html", "css"],
    "angular": ["typescript", "html", "css"],
    "django": ["python", "sql"],
    "fastapi": ["python", "sql"],
    "spring": ["java"],
    "databases": ["sql"],
    "data science": ["python", "statistics"],
    "machine learning": ["python", "statistics", "data science"],
    "deep learning": ["machine learning", "python"],
    "devops": ["linux", "shell scripting"],
    "kubernetes": ["devops", "docker"],
    "docker": ["devops", "linux"],
}


def _level_for(skill: str, current: dict[str, float]) -> float:
    return float(current.get(skill.lower(), 0.0))


def _estimate_hours(current_level: float, target_level: float) -> int:
    gap = max(target_level - current_level, 0.0)
    # ~12 focused hours per 0.1 of skill gain, floored.
    return max(4, int(round(gap * 120)))


def generate_path(
    current_skills: dict[str, float],
    target_skills: list[str],
    max_steps: int,
    time_budget_weeks: int | None = None,
) -> dict[str, Any]:
    current_lower = {k.lower(): v for k, v in current_skills.items()}

    # Compute a "gap" for each target skill.
    targets = []
    for skill in target_skills:
        lskill = skill.lower()
        cur = current_lower.get(lskill, 0.0)
        gap = 1.0 - cur
        targets.append((skill, cur, gap))

    # Pre-sort by gap descending but inject prerequisites first.
    ordered: list[str] = []
    seen: set[str] = set()

    def _add(skill: str, cur_level: float):
        lskill = skill.lower()
        if lskill in seen:
            return
        seen.add(lskill)
        for prereq in _PREREQS.get(lskill, []):
            # include prereqs as steps too (even if partially known) so the
            # path strengthens foundations before advanced targets
            _add(prereq, current_lower.get(prereq, 0.0))
        ordered.append(skill)

    for skill, cur, _ in targets:
        _add(skill, cur)

    steps = []
    for i, skill in enumerate(ordered[:max_steps], start=1):
        lskill = skill.lower()
        cur = current_lower.get(lskill, 0.0)
        # target level: 0.8 unless it's an intermediate prereq already partly known
        target_level = 0.8 if lskill in {t.lower() for t, _, _ in targets} else 0.6
        difficulty = min(0.3 + (1.0 - cur) * 0.6, 1.0)
        prereqs = [p for p in _PREREQS.get(lskill, []) if p not in current_lower]
        steps.append(
            LearningStepResult(
                skill=skill,
                current_level=cur,
                target_level=target_level,
                difficulty=round(difficulty, 4),
                estimated_hours=_estimate_hours(cur, target_level),
                reason=f"Bridge gap from {cur:.0%} to {target_level:.0%} proficiency.",
                prerequisites=prereqs,
            )
        )

    total_hours = sum(s.estimated_hours for s in steps)
    if time_budget_weeks:
        weeks = float(time_budget_weeks)
    else:
        weeks = round(total_hours / 10.0, 1)

    warning = None
    missing_prereqs = sorted({p for s in steps for p in s.prerequisites})
    if missing_prereqs:
        warning = (
            f"This path assumes prior knowledge of: {', '.join(missing_prereqs)}. "
            "Add these as early milestones if they're new to you."
        )

    return {
        "steps": steps,
        "total_estimated_hours": total_hours,
        "weeks_estimate": weeks,
        "prerequisites_warning": warning,
    }


def recommend_next_milestone(
    current_skills: dict[str, float],
    completed_milestones: list[str],
    candidate_skills: list[str],
) -> dict[str, Any]:
    current_lower = {k.lower(): v for k, v in current_skills.items()}
    completed = {c.lower() for c in completed_milestones}

    best = None
    for skill in candidate_skills:
        lskill = skill.lower()
        if lskill in completed:
            continue
        cur = current_lower.get(lskill, 0.0)
        # readiness: higher if prerequisites are met and gap is in the
        # learner's zone of proximal development (~0.3-0.7 gap)
        prereqs = _PREREQS.get(lskill, [])
        prereq_readiness = (
            sum(min(current_lower.get(p, 0.0), 1.0) for p in prereqs) / len(prereqs)
            if prereqs else 0.5
        )
        gap = 1.0 - cur
        # prefer a skill that is challenging but within reach (gap ~0.5)
        challenge_fit = 1.0 - abs(gap - 0.5) * 1.5
        readiness = 0.7 * prereq_readiness + 0.3 * challenge_fit
        difficulty = min(0.3 + gap * 0.6, 1.0)
        if best is None or readiness > best["readiness_score"]:
            best = {
                "next_skill": skill,
                "difficulty": round(difficulty, 4),
                "estimated_hours": _estimate_hours(cur, 0.8),
                "reason": f"Best next step: {cur:.0%} now, gap of {gap:.0%} is in your learning zone.",
                "readiness_score": round(max(0.0, min(1.0, readiness)), 4),
            }

    if best is None:
        best = {
            "next_skill": candidate_skills[0],
            "difficulty": 0.5,
            "estimated_hours": 40,
            "reason": "Fallback: no clear readiness signal; pick a target skill.",
            "readiness_score": 0.3,
        }
    return best
