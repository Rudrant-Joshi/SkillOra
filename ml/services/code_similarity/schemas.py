from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CodeSimilarityRequest(BaseModel):
    candidate_code: str
    reference_code: Optional[str] = None
    language: str = "python"
    comparison_type: str = Field(default="reference_solution", description="reference_solution | candidate_vs_candidate | corpus")


class CodeSimilarityPrediction(BaseModel):
    similarity: float = Field(ge=0.0, le=1.0)
    method: str
    comparison: str
    confidence: float = Field(ge=0.0, le=1.0)
