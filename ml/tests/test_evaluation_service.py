from services.evaluation.schemas import EvaluateRequest, TestResult
from services.evaluation.service import evaluate


def test_service_routes_mcq_to_deterministic():
    req = EvaluateRequest(
        question_id="q1", question_type="mcq",
        correct_options=["A"], submitted_options=["A"],
    )
    resp = evaluate(req)
    assert resp.prediction.evaluation_method == "deterministic"
    assert resp.prediction.score == 100.0
    assert resp.confidence == 1.0
    assert resp.prediction.needs_human_review is False


def test_service_routes_coding_to_deterministic():
    req = EvaluateRequest(
        question_id="q2", question_type="coding", compiled=True,
        test_results=[TestResult(name="t1", passed=False)],
    )
    resp = evaluate(req)
    assert resp.prediction.evaluation_method == "deterministic"
    assert resp.prediction.score == 0.0
