from pydantic import BaseModel, Field

from performance_decision_engine.domain.value_objects.recommendation_decision import (
    RecommendationDecision,
)
from performance_decision_engine.domain.value_objects.recommendation_evidence import (
    RecommendationEvidence,
)


class RuleEvaluation(BaseModel):
    rule_id: str
    triggered: bool
    priority: int = Field(ge=0)
    decision: RecommendationDecision | None = None
    evidence: list[RecommendationEvidence] = Field(default_factory=list)
    affected_endpoints: list[str] = Field(default_factory=list)
