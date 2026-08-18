from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AssessmentRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    company: Optional[str] = None
    duration_minutes: int
    total_questions: int
    skills: list[str]
    difficulty_distribution: dict[str, float]
    allowed_question_types: list[str]
    coding_languages: list[str]
    is_active: bool
    is_adaptive: bool
    created_at: str

    model_config = {"from_attributes": True}


class AssessmentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    duration_minutes: int = Field(default=60, ge=1, le=300)
    total_questions: int = Field(default=25, ge=1, le=200)
    skills: list[str] = Field(default_factory=list)
    difficulty_distribution: dict[str, float] = Field(default_factory=dict)
    allowed_question_types: list[str] = Field(default_factory=list)
    coding_languages: list[str] = Field(default_factory=list)
    is_adaptive: bool = True


class AssessmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    total_questions: Optional[int] = None
    skills: Optional[list[str]] = None
    is_active: Optional[bool] = None
    is_adaptive: Optional[bool] = None
