from collections.abc import Sequence

from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import (
    EndpointRecommendation,
    Recommendation,
    RecommendationEngineInfo,
)
from performance_decision_engine.domain.services.recommendation_rule import RecommendationRule
from performance_decision_engine.domain.value_objects.load_level import LoadLevel
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


class RecommendationService:
    def __init__(
        self,
        rules: Sequence[RecommendationRule],
        engine_version: str = "1.0",
    ) -> None:
        self._rules = tuple(rules)
        self._engine_version = engine_version

    def recommend(self, execution: NormalizedExecution) -> Recommendation:
        evaluations = [rule.evaluate(execution) for rule in self._rules]
        triggered = sorted(
            (evaluation for evaluation in evaluations if evaluation.triggered),
            key=lambda evaluation: evaluation.priority,
            reverse=True,
        )
        decision = (
            triggered[0].decision
            if triggered and triggered[0].decision is not None
            else RecommendationDecision.REVIEW
        )

        evidence = [item for evaluation in triggered for item in evaluation.evidence]
        warnings = list(execution.warnings)
        enabled_endpoints = [
            endpoint for endpoint in execution.configuration.endpoints if endpoint.enabled
        ]
        if len(enabled_endpoints) > 1:
            warnings.append(
                "Global execution metrics are shared by all enabled endpoints; "
                "they are not endpoint-specific."
            )
            evidence.append(
                RecommendationEvidence(
                    code="GLOBAL_METRICS_ONLY",
                    message=(
                        "The recommendation uses execution-level metrics because endpoint-level "
                        "metrics are not available."
                    ),
                )
            )

        endpoint_recommendations = [
            EndpointRecommendation(
                endpoint_name=endpoint.name,
                feature_reference=endpoint.feature_reference,
                current_triplet=endpoint.triplet,
                proposed_triplet=RecommendedTriplet(
                    concurrency_level=LoadLevel.parse(endpoint.triplet.concurrency_level),
                    iterations_level=LoadLevel.parse(endpoint.triplet.iterations_level),
                    response_time_level=LoadLevel.parse(endpoint.triplet.response_time_level),
                    concurrency_value=endpoint.triplet.concurrency_value,
                    iterations_value=endpoint.triplet.iterations_value,
                    response_time_ms=endpoint.triplet.response_time_ms,
                ),
                decision=decision,
                evidence_codes=[item.code for item in evidence],
                warnings=(
                    ["Recommendation is based on global execution metrics."]
                    if len(enabled_endpoints) > 1
                    else []
                ),
            )
            for endpoint in enabled_endpoints
        ]

        return Recommendation(
            decision=decision,
            scope=RecommendationScope.EXECUTION,
            endpoint_recommendations=endpoint_recommendations,
            evidence=evidence,
            applied_rules=evaluations,
            warnings=list(dict.fromkeys(warnings)),
            engine=RecommendationEngineInfo(
                engine_type="rule_based",
                engine_version=self._engine_version,
            ),
        )
