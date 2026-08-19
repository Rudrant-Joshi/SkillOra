from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_type = Column(String(30), nullable=False)  # mcq, multi_select, coding, sql, short_answer, system_design
    prompt = Column(Text, nullable=False)
    # For MCQ/multi_select: list of option strings
    options = Column(JSON, default=list)
    # For MCQ/multi_select: list of indices of correct options
    correct_options = Column(JSON, default=list)
    difficulty = Column(Float, default=0.5)  # 0..1
    skills = Column(Text, default="")  # comma-separated
    language = Column(String(30), default="python")
    # For coding: list of test case objects [{name, passed, hidden}]
    test_cases_template = Column(JSON, default=list)
    # For coding: starter code
    starter_code = Column(Text, default="")
    # For short_answer/system_design: grading rubric
    rubric = Column(JSON, default=list)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    assessment = relationship("Assessment", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
