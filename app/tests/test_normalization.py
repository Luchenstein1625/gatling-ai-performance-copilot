from pathlib import Path

from performance_decision_engine.adapters.execution_builder import build_execution_summary


def test_build_execution_summary() -> None:
    summary = build_execution_summary(
        performance_path=Path("examples/input/performance.yaml"),
        parameters_path=Path("examples/input/parametricConfigurationValues.yaml"),
        gatling_path=Path("examples/input/global_stats.json"),
    )

    assert summary.load_type == "sequence"
    assert len(summary.features) == 2
    assert summary.features[0].triplet.concurrency_value == 20
    assert summary.features[1].triplet.response_time_ms == 15000
    assert summary.gatling_global.total_requests == 2801
    assert summary.gatling_global.failed_requests == 0
