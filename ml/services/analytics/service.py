from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from services.analytics.schemas import AnalyticsQuery, AnalyticsSummary
from shared.logging.logger import get_inference_logs
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "analytics-v1"


def summarize_analytics(query: AnalyticsQuery) -> MLResponse[AnalyticsSummary]:
    request_id = new_request_id()
    start = time.perf_counter()

    logs = get_inference_logs()
    filtered = logs
    if query.service:
        filtered = [l for l in filtered if l.get("service") == query.service]
    if query.model_version:
        filtered = [l for l in filtered if l.get("model_version") == query.model_version]
    if query.since:
        try:
            since_dt = datetime.fromisoformat(query.since)
        except ValueError:
            since_dt = None
        if since_dt is not None:
            filtered = [
                l for l in filtered
                if datetime.fromtimestamp(l.get("ts", 0), tz=timezone.utc) >= since_dt
            ]
    filtered = filtered[-query.limit:]

    total = len(filtered)
    latencies = [l.get("latency_ms", 0) for l in filtered if l.get("latency_ms") is not None]
    confidences = [l.get("confidence") for l in filtered if l.get("confidence") is not None]
    errors = [l for l in filtered if l.get("success") is False]
    service_counts: dict[str, int] = defaultdict(int)
    for l in filtered:
        service_counts[l.get("service", "unknown")] += 1

    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    avg_confidence = sum(confidences) / len(confidences) if confidences else None
    error_rate = len(errors) / total if total else 0.0

    summary = AnalyticsSummary(
        total_requests=total,
        avg_latency_ms=round(avg_latency, 2),
        avg_confidence=round(avg_confidence, 4) if avg_confidence is not None else None,
        error_rate=round(error_rate, 4),
        service_breakdown=dict(service_counts),
    )

    return MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=summary,
        confidence=0.7,
        evidence=[f"analyzed={total} inference log(s)"],
        metadata={"note": "In-memory analytics. Production use requires persistent log store."},
    )
