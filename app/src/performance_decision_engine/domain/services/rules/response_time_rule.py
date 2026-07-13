from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.value_objects.recommendation_decision import (
    RecommendationDecision,
)
from performance_decision_engine.domain.value_objects.recommendation_evidence import (
    RecommendationEvidence,
)
from performance_decision_engine.domain.value_objects.rule_evaluation import RuleEvaluation


class ResponseTimeRule:
    rule_id = "response_time"
    priority = 70

    def evaluate(self, execution: NormalizedExecution) -> RuleEvaluation:
        metrics = execution.global_metrics
        metric_name: str | None = None
        observed: int | None = None
        for candidate_name, candidate_value in (
            ("p95_response_time_ms", metrics.p95_response_time_ms),
            ("p90_response_time_ms", metrics.p90_response_time_ms),
            ("mean_response_time_ms", metrics.mean_response_time_ms),
        ):
            if candidate_value is not None:
                metric_name = candidate_name
                observed = candidate_value
                break

        exceeded: list[tuple[str, int]] = []
        if observed is not None:
            for endpoint in execution.configuration.endpoints:
                if not endpoint.enabled or endpoint.triplet.response_time_ms is None:
                    continue
                if observed > endpoint.triplet.response_time_ms:
                    exceeded.append((endpoint.name, endpoint.triplet.response_time_ms))

        evidence = []
        if exceeded and observed is not None and metric_name is not None:
            strictest_target = min(target for _, target in exceeded)
            evidence.append(
                RecommendationEvidence(
                    code="RESPONSE_TIME_ABOVE_TARGET",
                    metric=metric_name,
                    observed_value=observed,
                    reference_value=strictest_target,
                    comparison=">",
                    message=(
                        "The global response-time metric exceeds the target of one or more "
                        "enabled endpoints."
                    ),
                )
            )

        triggered = bool(exceeded)
        return RuleEvaluation(
            rule_id=self.rule_id,
            triggered=triggered,
            priority=self.priority,
            decision=RecommendationDecision.REVIEW if triggered else None,
            evidence=evidence,
            affected_endpoints=[name for name, _ in exceeded],
        )
