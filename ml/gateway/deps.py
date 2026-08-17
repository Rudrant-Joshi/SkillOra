"""
Gateway-level dependency: extracts the AuthContext the backend has already
computed and signed/attested, and hands it to services. The ML gateway is
positioned behind the backend (master prompt §33: "The backend remains the
authority") — it trusts a service-to-service call, not an end-user token.

In production this would validate a service JWT / mTLS identity from the
backend and deserialize the AuthContext from a trusted header/claim. Phase
1 ships the trust boundary shape; wiring it to the real backend auth
mechanism is a backend-team integration task, not an ML concern.
"""
from __future__ import annotations

from fastapi import Header, HTTPException

from shared.schemas.common import AuthContext


def get_auth_context(
    x_user_id: str = Header(...),
    x_role: str = Header(...),
    x_company_id: str | None = Header(default=None),
    x_permission_scopes: str = Header(default=""),
    x_repository_ids: str = Header(default=""),
    x_company_ids_allowed: str = Header(default=""),
) -> AuthContext:
    if not x_user_id or not x_role:
        raise HTTPException(status_code=401, detail="Missing required auth headers.")

    return AuthContext(
        user_id=x_user_id,
        role=x_role,
        company_id=x_company_id,
        permission_scopes=[s for s in x_permission_scopes.split(",") if s],
        repository_ids=[s for s in x_repository_ids.split(",") if s],
        company_ids_allowed=[s for s in x_company_ids_allowed.split(",") if s],
    )
