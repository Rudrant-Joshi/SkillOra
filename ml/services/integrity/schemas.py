from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class IntegrityFlag(BaseModel):
    type: str
    count: int = Field(ge=0)
    detail: Optional[str] = None


class ASTSimilarityResult(BaseModel):
    max_similarity_pct: float = Field(ge=0.0, le=100.0)
    comparison_type: str = "reference_solution"
    compared_question_id: Optional[str] = None


class AnalyzeIntegrityRequest(BaseModel):
    candidate_id: str
    assessment_id: str
    signals: list[dict] = Field(default_factory=list, description="Proctoring signal events from the frontend collector")
    submitted_code: Optional[str] = None
    reference_solution: Optional[str] = None
    language: Optional[str] = None


class IntegrityPrediction(BaseModel):
    integrity_score: int = Field(ge=0, le=100)
    band: str
    flags: list[IntegrityFlag] = Field(default_factory=list)
    ast_similarity: Optional[ASTSimilarityResult] = None
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0)
