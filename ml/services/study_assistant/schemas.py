from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class StudyAssistRequest(BaseModel):
    user_id: str
    query: str = Field(min_length=1, max_length=4000)
    skill_profile: Optional[dict[str, float]] = Field(default=None, description="skill -> estimated_level 0..1")
    context: Optional[str] = None
    mode: str = Field(default="explain", description="explain | study_plan | flashcard")


class StudyAssistPrediction(BaseModel):
    answer: str
    mode: str
    grounded: bool = False
    sources: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
