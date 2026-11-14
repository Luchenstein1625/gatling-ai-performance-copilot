import pytest

from performance_decision_engine.infrastructure.configuration_training_v2 import (
    APPLIES,
    NOT_APPLIES,
    ConfigurationTrainingV2,
    eligibility_reason,
    feature_row,
    technical_label,
)


def row(**updates: str) -> dict[str, str]:
    base = {
        "Build_Id": "build-1",
        "Performance": "1",
        "Estado": "success",
        "errorCount": "0",
        "successCount": "10",
        "Concurrency": "medium",
        "Iterations": "medium",
        "ResponseTime": "low",
    }
    base.update(updates)
    return base


def test_performance_zero_abstains() -> None:
    assert eligibility_reason(row(Performance="0")) == "not_executed"


def test_complete_success_applies() -> None:
    assert eligibility_reason(row()) == "trainable"
    assert technical_label(row()) == APPLIES


def test_executed_error_is_not_applies() -> None:
    assert technical_label(row(errorCount="2", Estado="failed")) == NOT_APPLIES


def test_incomplete_result_abstains() -> None:
    assert eligibility_reason(row(errorCount="")) == "incomplete_result_evidence"


def test_only_three_configuration_features() -> None:
    assert feature_row(row()) == ["medium", "medium", "low"]


def test_label_rejects_non_trainable_row() -> None:
    with pytest.raises(ValueError):
        technical_label(row(Performance="0"))


def test_group_split_has_no_overlap() -> None:
    labels = [APPLIES, NOT_APPLIES] * 10
    groups = [f"build-{index // 2}" for index in range(20)]
    train, test = ConfigurationTrainingV2._split(labels, groups)
    assert {groups[i] for i in train}.isdisjoint({groups[i] for i in test})
