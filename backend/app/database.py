from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from functools import lru_cache

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


def utcnow() -> datetime:
    """Timezone-aware UTC timestamp (replaces deprecated datetime.utcnow).

    Stored timestamps are tz-aware so they round-trip correctly under SQLite and
    never trigger a naive/aware comparison error against aware datetimes.
    """
    return datetime.now(timezone.utc)


logger = logging.getLogger("backend")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class Base(DeclarativeBase):
    pass


def _create_engine():
    settings = get_settings()
    url = settings.DATABASE_URL
    logger.info("Database URL: %s", url)
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine = create_engine(url, connect_args=connect_args, echo=settings.DEBUG)
    return engine


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import user, assessment, question, attempt, skill, ml_prediction, offline_sync
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")
