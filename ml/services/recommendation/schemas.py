from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CandidateSkillProfile(BaseModel):
    skills: dict[str, float] = Field(description="skill -> estimated_level 0..1")


class QuestionCandidate(BaseModel):
    question_id: str
    skills: list[str]
    difficulty: float = Field(ge=0.0, le=1.0)
    question_type: str
    times_shown_to_candidate: int = 0
    company_id: Optional[str] = None


class RecommendQuestionRequest(BaseModel):
    candidate_id: str
    candidate_profile: CandidateSkillProfile
    # The blueprint constrains the pool — the ML layer selects WITHIN it,
    # never redefines it (master prompt §9 critical rule).
    approved_question_pool: list[QuestionCandidate]
    target_skills: list[str] = Field(default_factory=list)
    exclude_question_ids: list[str] = Field(default_factory=list)
    top_k: int = Field(default=1, ge=1, le=20)


class RecommendedQuestion(BaseModel):
    question_id: str
    selection_score: float
    reason: str


class RecommendQuestionPrediction(BaseModel):
    recommendations: list[RecommendedQuestion]
