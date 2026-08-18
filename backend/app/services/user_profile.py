"""
User profile service — builds evidence for skill estimation from a user's
assessment attempts and activities.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

logger = logging.getLogger("backend.profile")


def build_user_activity_evidence(user_id: int, db: Session) -> dict[str, list[dict]]:
    """
    Build skill evidence from the user's completed assessment attempts.

    Returns {skill_name: [evidence_item, ...]} in the format expected by
    the ML gateway's /ml/skill/estimate-batch endpoint.
    """
    from app.models.attempt import Attempt, Answer

    attempts = db.query(Attempt).filter(
        Attempt.user_id == user_id, Attempt.status == "graded"
    ).all()

    skill_evidence: dict[str, list[dict]] = {}
    for att in attempts:
        answers = db.query(Answer).filter(Answer.attempt_id == att.id).all()
        for ans in answers:
            try:
                eval_data = json.loads(ans.ml_evaluation) if ans.ml_evaluation else {}
            except (json.JSONDecodeError, TypeError):
                eval_data = {}
            score = eval_data.get("score", 0.0)
            observed = score / 100.0
            ts = ans.created_at.isoformat() if ans.created_at else datetime.now(timezone.utc).isoformat()
            # Get skill from question
            q = ans.question
            if q and q.skills:
                for skill_name in [s.strip() for s in q.skills.split(",") if s.strip()]:
                    skill_evidence.setdefault(skill_name, []).append({
                        "source": "assessment",
                        "observed_value": observed,
                        "timestamp": ts,
                        "detail": f"Attempt #{att.id}, Q{q.id}: {score} points",
                    })

    return skill_evidence
