"""
Initialize the backend database and seed initial data.

Usage:
  cd backend
  python -m app.init_db
"""
from __future__ import annotations

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("backend.init")

# Ensure the backend package root is on sys.path
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))


def main():
    from app.database import init_db
    from app.services.seed import seed_database

    logger.info("Creating database tables...")
    init_db()

    logger.info("Seeding initial data...")
    seed_database()

    logger.info("Database initialization complete.")


if __name__ == "__main__":
    main()
