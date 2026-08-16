"""
Integrity Risk Model (master prompt §14).

Hybrid statistical anomaly detection layered on top of the rule engine.
Uses classical ML (z-score based anomaly detection) to flag unusual
signal patterns that rule thresholds alone might miss.

This is intentionally lightweight and replaceable — a production deployment
can swap this for a trained classifier without changing the service contract.
"""
from __future__ import annotations

import math
from collections import defaultdict
from statistics import mean, stdev

from services.integrity.schemas import ASTSimilarityResult, IntegrityFlag


def _z_score(value: float, values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    s = stdev(values)
    if s == 0:
        return 0.0
    return (value - m) / s


def detect_anomalies(signals: list[dict], ast_similarity: Optional[ASTSimilarityResult] = None) -> list[IntegrityFlag]:
    if not signals:
        return []

    anomalies: list[IntegrityFlag] = []

    # Time-per-question anomaly
    timestamps = sorted(s.get("timestamp", 0) for s in signals if s.get("timestamp"))
    if len(timestamps) >= 2:
        gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_gap = mean(gaps)
        gap_std = stdev(gaps) if len(gaps) >= 2 else 0
        if gap_std > 0 and any(_z_score(g, gaps) > 3.0 for g in gaps):
            anomalies.append(IntegrityFlag(
                type="time_per_question_anomaly",
                count=1,
                detail=f"z-score anomaly detected; avg_gap={avg_gap:.1f}s"
            ))

    # Paste-to-keystroke ratio anomaly
    paste_count = sum(1 for s in signals if s.get("type") == "paste_event")
    key_count = sum(1 for s in signals if s.get("type") == "keystroke")
    if key_count > 0 and paste_count / key_count > 0.5:
        anomalies.append(IntegrityFlag(
            type="paste_to_keystroke_ratio_high",
            count=paste_count,
            detail=f"paste/key ratio={paste_count/key_count:.2f}"
        ))

    # AST similarity spike
    if ast_similarity and ast_similarity.max_similarity_pct > 70:
        anomalies.append(IntegrityFlag(
            type="ast_similarity_spike",
            count=1,
            detail=f"AST similarity {ast_similarity.max_similarity_pct:.1f}% exceeds threshold"
        ))

    return anomalies
