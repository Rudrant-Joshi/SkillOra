"""
Pytest configuration: initializes a fresh test database and seeds data
before running the test suite.
"""
import os
import sys

# Ensure backend is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use isolated test database
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_skillgraph.db")
os.environ.setdefault("SECRET_KEY", "skillora-test-secret-key-min-32-bytes-long-xyz")
os.environ.setdefault("ML_GATEWAY_URL", "http://localhost:8000")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.database import Base, engine, SessionLocal
from app.models import user, assessment, question, attempt, skill, ml_prediction, offline_sync
from app.services.seed import seed_database


@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    """Create all tables and seed data once for the entire test session."""
    # Drop and recreate all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed the database
    db = SessionLocal()
    seed_database(db)
    db.close()

    yield

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a clean database session for each test."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
