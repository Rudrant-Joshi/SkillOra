from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class EstimateDifficultyRequest(BaseModel):
    title: str
    description: str
    starter_code: Optional[str] = None
    language: Optional[str] = None
    test_cases_count: Optional[int] = None
    constraints_count: Optional[int] = None
    topics: list[str] = Field(default_factory=list)


class DifficultyPrediction(BaseModel):
    difficulty: float = Field(ge=0.0, le=1.0)  # 0=easy, 1=hard
    difficulty_label: str  # easy | medium | hard
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    signal_scores: dict[str, float] = Field(default_factory=dict)


class SubmissionOutcome(BaseModel):
    passed: bool
    runtime_ms: Optional[float] = None
    attempts: int = 1


class CalibrateDifficultyRequest(BaseModel):
    problem_id: str
    title: str
    submission_outcomes: list[SubmissionOutcome] = Field(min_length=1, max_length=500)
    prior_difficulty: float = Field(default=0.5, ge=0.0, le=1.0)


class CalibratedDifficultyPrediction(BaseModel):
    calibrated_difficulty: float = Field(ge=0.0, le=1.0)
    difficulty_label: str
    confidence: float = Field(ge=0.0, le=1.0)
    sample_size: int
    pass_rate: float
    reasoning: str
