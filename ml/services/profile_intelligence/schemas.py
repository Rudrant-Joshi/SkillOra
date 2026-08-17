from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ActivitySummaryInput(BaseModel):
    activity_type: Literal["snippet", "submission", "follow", "profile_update"]
    title: str
    description: Optional[str] = None
    language: Optional[str] = None
    skills_mentioned: list[str] = Field(default_factory=list)
    created_at: str


class GenerateProfileSummaryRequest(BaseModel):
    user_id: str
    username: str
    activities: list[ActivitySummaryInput] = Field(min_length=0, max_length=50)
    current_skills: dict[str, float] = Field(default_factory=dict, description="skill -> level 0..1")
    bio: Optional[str] = None


class ProfileSummaryPrediction(BaseModel):
    summary: str
    top_skills: list[str]
    suggested_headline: str
    activity_count: int
    profile_strength: Literal["empty", "emerging", "active", "established"]


class InferredSkill(BaseModel):
    skill: str
    inferred_level: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class InferSkillsFromActivityRequest(BaseModel):
    user_id: str
    activities: list[ActivitySummaryInput] = Field(min_length=1, max_length=100)
    current_skills: dict[str, float] = Field(default_factory=dict)


class InferredSkillsPrediction(BaseModel):
    inferred_skills: list[InferredSkill]
    new_skills_detected: list[str]
    confidence: float


class ScoreProfileCompletenessRequest(BaseModel):
    user_id: str
    username: str
    bio: Optional[str] = None
    activities: list[ActivitySummaryInput] = Field(min_length=0, max_length=50)
    current_skills: dict[str, float] = Field(default_factory=dict)


class ProfileCompletenessPrediction(BaseModel):
    completeness_score: float = Field(ge=0.0, le=100.0)
    band: Literal["empty", "incomplete", "partial", "complete", "verified"]
    missing_fields: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    verification_eligible: bool = False
