from pathlib import Path

import pytest

from performance_decision_engine.infrastructure.batch_execution_discovery import (
    BatchExecutionDiscovery,
)


def test_discovers_executions_with_shared_parameters(tmp_path: Path) -> None:
    source = tmp_path / "historical"
    source.mkdir()
    shared_parameters = source / "parametricConfigurationValues.yaml"
    shared_parameters.write_text("values: {}", encoding="utf-8")

    for name in ("run-a", "run-b"):
        execution = source / name
        execution.mkdir()
        (execution / "performance.yaml").write_text("load: {}", encoding="utf-8")
        (execution / "global_stats.json").write_text("{}", encoding="utf-8")
        (execution / "assertions.json").write_text("{}", encoding="utf-8")

    discovered = BatchExecutionDiscovery().discover(source)

    assert [item.execution_id for item in discovered] == ["run-a", "run-b"]
    assert all(item.parameters == shared_parameters for item in discovered)
    assert all(item.assertions is not None for item in discovered)


def test_rejects_source_without_results(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No global_stats.json"):
        BatchExecutionDiscovery().discover(tmp_path)


def test_discovers_sibling_execution_files(tmp_path: Path) -> None:
    source = tmp_path / "historical"
    execution = source / "service-a" / "20250206"
    results_directory = execution / "Gatling" / "js"
    configuration_directory = execution / "configuration"

    results_directory.mkdir(parents=True)
    configuration_directory.mkdir(parents=True)

    shared_parameters = source / "parametricConfigurationValues.yaml"
    shared_parameters.write_text("values: {}", encoding="utf-8")
    performance = configuration_directory / "performance.yaml"
    performance.write_text("load: {}", encoding="utf-8")
    assertions = execution / "Gatling" / "assertions.json"
    assertions.write_text("{}", encoding="utf-8")
    results = results_directory / "global_stats.json"
    results.write_text("{}", encoding="utf-8")

    discovered = BatchExecutionDiscovery().discover(source)

    assert len(discovered) == 1
    assert discovered[0].performance == performance
    assert discovered[0].assertions == assertions
    assert discovered[0].parameters == shared_parameters
