from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

QuestionType = Literal[
    "mcq", "multi_select", "sql", "coding", "short_answer", "system_design"
]


class TestResult(BaseModel):
    name: str
    passed: bool
    hidden: bool = False


class EvaluateRequest(BaseModel):
    question_id: str
    question_type: QuestionType
    # deterministic inputs
    correct_options: Optional[list[str]] = None
    submitted_options: Optional[list[str]] = None
    test_results: Optional[list[TestResult]] = None  # for coding/sql
    time_limit_exceeded: Optional[bool] = None
    memory_limit_exceeded: Optional[bool] = None
    compiled: Optional[bool] = None
    # AI-assisted inputs (free text / design answers)
    prompt: Optional[str] = None
    submitted_answer: Optional[str] = None
    rubric: Optional[list[str]] = Field(
        default=None, description="Grading criteria the AI grader must weigh"
    )


class EvaluationPrediction(BaseModel):
    score: float = Field(ge=0.0, le=100.0)
    evaluation_method: Literal["deterministic", "ai_assisted", "hybrid"]
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    reasoning: str = ""
    needs_human_review: bool = False
