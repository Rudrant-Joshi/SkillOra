from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.question import Question
from app.models.user import User
from app.schemas.question import QuestionRead, QuestionWrite

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("/assessment/{assessment_id}", response_model=list[QuestionRead])
def list_questions(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.assessment import Assessment
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    if current_user.role not in ("trainer", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    questions = db.query(Question).filter(Question.assessment_id == assessment_id).order_by(Question.id).all()
    return [_question_to_read(q) for q in questions]


@router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
def create_question(
    req: QuestionWrite,
    current_user: User = Depends(require_role("trainer")),
    db: Session = Depends(get_db),
):
    from app.models.assessment import Assessment
    a = db.query(Assessment).filter(Assessment.id == req.assessment_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    if current_user.company_id and a.company_id != current_user.company_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    q = Question(
        assessment_id=req.assessment_id,
        question_type=req.question_type,
        prompt=req.prompt,
        options=req.options,
        correct_options=req.correct_options,
        difficulty=req.difficulty,
        skills=",".join(req.skills),
        language=req.language,
        starter_code=req.starter_code or "",
        rubric=req.rubric,
        test_cases_template=req.test_cases_template,
        is_public=False,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return _question_to_read(q)


@router.get("/{question_id}", response_model=QuestionRead)
def get_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return _question_to_read(q)


def _question_to_read(q: Question) -> QuestionRead:
    opts = q.options if isinstance(q.options, list) else []
    correct = q.correct_options if isinstance(q.correct_options, list) else []
    tct = q.test_cases_template if isinstance(q.test_cases_template, list) else []
    rub = q.rubric if isinstance(q.rubric, list) else []
    return QuestionRead(
        id=q.id,
        assessment_id=q.assessment_id,
        question_type=q.question_type,
        prompt=q.prompt,
        options=opts,
        correct_options=correct,
        difficulty=q.difficulty,
        skills=[s.strip() for s in q.skills.split(",")] if q.skills else [],
        language=q.language,
        starter_code=q.starter_code,
        test_cases_template=tct,
        rubric=rub,
        is_public=q.is_public,
    )
