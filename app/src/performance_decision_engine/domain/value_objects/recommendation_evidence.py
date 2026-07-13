from typing import TypeAlias

from pydantic import BaseModel

from performance_decision_engine.domain.value_objects.recommendation_scope import (
    RecommendationScope,
)

EvidenceValue: TypeAlias = str | int | float | bool | None


class RecommendationEvidence(BaseModel):
    code: str
    metric: str | None = None
    observed_value: EvidenceValue = None
    reference_value: EvidenceValue = None
    comparison: str | None = None
    scope: RecommendationScope = RecommendationScope.EXECUTION
    message: str
