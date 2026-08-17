from pathlib import Path

from pipelines.evaluation.harness import evaluate_regression
from pipelines.training.calibrate import (
    calibrate_difficulty,
    calibrate_feed,
    calibrate_reputation,
    run_calibration,
)
from pipelines.training.least_squares import fit_linear
from shared.calibration import load_calibration

ROOT = Path(__file__).resolve().parents[1]


def test_fit_linear_solves_exact_system():
    # y = 2*x1 + 3*x2
    X = [[1.0, 0.0], [2.0, 0.0], [0.0, 1.0], [0.0, 2.0]]
    y = [2.0, 4.0, 3.0, 6.0]
    w = fit_linear(X, y, ridge=0.0)
    assert abs(w[0] - 2.0) < 1e-6
    assert abs(w[1] - 3.0) < 1e-6


def test_evaluate_regression_basic():
    r = evaluate_regression([1.0, 2.0, 3.0], [1.0, 2.0, 3.0], label="perfect")
    assert r.mae == 0.0
    assert r.rmse == 0.0
    assert r.r2 == 1.0
    r2 = evaluate_regression([1.0, 2.0, 3.0], [2.0, 3.0, 4.0], label="off-by-1")
    assert r2.mae == 1.0


def test_calibrate_difficulty_improves_metrics():
    weights, before, after = calibrate_difficulty()
    assert set(weights.keys()) == {
        "bias", "length", "keyword", "test_case", "constraint", "starter", "topic"
    }
    assert after.mae < before.mae
    assert after.r2 > before.r2


def test_calibrate_reputation_improves_metrics():
    weights, before, after = calibrate_reputation()
    assert set(weights.keys()) == {
        "activity_volume", "problem_solving", "code_quality",
        "network", "profile_completeness", "verified_skills",
    }
    assert after.mae < before.mae
    assert after.r2 > before.r2


def test_calibrate_feed_improves_metrics():
    weights, before, after = calibrate_feed()
    assert set(weights.keys()) == {"recency", "social", "skill_relevance", "engagement"}
    assert after.mae < before.mae
    assert after.r2 > before.r2


def test_run_calibration_writes_and_is_loadable():
    load_calibration.cache_clear()
    run_calibration()
    cal = load_calibration()
    assert "problem_difficulty" in cal
    assert "reputation" in cal
    assert "activity_feed" in cal
    # the persisted file exists
    assert (ROOT / "configs" / "calibration.json").exists()
