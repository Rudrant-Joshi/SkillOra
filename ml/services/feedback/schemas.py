from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class FeedbackLogRequest(BaseModel):
    request_id: str
    service: str
    model_version: str
    prediction: dict
    actual_outcome: Optional[dict] = None
    user_feedback: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class FeedbackLogResponse(BaseModel):
    logged: bool
    feedback_id: str
