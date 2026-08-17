from services.problem_difficulty.schemas import (
    CalibrateDifficultyRequest,
    EstimateDifficultyRequest,
    SubmissionOutcome,
)
from services.problem_difficulty.service import calibrate_difficulty_service, estimate_difficulty


def test_estimate_difficulty_heuristic_labels():
    req = EstimateDifficultyRequest(
        title="Easy sum array",
        description="Given an array of integers, return the sum. Simple problem.",
        starter_code="def solve(nums):\n    return 0",
        language="python",
        test_cases_count=3,
        constraints_count=1,
        topics=["array"],
    )
    resp = estimate_difficulty(req)
    assert 0.0 <= resp.prediction.difficulty <= 1.0
    assert resp.prediction.difficulty_label in {"easy", "medium", "hard"}
    assert "easy" in resp.prediction.difficulty_label.lower() or resp.prediction.difficulty < 0.66


def test_estimate_difficulty_hard_keywords():
    req = EstimateDifficultyRequest(
        title="Hard DP on graphs",
        description=(
            "You are given a weighted graph. Use dynamic programming and "
            "backtracking with a segment tree to find the optimal path. "
            "This is an NP complete optimization problem."
        ),
        starter_code="",
        language="cpp",
        test_cases_count=25,
        constraints_count=5,
        topics=["dynamic programming", "graph"],
    )
    resp = estimate_difficulty(req)
    assert resp.prediction.difficulty > 0.5
    assert resp.prediction.difficulty_label in {"medium", "hard"}


def test_calibrate_difficulty_high_pass_rate_easy():
    outcomes = [SubmissionOutcome(passed=True, attempts=1) for _ in range(40)]
    req = CalibrateDifficultyRequest(
        problem_id="p1", title="t", submission_outcomes=outcomes, prior_difficulty=0.5
    )
    resp = calibrate_difficulty_service(req)
    assert resp.prediction.pass_rate == 1.0
    assert resp.prediction.calibrated_difficulty < 0.4
    assert resp.prediction.confidence > 0.8


def test_calibrate_difficulty_low_pass_rate_hard():
    outcomes = [SubmissionOutcome(passed=False, attempts=3) for _ in range(40)]
    req = CalibrateDifficultyRequest(
        problem_id="p2", title="t", submission_outcomes=outcomes, prior_difficulty=0.5
    )
    resp = calibrate_difficulty_service(req)
    assert resp.prediction.pass_rate == 0.0
    assert resp.prediction.calibrated_difficulty > 0.6
    assert resp.prediction.sample_size == 40
