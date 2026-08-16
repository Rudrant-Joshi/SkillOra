"""
Integrity Rule Engine (master prompt §14, §15).

Deterministic rule-based signal evaluation. Each proctoring signal type
has a penalty weight and a per-occurrence penalty. The rule engine
aggregates penalties and produces:
  - integrity_score = 100 - weighted penalties (clamped 0..100)
  - flags list with counts
  - band classification

This is intentionally rule-based rather than ML-only because the
architecture requires a hybrid RULE ENGINE + ML MODEL approach (§14).
The rule engine handles obvious violations; the risk model (in risk_model.py)
adds anomaly detection on top.
"""
from __future__ import annotations

from services.integrity.schemas import IntegrityFlag


_SIGNAL_PENALTIES: dict[str, dict] = {
    "tab_switch": {"base_penalty": 5, "per_occurrence": 3, "max_count": 20, "cap": 40},
    "window_blur": {"base_penalty": 2, "per_occurrence": 1, "max_count": 30, "cap": 20},
    "fullscreen_exit": {"base_penalty": 8, "per_occurrence": 5, "max_count": 10, "cap": 50},
    "paste_event": {"base_penalty": 10, "per_occurrence": 2, "max_count": 50, "cap": 60},
    "copy_event": {"base_penalty": 5, "per_occurrence": 2, "max_count": 30, "cap": 40},
    "typing_cadence_anomaly": {"base_penalty": 5, "per_occurrence": 3, "max_count": 20, "cap": 35},
    "time_per_question_anomaly": {"base_penalty": 5, "per_occurrence": 3, "max_count": 20, "cap": 35},
    "ip_change": {"base_penalty": 10, "per_occurrence": 5, "max_count": 10, "cap": 50},
}

_BANDS = [
    (90, 100, "clean"),
    (70, 89, "minor_flags"),
    (40, 69, "suspicious"),
    (0, 39, "high_risk"),
]


def _band_from_score(score: int) -> str:
    for low, high, band in _BANDS:
        if low <= score <= high:
            return band
    return "high_risk"


def evaluate_signals(signals: list[dict]) -> tuple[int, list[IntegrityFlag], str]:
    if not signals:
        return 100, [], "clean"

    aggregated: dict[str, int] = {}
    for s in signals:
        sig_type = s.get("type", "unknown")
        aggregated[sig_type] = aggregated.get(sig_type, 0) + 1

    total_penalty = 0
    flags: list[IntegrityFlag] = []

    for sig_type, count in aggregated.items():
        cfg = _SIGNAL_PENALTIES.get(sig_type, {"base_penalty": 3, "per_occurrence": 2, "max_count": 20, "cap": 30})
        effective_count = min(count, cfg["max_count"])
        penalty = cfg["base_penalty"] + effective_count * cfg["per_occurrence"]
        penalty = min(penalty, cfg["cap"])
        total_penalty += penalty
        flags.append(IntegrityFlag(type=sig_type, count=count, detail=f"penalty={penalty}"))

    score = max(0, min(100, 100 - total_penalty))
    band = _band_from_score(score)
    return score, flags, band
