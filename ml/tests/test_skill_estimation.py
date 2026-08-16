from datetime import datetime, timedelta, timezone

from models.skill_estimation.estimator import SkillEvidence, estimate_skill


def _now():
    return datetime.now(timezone.utc)


def test_no_evidence_returns_neutral_low_confidence():
    result = estimate_skill("python", [])
    assert result.estimated_level == 0.5
    assert result.confidence < 0.2


def test_strong_recent_evidence_moves_estimate_up():
    evidence = [
        SkillEvidence(
            source="coding_submission_tests_passed", observed_value=0.95, timestamp=_now()
        ),
        SkillEvidence(source="assessment", observed_value=0.9, timestamp=_now()),
    ]
    result = estimate_skill("python", evidence)
    assert result.estimated_level > 0.7
    assert result.confidence > 0.4


def test_self_declared_alone_barely_moves_estimate():
    evidence = [SkillEvidence(source="self_declared", observed_value=1.0, timestamp=_now())]
    result = estimate_skill("python", evidence)
    # low reliability source shouldn't swing a neutral prior all the way to 1.0
    assert result.estimated_level < 0.75


def test_stale_evidence_weighted_less_than_recent():
    stale = SkillEvidence(
        source="assessment", observed_value=0.9,
        timestamp=_now() - timedelta(days=365),
    )
    recent = SkillEvidence(source="assessment", observed_value=0.3, timestamp=_now())

    stale_result = estimate_skill("python", [stale])
    combined_result = estimate_skill("python", [stale, recent])

    # adding a strong recent contradicting signal should pull the estimate
    # down from the stale-only estimate
    assert combined_result.estimated_level < stale_result.estimated_level


def test_evidence_count_and_confidence_grow_with_more_evidence():
    single = estimate_skill(
        "sql", [SkillEvidence(source="assessment", observed_value=0.8, timestamp=_now())]
    )
    many = estimate_skill(
        "sql",
        [SkillEvidence(source="assessment", observed_value=0.8, timestamp=_now()) for _ in range(5)],
    )
    assert many.confidence >= single.confidence
    assert many.evidence_count == 5


def test_estimate_bounded_between_zero_and_one():
    evidence = [
        SkillEvidence(source="assessment", observed_value=1.0, timestamp=_now())
        for _ in range(20)
    ]
    result = estimate_skill("algorithms", evidence)
    assert 0.0 <= result.estimated_level <= 1.0
    assert 0.0 <= result.confidence <= 0.95
