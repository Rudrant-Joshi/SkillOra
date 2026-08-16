"""
Accuracy evaluator — the "label it + measure it" step.

Runs each calibrated model over its labeled seed dataset and reports:
  - regression quality: MAE / RMSE / R²
  - classification accuracy where a natural label exists:
      * difficulty  -> easy / medium / hard bucket accuracy + confusion
      * reputation  -> band accuracy (newcomer/contributor/trusted/elite)
      * feed        -> relevance accuracy (relevant if label >= 0.5)
It also writes a labeled-vs-predicted comparison to evaluation/predictions.jsonl
so every prediction is traceable to its ground-truth label.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.activity_feed import DEFAULT_FEED_WEIGHTS, feed_features
from models.problem_difficulty import difficulty_features, estimate_difficulty_heuristic
from models.reputation import compute_reputation, reputation_features
from pipelines.evaluation.harness import evaluate_regression
from shared.calibration import load_calibration

DATASET_DIR = Path(__file__).resolve().parents[1] / "datasets"
REPORT_DIR = Path(__file__).resolve().parents[1] / "evaluation"


def _load(name: str):
    with open(DATASET_DIR / name) as f:
        return json.load(f)


def _diff_band(x: float) -> str:
    if x < 0.33:
        return "easy"
    if x < 0.66:
        return "medium"
    return "hard"


def _rep_band(x: float) -> str:
    if x < 30:
        return "newcomer"
    if x < 60:
        return "contributor"
    if x < 85:
        return "trusted"
    return "elite"


def _accuracy(true_labels: list[str], pred_labels: list[str]) -> float:
    if not true_labels:
        return 0.0
    return sum(t == p for t, p in zip(true_labels, pred_labels)) / len(true_labels)


def evaluate_difficulty() -> dict:
    data = _load("seed_difficulty.json")
    true, pred, true_b, pred_b = [], [], [], []
    rows = []
    for r in data:
        est = estimate_difficulty_heuristic(
            r["title"], r["description"], r.get("starter_code"),
            r.get("test_cases_count"), r.get("constraints_count"), r.get("topics"),
        ).difficulty
        true.append(float(r["label"]))
        pred.append(est)
        true_b.append(_diff_band(float(r["label"])))
        pred_b.append(_diff_band(est))
        rows.append({"title": r["title"], "label": r["label"], "pred": round(est, 4),
                     "label_band": _diff_band(float(r["label"])), "pred_band": _diff_band(est)})
    reg = evaluate_regression(true, pred, label="problem_difficulty")
    acc = _accuracy(true_b, pred_b)
    conf = Counter((t, p) for t, p in zip(true_b, pred_b))
    return {"regression": reg, "accuracy": acc, "confusion": {f"{t}->{p}": c for (t, p), c in conf.items()}, "rows": rows}


def evaluate_reputation() -> dict:
    data = _load("seed_reputation.json")
    true, pred, true_b, pred_b = [], [], [], []
    rows = []
    for r in data:
        score = compute_reputation(r["activity"], r.get("verified_skills", [])).score
        true.append(float(r["label"]))
        pred.append(score)
        true_b.append(_rep_band(float(r["label"])))
        pred_b.append(_rep_band(score))
        rows.append({"verified": r.get("verified_skills", []), "label": r["label"],
                     "pred": round(score, 2), "label_band": _rep_band(float(r["label"])),
                     "pred_band": _rep_band(score)})
    reg = evaluate_regression(true, pred, label="reputation")
    acc = _accuracy(true_b, pred_b)
    conf = Counter((t, p) for t, p in zip(true_b, pred_b))
    return {"regression": reg, "accuracy": acc, "confusion": {f"{t}->{p}": c for (t, p), c in conf.items()}, "rows": rows}


def evaluate_feed() -> dict:
    data = _load("seed_feed.json")
    true, pred, true_b, pred_b = [], [], [], []
    rows = []
    for r in data:
        f = feed_features(r["activity"], r["viewer_skills"], set(), None)
        from models.activity_feed import DEFAULT_FEED_WEIGHTS
        from shared.calibration import get_calibrated_weights
        weights = get_calibrated_weights("activity_feed", DEFAULT_FEED_WEIGHTS)
        raw = sum(weights.get(k, 0.25) * f[k] for k in ("recency", "social", "skill_relevance", "engagement"))
        est = max(0.0, min(1.0, raw))
        true.append(float(r["label"]))
        pred.append(est)
        true_b.append("relevant" if float(r["label"]) >= 0.5 else "skip")
        pred_b.append("relevant" if est >= 0.5 else "skip")
        rows.append({"viewer": list(r["viewer_skills"].keys()), "followed": r["followed"],
                     "label": r["label"], "pred": round(est, 4),
                     "label_bin": true_b[-1], "pred_bin": pred_b[-1]})
    reg = evaluate_regression(true, pred, label="activity_feed")
    acc = _accuracy(true_b, pred_b)
    conf = Counter((t, p) for t, p in zip(true_b, pred_b))
    return {"regression": reg, "accuracy": acc, "confusion": {f"{t}->{p}": c for (t, p), c in conf.items()}, "rows": rows}


def run() -> dict:
    load_calibration.cache_clear()  # ensure we measure the persisted (trained) weights
    results = {
        "problem_difficulty": evaluate_difficulty(),
        "reputation": evaluate_reputation(),
        "activity_feed": evaluate_feed(),
    }

    print("=" * 70)
    print("MODEL ACCURACY REPORT (trained / calibrated weights)")
    print("=" * 70)
    for name, res in results.items():
        reg = res["regression"]
        print(f"\n[{name}]")
        print(f"  regression : n={reg.n} MAE={reg.mae:.4f} RMSE={reg.rmse:.4f} R2={reg.r2:.4f}")
        print(f"  accuracy  : {res['accuracy'] * 100:.1f}%")
        print(f"  confusion : {res['confusion']}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_DIR / "accuracy_report.json", "w") as f:
        json.dump({k: {kk: (vv.__dict__ if hasattr(vv, '__dict__') else vv)
                       for kk, vv in v.items() if kk != "rows"} for k, v in results.items()},
                  f, indent=2, default=str)
    # labeled predictions for traceability
    with open(REPORT_DIR / "predictions.jsonl", "w") as f:
        for name, res in results.items():
            for row in res["rows"]:
                f.write(json.dumps({"model": name, **row}) + "\n")
    print(f"\nReports written to {REPORT_DIR}/accuracy_report.json and predictions.jsonl")

    # headline accuracy summary
    print("\nSUMMARY ACCURACY:")
    for name, res in results.items():
        print(f"  {name:18s}: {res['accuracy'] * 100:.1f}%  (R2={res['regression'].r2:.3f})")
    return results


if __name__ == "__main__":
    run()
