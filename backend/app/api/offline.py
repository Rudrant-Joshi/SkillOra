from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.assessment import Assessment
from app.models.attempt import Attempt, Answer
from app.models.offline_sync import OfflineSync
from app.models.question import Question
from app.models.user import User
from app.services.scoring import build_scorecard_and_skills, evaluate_answer

router = APIRouter(prefix="/api/offline", tags=["offline"])


class OfflineSyncPayload(BaseModel):
    assessment_id: int
    answers: list[dict[str, Any]]
    started_at: Optional[str] = None
    time_spent_seconds: Optional[float] = None


@router.post("/sync")
def sync_offline_data(
    payloads: list[OfflineSyncPayload],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sync offline-captured assessment attempts to the server.
    Each payload contains an assessment_id and answers captured while
    the client had no connectivity. The server creates a proper attempt,
    stores the answers, and (if both the attempt is complete and the ML
    gateway is reachable) triggers scoring.
    """
    synced = []
    for payload in payloads:
        assessment = db.query(Assessment).filter(Assessment.id == payload.assessment_id).first()
        if not assessment:
            synced.append({"assessment_id": payload.assessment_id, "status": "error", "error": "Assessment not found"})
            continue

        # Create a new attempt marked as offline
        attempt = Attempt(
            user_id=current_user.id,
            assessment_id=payload.assessment_id,
            status="in_progress",
            started_at=datetime.fromisoformat(payload.started_at) if payload.started_at else datetime.now(timezone.utc),
            is_offline=True,
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        # Store answers
        question_ids = [a.get("question_id") for a in payload.answers]
        questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
        q_map = {q.id: q for q in questions}

        for a in payload.answers:
            q = q_map.get(a.get("question_id"))
            if not q:
                continue
            answer = Answer(
                attempt_id=attempt.id,
                user_id=current_user.id,
                question_id=a.get("question_id"),
                submitted_options=json.dumps(a.get("submitted_options", [])),
                submitted_code=a.get("submitted_code", ""),
                submitted_answer=a.get("submitted_answer", ""),
                test_results=json.dumps(a.get("test_results", [])),
                time_limit_exceeded=a.get("time_limit_exceeded", False),
                memory_limit_exceeded=a.get("memory_limit_exceeded", False),
                compiled=a.get("compiled", True),
                time_spent_seconds=a.get("time_spent_seconds", 0.0),
            )
            db.add(answer)

        db.commit()

        # Create offline sync record
        sync_record = OfflineSync(
            user_id=current_user.id,
            assessment_id=payload.assessment_id,
            data_json=json.dumps(payload.dict()),
            is_synced=True,
            synced_at=datetime.now(timezone.utc),
        )
        db.add(sync_record)

        # Evaluate answers
        answers = db.query(Answer).filter(Answer.attempt_id == attempt.id).all()
        for answer in answers:
            answer.question = q_map.get(answer.question_id)
            evaluate_answer(
                answer,
                user_id=current_user.id,
                role=current_user.role,
                company_id=current_user.company_id,
                db=db,
            )

        result = build_scorecard_and_skills(
            attempt,
            user_id=current_user.id,
            role=current_user.role,
            company_id=current_user.company_id,
            db=db,
        )

        synced.append({
            "assessment_id": payload.assessment_id,
            "attempt_id": attempt.id,
            "status": "graded",
            "overall_score": result.get("overall_score", 0),
        })

    return {"synced": synced, "count": len(synced)}
