from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class OfflineSync(Base):
    """
    Stores assessment data that was captured offline and syncs to the
    server when the client comes back online.
    """

    __tablename__ = "offline_syncs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    # JSON blob of the attempt payload the client captured while offline
    data_json = Column(Text, nullable=False)
    is_synced = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    synced_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="offline_syncs", foreign_keys=[user_id])
