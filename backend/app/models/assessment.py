from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    duration_minutes = Column(Integer, default=60)
    total_questions = Column(Integer, default=25)
    skills = Column(Text, default="")  # comma-separated skill names
    difficulty_distribution = Column(JSON, default=dict)
    allowed_question_types = Column(Text, default="")  # comma-separated
    coding_languages = Column(Text, default="")  # comma-separated
    is_active = Column(Boolean, default=True)
    is_adaptive = Column(Boolean, default=True)
    scoring_rubric = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="assessments")
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="assessment", cascade="all, delete-orphan")
