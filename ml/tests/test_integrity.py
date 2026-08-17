from __future__ import annotations

import pytest

from services.integrity.rule_engine import evaluate_signals
from services.integrity.risk_model import detect_anomalies
from services.integrity.service import analyze_integrity
from services.integrity.schemas import AnalyzeIntegrityRequest


def test_clean_session_no_signals():
    score, flags, band = evaluate_signals([])
    assert score == 100
    assert band == "clean"
    assert flags == []


def test_tab_switches_penalized():
    signals = [{"type": "tab_switch", "timestamp": 1.0}, {"type": "tab_switch", "timestamp": 2.0}]
    score, flags, band = evaluate_signals(signals)
    assert score < 100
    assert band in ("minor_flags", "suspicious", "high_risk")
    assert any(f.type == "tab_switch" and f.count == 2 for f in flags)


def test_fullscreen_exit_high_penalty():
    signals = [{"type": "fullscreen_exit", "timestamp": 1.0}]
    score, flags, band = evaluate_signals(signals)
    assert score < 100
    assert any(f.type == "fullscreen_exit" for f in flags)


def test_paste_event_high_penalty():
    signals = [{"type": "paste_event", "timestamp": 1.0, "chars": 240}]
    score, flags, band = evaluate_signals(signals)
    assert score < 100
    assert any(f.type == "paste_event" for f in flags)


def test_combined_signals_score_monotonic():
    signals1 = [{"type": "tab_switch", "timestamp": 1.0}]
    signals2 = signals1 + [{"type": "paste_event", "timestamp": 2.0}]
    s1, _, _ = evaluate_signals(signals1)
    s2, _, _ = evaluate_signals(signals2)
    assert s2 <= s1


def test_anomaly_detection_time_gap():
    signals = [
        {"type": "keystroke", "timestamp": i} for i in range(20)
    ] + [
        {"type": "keystroke", "timestamp": 5000},
    ]
    flags = detect_anomalies(signals)
    assert any(f.type == "time_per_question_anomaly" for f in flags)


def test_service_returns_prediction():
    req = AnalyzeIntegrityRequest(
        candidate_id="c1",
        assessment_id="a1",
        signals=[{"type": "tab_switch", "timestamp": 1.0}],
    )
    resp = analyze_integrity(req)
    assert resp.prediction.integrity_score >= 0
    assert resp.prediction.integrity_score <= 100
    assert resp.prediction.band in ("clean", "minor_flags", "suspicious", "high_risk")
    assert resp.confidence >= 0.0
    assert "never auto-reject" in resp.metadata.get("note", "").lower() or "decision-support" in resp.metadata.get("note", "").lower()
