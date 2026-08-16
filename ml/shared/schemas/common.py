"""
Common request/response envelopes used by every ML service.

Every ML service response follows the Backend <-> ML contract (master
prompt §41): request_id, model_version, prediction payload, confidence,
evidence, metadata. Errors follow a single error schema so the backend
can handle failures uniformly regardless of which service raised them.
"""
from __future__ import annotations

import uuid
from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field


def new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


class AuthContext(BaseModel):
    """
    Authorization context. This is ALWAYS supplied by the backend, never
    trusted verbatim from a client. The ML layer treats every field here
    as backend-attested, not user-attested (master prompt §33).
    """

    user_id: str
    company_id: Optional[str] = None
    role: str = Field(description="e.g. 'candidate', 'recruiter', 'learner', 'admin'")
    permission_scopes: list[str] = Field(default_factory=list)
    repository_ids: list[str] = Field(
        default_factory=list, description="Repos this caller may reference in retrieval/RAG"
    )
    company_ids_allowed: list[str] = Field(
        default_factory=list, description="Company-scoped content this caller may retrieve"
    )

    def has_scope(self, scope: str) -> bool:
        return scope in self.permission_scopes


class ErrorCode(str, Enum):
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED_SCOPE = "UNAUTHORIZED_SCOPE"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNSUPPORTED_LANGUAGE = "UNSUPPORTED_LANGUAGE"
    CONTENT_POLICY = "CONTENT_POLICY"


class MLError(BaseModel):
    code: ErrorCode
    message: str


class MLErrorResponse(BaseModel):
    request_id: str
    error: MLError


T = TypeVar("T")


class MLResponse(BaseModel, Generic[T]):
    """
    Standard success envelope for every ML endpoint (master prompt §25/§30/§41).

    - prediction: the actual output payload (service-specific shape)
    - confidence: 0..1, required for any high-impact output
    - evidence: list of short strings/refs backing the prediction — never
      return an unexplained score
    - metadata: model_version lives here alongside timing/cost info
    """

    request_id: str
    model_version: str
    prediction: T
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MLException(Exception):
    """Raised by services; translated to MLErrorResponse at the gateway edge."""

    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
