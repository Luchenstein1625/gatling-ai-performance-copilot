from pathlib import Path

from performance_decision_engine.domain.entities.configuration import (
    EndpointConfiguration,
    PerformanceConfiguration,
    ResolvedTriplet,
)
from performance_decision_engine.domain.entities.execution import (
    ExecutionMetrics,
    NormalizedExecution,
)
from performance_decision_engine.domain.entities.recommendation import Recommendation
from performance_decision_engine.infrastructure.reporting.html_report_generator import (
    HtmlReportGenerator,
)


def test_generates_self_contained_html_report(tmp_path: Path) -> None:
    execution = NormalizedExecution(
        configuration=PerformanceConfiguration(
            load_type="sequence",
            endpoints=[
                EndpointConfiguration(
                    name="<endpoint>",
                    feature_reference="classpath:example.feature",
                    enabled=True,
                    triplet=ResolvedTriplet(
                        concurrency_level="low",
                        concurrency_value=10,
                        iterations_level="low",
                        iterations_value=20,
                        response_time_level="low",
                        response_time_ms=1000,
                    ),
                )
            ],
        ),
        global_metrics=ExecutionMetrics(
            total_requests=10,
            successful_requests=9,
            failed_requests=1,
            error_rate_percent=10,
            p95_response_time_ms=1500,
        ),
        warnings=["Example warning"],
    )
    recommendation = Recommendation(
        action="review",
        explanation="Review <required>.",
        evidence={
            "triggered_rule": "error_rate",
            "decision_trace": [{"rule": "error_rate", "result": "failed"}],
        },
    )
    output = tmp_path / "report.html"

    HtmlReportGenerator().generate(
        execution,
        recommendation,
        output,
        training_status={"status": "skipped"},
    )

    content = output.read_text(encoding="utf-8")
    assert "H10 Local Proof of Concept" in content
    assert "REVIEW" in content
    assert "error_rate" in content
    assert "&lt;endpoint&gt;" in content
    assert "Review &lt;required&gt;." in content
    assert "<script" not in content
