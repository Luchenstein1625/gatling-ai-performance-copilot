from pathlib import Path

from performance_decision_engine.infrastructure.governance_v3_1 import (
    canonical_manifest_hash,
    preregistered_addendum,
    sha256_file,
)


def test_hash_is_reproducible(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    artifact.write_text('{"status":"frozen"}', encoding="utf-8")
    assert sha256_file(artifact) == sha256_file(artifact)


def test_manifest_hash_does_not_depend_on_dict_key_order() -> None:
    first = [{"path": "a", "sha256": "1"}]
    second = [{"sha256": "1", "path": "a"}]
    assert canonical_manifest_hash(first) == canonical_manifest_hash(second)


def test_addendum_prohibits_test_selection() -> None:
    addendum = preregistered_addendum("source", "test")
    assert addendum["integrity"]["no_model_or_threshold_selection_using_test"] is True
    assert addendum["status"] == "PRE_SPECIFIED_BEFORE_DIAGNOSTIC_EXECUTION"
    assert any("change model" in rule for rule in addendum["prohibited_actions"])


def test_a3_keeps_stability_guardrail() -> None:
    addendum = preregistered_addendum("source", "test")
    a3 = next(item for item in addendum["registered_analyses"] if item["id"] == "A3")
    assert a3["fixed_guardrails"]["minimum_action_stability"] == 0.80

