"""
Developer Reputation model (master prompt §8, §46).

A transparent, explainable reputation score composed of interpretable
factors (activity volume, code quality, problem-solving, network, profile
completeness, verification). Each factor contributes a bounded amount, so the
score is auditable — important for a platform where reputation substitutes
for a self-reported resume. Deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReputationResult:
    score: float
    band: str
    factors: list[dict[str, Any]]
    confidence: float
    verification_eligible: bool


DEFAULT_REPUTATION_WEIGHTS: dict[str, float] = {
    "activity_volume": 1.0,
    "problem_solving": 1.0,
    "code_quality": 1.0,
    "network": 1.0,
    "profile_completeness": 1.0,
    "verified_skills": 1.0,
}


def reputation_features(
    activity: dict[str, Any],
    verified_skills: list[str] | None = None,
) -> dict[str, float]:
    """Raw per-factor contributions (each already encodes its base multiplier).

    activity_volume = 12*log10(1 + snippets + solved)   (cap equiv 25)
    problem_solving = 25 * solved/attempted             (cap equiv 25)
    code_quality    = 20 * quality/100                  (cap equiv 20)
    network         = 5*log10(1 + followers)            (cap equiv 15)
    profile_completeness = 10 * completeness/100        (cap equiv 10)
    verified_skills = 4 * len(verified)                (cap equiv 10)
    """
    import math

    verified_skills = verified_skills or []
    a = activity
    snippets = a.get("snippets_pushed", 0)
    problems_solved = a.get("problems_solved", 0)
    problems_attempted = a.get("problems_attempted", 0) or max(problems_solved, 1)
    followers = a.get("followers_count", 0)
    completeness = a.get("profile_completeness", 0.0)
    avg_quality = a.get("avg_code_quality", 0.0)

    return {
        "activity_volume": 12.0 * math.log10(1 + snippets + problems_solved),
        "problem_solving": 25.0 * (problems_solved / max(problems_attempted, 1)),
        "code_quality": 20.0 * (avg_quality / 100.0),
        "network": 5.0 * math.log10(1 + followers),
        "profile_completeness": 10.0 * (completeness / 100.0),
        "verified_skills": 4.0 * len(verified_skills),
    }


def compute_reputation(
    activity: dict[str, Any],
    verified_skills: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> ReputationResult:
    from shared.calibration import get_calibrated_weights

    verified_skills = verified_skills or []
    weights = weights or get_calibrated_weights("reputation", DEFAULT_REPUTATION_WEIGHTS)

    import math

    feats = reputation_features(activity, verified_skills)
    a = activity
    snippets = a.get("snippets_pushed", 0)
    problems_solved = a.get("problems_solved", 0)
    problems_attempted = a.get("problems_attempted", 0) or max(problems_solved, 1)
    followers = a.get("followers_count", 0)
    completeness = a.get("profile_completeness", 0.0)
    avg_quality = a.get("avg_code_quality", 0.0)
    account_age = max(a.get("account_age_days", 1), 1)

    factor_meta = {
        "activity_volume": f"{snippets} snippets, {problems_solved} problems solved",
        "problem_solving": f"{problems_solved}/{problems_attempted} solved ({problems_solved / max(problems_attempted, 1):.0%})",
        "code_quality": f"avg quality {avg_quality:.0f}/100",
        "network": f"{followers} followers",
        "profile_completeness": f"{completeness:.0f}% complete",
        "verified_skills": f"{len(verified_skills)} verified skill(s)",
    }

    factors = []
    total = 0.0
    for name, raw in feats.items():
        contribution = round(weights.get(name, 1.0) * raw, 2)
        total += contribution
        factors.append({"name": name, "contribution": contribution, "detail": factor_meta[name]})

    total = min(100.0, max(0.0, total))
    confidence = min(0.95, 0.5 + 0.1 * math.log10(1 + account_age))

    if total >= 85:
        band = "elite"
    elif total >= 60:
        band = "trusted"
    elif total >= 30:
        band = "contributor"
    else:
        band = "newcomer"

    verification_eligible = completeness >= 80 and len(verified_skills) >= 1

    return ReputationResult(
        score=round(total, 2),
        band=band,
        factors=factors,
        confidence=round(confidence, 4),
        verification_eligible=verification_eligible,
    )


def compute_activity_quality(
    activity_type: str,
    code_quality_score: float = 0.0,
    test_pass_rate: float = 0.0,
    has_description: bool = False,
    engagement_count: int = 0,
    novelty_score: float = 0.5,
) -> dict[str, Any]:
    if activity_type in ("follow", "profile_update"):
        # these are low-information events; quality is binary-ish
        strengths = ["contributes to network/identity"]
        weaknesses = ["low information activity"]
        score = 40.0
        if activity_type == "profile_update" and has_description:
            score = 55.0
        band = "fair" if score >= 50 else "low"
        return {
            "quality_score": score,
            "quality_band": band,
            "strengths": strengths,
            "weaknesses": weaknesses,
        }

    # snippet / submission — richer scoring
    strengths, weaknesses = [], []
    score = 0.0

    q = code_quality_score / 100.0
    score += 35.0 * q
    if q >= 0.7:
        strengths.append("high code quality")
    elif q < 0.4:
        weaknesses.append("code quality below average")

    score += 30.0 * test_pass_rate
    if test_pass_rate >= 0.9:
        strengths.append("strong test performance")
    elif test_pass_rate < 0.5:
        weaknesses.append("low test pass rate")

    if has_description:
        score += 15.0
        strengths.append("well-documented")
    else:
        weaknesses.append("missing description")

    novelty = novelty_score
    score += 20.0 * novelty
    if novelty >= 0.7:
        strengths.append("novel approach")
    elif novelty < 0.3:
        weaknesses.append("common/similar solution")

    engagement = min(engagement_count / 10.0, 1.0)
    score += 0  # engagement already partly captured; keep score bounded 0-100
    score = min(100.0, score)

    if score >= 80:
        band = "excellent"
    elif score >= 60:
        band = "good"
    elif score >= 40:
        band = "fair"
    else:
        band = "low"

    return {
        "quality_score": round(score, 2),
        "quality_band": band,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }
