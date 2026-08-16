"""
Profile Intelligence model logic (master prompt §8).

Deterministic core: skill inference from activity signals, profile completeness
scoring, and strength classification. LLM is used only for generating the
natural-language profile summary when available.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from models.skill_estimation.estimator import SkillEvidence, estimate_skill

# Primary language skill only (avoids over-inflation — a Python snippet does
# not prove Django/FastAPI mastery; those come from explicit tags/keywords).
LANGUAGE_TO_SKILLS: dict[str, list[str]] = {
    "python": ["Python"],
    "javascript": ["JavaScript"],
    "typescript": ["TypeScript"],
    "java": ["Java"],
    "cpp": ["C++"],
    "c": ["C"],
    "csharp": ["C#"],
    "go": ["Go"],
    "rust": ["Rust"],
    "ruby": ["Ruby"],
    "php": ["PHP"],
    "swift": ["Swift"],
    "kotlin": ["Kotlin"],
    "sql": ["SQL"],
    "r": ["R"],
    "html": ["HTML"],
    "css": ["CSS"],
    "bash": ["Shell Scripting"],
    "shell": ["Shell Scripting"],
}

# Detected from titles/descriptions when a framework keyword appears.
FRAMEWORK_KEYWORDS: dict[str, str] = {
    "flask": "Flask", "django": "Django", "fastapi": "FastAPI",
    "pytorch": "PyTorch", "tensorflow": "TensorFlow",
    "react": "React", "angular": "Angular", "vue": "Vue", "svelte": "Svelte",
    "node": "Node.js", "express": "Express", "spring": "Spring",
    "rails": "Rails", "laravel": "Laravel", ".net": ".NET", "dotnet": ".NET",
    "unity": "Unity", "kubernetes": "Kubernetes", "docker": "Docker",
}

PROBLEM_TOPIC_TO_SKILLS: dict[str, list[str]] = {
    "array": ["Algorithms", "Data Structures"],
    "string": ["Algorithms", "Data Structures"],
    "dynamic programming": ["Algorithms", "Dynamic Programming"],
    "graph": ["Algorithms", "Graph Theory"],
    "tree": ["Data Structures", "Algorithms"],
    "linked list": ["Data Structures", "Algorithms"],
    "stack": ["Data Structures", "Algorithms"],
    "queue": ["Data Structures", "Algorithms"],
    "hash": ["Data Structures", "Algorithms"],
    "sorting": ["Algorithms", "Sorting"],
    "searching": ["Algorithms", "Search Algorithms"],
    "recursion": ["Algorithms", "Recursion"],
    "math": ["Mathematics", "Algorithms"],
    "database": ["SQL", "Databases"],
    "system design": ["System Design", "Architecture"],
}


@dataclass
class SkillInferenceResult:
    skill: str
    inferred_level: float
    confidence: float
    evidence: list[str]


@dataclass
class ProfileStrengthResult:
    band: str
    score: float


def infer_skills_from_activities(
    activities: list[dict[str, Any]],
    current_skills: dict[str, float] | None = None,
    now=None,
) -> list[SkillInferenceResult]:
    now = now or datetime.now(timezone.utc)
    canonical: dict[str, str] = {}  # lower -> display name
    skill_signals: dict[str, list[SkillEvidence]] = defaultdict(list)

    def add_skill(skill_display: str, source: str, obs: float, ts, detail: str):
        key = skill_display.lower()
        canonical.setdefault(key, skill_display)
        skill_signals[key].append(
            SkillEvidence(source=source, observed_value=obs, timestamp=ts, detail=detail)
        )

    for act in activities:
        act_type = act.get("activity_type", "")
        language = (act.get("language") or "").lower()
        title = (act.get("title") or "").lower()
        description = (act.get("description") or "").lower()
        text = f"{title} {description}"
        skills_mentioned = act.get("skills_mentioned", [])
        ts = now
        try:
            ts = datetime.fromisoformat(act.get("created_at", now.isoformat()))
        except (ValueError, TypeError):
            pass

        if act_type == "snippet":
            obs, source = 0.7, "snippet_activity"
        elif act_type == "submission":
            obs, source = 0.85, "coding_submission_tests_passed"
        elif act_type == "follow":
            obs, source = 0.1, "learning_activity"
        else:
            obs, source = 0.3, "project_activity"

        if language in LANGUAGE_TO_SKILLS:
            for sk in LANGUAGE_TO_SKILLS[language]:
                add_skill(sk, source, obs, ts, f"inferred from {act_type} in {language}")

        for kw, sk in FRAMEWORK_KEYWORDS.items():
            if kw in text:
                add_skill(sk, source, min(obs + 0.05, 1.0), ts, f"framework '{kw}' in {act_type}")

        for sk in skills_mentioned:
            add_skill(sk, source, min(obs + 0.05, 1.0), ts, f"tagged in {act_type}")

        for topic, skills in PROBLEM_TOPIC_TO_SKILLS.items():
            if topic in text:
                for sk in skills:
                    add_skill(sk, source, obs, ts, f"topic '{topic}' in {act_type}")

    results = []
    for key, evidence_list in skill_signals.items():
        estimate = estimate_skill(key, evidence_list)
        results.append(
            SkillInferenceResult(
                skill=canonical[key],
                inferred_level=estimate.estimated_level,
                confidence=estimate.confidence,
                evidence=estimate.evidence,
            )
        )

    results.sort(key=lambda r: r.inferred_level, reverse=True)
    return results


def score_profile_completeness(
    user_id: str,
    username: str,
    bio: str | None,
    activities: list[dict[str, Any]],
    skills: dict[str, float] | None = None,
) -> ProfileStrengthResult:
    score = 0.0
    missing = []
    suggestions = []

    if username and len(username.strip()) >= 2:
        score += 10
    else:
        missing.append("username")

    if bio and len(bio.strip()) >= 10:
        score += 20
    else:
        missing.append("bio")
        suggestions.append("Add a bio so others know what you're working on.")

    activity_count = len(activities)
    if activity_count >= 10:
        score += 30
    elif activity_count >= 5:
        score += 20
    elif activity_count >= 1:
        score += 10
    else:
        missing.append("activity_history")
        suggestions.append("Push a snippet or solve a problem to build your profile.")

    has_snippet = any(a.get("activity_type") == "snippet" for a in activities)
    has_submission = any(a.get("activity_type") == "submission" for a in activities)
    has_follows = any(a.get("activity_type") == "follow" for a in activities)

    if has_snippet:
        score += 15
    else:
        missing.append("code_snippets")
        suggestions.append("Push your first code snippet to start building your portfolio.")

    if has_submission:
        score += 15
    else:
        missing.append("problem_submissions")
        suggestions.append("Solve problems to get verified skill badges on your profile.")

    if has_follows:
        score += 5
    else:
        suggestions.append("Follow other developers to build your network.")

    skill_count = len(skills or {})
    if skill_count >= 5:
        score += 5
    elif skill_count >= 1:
        score += 3
    else:
        suggestions.append("Your skills will be auto-detected from your activity.")

    score = min(100.0, max(0.0, score))

    if score >= 80:
        band = "complete"
    elif score >= 60:
        band = "partial"
    elif score >= 30:
        band = "incomplete"
    elif score >= 10:
        band = "emerging"
    else:
        band = "empty"

    return ProfileStrengthResult(band=band, score=score)


def classify_profile_strength(completeness_score: float) -> str:
    if completeness_score >= 80:
        return "established"
    elif completeness_score >= 55:
        return "active"
    elif completeness_score >= 25:
        return "emerging"
    else:
        return "empty"


def build_profile_summary(
    username: str,
    top_skills: list[str],
    activity_count: int,
    profile_strength: str,
    bio: str | None = None,
) -> str:
    parts = []
    if bio:
        parts.append(bio.strip())
    else:
        parts.append(f"@{username} is a developer building in public on DevConnect.")

    if top_skills:
        parts.append(f"Primary skills: {', '.join(top_skills[:5])}.")

    if activity_count == 0:
        parts.append("No activity yet — just getting started.")
    elif activity_count < 5:
        parts.append(f"{activity_count} public activity items so far.")
    else:
        parts.append(f"{activity_count} public activities, actively contributing.")

    strength_map = {
        "empty": "Profile is just getting started.",
        "emerging": "Building momentum.",
        "active": "Consistently active on the platform.",
        "established": "Strong, verified portfolio.",
    }
    parts.append(strength_map.get(profile_strength, ""))

    return " ".join(parts)


def suggest_headline(
    username: str,
    top_skills: list[str],
    activity_count: int,
) -> str:
    if not top_skills:
        return f"@{username} — Developer"
    primary = top_skills[0]
    secondary = top_skills[1] if len(top_skills) > 1 else ""
    if secondary:
        return f"@{username} — {primary} & {secondary} Developer"
    return f"@{username} — {primary} Developer"
