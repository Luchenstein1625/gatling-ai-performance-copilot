from performance_decision_engine.infrastructure.label_audit import (
    APPLIES,
    NOT_APPLIES,
    audit_record,
    build_label_audit,
)


def _row(**updates: str) -> dict[str, str]:
    row = {
        "Build_Id": "build-1",
        "Performance": "1",
        "Estado": "success",
        "errorCount": "0",
        "successCount": "100",
        "p95": "1800",
        "rps": "10.5",
    }
    row.update(updates)
    return row


def test_complete_success_is_applies() -> None:
    result = audit_record(_row())
    assert result["binary_label"] == APPLIES
    assert result["primary_cause"] == "applies_complete"


def test_performance_zero_is_not_executed_not_failure() -> None:
    result = audit_record(
        _row(Performance="0", Estado="", errorCount="", successCount="", p95="", rps="")
    )
    assert result["binary_label"] == NOT_APPLIES
    assert result["primary_cause"] == "not_applies_not_executed"
    assert "execution_error" not in result["flags"]


def test_missing_result_is_incomplete_evidence() -> None:
    result = audit_record(_row(p95=""))
    assert result["binary_label"] == NOT_APPLIES
    assert result["primary_cause"] == "not_applies_incomplete_evidence"
    assert result["missing_label_fields"] == "p95"


def test_executed_row_with_errors_is_execution_error() -> None:
    result = audit_record(_row(errorCount="3"))
    assert result["binary_label"] == NOT_APPLIES
    assert result["primary_cause"] == "not_applies_execution_error"


def test_rps_missing_is_visible_even_when_legacy_label_applies() -> None:
    result = audit_record(_row(rps=""))
    assert result["binary_label"] == APPLIES
    assert result["primary_cause"] == "applies_incomplete_analysis_evidence"


def test_summary_counts_rows_and_distinct_builds() -> None:
    rows = [
        _row(Build_Id="a"),
        _row(Build_Id="a", errorCount="1"),
        _row(Build_Id="b", Performance="0"),
    ]
    report = build_label_audit(rows)
    assert report["usable_rows"] == 3
    assert report["distinct_builds"] == 2
    assert sum(item["rows"] for item in report["cause_distribution"]) == 3

