"""
Authorization + privacy guardrails shared by every service.

Master prompt §33: never blindly trust client-supplied user_id / company_id
/ role / permission / score / assessment_id. The backend remains the
authority — this module is where every service checks the AuthContext
before touching scoped data, so the check lives in one place instead of
being re-implemented (and possibly forgotten) per service.

Master prompt §27: strip PII/secrets before anything reaches a training
or logging path.
"""
from __future__ import annotations

import re

from shared.schemas.common import AuthContext, ErrorCode, MLException

_SECRET_PATTERNS = [
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[\w\-]{16,}"),
    re.compile(r"(?i)secret\s*[:=]\s*['\"]?[\w\-]{8,}"),
    re.compile(r"(?i)password\s*[:=]\s*['\"]?\S+"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),  # AWS access key id pattern
]

_EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def scrub_secrets_and_pii(text: str) -> str:
    """Redacts likely secrets/keys and emails before logging, storing, or training on text."""
    cleaned = text
    for pattern in _SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED_SECRET]", cleaned)
    cleaned = _EMAIL_PATTERN.sub("[REDACTED_EMAIL]", cleaned)
    return cleaned


def require_repository_access(auth: AuthContext, repository_id: str) -> None:
    if repository_id not in auth.repository_ids and "admin" not in auth.permission_scopes:
        raise MLException(
            ErrorCode.UNAUTHORIZED_SCOPE,
            f"Caller is not authorized to access repository '{repository_id}'.",
        )


def require_company_access(auth: AuthContext, company_id: str) -> None:
    if (
        company_id not in auth.company_ids_allowed
        and auth.company_id != company_id
        and "admin" not in auth.permission_scopes
    ):
        raise MLException(
            ErrorCode.UNAUTHORIZED_SCOPE,
            f"Caller is not authorized to access company '{company_id}' data.",
        )


def require_role(auth: AuthContext, allowed_roles: set[str]) -> None:
    if auth.role not in allowed_roles:
        raise MLException(
            ErrorCode.UNAUTHORIZED_SCOPE,
            f"Role '{auth.role}' is not permitted to call this endpoint.",
        )


# Fields that must never be used as model features (master prompt §31).
SENSITIVE_CHARACTERISTIC_FIELDS = frozenset(
    {
        "race",
        "ethnicity",
        "religion",
        "political_affiliation",
        "sexual_orientation",
        "health_status",
        "disability_status",
        "gender",
        "age",
        "marital_status",
        "nationality",
        "pregnancy_status",
    }
)


def assert_no_sensitive_fields(feature_dict: dict) -> None:
    """
    Defensive check callable from any scoring/matching feature builder.
    Raises rather than silently dropping, so a caller that accidentally
    wires in a forbidden field finds out immediately instead of shipping
    a biased feature set.
    """
    present = SENSITIVE_CHARACTERISTIC_FIELDS.intersection(k.lower() for k in feature_dict)
    if present:
        raise MLException(
            ErrorCode.VALIDATION_ERROR,
            f"Feature set includes prohibited sensitive characteristics: {sorted(present)}",
        )
