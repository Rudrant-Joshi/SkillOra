"""
Seed / demo data generator — produces a small, deterministic social graph of
fake developers with realistic activity (snippets, problem submissions, follows).

Used by `scripts/seed_demo.py` for the hackathon demo and by
`tests/test_integration.py` to prove the full ML connective-tissue pipeline
(activity -> inferred skills -> profile -> feed -> difficulty -> learning path ->
reputation) works end-to-end. Deterministic (seeded) so demos and tests are
reproducible.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

NOW = datetime(2026, 8, 16, tzinfo=timezone.utc)

# Small catalogue of real-ish problems for submissions.
PROBLEMS = [
    {"title": "Two Sum", "language": "python", "topics": ["array", "hash"], "difficulty": 0.25},
    {"title": "Valid Parentheses", "language": "python", "topics": ["stack", "string"], "difficulty": 0.35},
    {"title": "Binary Search", "language": "python", "topics": ["searching", "array"], "difficulty": 0.4},
    {"title": "Climbing Stairs", "language": "python", "topics": ["dynamic programming"], "difficulty": 0.5},
    {"title": "Longest Increasing Subsequence", "language": "python", "topics": ["dynamic programming", "array"], "difficulty": 0.62},
    {"title": "Dijkstra Shortest Path", "language": "python", "topics": ["graph"], "difficulty": 0.7},
    {"title": "Edit Distance", "language": "cpp", "topics": ["dynamic programming", "string"], "difficulty": 0.74},
    {"title": "Word Ladder", "language": "python", "topics": ["graph", "string"], "difficulty": 0.72},
]

SNIPPETS = [
    {"title": "Flask REST API", "language": "python", "skills_mentioned": ["Flask", "Python"], "quality": 82},
    {"title": "React Notes App", "language": "javascript", "skills_mentioned": ["React", "JavaScript"], "quality": 78},
    {"title": "Django Auth Middleware", "language": "python", "skills_mentioned": ["Django", "Python"], "quality": 85},
    {"title": "Rust CLI Tool", "language": "rust", "skills_mentioned": ["Rust"], "quality": 80},
    {"title": "Go Worker Pool", "language": "go", "skills_mentioned": ["Go"], "quality": 76},
    {"title": "SQL Migration Script", "language": "sql", "skills_mentioned": ["SQL"], "quality": 70},
]


def _days_ago(days: int) -> str:
    return (NOW - timedelta(days=days)).isoformat()


def generate_seed_profiles(seed: int = 42) -> list[dict]:
    """Return a deterministic list of user profiles with activity and edges."""
    rng = random.Random(seed)

    # Archetypes: (username, bio, languages, follower_count, account_age_days, verified)
    archetypes = [
        ("alice", "Backend engineer who loves Python and clean APIs.", ["python"], 120, 420, ["Python", "SQL"]),
        ("bob", "ML student learning one algorithm at a time.", ["python"], 35, 150, ["Python"]),
        ("carol", "Frontend dev building with React.", ["javascript"], 60, 300, ["React", "JavaScript"]),
        ("dave", "Systems programmer exploring Rust and Go.", ["rust", "go"], 80, 500, ["Rust", "Go"]),
        ("erin", "Full-stack developer, Django + React.", ["python", "javascript"], 95, 380, ["Python", "React"]),
        ("frank", "Data enthusiast, SQL and Python.", ["python", "sql"], 50, 220, ["SQL", "Python"]),
    ]

    users = []
    for uid, (username, bio, langs, followers, age, verified) in enumerate(archetypes, start=1):
        activities = []
        snippets = rng.sample(SNIPPETS, k=rng.randint(2, 4))
        for i, s in enumerate(snippets):
            activities.append({
                "activity_type": "snippet",
                "title": s["title"],
                "description": f"{s['title']} implementation in {s['language']}.",
                "language": s["language"],
                "skills_mentioned": s["skills_mentioned"],
                "created_at": _days_ago(rng.randint(1, age)),
                "engagement_count": rng.randint(0, 20),
                "quality_score": s["quality"],
            })
        n_sub = rng.randint(3, 8)
        subs = rng.sample(PROBLEMS, k=n_sub)
        for i, p in enumerate(subs):
            activities.append({
                "activity_type": "submission",
                "title": p["title"],
                "description": f"Solved {p['title']} in {p['language']}.",
                "language": p["language"],
                "skills_mentioned": p["topics"],
                "created_at": _days_ago(rng.randint(1, age)),
                "engagement_count": rng.randint(0, 15),
                "quality_score": 90 - int((p["difficulty"] * 20)),
            })

        users.append({
            "user_id": f"u{uid}",
            "username": username,
            "bio": bio,
            "languages": langs,
            "followers_count": followers,
            "account_age_days": age,
            "verified_skills": verified,
            "activities": activities,
            "snippets_pushed": len(snippets),
            "problems_solved": n_sub,
            "problems_attempted": n_sub + rng.randint(0, 3),
            "avg_code_quality": round(sum(a.get("quality_score", 70) for a in activities) / max(len(activities), 1), 1),
        })

    # Build follow edges (directed). Everyone follows alice/erin loosely; others random.
    follows = {
        "u1": ["u2", "u3", "u4", "u5", "u6"],
        "u2": ["u1", "u5", "u6"],
        "u3": ["u1", "u5"],
        "u4": ["u1", "u5"],
        "u5": ["u1", "u2", "u3", "u4", "u6"],
        "u6": ["u1", "u5"],
    }
    for u in users:
        u["following"] = follows.get(u["user_id"], [])
        # record follow activities into the timeline for feed realism
        for fid in u["following"]:
            target = next((x for x in users if x["user_id"] == fid), None)
            if target:
                u["activities"].append({
                    "activity_type": "follow",
                    "title": f"Started following @{target['username']}",
                    "description": None,
                    "language": None,
                    "skills_mentioned": [],
                    "created_at": _days_ago(rng.randint(1, u["account_age_days"])),
                    "engagement_count": 0,
                    "quality_score": 0,
                })
    return users


def build_feed_pool(users: list[dict], viewer_id: str) -> list[dict]:
    """Flatten non-follow activities of the whole graph into feed items."""
    pool = []
    for u in users:
        if u["user_id"] == viewer_id:
            continue
        for a in u["activities"]:
            if a["activity_type"] == "follow":
                continue
            pool.append({
                "activity_id": f"{u['user_id']}-{a['title']}",
                "activity_type": a["activity_type"],
                "user_id": u["user_id"],
                "username": u["username"],
                "title": a["title"],
                "description": a.get("description"),
                "language": a.get("language"),
                "skills_mentioned": a.get("skills_mentioned", []),
                "created_at": a["created_at"],
                "engagement_count": a.get("engagement_count", 0),
            })
    return pool


if __name__ == "__main__":
    profiles = generate_seed_profiles()
    print(f"Generated {len(profiles)} seed profiles.")
    for p in profiles:
        print(f"  @{p['username']}: {p['snippets_pushed']} snippets, "
              f"{p['problems_solved']} solved, follows {len(p['following'])}")
