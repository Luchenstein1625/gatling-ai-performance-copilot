from typing import Any

from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation


def recommend_baseline(
    error_rate_percent: float,
    p95_response_time_ms: int | None,
    expected_response_time_ms: int | None,
) -> Recommendation:
    """Apply the original baseline rules without changing their public contract."""
    evidence = {
        "error_rate_percent": error_rate_percent,
        "p95_response_time_ms": p95_response_time_ms,
        "expected_response_time_ms": expected_response_time_ms,
    }

    if error_rate_percent > 0:
        return Recommendation(
            action="review",
            explanation="La ejecución presenta solicitudes fallidas.",
            evidence=evidence,
        )

    if (
        p95_response_time_ms is not None
        and expected_response_time_ms is not None
        and p95_response_time_ms > expected_response_time_ms
    ):
        return Recommendation(
            action="review",
            explanation="El p95 observado supera el tiempo esperado.",
            evidence=evidence,
        )

    return Recommendation(
        action="maintain",
        explanation="Las reglas básicas evaluadas no detectaron incumplimientos.",
        evidence=evidence,
    )


def recommend_execution(execution: NormalizedExecution) -> Recommendation:
    """Recommend an action from one normalized performance-test execution.

    The current normalized model exposes global metrics. When several endpoints
    are enabled, the strictest available response-time target is used and the
    limitation is recorded in the evidence.
    """
    enabled_endpoints = [
        endpoint for endpoint in execution.configuration.endpoints if endpoint.enabled
    ]
    endpoint_targets = {
        endpoint.name: endpoint.triplet.response_time_ms
        for endpoint in enabled_endpoints
        if endpoint.triplet.response_time_ms is not None
    }
    expected_response_time_ms = min(endpoint_targets.values()) if endpoint_targets else None
    metrics = execution.global_metrics

    common_evidence: dict[str, Any] = {
        "total_requests": metrics.total_requests,
        "successful_requests": metrics.successful_requests,
        "failed_requests": metrics.failed_requests,
        "enabled_endpoints": [endpoint.name for endpoint in enabled_endpoints],
        "endpoint_response_time_targets_ms": endpoint_targets,
        "metrics_scope": "execution",
        "warnings": execution.warnings,
    }

    if len(enabled_endpoints) > 1:
        common_evidence["scope_note"] = (
            "Las métricas son globales para la ejecución; no representan resultados "
            "individuales por endpoint."
        )

    if not enabled_endpoints:
        return Recommendation(
            action="review",
            explanation="No existen endpoints habilitados para generar una recomendación.",
            evidence=common_evidence,
        )

    if metrics.total_requests == 0:
        return Recommendation(
            action="review",
            explanation="La ejecución no contiene solicitudes para evaluar.",
            evidence=common_evidence,
        )

    if metrics.assertions is not None and not metrics.assertions.all_passed:
        common_evidence["failed_assertions"] = metrics.assertions.failed
        return Recommendation(
            action="review",
            explanation="Una o más assertions de la ejecución fallaron.",
            evidence=common_evidence,
        )

    if metrics.p95_response_time_ms is None:
        return Recommendation(
            action="review",
            explanation="La ejecución no contiene p95 para evaluar el tiempo de respuesta.",
            evidence=common_evidence,
        )

    if expected_response_time_ms is None:
        return Recommendation(
            action="review",
            explanation=(
                "Los endpoints habilitados no contienen "
                "un objetivo de tiempo de respuesta resuelto."
            ),
            evidence=common_evidence,
        )

    recommendation = recommend_baseline(
        error_rate_percent=metrics.error_rate_percent,
        p95_response_time_ms=metrics.p95_response_time_ms,
        expected_response_time_ms=expected_response_time_ms,
    )
    recommendation.evidence.update(common_evidence)
    return recommendation
