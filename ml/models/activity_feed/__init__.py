"""
Activity Feed model logic (master prompt §8, §46).

Deterministic ranking algorithms for a developer social feed:
  - rank_feed: personalized relevance ranking with recency, social graph,
    skill relevance, and engagement signals
  - detect_trending: simple velocity-based trending detection
  - suggest_connections: skill-overlap based "who to follow" suggestions

All feature extraction is exposed so the linear ranking weights can be
*trained* (calibrated) against labeled seed data by
pipelines/training/calibrate.py.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class FeedScore:
    activity_id: str
    user_id: str
    activity_type: str
    score: float
    reason: str


_WEIGHTS = {
    "recency": 0.25,
    "social": 0.30,
    "skill_relevance": 0.25,
    "engagement": 0.20,
}

DEFAULT_FEED_WEIGHTS: dict[str, float] = dict(_WEIGHTS)


def _parse_ts(value: str, now) -> datetime:
    try:
        ts = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return now
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def _recency_score(ts: datetime, now) -> float:
    age_days = max(0.0, (now - ts).total_seconds() / 86400)
    return 1.0 / (1.0 + age_days)


def feed_features(
    activity: dict[str, Any],
    viewer_skills: dict[str, float],
    followed_user_ids: set[str],
    now=None,
) -> dict[str, float]:
    """Per-activity normalized relevance features (each 0..1)."""
    now = now or datetime.now(timezone.utc)
    ts = _parse_ts(activity.get("created_at", now.isoformat()), now)
    recency = _recency_score(ts, now)

    social = 1.0 if activity.get("user_id", "") in followed_user_ids else 0.2

    act_skills = {s.lower() for s in activity.get("skills_mentioned", [])}
    if activity.get("language"):
        act_skills.add(activity["language"].lower())
    viewer_lower = {s.lower() for s in viewer_skills}
    overlap = len(act_skills & viewer_lower)
    skill_relevance = min(overlap / max(len(viewer_lower), 1), 1.0)

    engagement = min(activity.get("engagement_count", 0) / 10.0, 1.0)

    return {
        "recency": recency,
        "social": social,
        "skill_relevance": skill_relevance,
        "engagement": engagement,
    }


def rank_feed(
    viewer_skills: dict[str, float],
    followed_user_ids: list[str],
    candidate_pool: list[dict[str, Any]],
    top_k: int,
    now=None,
    weights: dict[str, float] | None = None,
) -> tuple[list[FeedScore], bool]:
    from shared.calibration import get_calibrated_weights

    weights = weights or get_calibrated_weights("activity_feed", DEFAULT_FEED_WEIGHTS)
    now = now or datetime.now(timezone.utc)
    followed = set(followed_user_ids)

    scored: list[FeedScore] = []
    diversity_applied = False

    for act in candidate_pool:
        act_type = act["activity_type"]
        feats = feed_features(act, viewer_skills, followed, now)
        raw = (
            weights.get("recency", 0.25) * feats["recency"]
            + weights.get("social", 0.30) * feats["social"]
            + weights.get("skill_relevance", 0.25) * feats["skill_relevance"]
            + weights.get("engagement", 0.20) * feats["engagement"]
        )
        reason = "recent activity"
        if act["user_id"] in followed:
            reason = "from someone you follow"
        overlap = len({s.lower() for s in act.get("skills_mentioned", [])} & {s.lower() for s in viewer_skills})
        if overlap > 0:
            reason = f"{reason} matching your skills" if reason != "recent activity" else "matches your skills"
        if act.get("engagement_count", 0) >= 5:
            reason = f"{reason} with high engagement"

        scored.append(
            FeedScore(
                activity_id=act["activity_id"],
                user_id=act["user_id"],
                activity_type=act_type,
                score=round(raw, 4),
                reason=reason.strip(),
            )
        )

    # Diversity: cap each activity_type at a share to avoid feed monotony.
    scored.sort(key=lambda s: s.score, reverse=True)
    if len(scored) > top_k:
        diversity_applied = True
        final: list[FeedScore] = []
        per_type_cap = max(top_k // 3, 1)
        per_type_seen: dict[str, int] = defaultdict(int)
        overflow: list[FeedScore] = []
        for item in scored:
            if len(final) >= top_k:
                break
            if per_type_seen[item.activity_type] < per_type_cap:
                final.append(item)
                per_type_seen[item.activity_type] += 1
            else:
                overflow.append(item)
        for item in overflow:
            if len(final) >= top_k:
                break
            final.append(item)
        final.sort(key=lambda s: s.score, reverse=True)
        return final, diversity_applied

    return scored[:top_k], diversity_applied


def detect_trending(
    recent_activities: list[dict[str, Any]],
    category: str,
    window_days: int,
    top_k: int,
    now=None,
) -> list[dict[str, Any]]:
    now = now or datetime.now(timezone.utc)

    counts_by_day: dict[str, Counter] = defaultdict(Counter)
    total_counts: Counter = Counter()

    for act in recent_activities:
        ts = _parse_ts(act.get("created_at", now.isoformat()), now)
        age_days = (now - ts).total_seconds() / 86400
        if age_days > window_days:
            continue
        day_key = ts.strftime("%Y-%m-%d")
        items = _extract_category_items(act, category)
        for item in items:
            counts_by_day[day_key][item] += 1
            total_counts[item] += 1

    results = []
    for item, total in total_counts.items():
        daily = [counts_by_day[d][item] for d in sorted(counts_by_day)]
        recent_half = sum(daily[len(daily) // 2:])
        early_half = sum(daily[: len(daily) // 2])
        velocity = (recent_half - early_half) / max(early_half, 1)
        score = total + velocity * 2.0
        results.append({"item": item, "score": round(score, 4), "velocity": round(velocity, 4)})

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]


def _extract_category_items(act: dict[str, Any], category: str) -> list[str]:
    if category == "skills":
        items = list(act.get("skills_mentioned", []))
    elif category == "languages":
        items = [act["language"]] if act.get("language") else []
    else:  # topics — derive from title/description keywords
        text = f"{act.get('title', '')} {act.get('description', '')}".lower()
        items = []
        keywords = ["array", "string", "graph", "tree", "dynamic programming",
                    "sorting", "recursion", "system design", "database"]
        for kw in keywords:
            if kw in text:
                items.append(kw)
    return [i.lower() for i in items if i]


def suggest_connections(
    viewer_skills: dict[str, float],
    candidate_users: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    viewer_lower = {s.lower(): s for s in viewer_skills}
    viewer_set = set(viewer_lower)

    suggestions = []
    for user in candidate_users:
        user_id = user.get("user_id") or user.get("id", "")
        username = user.get("username", user_id)
        user_skill_display = {s.lower(): s for s in user.get("skills", [])}
        user_set = set(user_skill_display)

        shared_lower = viewer_set & user_set
        if not user_set:
            # no overlap possible; low score
            match = 0.1
        else:
            match = len(shared_lower) / len(user_set | viewer_set)

        reason = "similar skill interests"
        shared_display = [user_skill_display[s] for s in shared_lower]
        if shared_display:
            reason = f"both work with {', '.join(shared_display[:3])}"

        suggestions.append(
            {
                "user_id": user_id,
                "username": username,
                "match_score": round(match, 4),
                "reason": reason,
                "shared_skills": shared_display,
            }
        )

    suggestions.sort(key=lambda s: s["match_score"], reverse=True)
    return suggestions[:limit]
