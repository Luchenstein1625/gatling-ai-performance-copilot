from pathlib import Path

import pytest

from performance_decision_engine.infrastructure.claims_v3_1 import (
    additional_cases,
    audit_language,
    evidence_level,
    percentile_summary,
)


def test_additional_cases_uses_top_queue_size() -> None:
    assert additional_cases(264, 0.560606, 0.427273) == pytest.approx(35.2, abs=0.1)


def test_interval_including_null_is_not_conclusive() -> None:
    assert evidence_level(0.259, 0.30, 0.473) == "No concluyente"
    assert evidence_level(0.536, 0.50, 0.764) == "Demostrado"


def test_percentile_summary_requires_values() -> None:
    summary = percentile_summary([-13, 35, 74])
    assert summary["lower_95"] < summary["upper_95"]


def test_language_audit_detects_overclaim(tmp_path: Path) -> None:
    document = tmp_path / "README.md"
    document.write_text("El test confirma una señal útil y entrega valor demostrado.", encoding="utf-8")
    findings = audit_language([document])
    assert {row["rule_id"] for row in findings} == {"L-001", "L-002"}


def test_conditioned_projection_wording_is_allowed(tmp_path: Path) -> None:
    document = tmp_path / "README.md"
    document.write_text("La proyección condicionada supera el equilibrio si cobertura por reducción excede 4,02%.", encoding="utf-8")
    assert audit_language([document]) == []

