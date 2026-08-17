from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ReputationActivitySummary(BaseModel):
    snippets_pushed: int = 0
    problems_solved: int = 0
    problems_attempted: int = 0
    followers_count: int = 0
    following_count: int = 0
    profile_completeness: float = Field(default=0.0, ge=0.0, le=100.0)
    avg_code_quality: float = Field(default=0.0, ge=0.0, le=100.0)
    account_age_days: int = Field(default=1, ge=1)
    # Optional, used when per-activity quality is available
    quality_samples: list[float] = Field(default_factory=list)


class ComputeReputationRequest(BaseModel):
    user_id: str
    activity: ReputationActivitySummary
    verified_skills: list[str] = Field(default_factory=list)


class ReputationFactor(BaseModel):
    name: str
    contribution: float
    detail: str


class ReputationPrediction(BaseModel):
    reputation_score: float = Field(ge=0.0, le=100.0)
    band: Literal["newcomer", "contributor", "trusted", "elite"]
    factors: list[ReputationFactor] = Field(default_factory=list)
    confidence: float
    verification_eligible: bool


class ComputeActivityQualityRequest(BaseModel):
    activity_type: Literal["snippet", "submission", "follow", "profile_update"]
    code_quality_score: float = Field(default=0.0, ge=0.0, le=100.0)
    test_pass_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    has_description: bool = False
    engagement_count: int = 0
    novelty_score: float = Field(default=0.5, ge=0.0, le=1.0)


class ActivityQualityPrediction(BaseModel):
    quality_score: float = Field(ge=0.0, le=100.0)
    quality_band: Literal["low", "fair", "good", "excellent"]
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
