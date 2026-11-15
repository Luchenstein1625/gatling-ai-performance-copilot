from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


IMMUTABLE_RESULT_DIRS = (
    "protocol_v3",
    "model_selection_v3",
    "calibration_v3",
    "fine_threshold_v3",
    "final_test_v3",
    "recommender_v3",
    "economics_v3",
    "release_v3",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_manifest_hash(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def git_value(repository: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args], cwd=repository, check=True, capture_output=True,
            text=True, encoding="utf-8", errors="replace"
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def inventory_immutable_results(results_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for directory_name in IMMUTABLE_RESULT_DIRS:
        directory = results_root / directory_name
        if not directory.is_dir():
            missing.append(directory_name)
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                rows.append({
                    "result_set": directory_name,
                    "relative_path": path.relative_to(results_root).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                })
    return rows, missing


def preregistered_addendum(source_hash: str | None, test_hash: str | None) -> dict[str, Any]:
    return {
        "schema_version": "3.1",
        "status": "PRE_SPECIFIED_BEFORE_DIAGNOSTIC_EXECUTION",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "integrity": {
            "source_sha256": source_hash,
            "test_build_set_sha256": test_hash,
            "official_final_test_is_immutable": True,
            "no_model_or_threshold_selection_using_test": True,
        },
        "registered_analyses": [
            {
                "id": "A2",
                "name": "calibration audit",
                "selection_data": "train and dev only",
                "test_use": "descriptive raw versus frozen calibrated probabilities only",
                "metrics": ["ROC-AUC", "Brier", "log-loss", "ECE"],
                "decision_effect": "none; official final model and test remain unchanged",
            },
            {
                "id": "A3",
                "name": "recommender order and monotonicity audit",
                "selection_data": "train and dev only",
                "test_use": "none",
                "fixed_guardrails": {"minimum_action_stability": 0.80, "bootstrap_repetitions": 2000},
                "decision_effect": "publish only actions passing existing fixed guardrails",
            },
            {
                "id": "A4",
                "name": "claims uncertainty derivation",
                "selection_data": "none",
                "test_use": "derive additional cases from existing frozen bootstrap repetitions",
                "decision_effect": "language classification only",
            },
            {
                "id": "A5",
                "name": "historical split overlap audit",
                "selection_data": "none",
                "test_use": "descriptive sensitivity on test builds not present in previous exploratory holdouts, if any",
                "decision_effect": "limitation statement only; no retuning",
            },
            {
                "id": "A6",
                "name": "final model explainability",
                "selection_data": "dev",
                "test_use": "none",
                "metrics": ["grouped permutation ROC-AUC decrease", "PDP", "ICE"],
                "decision_effect": "explanation only",
            },
            {
                "id": "A1",
                "name": "evidence-anchored economics",
                "selection_data": "existing frozen test bootstrap only",
                "test_use": "no new model evaluation",
                "fixed_k_values": [0.5, 1.0, 2.0],
                "benefit_floor": 0.0,
                "decision_effect": "conditional projection only",
            },
        ],
        "prohibited_actions": [
            "replace or overwrite any Resultados/v3 artifact",
            "change model, calibration or threshold after observing test",
            "relax the 80 percent recommendation stability guardrail",
            "claim automatic release unless risk upper 95 percent is at most 5 percent",
            "describe projected economic benefit as realized saving",
        ],
    }


def initial_decisions() -> list[dict[str, str]]:
    now = datetime.now(timezone.utc).isoformat()
    decisions = [
        ("D-001", "Preserve v3 artifacts", "All corrections are written under Resultados/v3_1; v3 remains immutable."),
        ("D-002", "Do not select using test", "Any additional test calculation is descriptive and cannot alter the frozen model."),
        ("D-003", "Keep guardrails", "Stability 80%, release-risk upper bound 5%, and superiority interval excluding zero remain fixed."),
        ("D-004", "Audit calibration before reporting", "Compare identical raw scores, cross-fit calibration by Build_Id, and report ties explicitly."),
        ("D-005", "Audit ResponseTime direction", "Concurrency and Iterations increase with load; lower ResponseTime milliseconds are stricter."),
        ("D-006", "Economics is conditional", "Break-even and evidence-anchored scenarios precede any conditioned Monte Carlo result."),
        ("D-007", "Negative results remain valid", "No result is removed or guardrail changed to obtain a positive conclusion."),
    ]
    return [
        {"decision_id": decision_id, "registered_at_utc": now, "status": "PRE_SPECIFIED", "title": title, "decision": decision}
        for decision_id, title, decision in decisions
    ]


class GovernanceV31:
    def run(self, repository: Path, results_root: Path, source: Path, output_dir: Path) -> dict[str, Any]:
        repository = repository.resolve()
        results_root = results_root.resolve()
        source = source.resolve()
        output_dir = output_dir.resolve()
        inventory, missing = inventory_immutable_results(results_root)
        if missing:
            raise FileNotFoundError(f"Missing immutable result directories: {', '.join(missing)}")
        if not source.is_file():
            raise FileNotFoundError(f"Dataset not found: {source}")

        protocol_path = results_root / "protocol_v3/frozen_protocol_v3.json"
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        source_hash = sha256_file(source)
        if source_hash != protocol.get("source_sha256"):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        test_hash = protocol["test_lock"]["test_build_set_sha256"]
        root_hash = canonical_manifest_hash(inventory)

        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "baseline_v3_hashes.csv").open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=["result_set", "relative_path", "size_bytes", "sha256"])
            writer.writeheader()
            writer.writerows(inventory)
        decisions = initial_decisions()
        with (output_dir / "decision_register_v3_1.csv").open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(decisions[0]))
            writer.writeheader()
            writer.writerows(decisions)
        addendum = preregistered_addendum(source_hash, test_hash)
        (output_dir / "protocol_v3_1_addendum.json").write_text(
            json.dumps(addendum, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        report = {
            "schema_version": "3.1",
            "gate": "GOVERNANCE_BASELINE_FROZEN",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "repository": {
                "branch": git_value(repository, "branch", "--show-current"),
                "commit": git_value(repository, "rev-parse", "HEAD"),
                "dirty_files": (git_value(repository, "status", "--porcelain") or "").splitlines(),
            },
            "source_sha256": source_hash,
            "test_build_set_sha256": test_hash,
            "immutable_result_sets": list(IMMUTABLE_RESULT_DIRS),
            "files_frozen": len(inventory),
            "baseline_manifest_sha256": root_hash,
            "addendum_status": addendum["status"],
            "registered_decisions": len(decisions),
            "next_step": "Run A2 calibration audit and A3 order-encoding audit without changing v3 artifacts.",
        }
        (output_dir / "governance_baseline_v3_1.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report

