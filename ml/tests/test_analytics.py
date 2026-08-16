from __future__ import annotations

import pytest

from services.analytics.service import summarize_analytics
from services.analytics.schemas import AnalyticsQuery


def test_analytics_returns_summary():
    query = AnalyticsQuery(limit=10)
    resp = summarize_analytics(query)
    assert resp.prediction.total_requests >= 0
    assert "avg_latency_ms" in resp.prediction.model_dump()


def test_analytics_filter_by_service():
    query = AnalyticsQuery(service="code_intelligence", limit=10)
    resp = summarize_analytics(query)
    for svc in resp.prediction.service_breakdown.keys():
        assert svc == "code_intelligence" or resp.prediction.service_breakdown[svc] == 0
