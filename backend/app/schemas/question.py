from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class QuestionRead(BaseModel):
    id: int
    assessment_id: int
    question_type: str
    prompt: str
    options: list[str]
    correct_options: list[int]
    difficulty: float
    skills: list[str]
    language: str
    starter_code: Optional[str] = None
    rubric: list[str]
    test_cases_template: list[dict[str, Any]]
    is_public: bool

    model_config = {"from_attributes": True}


class QuestionWrite(BaseModel):
    assessment_id: int
    question_type: str = Field(..., pattern="^(mcq|multi_select|coding|sql|short_answer|system_design)$")
    prompt: str = Field(..., min_length=1)
    options: list[str] = Field(default_factory=list)
    correct_options: list[int] = Field(default_factory=list)
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    skills: list[str] = Field(default_factory=list)
    language: str = "python"
    starter_code: Optional[str] = None
    rubric: list[str] = Field(default_factory=list)
    test_cases_template: list[dict[str, Any]] = Field(default_factory=list)
