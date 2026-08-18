from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.attempt import Attempt
from app.models.ml_prediction import MLPrediction
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary, MLPredictionLog

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=AnalyticsSummary)
def dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trainer/Admin dashboard analytics overview."""
    total_users = db.query(User).filter(User.company_id == current_user.company_id).count()
    total_assessments = db.query(Attempt).filter(Attempt.user_id.in_(
        db.query(User.id).filter(User.company_id == current_user.company_id)
    )).count()
    total_attempts = db.query(Attempt).count() if current_user.role == "admin" else db.query(Attempt).filter(
        Attempt.user_id.in_(db.query(User.id).filter(User.company_id == current_user.company_id))
    ).count()

    from app.models.question import Question
    from app.models.assessment import Assessment
    total_questions = db.query(Question).filter(Question.assessment_id.in_(
        db.query(Assessment.id).filter(
            Assessment.company_id == current_user.company_id if current_user.company_id else None
        )
    )).count()

    scored_attempts = db.query(Attempt).filter(
        Attempt.overall_score > 0,
        Attempt.user_id.in_(db.query(User.id).filter(User.company_id == current_user.company_id)) if current_user.company_id else True
    ).all()
    avg_score = round(sum(a.overall_score for a in scored_attempts) / len(scored_attempts), 2) if scored_attempts else 0.0

    ml_count = db.query(MLPrediction).count()
    recent_ml = db.query(MLPrediction).order_by(MLPrediction.created_at.desc()).limit(10).all()

    return AnalyticsSummary(
        total_users=total_users,
        total_assessments=total_attempts,
        total_attempts=total_attempts,
        total_questions=total_questions,
        average_score=avg_score,
        ml_prediction_count=ml_count,
        recent_ml_predictions=[
            MLPredictionLog(
                id=p.id,
                service_name=p.service_name,
                model_version=p.model_version,
                confidence=p.confidence,
                success=p.success,
                latency_ms=p.latency_ms,
                created_at=p.created_at.isoformat() if p.created_at else "",
            )
            for p in recent_ml
        ],
    )


@router.get("/assessment/{assessment_id}")
def assessment_analytics(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Detailed analytics for a specific assessment — trainer/admin only."""
    from app.models.assessment import Assessment
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    if current_user.role not in ("trainer", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if current_user.company_id and a.company_id and current_user.company_id != a.company_id:
        if current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    attempts = db.query(Attempt).filter(Attempt.assessment_id == assessment_id).all()
    completed = [a for a in attempts if a.status == "graded" or a.submitted_at]
    scores = [a.overall_score for a in completed if a.overall_score > 0]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    avg_ml = round(sum(a.ml_score for a in completed) / len(completed), 2) if completed else 0.0
    pass_rate = round(len([s for s in scores if s >= 60]) / len(scores) * 100, 2) if scores else 0.0

    # Dimension averages from ml_analysis
    dimension_avgs: dict[str, float] = {}
    dim_counts: dict[str, int] = {}
    for att in completed:
        try:
            analysis = att.ml_analysis and __import__("json").loads(att.ml_analysis)
        except Exception:
            analysis = {}
        dims = analysis.get("scorecard", {}).get("dimensions", {}) if analysis else {}
        for dim, val in dims.items():
            dimension_avgs[dim] = dimension_avgs.get(dim, 0) + val
            dim_counts[dim] = dim_counts.get(dim, 0) + 1
    dimension_averages = {k: round(v / dim_counts[k], 2) for k, v in dimension_avgs.items()} if dim_counts else {}

    # Question performance
    from app.models.attempt import Attempt, Answer
    from app.models.question import Question
    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    question_perf = []
    for q in questions:
        answers = db.query(Answer).filter(Answer.question_id == q.id).all()
        evals = []
        for ans in answers:
            try:
                ed = __import__("json").loads(ans.ml_evaluation) if ans.ml_evaluation else {}
            except Exception:
                ed = {}
            if ed.get("score") is not None:
                evals.append(ed["score"])
        avg = round(sum(evals) / len(evals), 2) if evals else None
        question_perf.append({
            "question_id": q.id,
            "prompt": q.prompt[:80],
            "question_type": q.question_type,
            "skills": q.skills.split(",") if q.skills else [],
            "average_score": avg,
            "attempts": len(evals),
        })

    return {
        "assessment_id": a.id,
        "title": a.title,
        "total_attempts": len(attempts),
        "completed_attempts": len(completed),
        "average_score": avg_score,
        "average_ml_score": avg_ml,
        "pass_rate": pass_rate,
        "dimension_averages": dimension_averages,
        "question_performance": question_perf,
    }


@router.get("/candidate/{user_id}")
def candidate_analytics(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Candidate progress analytics — candidate sees own, trainer/admin see company members."""
    _check_access(current_user, user_id, db)

    attempts = db.query(Attempt).filter(Attempt.user_id == user_id).all()
    completed = [a for a in attempts if a.submitted_at]
    scores = [a.overall_score for a in completed if a.overall_score > 0]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0

    # Skill progression from ml_analysis
    skill_data: dict[str, dict] = {}
    for att in completed:
        try:
            analysis = __import__("json").loads(att.ml_analysis) if att.ml_analysis else {}
        except Exception:
            analysis = {}
        skills = analysis.get("skills", {})
        for skill_name, est in skills.items():
            if skill_name not in skill_data:
                skill_data[skill_name] = []
            skill_data[skill_name].append({
                "attempt_id": att.id,
                "level": est.get("level", 0),
                "confidence": est.get("confidence", 0),
                "timestamp": att.submitted_at.isoformat() if att.submitted_at else "",
            })

    recent_attempts = []
    for att in completed[-5:]:
        a = att.assessment
        recent_attempts.append({
            "attempt_id": att.id,
            "assessment_title": a.title if a else "",
            "started_at": att.started_at.isoformat() if att.started_at else None,
            "submitted_at": att.submitted_at.isoformat() if att.submitted_at else None,
            "overall_score": att.overall_score,
            "ml_score": att.ml_score,
            "raw_score": att.raw_score,
            "status": att.status,
        })

    return {
        "user_id": user_id,
        "assessments_completed": len(completed),
        "assessments_total": len(attempts),
        "average_score": avg_score,
        "skill_progression": skill_data,
        "recent_attempts": recent_attempts,
    }


@router.get("/skill-gaps")
def skill_gap_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze skill gaps for the current user (or a team for trainers/admins)."""
    from app.models.skill import UserSkill
    if current_user.role == "candidate":
        user_ids = [current_user.id]
    else:
        user_ids = [u.id for u in db.query(User).filter(User.company_id == current_user.company_id).all()]

    gaps = []
    for uid in user_ids:
        user_skills = db.query(UserSkill).filter(UserSkill.user_id == uid).all()
        for us in user_skills:
            if us.level < 0.5:
                gaps.append({
                    "user_id": uid,
                    "skill": us.skill.name if us.skill else "unknown",
                    "current_level": us.level,
                    "confidence": us.confidence,
                    "priority": "high" if us.level < 0.3 else "medium",
                })
    gaps.sort(key=lambda g: g["current_level"])
    return {"gaps": gaps, "total": len(gaps)}


def _check_access(user: User, target_user_id: int, db: Session):
    if user.id == target_user_id:
        return
    if user.role in ("trainer", "admin") and user.company_id:
        target = db.query(User).filter(User.id == target_user_id).first()
        if target and target.company_id == user.company_id:
            return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
