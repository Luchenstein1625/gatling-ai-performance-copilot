from __future__ import annotations

import csv
from pathlib import Path

from performance_decision_engine.infrastructure.release_audit_v3_1 import (
    EXPECTED_CHECKS,
    b2_artifacts,
    sha256_file,
    verify_frozen_hashes,
)


def test_expected_release_has_26_checks() -> None:
    assert EXPECTED_CHECKS == 26


def test_sha256_is_reproducible(tmp_path: Path) -> None:
    path = tmp_path / "artifact.txt"
    path.write_text("unchanged", encoding="utf-8")
    assert sha256_file(path) == sha256_file(path)


def test_frozen_hashes_detect_unchanged_file(tmp_path: Path) -> None:
    results = tmp_path / "Resultados"
    results.mkdir()
    artifact = results / "artifact.json"
    artifact.write_text("{}", encoding="utf-8")
    inventory = tmp_path / "hashes.csv"
    with inventory.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=["relative_path", "sha256"])
        writer.writeheader()
        writer.writerow({"relative_path": "artifact.json", "sha256": sha256_file(artifact)})
    rows = verify_frozen_hashes(results, inventory)
    assert rows[0]["unchanged"] is True


def test_frozen_hashes_detect_mutation(tmp_path: Path) -> None:
    results = tmp_path / "Resultados"
    results.mkdir()
    artifact = results / "artifact.json"
    artifact.write_text("changed", encoding="utf-8")
    inventory = tmp_path / "hashes.csv"
    with inventory.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=["relative_path", "sha256"])
        writer.writeheader()
        writer.writerow({"relative_path": "artifact.json", "sha256": "incorrect"})
    rows = verify_frozen_hashes(results, inventory)
    assert rows[0]["unchanged"] is False


def test_b2_artifact_detection(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    results = repository / "Resultados"
    (repository / "app").mkdir(parents=True)
    (results / "v3_1").mkdir(parents=True)
    assert b2_artifacts(repository, results) == []
    unwanted = repository / "app" / "human_baseline_v3_1.py"
    unwanted.write_text("", encoding="utf-8")
    assert any("human_baseline" in item for item in b2_artifacts(repository, results))
