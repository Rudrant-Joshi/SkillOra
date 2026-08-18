from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.assessment import Assessment
from app.models.attempt import Attempt
from app.models.question import Question
from app.models.user import Company, User
from app.schemas.assessment import AssessmentCreate, AssessmentRead, AssessmentUpdate
from app.schemas.attempt import AttemptQuestion, AttemptQuestionsResponse, AttemptStartResponse

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


def _parse_list(text: str) -> list[str]:
    if not text:
        return []
    return [s.strip() for s in text.split(",") if s.strip()]


def _parse_floats(text: str) -> dict[str, float]:
    import json
    try:
        val = json.loads(text) if text else {}
        if isinstance(val, dict):
            return {k: float(v) for k, v in val.items()}
    except (json.JSONDecodeError, TypeError):
        return {}
    return {}


@router.get("/", response_model=list[AssessmentRead])
def list_assessments(
    company_id: Optional[int] = None,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all assessments available to the current user."""
    query = db.query(Assessment)
    if active_only:
        query = query.filter(Assessment.is_active == True)
    if current_user.role == "candidate":
        query = query.filter(Assessment.company_id == current_user.company_id)
    elif current_user.company_id and company_id is None:
        query = query.filter(Assessment.company_id == current_user.company_id)
    elif company_id:
        query = query.filter(Assessment.company_id == company_id)
    results = query.order_by(Assessment.created_at.desc()).all()
    return [_assessment_to_read(a, db) for a in results]


@router.get("/{assessment_id}", response_model=AssessmentRead)
def get_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    if a.is_active is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    _check_company_access(current_user, a.company_id)
    return _assessment_to_read(a, db)


@router.post("/", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED)
def create_assessment(
    req: AssessmentCreate,
    current_user: User = Depends(require_role("trainer")),
    db: Session = Depends(get_db),
):
    a = Assessment(
        title=req.title,
        description=req.description,
        company_id=current_user.company_id,
        duration_minutes=req.duration_minutes,
        total_questions=req.total_questions,
        skills=",".join(req.skills),
        difficulty_distribution=req.difficulty_distribution,
        allowed_question_types=",".join(req.allowed_question_types),
        coding_languages=",".join(req.coding_languages),
        is_adaptive=req.is_adaptive,
        scoring_rubric="{}",
        is_active=True,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return _assessment_to_read(a, db)


@router.put("/{assessment_id}", response_model=AssessmentRead)
def update_assessment(
    assessment_id: int,
    req: AssessmentUpdate,
    current_user: User = Depends(require_role("trainer")),
    db: Session = Depends(get_db),
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    _check_company_access(current_user, a.company_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        if field == "skills":
            setattr(a, field, ",".join(value))
        else:
            setattr(a, field, value)
    db.commit()
    db.refresh(a)
    return _assessment_to_read(a, db)


@router.post("/{assessment_id}/start", response_model=AttemptStartResponse)
def start_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Candidate starts an assessment — creates a new attempt in 'in_progress' state."""
    if current_user.role != "candidate":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only candidates can start assessments")
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    if not a.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assessment is not active")
    _check_company_access(current_user, a.company_id)

    # Prevent duplicate in-progress attempts
    existing = db.query(Attempt).filter(
        Attempt.user_id == current_user.id,
        Attempt.assessment_id == assessment_id,
        Attempt.status == "in_progress",
    ).first()
    if existing:
        return AttemptStartResponse(
            attempt_id=existing.id,
            assessment_id=a.id,
            assessment_title=a.title,
            duration_minutes=a.duration_minutes,
            total_questions=a.total_questions,
            started_at=existing.started_at.isoformat() if existing.started_at else "",
        )

    attempt = Attempt(
        user_id=current_user.id,
        assessment_id=assessment_id,
        status="in_progress",
        started_at=datetime.now(timezone.utc),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return AttemptStartResponse(
        attempt_id=attempt.id,
        assessment_id=a.id,
        assessment_title=a.title,
        duration_minutes=a.duration_minutes,
        total_questions=a.total_questions,
        started_at=attempt.started_at.isoformat() if attempt.started_at else "",
    )


@router.get("/{assessment_id}/questions", response_model=AttemptQuestionsResponse)
def get_assessment_questions(
    assessment_id: int,
    attempt_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch all questions for an assessment. If attempt_id is provided,
    returns questions with the user's previous answers (for resuming).
    For adaptive mode, returns the full pool or fetches next question via ML.
    """
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    _check_company_access(current_user, a.company_id)

    # Verify the user has an in-progress attempt (or create one)
    if not attempt_id:
        existing = db.query(Attempt).filter(
            Attempt.user_id == current_user.id,
            Attempt.assessment_id == assessment_id,
            Attempt.status == "in_progress",
        ).first()
        if existing:
            attempt_id = existing.id
        else:
            attempt = Attempt(
                user_id=current_user.id,
                assessment_id=assessment_id,
                status="in_progress",
                started_at=datetime.now(timezone.utc),
            )
            db.add(attempt)
            db.commit()
            db.refresh(attempt)
            attempt_id = attempt.id

    questions = db.query(Question).filter(Question.assessment_id == assessment_id).order_by(Question.id).all()

    return AttemptQuestionsResponse(
        attempt_id=attempt_id,
        assessment_id=a.id,
        duration_minutes=a.duration_minutes,
        questions=[_question_to_schema(q, db) for q in questions],
    )


@router.get("/{assessment_id}/attempts", response_model=list)
def list_attempts(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all attempts for an assessment (trainer/admin see all, candidate sees own)."""
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    _check_company_access(current_user, a.company_id)

    query = db.query(Attempt).filter(Attempt.assessment_id == assessment_id)
    if current_user.role == "candidate":
        query = query.filter(Attempt.user_id == current_user.id)
    attempts = query.order_by(Attempt.started_at.desc()).all()

    result = []
    for att in attempts:
        result.append({
            "id": att.id,
            "assessment_id": att.assessment_id,
            "assessment_title": a.title,
            "user_id": att.user_id,
            "started_at": att.started_at.isoformat() if att.started_at else None,
            "submitted_at": att.submitted_at.isoformat() if att.submitted_at else None,
            "status": att.status,
            "raw_score": att.raw_score,
            "ml_score": att.ml_score,
            "overall_score": att.overall_score,
            "is_offline": att.is_offline,
        })
    return result


# --- Helpers ---

def _check_company_access(user: User, company_id):
    """Admin and trainers can access their own company's data."""
    if user.role == "admin" and not user.company_id:
        return  # global admin
    if company_id is None and user.role in ("admin", "trainer"):
        return
    if user.company_id and company_id and user.company_id == company_id:
        return
    if user.role in ("admin", "trainer"):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this assessment")


def _assessment_to_read(a: Assessment, db: Session) -> AssessmentRead:
    company_name = None
    if a.company_id:
        co = db.query(Company).filter(Company.id == a.company_id).first()
        company_name = co.name if co else None
    diff_dist = a.difficulty_distribution
    if not isinstance(diff_dist, dict):
        diff_dist = _parse_floats(diff_dist) if isinstance(diff_dist, str) else {}
    return AssessmentRead(
        id=a.id,
        title=a.title,
        description=a.description,
        company=company_name,
        duration_minutes=a.duration_minutes,
        total_questions=a.total_questions,
        skills=_parse_list(a.skills),
        difficulty_distribution=diff_dist,
        allowed_question_types=_parse_list(a.allowed_question_types),
        coding_languages=_parse_list(a.coding_languages),
        is_active=a.is_active,
        is_adaptive=a.is_adaptive,
        created_at=a.created_at.isoformat() if a.created_at else "",
    )


def _question_to_schema(q: Question, db: Session) -> AttemptQuestion:
    opts = q.options if isinstance(q.options, list) else []
    tct = q.test_cases_template if isinstance(q.test_cases_template, list) else []
    rub = q.rubric if isinstance(q.rubric, list) else []
    return AttemptQuestion(
        id=q.id,
        question_type=q.question_type,
        prompt=q.prompt,
        options=opts,
        difficulty=q.difficulty,
        skills=_parse_list(q.skills),
        language=q.language,
        starter_code=q.starter_code,
        test_cases_template=tct,
        rubric=rub,
    )
