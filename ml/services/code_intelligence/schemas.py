from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Task = Literal["explain", "review", "analyze", "security_scan"]


class CodeAnalysisRequest(BaseModel):
    language: str
    repository: Optional[str] = None
    file: Optional[str] = None
    code: str = Field(min_length=1, max_length=200_000)
    context: Optional[str] = None
    task: Task = "review"


class Issue(BaseModel):
    type: str  # e.g. "bug", "security", "smell", "style", "complexity"
    severity: Literal["low", "medium", "high", "critical"]
    line: Optional[int] = None
    message: str
    source: Literal["static_analysis", "llm"]


class ComplexityMetrics(BaseModel):
    cyclomatic_complexity: Optional[int] = None
    lines_of_code: int
    max_nesting_depth: Optional[int] = None
    function_count: Optional[int] = None
    long_functions: list[str] = Field(default_factory=list)


class CodeAnalysisPrediction(BaseModel):
    summary: str
    issues: list[Issue] = Field(default_factory=list)
    severity: Literal["low", "medium", "high", "critical", "none"]
    suggestions: list[str] = Field(default_factory=list)
    complexity: ComplexityMetrics
    security_findings: list[Issue] = Field(default_factory=list)
    quality_score: int = Field(ge=0, le=100)
    duplicate_code_hints: list[str] = Field(default_factory=list)
