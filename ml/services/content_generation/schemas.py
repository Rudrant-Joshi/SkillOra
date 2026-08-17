from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class GenerateQuestionRequest(BaseModel):
    skill: str
    topic: str
    difficulty: float = Field(ge=0.0, le=1.0)
    question_type: str = "mcq"
    language: Optional[str] = None
    job_role: Optional[str] = None
    assessment_blueprint: Optional[dict] = None


class GeneratedQuestionDraft(BaseModel):
    draft_id: str
    skill: str
    topic: str
    difficulty: float
    question_type: str
    title: str
    prompt: str
    options: list[str] = Field(default_factory=list)
    correct_answer: Optional[str] = None
    explanation: str = ""
    starter_code: Optional[str] = None
    visible_tests: list[str] = Field(default_factory=list)
    hidden_tests: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    validation_flags: list[str] = Field(default_factory=list)
    requires_human_review: bool = True


class GenerateQuestionPrediction(BaseModel):
    draft: GeneratedQuestionDraft
    confidence: float = Field(ge=0.0, le=1.0)
