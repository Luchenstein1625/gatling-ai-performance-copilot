from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.value_objects.recommendation_decision import (
    RecommendationDecision,
)
from performance_decision_engine.domain.value_objects.recommendation_evidence import (
    RecommendationEvidence,
)
from performance_decision_engine.domain.value_objects.rule_evaluation import RuleEvaluation


class ExecutionDataRule:
    rule_id = "execution_data"
    priority = 100

    def evaluate(self, execution: NormalizedExecution) -> RuleEvaluation:
        evidence: list[RecommendationEvidence] = []
        endpoints = execution.configuration.endpoints

        if not endpoints:
            evidence.append(
                RecommendationEvidence(
                    code="NO_ENDPOINTS",
                    message="The execution does not contain endpoint configurations.",
                )
            )

        enabled = [endpoint for endpoint in endpoints if endpoint.enabled]
        if endpoints and not enabled:
            evidence.append(
                RecommendationEvidence(
                    code="NO_ENABLED_ENDPOINTS",
                    message="The execution does not contain enabled endpoints.",
                )
            )

        unresolved = [
            endpoint.name
            for endpoint in enabled
            if endpoint.triplet.concurrency_value is None
            or endpoint.triplet.iterations_value is None
            or endpoint.triplet.response_time_ms is None
        ]
        if unresolved:
            evidence.append(
                RecommendationEvidence(
                    code="UNRESOLVED_TRIPLET",
                    metric="triplet",
                    observed_value=", ".join(unresolved),
                    message="One or more enabled endpoints contain unresolved triplet values.",
                )
            )

        if execution.global_metrics.total_requests == 0:
            evidence.append(
                RecommendationEvidence(
                    code="ZERO_REQUESTS",
                    metric="total_requests",
                    observed_value=0,
                    reference_value=1,
                    comparison="<",
                    message="The execution contains zero requests.",
                )
            )

        triggered = bool(evidence)
        return RuleEvaluation(
            rule_id=self.rule_id,
            triggered=triggered,
            priority=self.priority,
            decision=RecommendationDecision.INSUFFICIENT_DATA if triggered else None,
            evidence=evidence,
            affected_endpoints=unresolved,
        )
