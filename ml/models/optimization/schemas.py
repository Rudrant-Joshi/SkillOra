from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class OptimizationRequest(BaseModel):
    model_role: str
    target_format: str = "onnx"
    opset_version: int = Field(default=17, ge=13, le=20)


class OptimizationResponse(BaseModel):
    model_role: str
    target_format: str
    optimized: bool
    output_path: Optional[str] = None
    message: str = ""
