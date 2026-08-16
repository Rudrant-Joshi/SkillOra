"""
Structured JSON logging, including a dedicated inference-log helper
(master prompt §35 MLOps: inference logging; §36 Monitoring).

Kept dependency-free (stdlib logging + json) so it works the same in
services, workers, and tests without pulling in an APM SDK.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any

from shared.config.settings import get_settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(get_settings().log_level)
    return logger


_inference_logger = get_logger("ml.inference")
_inference_log_buffer: list[dict[str, Any]] = []


def log_inference(
    *,
    service: str,
    model_version: str,
    request_id: str,
    latency_ms: float,
    confidence: float | None,
    success: bool,
    error_code: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """
    Emits one structured line per inference call. Feeds directly into the
    monitoring signals from master prompt §36: latency, error rate,
    model usage, confidence distribution.
    """
    record = {
        "ts": time.time(),
        "type": "inference",
        "service": service,
        "model_version": model_version,
        "request_id": request_id,
        "latency_ms": round(latency_ms, 2),
        "confidence": confidence,
        "success": success,
        "error_code": error_code,
        **(extra or {}),
    }
    _inference_logger.info(json.dumps(record))
    _inference_log_buffer.append(record)


def get_inference_logs() -> list[dict[str, Any]]:
    """Return a copy of the in-memory inference log buffer."""
    return list(_inference_log_buffer)


class Timer:
    """Small context manager for measuring latency_ms around a service call."""

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000
