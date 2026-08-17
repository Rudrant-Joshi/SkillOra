from datetime import datetime, timedelta, timezone

from services.activity_feed.schemas import (
    DetectTrendingRequest,
    FeedActivityInput,
    RankFeedRequest,
    SuggestConnectionsRequest,
)
from services.activity_feed.service import (
    detect_trending_service,
    rank_feed_service,
    suggest_connections_service,
)


def _now():
    return datetime.now(timezone.utc)


def _activity(activity_id, user_id, username, activity_type, skills=None, days_ago=0, engagement=0):
    return FeedActivityInput(
        activity_id=activity_id,
        activity_type=activity_type,
        user_id=user_id,
        username=username,
        title=f"{activity_type} by {username}",
        language="python",
        skills_mentioned=skills or [],
        created_at=(_now() - timedelta(days=days_ago)).isoformat(),
        engagement_count=engagement,
    )


def test_rank_feed_prioritizes_followed_and_recent():
    pool = [
        _activity("a1", "friend1", "f1", "snippet", ["Python"], days_ago=0, engagement=10),
        _activity("a2", "stranger", "s2", "snippet", ["Python"], days_ago=0, engagement=10),
        _activity("a3", "stranger", "s3", "snippet", ["Python"], days_ago=30, engagement=0),
    ]
    req = RankFeedRequest(
        viewer_id="me",
        viewer_skills={"Python": 0.8},
        followed_user_ids=["friend1"],
        candidate_pool=pool,
        top_k=3,
    )
    resp = rank_feed_service(req)
    ranked_ids = [r.activity_id for r in resp.prediction.ranked_items]
    assert ranked_ids[0] == "a1"  # followed + recent + relevant + engaged
    assert "a3" not in ranked_ids[:1]


def test_rank_feed_applies_diversity():
    pool = [_activity(f"a{i}", "s", "s", "snippet", ["Python"], engagement=5) for i in range(15)]
    pool += [_activity(f"b{i}", "s", "s", "submission", ["Python"], engagement=5) for i in range(15)]
    req = RankFeedRequest(
        viewer_id="me",
        viewer_skills={"Python": 0.8},
        followed_user_ids=[],
        candidate_pool=pool,
        top_k=10,
    )
    resp = rank_feed_service(req)
    types = [r.activity_type for r in resp.prediction.ranked_items]
    assert resp.prediction.diversity_applied is True
    assert types.count("snippet") < 10  # capped per type


def test_detect_trending_skills():
    now = _now()
    activities = [
        FeedActivityInput(
            activity_id=f"a{i}", activity_type="submission", user_id="u",
            username="u", title="dp problem", language="python",
            skills_mentioned=["Algorithms", "Dynamic Programming"],
            created_at=(now - timedelta(days=1)).isoformat(), engagement=0,
        )
        for i in range(10)
    ]
    req = DetectTrendingRequest(
        window_days=7, category="skills", recent_activities=activities, top_k=5
    )
    resp = detect_trending_service(req)
    items = {t.item for t in resp.prediction.trending_items}
    assert "dynamic programming" in items or "algorithms" in items


def test_suggest_connections_ranks_shared_skills():
    req = SuggestConnectionsRequest(
        user_id="me",
        viewer_skills={"Python": 0.8, "React": 0.6},
        candidate_users=[
            {"user_id": "c1", "username": "c1", "skills": ["Python", "Django"]},
            {"user_id": "c2", "username": "c2", "skills": ["Go"]},
            {"user_id": "c3", "username": "c3", "skills": ["Python", "React", "SQL"]},
        ],
        limit=3,
    )
    resp = suggest_connections_service(req)
    top = resp.prediction.suggestions[0]
    assert top.user_id == "c3"  # shares both Python and React
    assert "Python" in top.shared_skills
