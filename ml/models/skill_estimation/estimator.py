"""
Skill Estimation model (master prompt §8).

"Do not simply average scores. Use a weighted or probabilistic skill
model. Maintain uncertainty and evidence."

Approach: a lightweight Bayesian-flavored update, similar in spirit to a
simplified Elo/Glicko update — each new piece of evidence nudges a belief
(mean estimate) and its uncertainty (confidence), weighted by:
  - the source type's reliability (a coding submission with tests passing
    is stronger evidence than a self-declared skill)
  - recency (exponential decay so stale evidence matters less)
  - evidence volume (confidence grows with more independent evidence,
    but saturates — this is not "confidence = count of evidence" acting
    unboundedly)

This is intentionally classical/probabilistic rather than deep learning —
per §46, "use classical ML where classical ML is sufficient." A skill
estimate from a handful of structured signals does not need a neural net.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone

# Reliability weight per evidence source (master prompt §8 evidence list).
# Higher = more trustworthy signal of true skill.
SOURCE_RELIABILITY: dict[str, float] = {
    "coding_submission_tests_passed": 1.0,
    "assessment": 0.9,
    "interview_result": 0.9,
    "project_activity": 0.6,
    "repository_activity": 0.55,
    "code_quality_score": 0.6,
    "learning_activity": 0.35,
    "quiz": 0.5,
    "self_declared": 0.15,
}

DEFAULT_RELIABILITY = 0.4


@dataclass
class SkillEvidence:
    source: str  # key into SOURCE_RELIABILITY
    observed_value: float  # 0..1, this evidence's implied skill level
    timestamp: datetime
    weight_override: float | None = None  # e.g. downweight a low-difficulty question
    detail: str = ""  # human-readable, goes into `evidence` list in the response


@dataclass
class SkillEstimate:
    skill: str
    estimated_level: float  # 0..1
    confidence: float  # 0..1
    evidence: list[str] = field(default_factory=list)
    evidence_count: int = 0


def _recency_weight(ts: datetime, half_life_days: float, now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    age_days = max(0.0, (now - ts).total_seconds() / 86400)
    return 0.5 ** (age_days / half_life_days)


def estimate_skill(
    skill: str,
    evidence_items: list[SkillEvidence],
    *,
    half_life_days: float = 90.0,
    min_evidence_for_high_confidence: int = 3,
    low_confidence_floor: float = 0.35,
    prior: float = 0.5,
    prior_strength: float = 0.5,
) -> SkillEstimate:
    """
    Weighted Bayesian-style update.

    Starts from a neutral prior (0.5, i.e. "unknown") with weak strength,
    then each evidence item pulls the estimate toward its observed value,
    weighted by (source reliability * recency). This naturally means:
      - one strong recent signal (passing assessment) moves the estimate
        a lot
      - many weak/stale signals (old self-declared skill) barely move it
      - confidence grows with the amount of *reliable, non-redundant*
        evidence, not raw count
    """
    if not evidence_items:
        return SkillEstimate(
            skill=skill, estimated_level=prior, confidence=0.1,
            evidence=["no evidence available — returning neutral prior"], evidence_count=0,
        )

    total_weight = prior_strength
    weighted_sum = prior * prior_strength
    reliability_mass = 0.0
    evidence_strings: list[str] = []

    for item in evidence_items:
        reliability = item.weight_override or SOURCE_RELIABILITY.get(
            item.source, DEFAULT_RELIABILITY
        )
        recency = _recency_weight(item.timestamp, half_life_days)
        w = reliability * recency
        weighted_sum += item.observed_value * w
        total_weight += w
        reliability_mass += reliability * recency
        evidence_strings.append(
            item.detail or f"{item.source}:{item.observed_value:.2f}"
        )

    estimated_level = weighted_sum / total_weight if total_weight > 0 else prior
    estimated_level = max(0.0, min(1.0, estimated_level))

    # Confidence: saturating function of accumulated reliable evidence mass.
    # Reaches ~0.9 once reliability_mass is comfortably above the
    # min-evidence threshold; stays low with sparse/unreliable evidence.
    confidence = 1 - math.exp(-reliability_mass / max(min_evidence_for_high_confidence, 1e-6))
    confidence = max(low_confidence_floor if evidence_items else 0.1, min(0.95, confidence))

    return SkillEstimate(
        skill=skill,
        estimated_level=round(estimated_level, 4),
        confidence=round(confidence, 4),
        evidence=evidence_strings,
        evidence_count=len(evidence_items),
    )
