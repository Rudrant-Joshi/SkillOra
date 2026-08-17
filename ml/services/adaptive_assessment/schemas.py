from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SkillEstimateInput(BaseModel):
    skill: str
    estimated_level: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)


class QuestionBlueprintConstraints(BaseModel):
    total_questions: int = Field(ge=1, description="Total questions in this assessment")
    allowed_skills: list[str] = Field(default_factory=list)
    allowed_question_types: list[str] = Field(default_factory=list)
    difficulty_distribution: dict[str, float] = Field(
        default_factory=dict,
        description="Map of difficulty bucket ('easy','medium','hard') to required count or weight",
    )
    max_duration_seconds: Optional[int] = None
    coding_languages: list[str] = Field(default_factory=list)


class AssessmentHistoryEntry(BaseModel):
    question_id: str
    skill: str
    difficulty: float = Field(ge=0.0, le=1.0)
    correct: bool
    time_spent_seconds: Optional[float] = None
    question_type: str


class AdaptiveSelectRequest(BaseModel):
    candidate_id: str
    assessment_id: str
    blueprint: QuestionBlueprintConstraints
    skill_profile: dict[str, SkillEstimateInput] = Field(default_factory=dict)
    answered_questions: list[AssessmentHistoryEntry] = Field(default_factory=list)
    remaining_approved_pool: list[dict] = Field(
        default_factory=list,
        description="Approved question pool from backend; each item must include question_id, skills, difficulty, question_type",
    )
    target_skills: list[str] = Field(default_factory=list)
    top_k: int = Field(default=1, ge=1, le=20)


class RecommendedAdaptiveQuestion(BaseModel):
    question_id: str
    selection_score: float
    reason: str
    skill_targeted: str
    estimated_difficulty: float
    blueprint_alignment: dict[str, str]


class AdaptiveSelectPrediction(BaseModel):
    next_question: Optional[RecommendedAdaptiveQuestion] = None
    current_skill_estimates: dict[str, float]
    updated_confidence: dict[str, float]
    questions_answered: int
    questions_remaining: int
    blueprint_progress: dict[str, int]
