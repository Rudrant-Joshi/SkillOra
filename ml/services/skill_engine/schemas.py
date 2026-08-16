from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EvidenceInput(BaseModel):
    source: str = Field(description="e.g. 'assessment', 'coding_submission_tests_passed', 'self_declared'")
    observed_value: float = Field(ge=0.0, le=1.0)
    timestamp: datetime
    weight_override: Optional[float] = None
    detail: Optional[str] = None


class SkillEstimateRequest(BaseModel):
    user_id: str
    skill: str
    evidence: list[EvidenceInput] = Field(min_length=0)


class BatchSkillEstimateRequest(BaseModel):
    user_id: str
    skills: dict[str, list[EvidenceInput]]  # skill_name -> evidence list


class SkillEstimatePrediction(BaseModel):
    skill: str
    estimated_level: float
    confidence: float
    evidence_count: int
