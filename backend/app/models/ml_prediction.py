from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"), nullable=True)
    service_name = Column(String(60), nullable=False)  # evaluation, scorecard, skill_engine, etc.
    model_version = Column(String(60), nullable=False)
    prediction_json = Column(Text, nullable=False)  # full prediction payload
    confidence = Column(Float, default=0.0)
    evidence = Column(Text, default="[]")  # JSON string of evidence strings
    request_id = Column(String(60), nullable=True)
    latency_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    error_code = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions", foreign_keys=[user_id])
    attempt = relationship("Attempt", back_populates="predictions", foreign_keys=[attempt_id])
