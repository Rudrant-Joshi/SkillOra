from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)
    category = Column(String(40), default="lang")  # lang, fw, db, tool, concept
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user_skills = relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan")


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    # level 0..1
    level = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)  # 0..1
    source = Column(String(40), default="assessment")  # assessment, activity, self_declared
    updated_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="user_skills", foreign_keys=[user_id])
    skill = relationship("Skill", back_populates="user_skills", foreign_keys=[skill_id])
