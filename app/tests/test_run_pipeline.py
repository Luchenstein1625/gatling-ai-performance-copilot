from pathlib import Path

from performance_decision_engine.application.use_cases.run_pipeline import RunPipeline
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


def _execution() -> NormalizedExecution:
    return NormalizedExecution(
        configuration=PerformanceConfiguration(
            load_type="sequence",
            endpoints=[
                EndpointConfiguration(
                    name="example",
                    feature_reference="classpath:example.feature",
                    enabled=True,
                    triplet=ResolvedTriplet(
                        concurrency_level="medium",
                        concurrency_value=20,
                        iterations_level="medium",
                        iterations_value=40,
                        response_time_level="medium",
                        response_time_ms=2000,
                    ),
                )
            ],
        ),
        global_metrics=ExecutionMetrics(
            total_requests=10,
            successful_requests=10,
            failed_requests=0,
            error_rate_percent=0,
            p95_response_time_ms=500,
        ),
        warnings=[],
    )


class FakeNormalization:
    def execute(
        self,
        performance_path: Path,
        parameters_path: Path,
        results_path: Path,
        assertions_path: Path | None = None,
    ) -> NormalizedExecution:
        return _execution()


class FakeRecommendation:
    def execute(self, execution: NormalizedExecution) -> Recommendation:
        return Recommendation(
            action="maintain",
            explanation="Compliant execution.",
            evidence={"decision_trace": []},
        )


class FakeDataset:
    fieldnames = ("schema_version", "recommendation_action")

    def execute(
        self,
        execution: NormalizedExecution,
        recommendation: Recommendation,
    ) -> dict[str, str | int | float | bool | None]:
        return {
            "schema_version": "1",
            "recommendation_action": recommendation.action,
        }


def test_integrates_existing_use_cases() -> None:
    result = RunPipeline(
        normalization=FakeNormalization(),
        recommendation=FakeRecommendation(),
        dataset=FakeDataset(),
    ).execute(
        Path("performance.yaml"),
        Path("parameters.yaml"),
        Path("global_stats.json"),
    )

    assert result.execution.global_metrics.total_requests == 10
    assert result.recommendation.action == "maintain"
    assert result.dataset_row["recommendation_action"] == "maintain"
    assert result.dataset_fieldnames == (
        "schema_version",
        "recommendation_action",
    )
