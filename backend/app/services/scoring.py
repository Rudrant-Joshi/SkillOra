"""
Scoring Orchestrator — ties the backend to the ML gateway for assessment scoring.

Flow:
  1. For each submitted answer, normalize to an EvaluateRequest and call
     /ml/assessment/evaluate (deterministic for MCQ/tests/coding, AI-assisted
     for short_answer/system_design).
  2. Persist each evaluation as an MLPrediction record.
  3. Build per-skill dimension scores and call /ml/assessment/scorecard.
  4. Build skill evidence from question scores and call /ml/skill/estimate-batch.
  5. Persist the scorecard and skill estimates.
  6. Return a unified result DTO to the caller (the result API route).

If the ML gateway is down, scores deterministically on the backend and marks
the attempt for deferred ML analysis.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.models.attempt import Answer, Attempt
from app.models.ml_prediction import MLPrediction
from app.services.ml_client import MLUnavailableError, call_ml

logger = logging.getLogger("backend.scoring")


def _as_json(value):
    """Handle both JSON columns (already a list/dict) and Text columns (JSON string)."""
    if value is None:
        return []
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    return value


def _normalize_skills(skills_text: str) -> list[str]:
    if not skills_text:
        return []
    return [s.strip() for s in skills_text.split(",") if s.strip()]


def _score_answer_locally(answer: Answer) -> dict[str, Any]:
    """
    Deterministic fallback scoring when the ML gateway is unavailable.
    Mirrors the ML gateway's deterministic evaluators for MCQ / multi_select / coding / sql.
    """
    q = answer.question
    qtype = q.question_type
    if qtype in ("mcq", "multi_select"):
        correct = set(_as_json(q.correct_options))
        submitted = set(_as_json(answer.submitted_options))
        if qtype == "mcq":
            score = 100.0 if correct == submitted else 0.0
            reasoning = "Exact match (local fallback)" if score == 100 else "Mismatch (local fallback)"
        else:
            tp = len(correct & submitted)
            fp = len(submitted - correct)
            score = max(0.0, (tp - fp) / len(correct)) * 100 if correct else 0.0
            reasoning = f"{tp}/{len(correct)} correct, {fp} wrong (local fallback)"
        return {"score": round(score, 2), "method": "deterministic", "reasoning": reasoning, "confidence": 1.0, "needs_human_review": False}
    elif qtype in ("coding", "sql"):
        if not answer.compiled:
            return {"score": 0.0, "method": "deterministic", "reasoning": "Did not compile (local fallback)", "confidence": 1.0, "needs_human_review": False}
        if answer.time_limit_exceeded or answer.memory_limit_exceeded:
            return {"score": 0.0, "method": "deterministic", "reasoning": "Exceeded resource limits (local fallback)", "confidence": 1.0, "needs_human_review": False}
        tests = _as_json(answer.test_results)
        if not tests:
            return {"score": 0.0, "method": "deterministic", "reasoning": "No test results (local fallback)", "confidence": 1.0, "needs_human_review": False}
        passed = sum(1 for t in tests if t.get("passed"))
        score = (passed / len(tests)) * 100
        return {"score": round(score, 2), "method": "deterministic", "reasoning": f"{passed}/{len(tests)} tests passed (local fallback)", "confidence": 1.0, "needs_human_review": False}
    else:
        return {"score": 0.0, "method": "deterministic", "reasoning": "No evaluation (local fallback, requires ML for short_answer/system_design)", "confidence": 0.5, "needs_human_review": True}


def evaluate_answer(
    answer: Answer,
    *,
    user_id: int,
    role: str,
    company_id: int | None,
    db,
) -> dict[str, Any]:
    """
    Evaluate a single answer via the ML gateway.
    Returns the evaluation prediction and persists the MLPrediction record.
    """
    q = answer.question
    qtype = q.question_type

    if qtype in ("mcq", "multi_select"):
        correct = _as_json(q.correct_options)
        payload = {
            "question_id": str(q.id),
            "question_type": qtype,
            "correct_options": [str(c) for c in correct],
            "submitted_options": [str(o) for o in _as_json(answer.submitted_options)],
            "time_limit_exceeded": answer.time_limit_exceeded,
            "memory_limit_exceeded": answer.memory_limit_exceeded,
            "compiled": answer.compiled,
        }
    elif qtype in ("coding", "sql"):
        tests = _as_json(answer.test_results)
        payload = {
            "question_id": str(q.id),
            "question_type": qtype,
            "test_results": tests,
            "time_limit_exceeded": answer.time_limit_exceeded,
            "memory_limit_exceeded": answer.memory_limit_exceeded,
            "compiled": answer.compiled,
        }
    else:
        # short_answer or system_design — AI-assisted
        payload = {
            "question_id": str(q.id),
            "question_type": qtype,
            "prompt": q.prompt,
            "submitted_answer": answer.submitted_answer,
            "rubric": _as_json(q.rubric),
        }

    ml_result = None
    prediction = None
    try:
        ml_result = call_ml(
            "/ml/assessment/evaluate",
            payload,
            user_id=user_id,
            role=role,
            company_id=company_id,
        )
        prediction = ml_result["prediction"]
        ml_score = prediction.get("score", 0.0)
        ml_method = prediction.get("evaluation_method", "unknown")
        ml_reasoning = prediction.get("reasoning", "")
        ml_confidence = ml_result.get("confidence", 0.5)
        ml_needs_review = prediction.get("needs_human_review", False)
        strengths = prediction.get("strengths", [])
        weaknesses = prediction.get("weaknesses", [])
    except MLUnavailableError:
        logger.warning("ML gateway unavailable for evaluation of answer %s; using local fallback", answer.id)
        eval_result = _score_answer_locally(answer)
        ml_score = eval_result["score"]
        ml_method = eval_result["method"]
        ml_reasoning = eval_result["reasoning"]
        ml_confidence = eval_result["confidence"]
        ml_needs_review = eval_result["needs_human_review"]
        strengths = []
        weaknesses = []

    eval_data = {
        "score": ml_score,
        "method": ml_method,
        "reasoning": ml_reasoning,
        "confidence": ml_confidence,
        "needs_human_review": ml_needs_review,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "latency_ms": ml_result["latency_ms"] if ml_result else 0,
    }

    # Persist the evaluation
    answer.ml_evaluation = json.dumps(eval_data)
    db.add(answer)
    db.commit()
    db.refresh(answer)

    # Persist MLPrediction
    pred_record = MLPrediction(
        user_id=user_id,
        attempt_id=answer.attempt_id,
        service_name="evaluation",
        model_version=(ml_result.get("model_version", "evaluation-v1") if ml_result else "evaluation-v1"),
        prediction_json=json.dumps(prediction if prediction is not None else eval_data),
        confidence=ml_confidence,
        evidence=json.dumps((ml_result or {}).get("evidence", [])),
        request_id=(ml_result or {}).get("request_id", ""),
        latency_ms=eval_data["latency_ms"],
        success=True,
    )
    db.add(pred_record)
    db.commit()

    return eval_data


def build_scorecard_and_skills(
    attempt: Attempt,
    *,
    user_id: int,
    role: str,
    company_id: int | None,
    db,
) -> dict[str, Any]:
    """
    After all answers are evaluated:
      1. Build dimension scores and call /ml/assessment/scorecard.
      2. Build skill evidence and call /ml/skill/estimate-batch.
    Returns the combined result.
    """
    q = attempt.assessment
    questions = {a.question_id: a for a in attempt.answers}
    all_questions = q.questions
    question_map = {question.id: question for question in all_questions}

    # --- Build dimension scores for scorecard ---
    dimension_scores = []
    for answer in attempt.answers:
        q_obj = question_map.get(answer.question_id)
        if not q_obj:
            continue
        try:
            eval_data = _as_json(answer.ml_evaluation) if answer.ml_evaluation else {}
        except (json.JSONDecodeError, TypeError):
            eval_data = {}

        skills = _normalize_skills(q_obj.skills or "")
        # Use the first skill as the dimension; if none, use the question type
        dimension = skills[0] if skills else q_obj.question_type
        score = eval_data.get("score", 0.0)
        confidence = eval_data.get("confidence", 0.5)
        dimension_scores.append({
            "dimension": dimension,
            "score": score,
            "confidence": confidence,
            "question_id": str(q_obj.id),
        })

    scorecard_result = None
    try:
        result = call_ml(
            "/ml/assessment/scorecard",
            {
                "candidate_id": str(user_id),
                "assessment_id": str(attempt.assessment_id),
                "dimension_scores": dimension_scores,
            },
            user_id=user_id,
            role=role,
            company_id=company_id,
        )
        scorecard_result = result["prediction"]
        scorecard_result["confidence"] = result.get("confidence")
        scorecard_result["evidence"] = result.get("evidence", [])
        scorecard_result["model_version"] = result.get("model_version")

        # Persist scorecard prediction
        pred_record = MLPrediction(
            user_id=user_id,
            attempt_id=attempt.id,
            service_name="scorecard",
            model_version=result.get("model_version", "scorecard-v1"),
            prediction_json=json.dumps(scorecard_result),
            confidence=result.get("confidence", 0.0),
            evidence=json.dumps(result.get("evidence", [])),
            latency_ms=result.get("latency_ms", 0),
            success=True,
        )
        db.add(pred_record)
    except MLUnavailableError as e:
        logger.warning("ML gateway unavailable for scorecard; computing locally: %s", e)
        # Local fallback: simple average
        dims = {}
        dim_confs = {}
        for ds in dimension_scores:
            d = ds["dimension"]
            dims.setdefault(d, []).append(ds["score"])
            dim_confs.setdefault(d, []).append(ds["confidence"])
        overall = round(sum(sum(v) / len(v) for v in dims.values()) / len(dims), 2) if dims else 0.0
        scorecard_result = {
            "overall_score": overall,
            "dimensions": {d: round(sum(v) / len(v), 2) for d, v in dims.items()},
            "dimension_confidence": {d: round(sum(v) / len(v), 4) for d, v in dim_confs.items()},
        }

    # --- Build skill evidence and estimate skills ---
    skill_evidence: dict[str, list[dict]] = {}
    now_iso = datetime.now(timezone.utc).isoformat()
    for answer in attempt.answers:
        q_obj = question_map.get(answer.question_id)
        if not q_obj:
            continue
        try:
            eval_data = _as_json(answer.ml_evaluation) if answer.ml_evaluation else {}
        except (json.JSONDecodeError, TypeError):
            eval_data = {}
        score = eval_data.get("score", 0.0)
        observed = score / 100.0  # normalize 0..1
        for skill_name in _normalize_skills(q_obj.skills or ""):
            skill_evidence.setdefault(skill_name, []).append({
                "source": "assessment",
                "observed_value": observed,
                "timestamp": now_iso,
                "detail": f"Question {q_obj.id}: {score} points",
            })

    skill_estimates = {}
    if skill_evidence:
        try:
            batch_result = call_ml(
                "/ml/skill/estimate-batch",
                {"user_id": str(user_id), "skills": skill_evidence},
                user_id=user_id,
                role=role,
                company_id=company_id,
                unwrap=False,
            )
            # batch returns {skill_name: {MLResponse envelope}}
            for skill_name, ml_resp in batch_result.get("prediction", {}).items():
                pred = ml_resp.get("prediction", ml_resp)
                skill_estimates[skill_name] = {
                    "level": pred.get("estimated_level", 0.0),
                    "confidence": pred.get("confidence", ml_resp.get("confidence", 0.0)),
                    "evidence_count": pred.get("evidence_count", 0),
                    "evidence": ml_resp.get("evidence", pred.get("evidence", [])),
                }
        except MLUnavailableError as e:
            logger.warning("ML gateway unavailable for skill estimation: %s", e)
            # Local fallback: simple weighted average with confidence decay
            for skill_name, evidence_list in skill_evidence.items():
                if not evidence_list:
                    continue
                total_w = 0.0
                weighted_sum = 0.0
                for ev in evidence_list:
                    reliability = {"assessment": 0.9, "self_declared": 0.15}.get(ev["source"], 0.4)
                    w = reliability  # simplified: no recency decay in fallback
                    weighted_sum += ev["observed_value"] * w
                    total_w += w
                level = weighted_sum / total_w if total_w > 0 else 0.5
                level = max(0.0, min(1.0, level))
                confidence = min(0.95, 1 - 0.5 ** len(evidence_list))
                skill_estimates[skill_name] = {
                    "level": round(level, 4),
                    "confidence": round(confidence, 4),
                    "evidence_count": len(evidence_list),
                    "evidence": [e.get("detail", "") for e in evidence_list],
                }

    # --- Persist skill estimates ---
    from app.models.skill import Skill, UserSkill
    for skill_name, est_data in skill_estimates.items():
        skill_obj = db.query(Skill).filter(Skill.name == skill_name).first()
        if not skill_obj:
            skill_obj = Skill(name=skill_name, category="concept")
            db.add(skill_obj)
            db.commit()
            db.refresh(skill_obj)
        existing = db.query(UserSkill).filter(
            UserSkill.user_id == user_id, UserSkill.skill_id == skill_obj.id
        ).first()
        if existing:
            existing.level = est_data["level"]
            existing.confidence = est_data["confidence"]
            existing.source = "assessment"
            existing.updated_at = datetime.now(timezone.utc)
        else:
            us = UserSkill(
                user_id=user_id, skill_id=skill_obj.id,
                level=est_data["level"], confidence=est_data["confidence"],
                source="assessment",
            )
            db.add(us)
    db.commit()

    # --- Build dimension details ---
    dimension_details = {}
    for skill_name, est_data in skill_estimates.items():
        dimension_details[skill_name] = {
            "level": est_data["level"],
            "confidence": est_data["confidence"],
            "evidence_count": est_data["evidence_count"],
            "evidence": est_data["evidence"],
        }

    raw_score = round(sum(d["score"] for d in dimension_scores) / len(dimension_scores), 2) if dimension_scores else 0.0
    ml_score = scorecard_result.get("overall_score", raw_score)

    # Overall = weighted blend of raw_score (deterministic) and ml_score (ML)
    overall = round(0.6 * raw_score + 0.4 * ml_score, 2) if dimension_scores else 0.0

    attempt.raw_score = raw_score
    attempt.ml_score = ml_score
    attempt.overall_score = overall
    attempt.status = "graded"
    attempt.submitted_at = datetime.now(timezone.utc)
    attempt.ml_analysis = json.dumps({
        "scorecard": scorecard_result,
        "skills": skill_estimates,
        "dimension_scores": dimension_scores,
    })
    db.commit()
    db.refresh(attempt)

    return {
        "overall_score": overall,
        "raw_score": raw_score,
        "ml_score": ml_score,
        "dimension_scores": scorecard_result.get("dimensions", {}),
        "dimension_details": dimension_details,
        "skills": skill_estimates,
        "evidence": scorecard_result.get("evidence", []),
        "questions_count": len(dimension_scores),
    }
