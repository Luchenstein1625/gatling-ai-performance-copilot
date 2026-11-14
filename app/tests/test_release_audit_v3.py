from pathlib import Path

from performance_decision_engine.infrastructure.release_audit_v3 import sha256_file


def test_sha256_file_is_reproducible(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("capstone-v3", encoding="utf-8")
    assert sha256_file(artifact) == sha256_file(artifact)
    assert len(sha256_file(artifact)) == 64


def test_expected_feature_contract() -> None:
    from performance_decision_engine.infrastructure.release_audit_v3 import EXPECTED_FEATURES
    assert EXPECTED_FEATURES == ["Concurrency", "Iterations", "ResponseTime"]


def test_missing_json_fails_explicitly(tmp_path: Path) -> None:
    from performance_decision_engine.infrastructure.release_audit_v3 import read_json
    try:
        read_json(tmp_path / "missing.json")
    except FileNotFoundError as error:
        assert "Required artifact not found" in str(error)
    else:
        raise AssertionError("Missing mandatory artifact must fail")
