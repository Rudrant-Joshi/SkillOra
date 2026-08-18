from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    company_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
