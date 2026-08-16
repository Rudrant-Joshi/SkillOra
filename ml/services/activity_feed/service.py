"""
Activity Feed service — ranks a developer social feed, detects trending
skills/topics, and suggests who to follow. All deterministic (master prompt
§46: classical ML where classical is sufficient).
"""
from __future__ import annotations

import time

from models.activity_feed import (
    detect_trending,
    rank_feed,
    suggest_connections,
)
from services.activity_feed.schemas import (
    DetectTrendingRequest,
    RankFeedRequest,
    RankFeedPrediction,
    RankedFeedItem,
    SuggestConnectionsPrediction,
    SuggestConnectionsRequest,
    TrendingPrediction,
    TrendingItem,
)
from shared.logging.logger import log_inference
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "activity-feed-v1"


def rank_feed_service(req: RankFeedRequest) -> MLResponse[RankFeedPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    scored, diversity_applied = rank_feed(
        req.viewer_skills,
        req.followed_user_ids,
        [a.model_dump() for a in req.candidate_pool],
        req.top_k,
    )

    ranked = [
        RankedFeedItem(
            activity_id=s.activity_id,
            user_id=s.user_id,
            activity_type=s.activity_type,
            score=s.score,
            reason=s.reason,
        )
        for s in scored
    ]

    prediction = RankFeedPrediction(
        ranked_items=ranked,
        total_scored=len(req.candidate_pool),
        diversity_applied=diversity_applied,
    )

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=0.85,
        evidence=[f"ranked {len(ranked)} of {len(req.candidate_pool)} activities"],
        metadata={"viewer_id": req.viewer_id},
    )
    log_inference(
        service="activity_feed",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=0.85,
        success=True,
    )
    return response


def detect_trending_service(req: DetectTrendingRequest) -> MLResponse[TrendingPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    results = detect_trending(
        [a.model_dump() for a in req.recent_activities],
        req.category,
        req.window_days,
        req.top_k,
    )

    trending = [
        TrendingItem(item=r["item"], score=r["score"], velocity=r["velocity"], category=req.category)
        for r in results
    ]

    prediction = TrendingPrediction(trending_items=trending, window_days=req.window_days)
    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=0.7,
        evidence=[f"detected {len(trending)} trending {req.category}"],
        metadata={"window_days": req.window_days},
    )
    log_inference(
        service="activity_feed",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=0.7,
        success=True,
    )
    return response


def suggest_connections_service(req: SuggestConnectionsRequest) -> MLResponse[SuggestConnectionsPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()

    suggestions = suggest_connections(req.viewer_skills, req.candidate_users, req.limit)
    prediction = SuggestConnectionsPrediction(suggestions=suggestions)  # type: ignore[arg-type]
    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=0.8,
        evidence=[f"suggested {len(suggestions)} connections"],
        metadata={"viewer_id": req.user_id},
    )
    log_inference(
        service="activity_feed",
        model_version=SERVICE_VERSION,
        request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000,
        confidence=0.8,
        success=True,
    )
    return response
