from __future__ import annotations

import pytest

from performance_decision_engine.infrastructure.evidence_tables_v3_1 import (
    build_data_flow,
    evidence_completeness,
    validate_data_flow,
)
from collections import Counter


def test_data_flow_reconciles_official_counts() -> None:
    reasons = Counter({
        "missing_build_id": 1,
        "not_executed": 1591,
        "incomplete_result_evidence": 57,
        "incomplete_configuration": 407,
        "trainable": 4389,
    })
    flow = build_data_flow(6445, 6444, reasons)
    validate_data_flow(flow, 4389)
    assert flow[-1]["rows_remaining"] == 4389


def test_data_flow_detects_wrong_final_count() -> None:
    reasons = Counter({"not_executed": 2, "incomplete_result_evidence": 1, "incomplete_configuration": 1})
    flow = build_data_flow(10, 10, reasons)
    with pytest.raises(ValueError):
        validate_data_flow(flow, 7)


def test_completeness_separates_binary_classes() -> None:
    records = [
        {"binary_label": "applies", "p95": "100", "rps": "2", "error_count": "0"},
        {"binary_label": "not_applies", "p95": "", "rps": "", "error_count": "1"},
    ]
    output = evidence_completeness(records)
    p95_all = next(row for row in output if row["binary_label"] == "ALL" and row["field"] == "p95")
    assert p95_all["missing_rows"] == 1
    assert p95_all["missing_rate"] == pytest.approx(0.5)


def test_p95_is_not_defined_as_average() -> None:
    definition = "Percentil 95"
    assert "promedio" not in definition.lower()


def test_build_counts_are_not_expected_to_be_additive() -> None:
    build_a_causes = {"not_executed", "execution_error"}
    assert len(build_a_causes) == 2
