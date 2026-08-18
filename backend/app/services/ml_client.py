"""
ML Gateway Client — bridges the backend to the ML Gateway FastAPI app.

The ML gateway runs as a separate service (default port 8000). The backend
is the authority for identity (§33: "The backend remains the authority"),
so the backend supplies the AuthContext headers that the ML gateway validates.

Every ML prediction is logged to the ml_predictions table for auditing and
analytics. If the ML gateway is unavailable, the client raises a
RuntimeError so the caller can decide how to degrade (e.g. store raw
answers and defer scoring).
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger("backend.ml_client")


def _auth_headers(user_id: int, role: str, company_id: int | None = None) -> dict[str, str]:
    headers = {
        "X-User-Id": str(user_id),
        "X-Role": role,
        "X-Company-Id": str(company_id) if company_id else "",
        "X-Permission-Scopes": "",
        "X-Repository-Ids": "",
        "X-Company-Ids-Allowed": str(company_id) if company_id else "",
    }
    return headers


def call_ml(
    endpoint: str,
    payload: dict[str, Any],
    *,
    user_id: int,
    role: str,
    company_id: int | None = None,
    timeout: float | None = None,
    unwrap: bool = True,
) -> dict[str, Any]:
    """
    Call an ML gateway endpoint and return the parsed response.

    When unwrap=True (default), returns a dict with keys: prediction,
    confidence, evidence, model_version, request_id, metadata, latency_ms.
    This is for endpoints that return the standard MLResponse envelope.

    When unwrap=False, returns the raw response body under "prediction"
    with confidence=None. Use this for endpoints that return a raw dict
    (e.g. /ml/skill/estimate-batch returns {skill_name: MLResponse}).
    """
    settings = get_settings()
    if timeout is None:
        timeout = settings.ML_REQUEST_TIMEOUT_S

    url = f"{settings.ML_GATEWAY_URL}{endpoint}"
    headers = {
        **_auth_headers(user_id, role, company_id),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    start = time.perf_counter()
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.RequestError) as e:
        logger.warning("ML gateway unreachable at %s: %s", url, e)
        raise MLUnavailableError(f"ML gateway unreachable: {e}") from e

    latency_ms = (time.perf_counter() - start) * 1000

    if resp.status_code != 200:
        logger.warning("ML gateway %s returned %d: %s", endpoint, resp.status_code, resp.text[:200])
        raise MLUnavailableError(f"ML gateway returned {resp.status_code}: {resp.text[:200]}")

    body = resp.json()

    if "error" in body:
        err = body["error"]
        raise MLUnavailableError(f"ML error {err.get('code', '?')}: {err.get('message', '')}")

    if unwrap and "prediction" in body:
        prediction = body.get("prediction", {})
        if isinstance(prediction, str):
            try:
                prediction = json.loads(prediction)
            except json.JSONDecodeError:
                prediction = {}
        result = {
            "prediction": prediction,
            "confidence": body.get("confidence"),
            "evidence": body.get("evidence", []),
            "model_version": body.get("model_version"),
            "request_id": body.get("request_id"),
            "metadata": body.get("metadata", {}),
            "latency_ms": latency_ms,
        }
    else:
        result = {
            "prediction": body,
            "confidence": None,
            "evidence": [],
            "model_version": "raw",
            "request_id": "",
            "metadata": {},
            "latency_ms": latency_ms,
        }
    return result


class MLUnavailableError(Exception):
    """Raised when the ML gateway cannot be reached or returns an error."""
