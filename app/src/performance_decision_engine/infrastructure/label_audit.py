"""Audit the operational causes hidden inside the historical binary label.

The current project intentionally preserves its historical label policy.  This
module does not relabel the model dataset; it makes the causes auditable before
the final-defense protocol is frozen.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from performance_decision_engine.infrastructure.historical_binary_evaluator import (
    GROUP_COLUMN,
    HistoricalBinaryEvaluator,
)

APPLIES = "applies"
NOT_APPLIES = "not_applies"

# These fields are required to interpret an executed performance test.  RPS is
# included for the audit even though the legacy binary label does not use it.
ANALYSIS_EVIDENCE_FIELDS = ("p95", "rps", "errorCount")
LABEL_EVIDENCE_FIELDS = ("Estado", "errorCount", "successCount", "p95")


def _missing_fields(row: dict[str, str], fields: tuple[str, ...]) -> list[str]:
    return [name for name in fields if not str(row.get(name, "")).strip()]


def audit_record(row: dict[str, str]) -> dict[str, object]:
    """Return the legacy label and the evidence explaining it.

    ``Performance == 0`` is reported as ``not_executed`` rather than as a
    technical failure.  This matches the operational meaning supplied by the
    project team and prevents the final-defense analysis from claiming that an
    execution failed when it never ran.
    """

    policy_label = HistoricalBinaryEvaluator._label(row)
    binary_label = NOT_APPLIES if policy_label == "review" else APPLIES

    performance = str(row.get("Performance", "")).strip()
    status = str(row.get("Estado", "")).strip().lower()
    errors = HistoricalBinaryEvaluator._number(row.get("errorCount"))
    successes = HistoricalBinaryEvaluator._number(row.get("successCount"))

    missing_analysis = _missing_fields(row, ANALYSIS_EVIDENCE_FIELDS)
    missing_label = _missing_fields(row, LABEL_EVIDENCE_FIELDS)
    not_executed = performance == "0"
    execution_error = bool(
        performance == "1"
        and (
            (status not in {"", "success"})
            or (errors is not None and errors > 0)
            or (successes is not None and successes <= 0)
        )
    )
    incomplete_evidence = bool(missing_label)
    incomplete_analysis_evidence = bool(missing_analysis)

    if binary_label == APPLIES:
        primary_cause = (
            "applies_incomplete_analysis_evidence"
            if incomplete_analysis_evidence
            else "applies_complete"
        )
    elif not_executed:
        primary_cause = "not_applies_not_executed"
    elif execution_error and incomplete_evidence:
        primary_cause = "not_applies_multiple_causes"
    elif execution_error:
        primary_cause = "not_applies_execution_error"
    elif incomplete_evidence:
        primary_cause = "not_applies_incomplete_evidence"
    else:
        primary_cause = "not_applies_other_policy"

    flags = [
        name
        for name, enabled in (
            ("not_executed", not_executed),
            ("execution_error", execution_error),
            ("incomplete_label_evidence", incomplete_evidence),
            ("incomplete_analysis_evidence", incomplete_analysis_evidence),
        )
        if enabled
    ]

    return {
        "build_id": row.get(GROUP_COLUMN, ""),
        "binary_label": binary_label,
        "policy_label": policy_label,
        "primary_cause": primary_cause,
        "flags": "|".join(flags),
        "missing_label_fields": "|".join(missing_label),
        "missing_analysis_fields": "|".join(missing_analysis),
        "performance": performance,
        "estado": row.get("Estado", ""),
        "error_count": row.get("errorCount", ""),
        "success_count": row.get("successCount", ""),
        "p95": row.get("p95", ""),
        "rps": row.get("rps", ""),
    }


def build_label_audit(rows: list[dict[str, str]]) -> dict[str, object]:
    """Audit usable rows and summarize causes by rows and Build_Id."""

    usable = [row for row in rows if HistoricalBinaryEvaluator._has_required_result(row)]
    records = [audit_record(row) for row in usable]
    row_counts = Counter(str(record["primary_cause"]) for record in records)
    builds_by_cause: defaultdict[str, set[str]] = defaultdict(set)
    for record in records:
        build_id = str(record["build_id"])
        if build_id:
            builds_by_cause[str(record["primary_cause"])].add(build_id)

    total = len(records)
    distribution = [
        {
            "cause": cause,
            "rows": count,
            "builds": len(builds_by_cause[cause]),
            "percentage_rows": count / total if total else 0.0,
        }
        for cause, count in sorted(row_counts.items())
    ]
    binary_counts = Counter(str(record["binary_label"]) for record in records)
    return {
        "source_rows": len(rows),
        "usable_rows": total,
        "discarded_rows": len(rows) - total,
        "distinct_builds": len({str(record["build_id"]) for record in records}),
        "binary_distribution": dict(sorted(binary_counts.items())),
        "cause_distribution": distribution,
        "records": records,
        "interpretation": {
            "not_executed": "Performance=0 means the test did not execute; it is not a measured failure.",
            "incomplete_evidence": "Required result evidence is missing; do not recommend load changes.",
            "execution_error": "The execution ran and contains failed status, errors or no successes.",
            "recommendation_guardrail": (
                "Parameter recommendations require complete evidence; otherwise the system abstains."
            ),
        },
    }


def write_label_audit(report: dict[str, object], output_dir: Path) -> None:
    """Write detailed, summarized and machine-readable audit artifacts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    records = report["records"]
    distribution = report["cause_distribution"]
    if not isinstance(records, list) or not isinstance(distribution, list):
        raise ValueError("Invalid label audit report.")

    if records:
        with (output_dir / "label_cause_records.csv").open(
            "w", encoding="utf-8", newline=""
        ) as target:
            writer = csv.DictWriter(target, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)

    if distribution:
        with (output_dir / "label_cause_distribution.csv").open(
            "w", encoding="utf-8", newline=""
        ) as target:
            writer = csv.DictWriter(target, fieldnames=list(distribution[0]))
            writer.writeheader()
            writer.writerows(distribution)

    serializable = {key: value for key, value in report.items() if key != "records"}
    (output_dir / "label_audit.json").write_text(
        json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8"
    )

