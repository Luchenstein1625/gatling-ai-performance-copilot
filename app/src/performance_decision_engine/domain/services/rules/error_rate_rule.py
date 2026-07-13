from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.value_objects.recommendation_decision import (
    RecommendationDecision,
)
from performance_decision_engine.domain.value_objects.recommendation_evidence import (
    RecommendationEvidence,
)
from performance_decision_engine.domain.value_objects.rule_evaluation import RuleEvaluation


class ErrorRateRule:
    rule_id = "error_rate"
    priority = 80

    def evaluate(self, execution: NormalizedExecution) -> RuleEvaluation:
        error_rate = execution.global_metrics.error_rate_percent
        triggered = error_rate > 0.0
        evidence = []
        if triggered:
            evidence.append(
                RecommendationEvidence(
                    code="ERROR_RATE_DETECTED",
                    metric="error_rate_percent",
                    observed_value=error_rate,
                    reference_value=0.0,
                    comparison=">",
                    message="The execution contains failed requests.",
                )
            )
        return RuleEvaluation(
            rule_id=self.rule_id,
            triggered=triggered,
            priority=self.priority,
            decision=RecommendationDecision.REVIEW if triggered else None,
            evidence=evidence,
        )
