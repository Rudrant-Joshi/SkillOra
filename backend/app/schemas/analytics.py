from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class CandidateProgress(BaseModel):
    user_id: int
    email: str
    full_name: str
    assessments_completed: int
    assessments_total: int
    average_score: float
    recent_attempts: list[dict[str, Any]]


class SkillGapAnalysis(BaseModel):
    skill_name: str
    current_level: float
    current_confidence: float
    target_level: float
    gap: float
    priority: str  # high, medium, low
    recommended_milestones: list[str]


class AssessmentAnalytics(BaseModel):
    assessment_id: int
    title: str
    total_attempts: int
    completed_attempts: int
    average_score: float
    average_ml_score: float
    pass_rate: float
    dimension_averages: dict[str, float]
    question_performance: list[dict[str, Any]]
    time_distribution: dict[str, Any]


class MLPredictionLog(BaseModel):
    id: int
    service_name: str
    model_version: str
    confidence: float
    success: bool
    latency_ms: float
    created_at: str


class AnalyticsSummary(BaseModel):
    total_users: int
    total_assessments: int
    total_attempts: int
    total_questions: int
    average_score: float
    ml_prediction_count: int
    recent_ml_predictions: list[MLPredictionLog]
