"""
Convenience runner: calibrate (train) the ML models against labeled seed data
and emit an offline evaluation report.

Usage:
    python train.py
Equivalent to:  python -m pipelines.training.calibrate
"""
from __future__ import annotations

from pipelines.training.calibrate import run_calibration


if __name__ == "__main__":
    run_calibration()
