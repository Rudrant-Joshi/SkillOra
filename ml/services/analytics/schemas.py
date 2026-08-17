from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AnalyticsQuery(BaseModel):
    service: Optional[str] = None
    model_version: Optional[str] = None
    since: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)


class AnalyticsSummary(BaseModel):
    total_requests: int
    avg_latency_ms: float
    avg_confidence: Optional[float]
    error_rate: float
    service_breakdown: dict[str, int] = Field(default_factory=dict)
