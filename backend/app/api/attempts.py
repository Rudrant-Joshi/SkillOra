from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.attempt import Attempt, Answer
from app.models.question import Question
from app.models.user import User
from app.schemas.attempt import AnswerSubmit, AttemptSubmitRequest, AttemptRead
from app.services.scoring import build_scorecard_and_skills, evaluate_answer

router = APIRouter(prefix="/api/attempts", tags=["attempts"])


@router.get("/{attempt_id}", response_model=AttemptRead)
def get_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    if attempt.user_id != current_user.id and current_user.role not in ("trainer", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    a = attempt.assessment
    ml_analysis = {}
    try:
        ml_analysis = json.loads(attempt.ml_analysis) if attempt.ml_analysis else {}
    except (json.JSONDecodeError, TypeError):
        ml_analysis = {}

    scorecard = ml_analysis.get("scorecard", {})
    skills = ml_analysis.get("skills", {})
    dimension_details = {skill_name: est_data for skill_name, est_data in skills.items() if isinstance(est_data, dict)}

    questions_count = len(ml_analysis.get("dimension_scores", [])) if isinstance(ml_analysis.get("dimension_scores"), list) else 0
    if questions_count == 0:
        questions_count = db.query(Answer).filter(Answer.attempt_id == attempt_id).count()

    return AttemptRead(
        id=attempt.id,
        assessment_id=attempt.assessment_id,
        assessment_title=a.title if a else "",
        started_at=attempt.started_at.isoformat() if attempt.started_at else None,
        submitted_at=attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        status=attempt.status,
        raw_score=attempt.raw_score,
        ml_score=attempt.ml_score,
        overall_score=attempt.overall_score,
        is_offline=attempt.is_offline,
        ml_analysis=ml_analysis,
        dimension_scores=scorecard.get("dimensions", {}) if isinstance(scorecard, dict) else {},
        dimension_details=dimension_details,
        skills=skills if isinstance(skills, dict) else {},
        evidence=scorecard.get("evidence", []) if isinstance(scorecard, dict) else [],
        questions_count=questions_count,
    )


@router.post("/{attempt_id}/submit")
def submit_attempt(
    attempt_id: int,
    req: AttemptSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit all answers for an attempt and trigger full scoring + ML analysis."""
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if attempt.status != "in_progress":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attempt is not in progress")

    # Map submitted answers to Answer records
    q_ids = [a.question_id for a in req.answers]
    questions = db.query(Question).filter(Question.id.in_(q_ids)).all()
    q_map = {q.id: q for q in questions}

    for ans in req.answers:
        q_obj = q_map.get(ans.question_id)
        if not q_obj:
            continue
        existing = db.query(Answer).filter(
            Answer.attempt_id == attempt_id,
            Answer.question_id == ans.question_id,
        ).first()
        if existing:
            existing.submitted_options = json.dumps(ans.submitted_options) if ans.submitted_options else "[]"
            existing.submitted_code = ans.submitted_code
            existing.submitted_answer = ans.submitted_answer
            existing.test_results = json.dumps(ans.test_results) if ans.test_results else "[]"
            existing.time_limit_exceeded = ans.time_limit_exceeded
            existing.memory_limit_exceeded = ans.memory_limit_exceeded
            existing.compiled = ans.compiled
            existing.time_spent_seconds = ans.time_spent_seconds
            existing.updated_at = datetime.now(timezone.utc)
        else:
            answer = Answer(
                attempt_id=attempt_id,
                user_id=current_user.id,
                question_id=ans.question_id,
                submitted_options=json.dumps(ans.submitted_options) if ans.submitted_options else "[]",
                submitted_code=ans.submitted_code,
                submitted_answer=ans.submitted_answer,
                test_results=json.dumps(ans.test_results) if ans.test_results else "[]",
                time_limit_exceeded=ans.time_limit_exceeded,
                memory_limit_exceeded=ans.memory_limit_exceeded,
                compiled=ans.compiled,
                time_spent_seconds=ans.time_spent_seconds,
            )
            db.add(answer)

    db.commit()

    # --- Evaluate each answer via ML gateway ---
    answers = db.query(Answer).filter(Answer.attempt_id == attempt_id).all()
    for answer in answers:
        answer.question = q_map.get(answer.question_id)
        evaluate_answer(
            answer,
            user_id=current_user.id,
            role=current_user.role,
            company_id=current_user.company_id,
            db=db,
        )

    # --- Build scorecard + skill estimation via ML gateway ---
    result = build_scorecard_and_skills(
        attempt,
        user_id=current_user.id,
        role=current_user.role,
        company_id=current_user.company_id,
        db=db,
    )

    db.refresh(attempt)
    return result


@router.get("/{attempt_id}/answers", response_model=list)
def get_attempt_answers(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    if attempt.user_id != current_user.id and current_user.role not in ("trainer", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    answers = db.query(Answer).filter(Answer.attempt_id == attempt_id).all()
    result = []
    for ans in answers:
        q = db.query(Question).filter(Question.id == ans.question_id).first()
        eval_data = {}
        if ans.ml_evaluation:
            try:
                eval_data = json.loads(ans.ml_evaluation)
            except (json.JSONDecodeError, TypeError):
                eval_data = {}
        result.append({
            "id": ans.id,
            "question_id": ans.question_id,
            "question_prompt": q.prompt if q else "",
            "question_type": q.question_type if q else "",
            "question_skills": q.skills.split(",") if q and q.skills else [],
            "submitted_options": json.loads(ans.submitted_options) if ans.submitted_options else [],
            "submitted_code": ans.submitted_code,
            "submitted_answer": ans.submitted_answer,
            "test_results": json.loads(ans.test_results) if ans.test_results else [],
            "ml_evaluation": eval_data,
            "time_spent_seconds": ans.time_spent_seconds,
        })
    return result


@router.get("/user/{user_id}", response_model=list[AttemptRead])
def list_user_attempts(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List attempts for a specific user. Candidates see their own; trainers/admins see anyone in their company."""
    if current_user.id != user_id and current_user.role not in ("trainer", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if current_user.role == "candidate" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    attempts = db.query(Attempt).filter(Attempt.user_id == user_id).order_by(Attempt.started_at.desc()).all()
    result = []
    for att in attempts:
        a = att.assessment
        result.append(AttemptRead(
            id=att.id,
            assessment_id=att.assessment_id,
            assessment_title=a.title if a else "",
            started_at=att.started_at.isoformat() if att.started_at else None,
            submitted_at=att.submitted_at.isoformat() if att.submitted_at else None,
            status=att.status,
            raw_score=att.raw_score,
            ml_score=att.ml_score,
            overall_score=att.overall_score,
            is_offline=att.is_offline,
            ml_analysis=json.loads(att.ml_analysis) if att.ml_analysis else {},
        ))
    return result
