from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.api.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.user import Company, User
from app.schemas.auth import LoginRequest, SignupRequest, Token
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    token = create_access_token(user.id, user.role, user.company_id)
    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        company_id=user.company_id,
    )


@router.post("/signup", response_model=Token)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if req.role not in ("candidate", "trainer", "admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        company_id=None,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.role, user.company_id)
    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        company_id=user.company_id,
    )


@router.get("/me", response_model=UserRead)
def read_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/roles", response_model=dict)
def get_roles():
    """Public endpoint listing available roles."""
    return {
        "roles": [
            {"id": "candidate", "label": "Candidate"},
            {"id": "trainer", "label": "Trainer"},
            {"id": "admin", "label": "Admin"},
        ]
    }
