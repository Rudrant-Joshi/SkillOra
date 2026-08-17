from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class JobRequirement(BaseModel):
    job_id: str
    title: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_experience_years: Optional[float] = None
    description: Optional[str] = None


class CandidateProfile(BaseModel):
    candidate_id: str
    skills: dict[str, float] = Field(default_factory=dict, description="skill -> estimated_level 0..1")
    experience_years: Optional[float] = None
    summary: Optional[str] = None


class CandidateJobMatchRequest(BaseModel):
    job: JobRequirement
    candidate: CandidateProfile
    assessment_results: Optional[dict] = Field(
        default=None, description="Optional assessment scores keyed by skill or overall"
    )
    shared_repository_ids: list[str] = Field(default_factory=list)
    shared_project_ids: list[str] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)


class SkillMatchEvidence(BaseModel):
    skill: str
    matched: bool
    candidate_level: Optional[float] = None
    required_level: float = 0.0
    source: str = "skill_profile"


class CandidateJobMatchPrediction(BaseModel):
    match_score: float = Field(ge=0.0, le=1.0)
    matched_skills: list[SkillMatchEvidence] = Field(default_factory=list)
    missing_skills: list[SkillMatchEvidence] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
