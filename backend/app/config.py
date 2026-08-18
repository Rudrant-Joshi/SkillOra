from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field

# Load .env from the backend root directory
_env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_env_path)
# Fallback: also check from cwd (covers uvicorn launched from project root)
load_dotenv()


class Settings:
    """
    Backend environment configuration.
    All secrets are sourced from the environment — never hard-coded.
    """

    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # --- Database ---
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./skillgraph.db")

    # --- Auth ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 days for dev
    ALGORITHM = "HS256"

    # --- ML Gateway ---
    ML_GATEWAY_URL = os.getenv("ML_GATEWAY_URL", "http://localhost:8000")
    ML_REQUEST_TIMEOUT_S = float(os.getenv("ML_REQUEST_TIMEOUT_S", "30"))

    # --- Mode ---
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"


@lru_cache
def get_settings() -> Settings:
    return Settings()
