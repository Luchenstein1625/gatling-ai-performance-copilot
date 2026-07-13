from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.value_objects.recommendation_decision import (
    RecommendationDecision,
)
from performance_decision_engine.domain.value_objects.recommendation_evidence import (
    RecommendationEvidence,
)
from performance_decision_engine.domain.value_objects.rule_evaluation import RuleEvaluation


class AssertionRule:
    rule_id = "assertions"
    priority = 90

    def evaluate(self, execution: NormalizedExecution) -> RuleEvaluation:
        assertions = execution.global_metrics.assertions
        triggered = assertions is not None and not assertions.all_passed
        evidence = []
        if triggered and assertions is not None:
            evidence.append(
                RecommendationEvidence(
                    code="ASSERTION_FAILURE",
                    metric="failed_assertions",
                    observed_value=assertions.failed,
                    reference_value=0,
                    comparison=">",
                    message="One or more execution assertions failed.",
                )
            )
        return RuleEvaluation(
            rule_id=self.rule_id,
            triggered=triggered,
            priority=self.priority,
            decision=RecommendationDecision.REVIEW if triggered else None,
            evidence=evidence,
        )
