from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_FEATURES = ["Concurrency", "Iterations", "ResponseTime"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


class ReleaseAuditV3:
    REQUIRED_REPORTS = {
        "protocol": Path("protocol_v3/frozen_protocol_v3.json"),
        "selection": Path("model_selection_v3/model_selection_dev_v3.json"),
        "calibration": Path("calibration_v3/calibration_decision_v3.json"),
        "threshold": Path("fine_threshold_v3/fine_threshold_decision_v3.json"),
        "final_test": Path("final_test_v3/final_test_evaluation_v3.json"),
        "recommender": Path("recommender_v3/recommender_v3.json"),
        "economics": Path("economics_v3/economic_evaluation_v3.json"),
    }

    def __init__(self) -> None:
        self.checks: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, evidence: str) -> None:
        self.checks.append(
            {"check": name, "status": "PASS" if condition else "FAIL", "evidence": evidence}
        )

    @staticmethod
    def _git(repository: Path, *args: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", *args], cwd=repository, check=True, capture_output=True,
                text=True, encoding="utf-8", errors="replace"
            )
            return result.stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    def _verify_assignments(self, path: Path, protocol: dict[str, Any]) -> None:
        if not path.is_file():
            self.check("partition assignment file exists", False, str(path))
            return
        by_partition: dict[str, set[str]] = {"train": set(), "dev": set(), "test": set()}
        duplicates: set[str] = set()
        seen: set[str] = set()
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                key = row["build_id_sha256"]
                partition = row["partition"]
                if key in seen:
                    duplicates.add(key)
                seen.add(key)
                by_partition.setdefault(partition, set()).add(key)
        expected = {
            name: int(protocol["partitions"][name]["builds"])
            for name in ("train", "dev", "test")
        }
        observed = {name: len(by_partition[name]) for name in expected}
        self.check("zero Build_Id overlap", not duplicates, f"duplicate hashes={len(duplicates)}")
        self.check("partition build counts", observed == expected, f"observed={observed}; expected={expected}")

    def _inventory(self, results_root: Path, output_dir: Path) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        output_resolved = output_dir.resolve()
        for path in sorted(results_root.rglob("*")):
            if not path.is_file() or output_resolved in path.resolve().parents:
                continue
            rows.append({
                "path": path.relative_to(results_root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
        return rows

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        fields = list(rows[0]) if rows else ["path", "size_bytes", "sha256"]
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def run(
        self,
        repository: Path,
        results_root: Path,
        source: Path,
        output_dir: Path,
        run_test_suite: bool = False,
    ) -> dict[str, Any]:
        repository = repository.resolve()
        results_root = results_root.resolve()
        output_dir = output_dir.resolve()
        reports = {
            name: read_json(results_root / relative)
            for name, relative in self.REQUIRED_REPORTS.items()
        }
        protocol = reports["protocol"]
        selection = reports["selection"]
        calibration = reports["calibration"]
        threshold = reports["threshold"]
        final_test = reports["final_test"]
        recommender = reports["recommender"]
        economics = reports["economics"]

        self.check("model selection kept test locked", selection.get("test_status") == "LOCKED_NOT_EVALUATED", str(selection.get("test_status")))
        self.check("calibration kept test locked", calibration.get("test_status") == "LOCKED_NOT_EVALUATED", str(calibration.get("test_status")))
        self.check("threshold analysis kept test locked", threshold.get("test_status") == "LOCKED_NOT_EVALUATED", str(threshold.get("test_status")))
        self.check("independent test opened once", final_test.get("test_status") == "OPENED_ONCE_EVALUATION_COMPLETE", str(final_test.get("test_status")))
        self.check("no selection after test", final_test.get("selection_changes_after_test") is False, str(final_test.get("selection_changes_after_test")))
        expected_hash = protocol["test_lock"]["test_build_set_sha256"]
        self.check("test Build_Id hash preserved", final_test.get("test_build_set_sha256") == expected_hash, f"expected={expected_hash}; final={final_test.get('test_build_set_sha256')}")
        self.check("final feature contract", final_test.get("final_model", {}).get("features") == EXPECTED_FEATURES, str(final_test.get("final_model", {}).get("features")))
        self.check("human review policy", final_test.get("operational_policy", {}).get("name") == "review_all_with_ranking_assistance" and final_test.get("operational_policy", {}).get("automatic_release_enabled") is False, str(final_test.get("operational_policy")))
        self.check("fine threshold policy consistent", threshold.get("recommended_policy") == "review_all_with_ranking_assistance", str(threshold.get("recommended_policy")))
        self.check("recommender did not access test", recommender.get("test_status") == "NOT_ACCESSED_RECOMMENDER_TRAIN_DEV_ONLY", str(recommender.get("test_status")))
        self.check("recommender guardrail passed", recommender.get("gate_status") == "PASSED_WITH_CONSERVATIVE_STABILITY_FILTER", str(recommender.get("gate_status")))
        self.check("economics remains conditional", economics.get("evidence_status") == "conditional_projection_not_realized_saving", str(economics.get("evidence_status")))

        self._verify_assignments(results_root / "protocol_v3/build_partition_hashes_v3.csv", protocol)
        self.check("source dataset exists", source.is_file(), str(source))
        if source.is_file():
            observed_source_hash = sha256_file(source)
            expected_source_hash = protocol.get("source_sha256")
            self.check("source dataset hash", observed_source_hash == expected_source_hash, f"observed={observed_source_hash}; expected={expected_source_hash}")
        else:
            observed_source_hash = None

        test_result: dict[str, Any] = {"executed": False, "return_code": None}
        if run_test_suite:
            completed = subprocess.run(
                [sys.executable, "-m", "pytest", "tests", "-q"],
                cwd=repository / "app", capture_output=True, text=True,
                encoding="utf-8", errors="replace"
            )
            test_result = {
                "executed": True,
                "return_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
            self.check("complete pytest suite", completed.returncode == 0, f"return_code={completed.returncode}")

        failed = [row for row in self.checks if row["status"] == "FAIL"]
        metrics = final_test["ranking_test_metrics"]
        official = {
            "dataset": {
                "eligible_rows": sum(int(protocol["partitions"][p]["rows"]) for p in ("train", "dev", "test")),
                "features": EXPECTED_FEATURES,
                "source_sha256": protocol.get("source_sha256"),
            },
            "independent_test": {
                "rows": final_test["rows"]["test"],
                "builds": final_test["rows"]["test_builds"],
                **metrics,
                "grouped_bootstrap_ic95": final_test["ranking_grouped_bootstrap_ic95"],
            },
            "operational_policy": final_test["operational_policy"],
            "recommender": {
                "gate_status": recommender["gate_status"],
                "published_actions": recommender["action_distribution_published"],
                "experimental_upgrade_candidates": recommender["experimental_upgrade_candidates"],
                "publishable_upgrades": recommender["publishable_upgrades"],
            },
            "economics": {
                "evidence_status": economics["evidence_status"],
                "annual_budget_clp": economics["budgetary_inputs"]["annual_budget_clp"],
                "annual_operating_cost_clp": economics["operating_cost_inputs"]["annual_operating_cost_clp"],
                "break_even_coverage_times_reduction": economics["break_even"]["minimum_coverage_times_effort_reduction"],
                "scenarios": economics["effort_scenarios"],
            },
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        inventory = self._inventory(results_root, output_dir)
        self._write_csv(output_dir / "artifact_inventory_v3.csv", inventory)
        (output_dir / "official_metrics_v3.json").write_text(json.dumps(official, indent=2, ensure_ascii=False), encoding="utf-8")
        reproducibility = {
            "schema_version": "3.0",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "release_status": "READY_FOR_DOCUMENTATION" if not failed else "BLOCKED",
            "checks_passed": len(self.checks) - len(failed),
            "checks_failed": len(failed),
            "checks": self.checks,
            "test_suite": test_result,
        }
        (output_dir / "reproducibility_check_v3.json").write_text(json.dumps(reproducibility, indent=2, ensure_ascii=False), encoding="utf-8")
        manifest = {
            "schema_version": "3.0",
            "release_status": reproducibility["release_status"],
            "generated_at_utc": reproducibility["generated_at_utc"],
            "repository": {
                "commit": self._git(repository, "rev-parse", "HEAD"),
                "branch": self._git(repository, "branch", "--show-current"),
                "dirty_files": (self._git(repository, "status", "--porcelain") or "").splitlines(),
            },
            "runtime": {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "numpy": package_version("numpy"),
                "pandas": package_version("pandas"),
                "scikit_learn": package_version("scikit-learn"),
                "joblib": package_version("joblib"),
            },
            "source": {"path": str(source), "sha256": observed_source_hash},
            "test_build_set_sha256": expected_hash,
            "artifact_count": len(inventory),
            "official_metrics_file": "official_metrics_v3.json",
            "reproducibility_file": "reproducibility_check_v3.json",
            "inventory_file": "artifact_inventory_v3.csv",
        }
        (output_dir / "release_manifest_v3.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"manifest": manifest, "reproducibility": reproducibility, "official_metrics": official}
