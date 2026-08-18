from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SkillRead(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class UserSkillRead(BaseModel):
    id: int
    user_id: int
    skill: SkillRead
    level: float  # 0..1
    confidence: float  # 0..1
    source: str
    updated_at: str

    model_config = {"from_attributes": True}


class UserSkillEstimateResponse(BaseModel):
    user_id: int
    skills: dict[str, dict]  # skill_name -> {level, confidence, evidence_count, evidence}
