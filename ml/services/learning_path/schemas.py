from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class GeneratePathRequest(BaseModel):
    user_id: str
    current_skills: dict[str, float] = Field(description="skill -> level 0..1")
    target_skills: list[str] = Field(min_length=1)
    time_budget_weeks: Optional[int] = Field(default=None, ge=1, le=104)
    max_steps: int = Field(default=10, ge=1, le=30)
    include_problems: bool = False


class LearningStep(BaseModel):
    step_number: int
    skill: str
    current_level: float = Field(ge=0.0, le=1.0)
    target_level: float = Field(ge=0.0, le=1.0)
    difficulty: float = Field(ge=0.0, le=1.0)
    estimated_hours: int
    reason: str
    prerequisites: list[str] = Field(default_factory=list)


class LearningPathPrediction(BaseModel):
    steps: list[LearningStep]
    total_estimated_hours: int
    weeks_estimate: float
    confidence: float
    prerequisites_warning: Optional[str] = None


class RecommendNextMilestoneRequest(BaseModel):
    user_id: str
    current_skills: dict[str, float] = Field(default_factory=dict)
    completed_milestones: list[str] = Field(default_factory=list)
    candidate_skills: list[str] = Field(min_length=1)


class MilestonePrediction(BaseModel):
    next_skill: str
    difficulty: float = Field(ge=0.0, le=1.0)
    estimated_hours: int
    reason: str
    readiness_score: float = Field(ge=0.0, le=1.0)
