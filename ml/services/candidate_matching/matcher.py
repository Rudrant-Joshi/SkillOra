"""
Candidate-job matching logic (master prompt §13).

Deterministic, explainable scoring over job-relevant evidence only.
No sensitive personal characteristics are used.
"""
from __future__ import annotations

from services.candidate_matching.schemas import (
    CandidateJobMatchRequest,
    CandidateJobMatchPrediction,
    SkillMatchEvidence,
)


_REQUIRED_SKILL_WEIGHT = 0.7
_PREFERRED_SKILL_WEIGHT = 0.3
_ASSESSMENT_BONUS_WEIGHT = 0.15
_EXPERIENCE_BONUS_WEIGHT = 0.1


def _skill_match_score(candidate_skills: dict[str, float], required: list[str], preferred: list[str]) -> tuple[float, list[SkillMatchEvidence], list[SkillMatchEvidence]]:
    matched: list[SkillMatchEvidence] = []
    missing: list[SkillMatchEvidence] = []
    required_hits = 0
    required_total = len(required) or 1
    preferred_hits = 0
    preferred_total = len(preferred) or 1

    for skill in required:
        level = candidate_skills.get(skill)
        if level is not None:
            required_hits += level
            matched.append(SkillMatchEvidence(skill=skill, matched=True, candidate_level=level, required_level=0.5, source="skill_profile"))
        else:
            missing.append(SkillMatchEvidence(skill=skill, matched=False, required_level=0.5, source="skill_profile"))

    for skill in preferred:
        level = candidate_skills.get(skill)
        if level is not None:
            preferred_hits += level
            matched.append(SkillMatchEvidence(skill=skill, matched=True, candidate_level=level, required_level=0.3, source="skill_profile"))
        else:
            missing.append(SkillMatchEvidence(skill=skill, matched=False, required_level=0.3, source="skill_profile"))

    required_score = required_hits / required_total
    preferred_score = preferred_hits / preferred_total if preferred_total else 0.0
    skill_score = _REQUIRED_SKILL_WEIGHT * required_score + _PREFERRED_SKILL_WEIGHT * preferred_score
    return skill_score, matched, missing


def match_candidate_to_job(req: CandidateJobMatchRequest) -> CandidateJobMatchPrediction:
    skill_score, matched, missing = _skill_match_score(
        req.candidate.skills, req.job.required_skills, req.job.preferred_skills
    )

    evidence: list[str] = []
    confidence = 0.6

    assessment_bonus = 0.0
    if req.assessment_results:
        overall = req.assessment_results.get("overall")
        if overall is not None:
            assessment_bonus = _ASSESSMENT_BONUS_WEIGHT * min(max(float(overall) / 100.0, 0.0), 1.0)
            evidence.append(f"assessment_overall={overall}")
        confidence = min(1.0, confidence + 0.15)

    experience_bonus = 0.0
    if req.candidate.experience_years is not None and req.job.min_experience_years is not None:
        if req.candidate.experience_years >= req.job.min_experience_years:
            experience_bonus = _EXPERIENCE_BONUS_WEIGHT
            evidence.append(f"experience_met={req.candidate.experience_years}")
        else:
            evidence.append(f"experience_below_min={req.candidate.experience_years}<{req.job.min_experience_years}")

    match_score = min(1.0, max(0.0, skill_score + assessment_bonus + experience_bonus))

    if req.shared_repository_ids:
        evidence.append(f"shared_repositories={len(req.shared_repository_ids)}")
        confidence = min(1.0, confidence + 0.05)
    if req.shared_project_ids:
        evidence.append(f"shared_projects={len(req.shared_project_ids)}")
        confidence = min(1.0, confidence + 0.05)

    evidence.append(f"required_skills_matched={len([m for m in matched if m.skill in req.job.required_skills])}/{len(req.job.required_skills)}")

    return CandidateJobMatchPrediction(
        match_score=round(match_score, 4),
        matched_skills=matched,
        missing_skills=missing,
        evidence=evidence,
        confidence=round(confidence, 4),
    )
