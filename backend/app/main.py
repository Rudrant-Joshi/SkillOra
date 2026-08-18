"""
Skillora Backend API

This is the business-logic + data-persistence layer for the AI-Enabled
Standardized Assessment Platform. It sits between the frontend (React/Vite)
and the ML Gateway (FastAPI), managing:

  - Authentication & RBAC (JWT, candidate/trainer/admin)
  - Database persistence (SQLAlchemy + SQLite/PostgreSQL)
  - Assessment workflow: create, start, fetch questions, submit, score
  - ML integration: calls the ML Gateway for evaluation, skill estimation,
    scorecard aggregation, and analytics
  - Analytics: assessment stats, candidate progress, skill gaps

Architecture:
  Frontend → Backend (port 8001) → ML Gateway (port 8000)

Run:
  python -m app.init_db    # initialize database + seed data
  uvicorn app.main:app --reload --port 8001
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db
from app.api import analytics, auth, assessments, attempts, questions, skills, offline

logger = logging.getLogger("backend")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Skillora Backend starting on %s", settings.DEBUG)
    init_db()
    # Seed data
    try:
        from app.services.seed import seed_database
        seed_database()
    except Exception as e:
        logger.warning("Seed data error: %s", e)
    yield


app = FastAPI(
    title="Skillora Backend API",
    version="1.0.0",
    description="Business logic + data layer for the AI-Enabled Assessment Platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth.router)
app.include_router(assessments.router)
app.include_router(attempts.router)
app.include_router(questions.router)
app.include_router(skills.router)
app.include_router(analytics.router)
app.include_router(offline.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "skillora-backend"}


@app.get("/")
def root():
    return {
        "service": "Skillora Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )
