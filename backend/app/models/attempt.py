from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    started_at = Column(DateTime, default=utcnow)
    submitted_at = Column(DateTime, nullable=True)
    # in_progress, submitted, graded, abandoned
    status = Column(String(20), default="in_progress")
    # Final scores (0-100)
    raw_score = Column(Float, default=0.0)
    ml_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    # ML analysis results stored as JSON string
    ml_analysis = Column(Text, default="{}")
    is_offline = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="attempts", foreign_keys=[user_id])
    assessment = relationship("Assessment", back_populates="attempts")
    answers = relationship("Answer", back_populates="attempt", cascade="all, delete-orphan")
    predictions = relationship("MLPrediction", back_populates="attempt", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    # For MCQ/multi_select: JSON string of selected option indices
    submitted_options = Column(Text, default="[]")
    # For coding/sql: the code text
    submitted_code = Column(Text, default="")
    # For short_answer/system_design: text answer
    submitted_answer = Column(Text, default="")
    # Test results from sandbox for coding/sql: JSON string
    test_results = Column(Text, default="[]")
    time_limit_exceeded = Column(Boolean, default=False)
    memory_limit_exceeded = Column(Boolean, default=False)
    compiled = Column(Boolean, default=True)
    # ML evaluation result for this answer: score 0-100, method, reasoning, etc.
    ml_evaluation = Column(Text, default="{}")
    time_spent_seconds = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utcnow)

    attempt = relationship("Attempt", back_populates="answers", foreign_keys=[attempt_id])
    user = relationship("User", back_populates="answers", foreign_keys=[user_id])
    question = relationship("Question", back_populates="answers", foreign_keys=[question_id])
