"""
Analytics service — helper queries for trainer/admin analytics dashboards.
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.models.user import User

logger = logging.getLogger("backend.analytics")


def check_company_member(user: User, target: User, db: Session) -> None:
    """Verify that target user is in the same company as the current user (for trainers)."""
    from fastapi import HTTPException, status

    if user.role == "admin":
        return  # global admin can access anyone
    if user.company_id is None or target.company_id is None:
        if user.company_id != target.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: user not in your company",
            )
        return
    if user.company_id != target.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user not in your company",
        )
