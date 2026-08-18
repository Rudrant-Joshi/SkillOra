from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.skill import Skill, UserSkill
from app.models.user import User
from app.schemas.skill import SkillRead, UserSkillRead, UserSkillEstimateResponse
from app.services.ml_client import MLUnavailableError, call_ml

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("/", response_model=list[SkillRead])
def list_skills(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    return query.all()


@router.get("/me", response_model=UserSkillEstimateResponse)
def get_user_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    skills_map = {}
    for us in user_skills:
        skill_name = us.skill.name if us.skill else "unknown"
        skills_map[skill_name] = {
            "level": us.level,
            "confidence": us.confidence,
            "source": us.source,
            "updated_at": us.updated_at.isoformat() if us.updated_at else None,
        }

    # If no stored skills, estimate them via ML from the user's activities
    if not skills_map:
        try:
            from app.services.user_profile import build_user_activity_evidence
            evidence = build_user_activity_evidence(current_user.id, db)
            if evidence:
                batch_result = call_ml(
                    "/ml/skill/estimate-batch",
                    {"user_id": str(current_user.id), "skills": evidence},
                    user_id=current_user.id,
                    role=current_user.role,
                    company_id=current_user.company_id,
                    unwrap=False,
                )
                for skill_name, ml_resp in batch_result.get("prediction", {}).items():
                    pred = ml_resp.get("prediction", {})
                    skills_map[skill_name] = {
                        "level": pred.get("estimated_level", 0.0),
                        "confidence": pred.get("confidence", 0.0),
                        "evidence_count": pred.get("evidence_count", 0),
                        "evidence": pred.get("evidence", []),
                    }
        except MLUnavailableError:
            pass

    return UserSkillEstimateResponse(user_id=current_user.id, skills=skills_map)


@router.get("/user/{user_id}", response_model=UserSkillEstimateResponse)
def get_user_skills_admin(
    user_id: int,
    current_user: User = Depends(require_role("trainer")),
    db: Session = Depends(get_db),
):
    """Trainer/Admin can view any user's skill profile within their company."""
    from app.services.analytics_service import check_company_member
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    check_company_member(current_user, target, db)

    user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    skills_map = {}
    for us in user_skills:
        skill_name = us.skill.name if us.skill else "unknown"
        skills_map[skill_name] = {
            "level": us.level,
            "confidence": us.confidence,
            "source": us.source,
            "updated_at": us.updated_at.isoformat() if us.updated_at else None,
        }
    return UserSkillEstimateResponse(user_id=user_id, skills=skills_map)
