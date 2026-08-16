"""
Calibration ("training") pipeline — fits the linear weights of the difficulty,
reputation, and feed-ranking models against labeled seed data.

This is the classical-ML equivalent of "training" for these interpretable,
linear-in-features models: no neural net, just least-squares weight fitting so
the shipped heuristics track expert labels. Writes the result to
configs/calibration.json, which the services load at runtime.

Run:  python -m pipelines.training.calibrate
"""
from __future__ import annotations

import json
from pathlib import Path

from models.activity_feed import DEFAULT_FEED_WEIGHTS, feed_features, rank_feed
from models.problem_difficulty import (
    DEFAULT_DIFFICULTY_WEIGHTS,
    difficulty_features,
    estimate_difficulty_heuristic,
)
from models.reputation import (
    DEFAULT_REPUTATION_WEIGHTS,
    compute_reputation,
    reputation_features,
)
from pipelines.evaluation.harness import (
    RegressionReport,
    evaluate_regression,
    print_report,
    write_reports,
)
from pipelines.training.least_squares import fit_linear
from shared.calibration import save_calibration

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"
CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"

DIFFICULTY_FEATS = ["bias", "length", "keyword", "test_case", "constraint", "starter", "topic"]
REPUTATION_FEATS = [
    "activity_volume", "problem_solving", "code_quality",
    "network", "profile_completeness", "verified_skills",
]
FEED_FEATS = ["recency", "social", "skill_relevance", "engagement"]


def _load(name: str) -> list[dict]:
    with open(DATASET_DIR / name) as f:
        return json.load(f)


def calibrate_difficulty() -> tuple[dict, RegressionReport, RegressionReport]:
    data = _load("seed_difficulty.json")
    feats, targets = [], []
    for row in data:
        f = difficulty_features(
            row["title"], row["description"], row.get("starter_code"),
            row.get("test_cases_count"), row.get("constraints_count"), row.get("topics"),
        )
        feats.append([f[k] for k in DIFFICULTY_FEATS])
        targets.append(float(row["label"]))

    before = evaluate_regression(
        targets,
        [estimate_difficulty_heuristic(
            r["title"], r["description"], r.get("starter_code"),
            r.get("test_cases_count"), r.get("constraints_count"), r.get("topics"),
            weights=DEFAULT_DIFFICULTY_WEIGHTS,
        ).difficulty for r in data],
        label="difficulty (default weights)",
    )

    w = fit_linear(feats, targets)
    weights = dict(zip(DIFFICULTY_FEATS, w))
    after = evaluate_regression(
        targets,
        [estimate_difficulty_heuristic(
            r["title"], r["description"], r.get("starter_code"),
            r.get("test_cases_count"), r.get("constraints_count"), r.get("topics"),
            weights=weights,
        ).difficulty for r in data],
        label="difficulty (calibrated weights)",
    )
    return weights, before, after


def calibrate_reputation() -> tuple[dict, RegressionReport, RegressionReport]:
    data = _load("seed_reputation.json")
    feats, targets = [], []
    for row in data:
        f = reputation_features(row["activity"], row.get("verified_skills", []))
        feats.append([f[k] for k in REPUTATION_FEATS])
        targets.append(float(row["label"]))

    def score(row, weights=None):
        return compute_reputation(row["activity"], row.get("verified_skills", []), weights=weights).score

    before = evaluate_regression(targets, [score(r, DEFAULT_REPUTATION_WEIGHTS) for r in data], label="reputation (default weights)")

    w = fit_linear(feats, targets)
    weights = dict(zip(REPUTATION_FEATS, w))
    after = evaluate_regression(targets, [score(r, weights) for r in data], label="reputation (calibrated weights)")
    return weights, before, after


def calibrate_feed() -> tuple[dict, RegressionReport, RegressionReport]:
    data = _load("seed_feed.json")
    feats, targets = [], []
    for row in data:
        f = feed_features(row["activity"], row["viewer_skills"], set(), None)
        feats.append([f[k] for k in FEED_FEATS])
        targets.append(float(row["label"]))

    def predict(row, weights=None):
        f = feed_features(row["activity"], row["viewer_skills"], set(), None)
        if weights is None:
            weights = DEFAULT_FEED_WEIGHTS
        raw = sum(weights.get(k, 0.25) * f[k] for k in FEED_FEATS)
        return max(0.0, min(1.0, raw))

    before = evaluate_regression(targets, [predict(r, DEFAULT_FEED_WEIGHTS) for r in data], label="feed (default weights)")
    w = fit_linear(feats, targets)
    weights = dict(zip(FEED_FEATS, w))
    after = evaluate_regression(targets, [predict(r, weights) for r in data], label="feed (calibrated weights)")
    return weights, before, after


def run_calibration() -> dict:
    calibration: dict[str, dict] = {}

    diff_w, diff_before, diff_after = calibrate_difficulty()
    calibration["problem_difficulty"] = diff_w

    rep_w, rep_before, rep_after = calibrate_reputation()
    calibration["reputation"] = rep_w

    feed_w, feed_before, feed_after = calibrate_feed()
    calibration["activity_feed"] = feed_w

    save_calibration(calibration)

    print("=== Problem Difficulty calibration ===")
    print_report(diff_before)
    print_report(diff_after)
    print("  fitted weights:", {k: round(v, 4) for k, v in diff_w.items()})

    print("\n=== Reputation calibration ===")
    print_report(rep_before)
    print_report(rep_after)
    print("  fitted weights:", {k: round(v, 4) for k, v in rep_w.items()})

    print("\n=== Feed Ranking calibration ===")
    print_report(feed_before)
    print_report(feed_after)
    print("  fitted weights:", {k: round(v, 4) for k, v in feed_w.items()})

    write_reports({
        "difficulty_default": diff_before,
        "difficulty_calibrated": diff_after,
        "reputation_default": rep_before,
        "reputation_calibrated": rep_after,
        "feed_default": feed_before,
        "feed_calibrated": feed_after,
    })

    return calibration


if __name__ == "__main__":
    run_calibration()
