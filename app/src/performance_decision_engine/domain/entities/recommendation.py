from typing import Any

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    action: str
    explanation: str
    evidence: dict[str, Any] = Field(default_factory=dict)
