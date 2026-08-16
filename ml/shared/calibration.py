"""
Calibration loader — reads tuned model weights from configs/calibration.json.

The ML services ship with sensible default weights (see each model module).
The training pipeline (`pipelines/training/calibrate.py`) fits better weights
against labeled seed data and writes them here. At runtime, services call
`load_calibration()` and fall back to defaults when no calibration file exists,
so the system works out-of-the-box and improves after training.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"
CALIBRATION_PATH = CONFIG_DIR / "calibration.json"


@lru_cache(maxsize=1)
def load_calibration() -> dict:
    if CALIBRATION_PATH.exists():
        try:
            with open(CALIBRATION_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def get_calibrated_weights(key: str, defaults: dict) -> dict:
    cal = load_calibration()
    return cal.get(key, defaults)


def save_calibration(calibration: dict, path: Path | None = None) -> Path:
    path = path or CALIBRATION_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(calibration, f, indent=2)
    # invalidate cache so a later load picks up the new file
    load_calibration.cache_clear()
    return path
