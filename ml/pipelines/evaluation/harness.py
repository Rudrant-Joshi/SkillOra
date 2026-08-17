"""
Offline evaluation harness (master prompt §36 monitoring / §46 model quality).

Pure-Python regression metrics (MAE, RMSE, R^2) for the calibrated models, plus
a report writer that dumps evaluation JSON into ml/evaluation/ so model-quality
regression is auditable across training runs.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

REPORT_DIR = Path(__file__).resolve().parents[2] / "evaluation"


@dataclass
class RegressionReport:
    label: str
    n: int
    mae: float
    rmse: float
    r2: float
    mean_target: float


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def evaluate_regression(
    y_true: Sequence[float],
    y_pred: Sequence[float],
    label: str = "model",
) -> RegressionReport:
    yt = list(map(float, y_true))
    yp = list(map(float, y_pred))
    n = len(yt)
    if n == 0:
        return RegressionReport(label=label, n=0, mae=0.0, rmse=0.0, r2=0.0, mean_target=0.0)

    mae = _mean([abs(a - b) for a, b in zip(yt, yp)])
    mse = _mean([(a - b) ** 2 for a, b in zip(yt, yp)])
    rmse = mse ** 0.5

    ybar = _mean(yt)
    ss_res = sum((a - b) ** 2 for a, b in zip(yt, yp))
    ss_tot = sum((a - ybar) ** 2 for a in yt)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    return RegressionReport(
        label=label, n=n, mae=round(mae, 4), rmse=round(rmse, 4),
        r2=round(r2, 4), mean_target=round(ybar, 4),
    )


def print_report(report: RegressionReport) -> None:
    print(
        f"  [{report.label}] n={report.n}  MAE={report.mae:.4f}  "
        f"RMSE={report.rmse:.4f}  R2={report.r2:.4f}"
    )


def write_reports(reports: dict[str, RegressionReport], path: Path | None = None) -> Path:
    path = path or (REPORT_DIR / "calibration_report.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {name: asdict(r) for name, r in reports.items()}
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return path
