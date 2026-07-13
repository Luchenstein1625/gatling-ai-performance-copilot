from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.value_objects.recommendation_decision import (
    RecommendationDecision,
)
from performance_decision_engine.domain.value_objects.recommendation_evidence import (
    RecommendationEvidence,
)
from performance_decision_engine.domain.value_objects.rule_evaluation import RuleEvaluation


class StableExecutionRule:
    rule_id = "stable_execution"
    priority = 10

    def evaluate(self, execution: NormalizedExecution) -> RuleEvaluation:
        assertions = execution.global_metrics.assertions
        enabled = [endpoint for endpoint in execution.configuration.endpoints if endpoint.enabled]
        resolved = all(
            endpoint.triplet.concurrency_value is not None
            and endpoint.triplet.iterations_value is not None
            and endpoint.triplet.response_time_ms is not None
            for endpoint in enabled
        )
        assertions_ok = assertions is None or assertions.all_passed
        triggered = (
            bool(enabled)
            and resolved
            and execution.global_metrics.total_requests > 0
            and execution.global_metrics.failed_requests == 0
            and assertions_ok
        )
        evidence = []
        if triggered:
            evidence.append(
                RecommendationEvidence(
                    code="STABLE_EXECUTION",
                    metric="failed_requests",
                    observed_value=0,
                    reference_value=0,
                    comparison="=",
                    message="The execution is eligible to keep its current configuration.",
                )
            )
        return RuleEvaluation(
            rule_id=self.rule_id,
            triggered=triggered,
            priority=self.priority,
            decision=RecommendationDecision.KEEP if triggered else None,
            evidence=evidence,
            affected_endpoints=[endpoint.name for endpoint in enabled],
        )
