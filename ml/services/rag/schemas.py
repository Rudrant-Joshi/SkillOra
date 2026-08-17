from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RagFilters(BaseModel):
    """Metadata filters, master prompt §6. All optional; caller supplies
    only what's relevant to the query's authorization scope."""

    user_id: Optional[str] = None
    company_id: Optional[str] = None
    repository_id: Optional[str] = None
    course_id: Optional[str] = None
    topic: Optional[str] = None
    skill: Optional[str] = None
    language: Optional[str] = None
    visibility: Optional[str] = None  # e.g. "public", "company_private", "user_private"


class RagQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    filters: RagFilters = Field(default_factory=RagFilters)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    text: str
    similarity: float
    metadata: dict


class RagAnswerPrediction(BaseModel):
    answer: str
    grounded: bool
    retrieved_chunks: list[RetrievedChunk]
    uncertain: bool = False
