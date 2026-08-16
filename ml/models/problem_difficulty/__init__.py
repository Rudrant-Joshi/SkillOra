"""
Problem Difficulty model (master prompt §8, §46).

Difficulty is estimated two ways:
  1. Heuristic, from problem text features (length, constraint count, topic
     rarity, presence of advanced keywords). Deterministic, no model call.
  2. Calibration, from aggregate submission outcomes (pass rate, attempts).
     This is the more trustworthy signal once enough submissions exist.

Both are linear-in-features so weights can be *trained* (calibrated) against
labeled seed data by pipelines/training/calibrate.py (master prompt §46:
classical ML where classical is sufficient).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.calibration import get_calibrated_weights

DEFAULT_DIFFICULTY_WEIGHTS: dict[str, float] = {
    "bias": 0.225,
    "length": 0.30,
    "keyword": 0.30,
    "test_case": 1.0,
    "constraint": 1.0,
    "starter": 1.0,
    "topic": 0.15,
}

_HARD_KEYWORDS = {
    "dynamic programming": 0.35, "dp": 0.30, "optimization": 0.25,
    "np complete": 0.5, "graph": 0.2, "binary search": 0.15,
    "recursion": 0.1, "backtracking": 0.25, "bitmask": 0.3,
    "segment tree": 0.4, "fenwick": 0.35, "trie": 0.25,
    "disjoint set": 0.25, "topological": 0.2, "greedy": 0.1,
    "monotonic": 0.15, "sliding window": 0.1,
}

_EASY_KEYWORDS = {
    "hello world": -0.3, "print": -0.15, "simple": -0.2, "basic": -0.2,
    "sum": -0.1, "count": -0.05, "sort": 0.05, "array": 0.0,
}

_LABEL_THRESHOLDS = [(0.66, "hard"), (0.33, "medium"), (0.0, "easy")]


@dataclass
class DifficultyEstimate:
    difficulty: float
    label: str
    confidence: float
    reasoning: str
    signal_scores: dict[str, float] = field(default_factory=dict)
    features: dict[str, float] = field(default_factory=dict)


def _label_for(diff: float) -> str:
    for threshold, label in _LABEL_THRESHOLDS:
        if diff >= threshold:
            return label
    return "easy"


def difficulty_features(
    title: str,
    description: str,
    starter_code: str | None = None,
    test_cases_count: int | None = None,
    constraints_count: int | None = None,
    topics: list[str] | None = None,
) -> dict[str, float]:
    """Normalized 0..1-ish features used by the linear difficulty model."""
    text = f"{title} {description}".lower()
    desc_len = len(description or "")

    length = min(desc_len / 1500.0, 1.0)

    keyword_score = 0.0
    for kw, weight in _HARD_KEYWORDS.items():
        if kw in text:
            keyword_score += weight
    for kw, weight in _EASY_KEYWORDS.items():
        if kw in text:
            keyword_score += weight
    keyword_score = max(-0.5, min(0.6, keyword_score))

    tc_score = 0.0
    if test_cases_count is not None:
        tc_score = min(test_cases_count / 20.0, 1.0) * 0.3
    cons_score = 0.0
    if constraints_count is not None:
        cons_score = min(constraints_count / 5.0, 1.0) * 0.2
    code_score = 0.0
    if starter_code:
        lines = starter_code.count("\n") + 1
        code_score = min(lines / 30.0, 1.0) * 0.15
    topic_score = 0.0
    if topics:
        for t in topics:
            tl = t.lower()
            if tl in _HARD_KEYWORDS:
                topic_score += _HARD_KEYWORDS[tl]
        topic_score = max(-0.2, min(0.5, topic_score))

    # Shifted features so default linear weights reproduce the original formula
    return {
        "bias": 1.0,
        "length": length,
        "keyword": keyword_score + 0.5,
        "test_case": tc_score,
        "constraint": cons_score,
        "starter": code_score,
        "topic": topic_score + 0.5,
    }


def estimate_difficulty_heuristic(
    title: str,
    description: str,
    starter_code: str | None = None,
    test_cases_count: int | None = None,
    constraints_count: int | None = None,
    topics: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> DifficultyEstimate:
    weights = weights or get_calibrated_weights("problem_difficulty", DEFAULT_DIFFICULTY_WEIGHTS)
    feats = difficulty_features(
        title, description, starter_code, test_cases_count, constraints_count, topics
    )
    raw = sum(weights.get(k, 0.0) * v for k, v in feats.items())
    raw = max(0.0, min(1.0, raw))

    confidence = 0.55
    reasoning = (
        f"Estimated from problem text features. Length={feats['length']:.2f}, "
        f"keyword_complexity={feats['keyword'] - 0.5:.2f}, topics={topics or []}."
    )
    return DifficultyEstimate(
        difficulty=round(raw, 4),
        label=_label_for(raw),
        confidence=confidence,
        reasoning=reasoning,
        signal_scores={k: round(v, 4) for k, v in feats.items()},
        features=feats,
    )


def calibrate_difficulty(
    submission_outcomes: list[dict[str, Any]],
    prior_difficulty: float = 0.5,
) -> DifficultyEstimate:
    n = len(submission_outcomes)
    if n == 0:
        return DifficultyEstimate(
            difficulty=prior_difficulty, label=_label_for(prior_difficulty),
            confidence=0.2, reasoning="No submissions; using prior.", signal_scores={},
        )

    passes = sum(1 for o in submission_outcomes if o.get("passed"))
    pass_rate = passes / n
    difficulty_from_pass = 1.0 - pass_rate

    avg_attempts = sum(max(1, o.get("attempts", 1)) for o in submission_outcomes) / n
    attempt_penalty = min((avg_attempts - 1) / 5.0, 0.3)

    runtimes = [o["runtime_ms"] for o in submission_outcomes if o.get("runtime_ms") is not None]
    runtime_factor = 0.0
    if runtimes:
        avg_rt = sum(runtimes) / len(runtimes)
        runtime_factor = min(avg_rt / 5000.0, 0.2)

    calibrated = difficulty_from_pass * 0.7 + attempt_penalty + runtime_factor
    calibrated = max(0.0, min(1.0, calibrated))

    trust = min(n / 30.0, 1.0)
    blended = prior_difficulty * (1 - trust) + calibrated * trust

    confidence = 0.5 + 0.45 * trust
    reasoning = (
        f"Calibrated from {n} submissions. Pass rate={pass_rate:.2f}, "
        f"avg attempts={avg_attempts:.1f}. Sample trust={trust:.2f}."
    )
    return DifficultyEstimate(
        difficulty=round(blended, 4),
        label=_label_for(blended),
        confidence=round(confidence, 4),
        reasoning=reasoning,
        signal_scores={"pass_rate": round(pass_rate, 4), "avg_attempts": round(avg_attempts, 2)},
    )
