from pydantic import BaseModel, Field

from performance_decision_engine.domain.entities.configuration import ResolvedTriplet
from performance_decision_engine.domain.value_objects.recommendation_decision import (
    RecommendationDecision,
)
from performance_decision_engine.domain.value_objects.recommendation_evidence import (
    RecommendationEvidence,
)
from performance_decision_engine.domain.value_objects.recommendation_scope import (
    RecommendationScope,
)
from performance_decision_engine.domain.value_objects.recommended_triplet import (
    RecommendedTriplet,
)
from performance_decision_engine.domain.value_objects.rule_evaluation import RuleEvaluation


class RecommendationEngineInfo(BaseModel):
    engine_type: str
    engine_version: str


class EndpointRecommendation(BaseModel):
    endpoint_name: str
    feature_reference: str
    current_triplet: ResolvedTriplet
    proposed_triplet: RecommendedTriplet
    decision: RecommendationDecision
    evidence_codes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    decision: RecommendationDecision
    scope: RecommendationScope
    endpoint_recommendations: list[EndpointRecommendation] = Field(default_factory=list)
    evidence: list[RecommendationEvidence] = Field(default_factory=list)
    applied_rules: list[RuleEvaluation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    engine: RecommendationEngineInfo
