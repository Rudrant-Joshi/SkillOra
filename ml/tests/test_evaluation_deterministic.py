from services.evaluation.deterministic import evaluate_mcq, evaluate_multi_select, evaluate_tests
from services.evaluation.schemas import EvaluateRequest, TestResult


def test_mcq_exact_match_scores_100():
    req = EvaluateRequest(
        question_id="q1", question_type="mcq",
        correct_options=["A"], submitted_options=["A"],
    )
    score, _ = evaluate_mcq(req)
    assert score == 100.0


def test_mcq_wrong_answer_scores_0():
    req = EvaluateRequest(
        question_id="q1", question_type="mcq",
        correct_options=["A"], submitted_options=["B"],
    )
    score, _ = evaluate_mcq(req)
    assert score == 0.0


def test_multi_select_partial_credit():
    req = EvaluateRequest(
        question_id="q2", question_type="multi_select",
        correct_options=["A", "B", "C"], submitted_options=["A", "B"],
    )
    score, _ = evaluate_multi_select(req)
    assert 0 < score < 100


def test_multi_select_penalizes_wrong_picks():
    req = EvaluateRequest(
        question_id="q2", question_type="multi_select",
        correct_options=["A", "B"], submitted_options=["A", "B", "C", "D"],
    )
    score, _ = evaluate_multi_select(req)
    assert score < 100


def test_coding_all_tests_pass():
    req = EvaluateRequest(
        question_id="q3", question_type="coding", compiled=True,
        test_results=[TestResult(name="t1", passed=True), TestResult(name="t2", passed=True)],
    )
    score, _ = evaluate_tests(req)
    assert score == 100.0


def test_coding_time_limit_exceeded_scores_zero():
    req = EvaluateRequest(
        question_id="q3", question_type="coding", compiled=True, time_limit_exceeded=True,
        test_results=[TestResult(name="t1", passed=True)],
    )
    score, reasoning = evaluate_tests(req)
    assert score == 0.0
    assert "time limit" in reasoning.lower()


def test_coding_does_not_compile_scores_zero():
    req = EvaluateRequest(question_id="q3", question_type="coding", compiled=False)
    score, _ = evaluate_tests(req)
    assert score == 0.0
