from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    users = relationship("User", back_populates="company", foreign_keys="User.company_id")
    assessments = relationship("Assessment", back_populates="company")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(20), nullable=False)  # candidate, trainer, admin
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company", back_populates="users", foreign_keys=[company_id])
    attempts = relationship("Attempt", back_populates="user", foreign_keys="Attempt.user_id")
    answers = relationship("Answer", back_populates="user", foreign_keys="Answer.user_id")
    user_skills = relationship("UserSkill", back_populates="user", foreign_keys="UserSkill.user_id")
    predictions = relationship("MLPrediction", back_populates="user", foreign_keys="MLPrediction.user_id")
    offline_syncs = relationship("OfflineSync", back_populates="user", foreign_keys="OfflineSync.user_id")
