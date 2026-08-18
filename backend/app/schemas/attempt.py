from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class AttemptStartResponse(BaseModel):
    attempt_id: int
    assessment_id: int
    assessment_title: str
    duration_minutes: int
    total_questions: int
    started_at: str


class AttemptQuestion(BaseModel):
    id: int
    question_type: str
    prompt: str
    options: list[str]
    difficulty: float
    skills: list[str]
    language: str
    starter_code: Optional[str] = None
    test_cases_template: list[dict[str, Any]]
    rubric: list[str]


class AttemptQuestionsResponse(BaseModel):
    attempt_id: int
    assessment_id: int
    questions: list[AttemptQuestion]
    duration_minutes: int


class AnswerSubmit(BaseModel):
    question_id: int
    question_type: str
    submitted_options: list[int] = Field(default_factory=list)
    submitted_code: str = ""
    submitted_answer: str = ""
    test_results: list[dict[str, Any]] = Field(default_factory=list)
    time_limit_exceeded: bool = False
    memory_limit_exceeded: bool = False
    compiled: bool = True
    time_spent_seconds: float = 0.0


class AttemptSubmitRequest(BaseModel):
    answers: list[AnswerSubmit]


class AttemptRead(BaseModel):
    id: int
    assessment_id: int
    assessment_title: str
    started_at: str
    submitted_at: Optional[str] = None
    status: str
    raw_score: float
    ml_score: float
    overall_score: float
    is_offline: bool
    ml_analysis: dict[str, Any]
    dimension_scores: Optional[dict[str, float]] = None
    dimension_details: Optional[dict[str, dict[str, Any]]] = None
    skills: Optional[dict[str, dict[str, Any]]] = None
    evidence: Optional[list[str]] = None
    questions_count: Optional[int] = 0

    model_config = {"from_attributes": True}


class AttemptResultResponse(BaseModel):
    attempt_id: int
    assessment_id: int
    assessment_title: str
    overall_score: float
    raw_score: float
    ml_score: float
    dimension_scores: dict[str, float]
    dimension_details: dict[str, dict[str, Any]]
    skills: dict[str, dict[str, Any]]
    evidence: list[str]
    questions_count: int
    time_spent_seconds: float
    completed_at: Optional[str]
    ml_analysis: dict[str, Any]
