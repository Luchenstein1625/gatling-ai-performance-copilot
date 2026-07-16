from typing import Any

from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation


def _trace_entry(
    rule: str,
    result: str,
    *,
    observed: object | None = None,
    expected: object | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "rule": rule,
        "result": result,
    }
    if observed is not None:
        entry["observed"] = observed
    if expected is not None:
        entry["expected"] = expected
    return entry


def _with_trace(
    evidence: dict[str, Any],
    decision_trace: list[dict[str, Any]],
    triggered_rule: str | None,
) -> dict[str, Any]:
    return {
        **evidence,
        "decision_trace": decision_trace,
        "triggered_rule": triggered_rule,
    }


def recommend_baseline(
    error_rate_percent: float,
    p95_response_time_ms: int | None,
    expected_response_time_ms: int | None,
) -> Recommendation:
    """Apply the original baseline rules without changing their public contract."""
    evidence: dict[str, Any] = {
        "error_rate_percent": error_rate_percent,
        "p95_response_time_ms": p95_response_time_ms,
        "expected_response_time_ms": expected_response_time_ms,
    }
    decision_trace: list[dict[str, Any]] = []

    error_rate_failed = error_rate_percent > 0
    decision_trace.append(
        _trace_entry(
            "error_rate",
            "failed" if error_rate_failed else "passed",
            observed=error_rate_percent,
            expected=0,
        )
    )
    if error_rate_failed:
        return Recommendation(
            action="review",
            explanation="La ejecución presenta solicitudes fallidas.",
            evidence=_with_trace(evidence, decision_trace, "error_rate"),
        )

    p95_failed = (
        p95_response_time_ms is not None
        and expected_response_time_ms is not None
        and p95_response_time_ms > expected_response_time_ms
    )
    decision_trace.append(
        _trace_entry(
            "p95_target",
            "failed" if p95_failed else "passed",
            observed=p95_response_time_ms,
            expected=expected_response_time_ms,
        )
    )
    if p95_failed:
        return Recommendation(
            action="review",
            explanation="El p95 observado supera el tiempo esperado.",
            evidence=_with_trace(evidence, decision_trace, "p95_target"),
        )

    return Recommendation(
        action="maintain",
        explanation="Las reglas básicas evaluadas no detectaron incumplimientos.",
        evidence=_with_trace(evidence, decision_trace, None),
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
    decision_trace: list[dict[str, Any]] = []

    if len(enabled_endpoints) > 1:
        common_evidence["scope_note"] = (
            "Las métricas son globales para la ejecución; no representan resultados "
            "individuales por endpoint."
        )

    endpoints_available = bool(enabled_endpoints)
    decision_trace.append(
        _trace_entry(
            "enabled_endpoints",
            "passed" if endpoints_available else "failed",
            observed=len(enabled_endpoints),
            expected="at_least_one",
        )
    )
    if not endpoints_available:
        return Recommendation(
            action="review",
            explanation="No existen endpoints habilitados para generar una recomendación.",
            evidence=_with_trace(common_evidence, decision_trace, "enabled_endpoints"),
        )

    requests_available = metrics.total_requests > 0
    decision_trace.append(
        _trace_entry(
            "total_requests",
            "passed" if requests_available else "failed",
            observed=metrics.total_requests,
            expected="greater_than_zero",
        )
    )
    if not requests_available:
        return Recommendation(
            action="review",
            explanation="La ejecución no contiene solicitudes para evaluar.",
            evidence=_with_trace(common_evidence, decision_trace, "total_requests"),
        )

    assertions_passed = metrics.assertions is None or metrics.assertions.all_passed
    decision_trace.append(
        _trace_entry(
            "assertions",
            "passed" if assertions_passed else "failed",
            observed=(
                None if metrics.assertions is None else metrics.assertions.failed
            ),
            expected=0,
        )
    )
    if not assertions_passed:
        if metrics.assertions is None:
            raise RuntimeError("Assertions state changed during recommendation.")
        common_evidence["failed_assertions"] = metrics.assertions.failed
        return Recommendation(
            action="review",
            explanation="Una o más assertions de la ejecución fallaron.",
            evidence=_with_trace(common_evidence, decision_trace, "assertions"),
        )

    p95_available = metrics.p95_response_time_ms is not None
    decision_trace.append(
        _trace_entry(
            "p95_available",
            "passed" if p95_available else "failed",
            observed=metrics.p95_response_time_ms,
            expected="available",
        )
    )
    if not p95_available:
        return Recommendation(
            action="review",
            explanation="La ejecución no contiene p95 para evaluar el tiempo de respuesta.",
            evidence=_with_trace(common_evidence, decision_trace, "p95_available"),
        )

    target_available = expected_response_time_ms is not None
    decision_trace.append(
        _trace_entry(
            "response_time_target_available",
            "passed" if target_available else "failed",
            observed=expected_response_time_ms,
            expected="available",
        )
    )
    if not target_available:
        return Recommendation(
            action="review",
            explanation=(
                "Los endpoints habilitados no contienen "
                "un objetivo de tiempo de respuesta resuelto."
            ),
            evidence=_with_trace(
                common_evidence,
                decision_trace,
                "response_time_target_available",
            ),
        )

    recommendation = recommend_baseline(
        error_rate_percent=metrics.error_rate_percent,
        p95_response_time_ms=metrics.p95_response_time_ms,
        expected_response_time_ms=expected_response_time_ms,
    )
    baseline_trace = recommendation.evidence.get("decision_trace", [])
    if not isinstance(baseline_trace, list):
        raise RuntimeError("Baseline decision trace must be a list.")

    recommendation.evidence.update(common_evidence)
    recommendation.evidence["decision_trace"] = decision_trace + baseline_trace
    return recommendation
