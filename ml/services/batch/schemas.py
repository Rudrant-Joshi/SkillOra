from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class BatchRecommendRequest(BaseModel):
    candidate_ids: list[str]
    approved_question_pool: list[dict] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=50)


class BatchRecommendResponse(BaseModel):
    results: dict[str, list[dict]] = Field(default_factory=dict)
    total_candidates: int
