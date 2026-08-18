"""
Environment-based configuration. No secrets hard-coded, no provider
hard-coded (master prompt §24, §33).
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"

# Load .env from the ml/ root if present
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseModel):
    env: str = os.getenv("ML_ENV", "development")

    llm_provider: str = os.getenv("LLM_PROVIDER", "anthropic")
    llm_model: str = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")

    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    vector_db_backend: str = os.getenv("VECTOR_DB_BACKEND", "faiss_local")
    vector_db_url: str = os.getenv("VECTOR_DB_URL", "")

    request_timeout_s: float = float(os.getenv("ML_REQUEST_TIMEOUT_S", "30"))
    log_level: str = os.getenv("ML_LOG_LEVEL", "INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_model_registry() -> dict:
    """
    Loads configs/model_registry.yaml — the single place that maps a
    logical model role (e.g. "code_review_llm") to a concrete provider +
    model id + version. Services ask ModelRouter for a role, never for a
    hard-coded model name (master prompt §24).
    """
    path = CONFIG_DIR / "model_registry.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


@lru_cache
def get_thresholds() -> dict:
    path = CONFIG_DIR / "thresholds.yaml"
    with open(path) as f:
        return yaml.safe_load(f)
