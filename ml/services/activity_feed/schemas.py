from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class FeedActivityInput(BaseModel):
    activity_id: str
    activity_type: Literal["snippet", "submission", "follow", "profile_update"]
    user_id: str
    username: str
    title: str
    description: Optional[str] = None
    language: Optional[str] = None
    skills_mentioned: list[str] = Field(default_factory=list)
    created_at: str  # ISO timestamp
    engagement_count: int = 0  # likes/comments/shares


class RankFeedRequest(BaseModel):
    viewer_id: str
    viewer_skills: dict[str, float] = Field(default_factory=dict)
    followed_user_ids: list[str] = Field(default_factory=list)
    candidate_pool: list[FeedActivityInput] = Field(min_length=1, max_length=200)
    top_k: int = Field(default=20, ge=1, le=100)


class RankedFeedItem(BaseModel):
    activity_id: str
    user_id: str
    activity_type: str
    score: float
    reason: str


class RankFeedPrediction(BaseModel):
    ranked_items: list[RankedFeedItem]
    total_scored: int
    diversity_applied: bool


class DetectTrendingRequest(BaseModel):
    window_days: int = Field(default=7, ge=1, le=365)
    category: Literal["skills", "topics", "languages"] = "skills"
    recent_activities: list[FeedActivityInput] = Field(min_length=1, max_length=500)
    top_k: int = Field(default=10, ge=1, le=50)


class TrendingItem(BaseModel):
    item: str
    score: float
    velocity: float
    category: str


class TrendingPrediction(BaseModel):
    trending_items: list[TrendingItem]
    window_days: int


class SuggestConnectionsRequest(BaseModel):
    user_id: str
    viewer_skills: dict[str, float] = Field(default_factory=dict)
    candidate_users: list[dict] = Field(min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=50)


class SuggestedConnection(BaseModel):
    user_id: str
    username: str
    match_score: float
    reason: str
    shared_skills: list[str] = Field(default_factory=list)


class SuggestConnectionsPrediction(BaseModel):
    suggestions: list[SuggestedConnection]
