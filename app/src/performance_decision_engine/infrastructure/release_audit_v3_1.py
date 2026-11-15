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
EXPECTED_CHECKS = 26


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


def verify_frozen_hashes(results_root: Path, baseline_csv: Path) -> list[dict[str, Any]]:
    if not baseline_csv.is_file():
        raise FileNotFoundError(f"Frozen v3 hash inventory not found: {baseline_csv}")
    output: list[dict[str, Any]] = []
    with baseline_csv.open("r", encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            path = results_root / row["relative_path"]
            exists = path.is_file()
            observed = sha256_file(path) if exists else ""
            expected = row["sha256"]
            output.append({
                "relative_path": row["relative_path"],
                "exists": exists,
                "expected_sha256": expected,
                "observed_sha256": observed,
                "unchanged": exists and observed == expected,
            })
    if not output:
        raise ValueError("Frozen v3 hash inventory is empty")
    return output


def b2_artifacts(repository: Path, results_root: Path) -> list[str]:
    patterns = ("human_baseline", "baseline_b2", "cuestionario_analista_b2", "instrucciones_b2")
    found: list[str] = []
    roots = (repository / "app", results_root / "v3_1", repository)
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            relative = path.relative_to(repository).as_posix() if repository in path.parents else str(path)
            if any(pattern in path.name.lower() or pattern in relative.lower() for pattern in patterns):
                found.append(relative)
    return sorted(set(found))


class ReleaseAuditV31:
    REPORTS = {
        "protocol": Path("protocol_v3/frozen_protocol_v3.json"),
        "selection": Path("model_selection_v3/model_selection_dev_v3.json"),
        "calibration": Path("calibration_v3/calibration_decision_v3.json"),
        "threshold": Path("fine_threshold_v3/fine_threshold_decision_v3.json"),
        "final_test": Path("final_test_v3/final_test_evaluation_v3.json"),
        "test_marker": Path("final_test_v3/test_opened_v3.json"),
        "recommender": Path("recommender_v3/recommender_v3.json"),
        "economics": Path("economics_v3/economic_evaluation_v3.json"),
        "governance": Path("v3_1/governance/governance_baseline_v3_1.json"),
        "calibration_audit": Path("v3_1/calibration_audit/audit_findings.json"),
        "recommender_audit": Path("v3_1/recommender_audit/recommender_audit_v3_1.json"),
        "confounding": Path("v3_1/recommender_confounding/recommender_confounding_audit_v3_1.json"),
        "claims": Path("v3_1/claims/claims_summary_v3_1.json"),
        "overlap": Path("v3_1/overlap_audit/overlap_audit_v3_1.json"),
        "explainability": Path("v3_1/explainability_final/final_model_explainability_v3.json"),
        "anchored_economics": Path("v3_1/economics_anchored/economics_anchored_v3_1.json"),
        "baselines": Path("v3_1/baselines/baselines_b0_b3_v3_1.json"),
        "evidence_tables": Path("v3_1/evidence_tables/evidence_tables_v3_1.json"),
    }

    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def check(self, number: int, name: str, condition: bool, evidence: str) -> None:
        self.checks.append({
            "number": number,
            "check": name,
            "status": "PASS" if condition else "FAIL",
            "evidence": evidence,
        })

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

    @staticmethod
    def _assignments(path: Path, protocol: dict[str, Any]) -> tuple[bool, bool, str]:
        if not path.is_file():
            return False, False, f"missing={path}"
        by_partition: dict[str, set[str]] = {"train": set(), "dev": set(), "test": set()}
        seen: set[str] = set()
        duplicates: set[str] = set()
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                key = row["build_id_sha256"]
                if key in seen:
                    duplicates.add(key)
                seen.add(key)
                by_partition[row["partition"]].add(key)
        observed = {name: len(by_partition[name]) for name in ("train", "dev", "test")}
        expected = {name: int(protocol["partitions"][name]["builds"]) for name in observed}
        return not duplicates, observed == expected, f"duplicates={len(duplicates)}; observed={observed}; expected={expected}"

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        fields = list(rows[0]) if rows else ["path"]
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _inventory(results_root: Path, output_dir: Path) -> list[dict[str, Any]]:
        output_resolved = output_dir.resolve()
        rows: list[dict[str, Any]] = []
        for path in sorted(results_root.rglob("*")):
            if not path.is_file() or output_resolved in path.resolve().parents:
                continue
            rows.append({
                "path": path.relative_to(results_root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
        return rows

    def run(
        self,
        repository: Path,
        results_root: Path,
        source: Path,
        output_dir: Path,
        run_test_suite: bool = True,
    ) -> dict[str, Any]:
        repository = repository.resolve()
        results_root = results_root.resolve()
        source = source.resolve()
        output_dir = output_dir.resolve()
        reports = {name: read_json(results_root / relative) for name, relative in self.REPORTS.items()}
        protocol = reports["protocol"]
        selection = reports["selection"]
        calibration = reports["calibration"]
        threshold = reports["threshold"]
        final_test = reports["final_test"]
        marker = reports["test_marker"]
        recommender = reports["recommender"]
        economics = reports["economics"]
        governance = reports["governance"]
        calibration_audit = reports["calibration_audit"]
        recommender_audit = reports["recommender_audit"]
        confounding = reports["confounding"]
        claims = reports["claims"]
        overlap = reports["overlap"]
        explainability = reports["explainability"]
        anchored = reports["anchored_economics"]
        baselines = reports["baselines"]
        evidence_tables = reports["evidence_tables"]

        expected_test_hash = protocol["test_lock"]["test_build_set_sha256"]
        self.check(1, "model selection kept test locked", selection.get("test_status") == "LOCKED_NOT_EVALUATED", str(selection.get("test_status")))
        self.check(2, "calibration kept test locked", calibration.get("test_status") == "LOCKED_NOT_EVALUATED", str(calibration.get("test_status")))
        self.check(3, "threshold analysis kept test locked", threshold.get("test_status") == "LOCKED_NOT_EVALUATED", str(threshold.get("test_status")))
        self.check(4, "independent test opened once", final_test.get("test_status") == "OPENED_ONCE_EVALUATION_COMPLETE" and marker.get("status") == "OPENED_ONCE_EVALUATION_COMPLETE", f"report={final_test.get('test_status')}; marker={marker.get('status')}")
        self.check(5, "no selection after test", final_test.get("selection_changes_after_test") is False, str(final_test.get("selection_changes_after_test")))
        self.check(6, "test Build_Id hash preserved", final_test.get("test_build_set_sha256") == expected_test_hash and marker.get("test_build_set_sha256") == expected_test_hash, expected_test_hash)
        self.check(7, "final feature contract", final_test.get("final_model", {}).get("features") == EXPECTED_FEATURES, str(final_test.get("final_model", {}).get("features")))
        policy = final_test.get("operational_policy", {})
        self.check(8, "human review policy", policy.get("name") == "review_all_with_ranking_assistance" and policy.get("automatic_release_enabled") is False, str(policy))
        self.check(9, "fine threshold policy consistent", threshold.get("recommended_policy") == "review_all_with_ranking_assistance", str(threshold.get("recommended_policy")))
        self.check(10, "recommender did not access test", recommender.get("test_status") == "NOT_ACCESSED_RECOMMENDER_TRAIN_DEV_ONLY", str(recommender.get("test_status")))
        self.check(11, "recommender guardrail passed", recommender.get("gate_status") == "PASSED_WITH_CONSERVATIVE_STABILITY_FILTER" and int(recommender.get("publishable_upgrades", -1)) == 0, f"gate={recommender.get('gate_status')}; upgrades={recommender.get('publishable_upgrades')}")
        self.check(12, "economics remains conditional", economics.get("evidence_status") == "conditional_projection_not_realized_saving", str(economics.get("evidence_status")))
        zero_overlap, counts_ok, assignment_evidence = self._assignments(results_root / "protocol_v3/build_partition_hashes_v3.csv", protocol)
        self.check(13, "zero Build_Id overlap", zero_overlap, assignment_evidence)
        self.check(14, "partition build counts", counts_ok, assignment_evidence)
        self.check(15, "source dataset exists", source.is_file(), str(source))
        observed_source_hash = sha256_file(source) if source.is_file() else ""
        self.check(16, "source dataset hash", observed_source_hash == protocol.get("source_sha256"), f"observed={observed_source_hash}; expected={protocol.get('source_sha256')}")

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
            suite_ok = completed.returncode == 0
            suite_evidence = f"return_code={completed.returncode}; {completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else ''}"
        else:
            suite_ok = False
            suite_evidence = "full suite was not executed"
        self.check(17, "complete pytest suite", suite_ok, suite_evidence)

        no_same_sample = calibration_audit.get("original_design", {}).get("same_sample_leakage_found") is False
        self.check(18, "A2 calibration audit", calibration_audit.get("status") == "CALIBRATION_AUDIT_COMPLETE" and no_same_sample and calibration_audit.get("official_v3_changed") is False, f"status={calibration_audit.get('status')}; same_sample_leakage={not no_same_sample}")
        order_ok = recommender_audit.get("order_encoding_correct") is True
        confounding_ok = confounding.get("status") == "CONFOUNDING_DIAGNOSTIC_COMPLETE" and confounding.get("test_status") == "NOT_ACCESSED_TRAIN_DEV_ONLY"
        self.check(19, "A3 order and confounding audit", recommender_audit.get("status") == "RECOMMENDER_AUDIT_COMPLETE" and order_ok and confounding_ok, f"order_correct={order_ok}; confounding={confounding.get('status')}")
        transitions_path = results_root / "v3_1/recommender_audit/action_transitions.csv"
        self.check(20, "A3 transition and stability evidence", transitions_path.is_file() and recommender_audit.get("publishable_upgrades") == 0 and recommender_audit.get("test_status") == "NOT_ACCESSED_RECOMMENDER_AUDIT_TRAIN_DEV_ONLY", f"transitions={transitions_path.is_file()}; upgrades={recommender_audit.get('publishable_upgrades')}")
        self.check(21, "A4 claims register", claims.get("status") == "CLAIMS_REGISTER_COMPLETE" and claims.get("official_v3_changed") is False and int(claims.get("claims", 0)) >= 10, f"status={claims.get('status')}; claims={claims.get('claims')}")
        information_map = results_root / "v3_1/overlap_audit/decision_information_map.md"
        self.check(22, "A5 overlap and information audit", overlap.get("status") == "OVERLAP_AUDIT_COMPLETE" and overlap.get("official_v3_changed") is False and information_map.is_file(), f"status={overlap.get('status')}; map={information_map.is_file()}")
        self.check(23, "A6 final model explainability", explainability.get("status") == "FINAL_MODEL_EXPLAINABILITY_COMPLETE" and explainability.get("test_status") == "NOT_ACCESSED_DEV_EXPLANATION_ONLY" and explainability.get("official_v3_changed") is False, f"status={explainability.get('status')}; test={explainability.get('test_status')}")
        self.check(24, "A1 evidence-anchored economics", anchored.get("status") == "ANCHORED_ECONOMICS_COMPLETE" and anchored.get("official_v3_changed") is False and anchored.get("annual_eligible_records_status") == "REQUIRES_BCI_MEASUREMENT", f"status={anchored.get('status')}; volume={anchored.get('annual_eligible_records_status')}")
        b2_found = b2_artifacts(repository, results_root)
        baseline_ok = baselines.get("status") == "BASELINES_B0_B3_COMPLETE" and baselines.get("test_status") == "NOT_ACCESSED_BASELINES_TRAIN_DEV_ONLY"
        flow_ok = evidence_tables.get("status") == "EVIDENCE_TABLES_COMPLETE" and evidence_tables.get("integrity", {}).get("flow_reconciled") is True
        self.check(25, "B0/B3 baselines and evidence tables; B2 excluded", baseline_ok and flow_ok and not b2_found, f"baselines={baselines.get('status')}; flow={flow_ok}; B2_artifacts={b2_found}")

        frozen_rows = verify_frozen_hashes(results_root, results_root / "v3_1/governance/baseline_v3_hashes.csv")
        frozen_ok = all(bool(row["unchanged"]) for row in frozen_rows)
        governance_ok = governance.get("gate") == "GOVERNANCE_BASELINE_FROZEN" and governance.get("test_build_set_sha256") == expected_test_hash
        marker_ok = marker.get("source_sha256") == protocol.get("source_sha256") and marker.get("test_build_set_sha256") == expected_test_hash
        self.check(26, "immutable v3 hashes and one-time test marker", frozen_ok and governance_ok and marker_ok, f"frozen={sum(bool(row['unchanged']) for row in frozen_rows)}/{len(frozen_rows)}; governance={governance_ok}; marker={marker_ok}")

        numbers = [int(row["number"]) for row in self.checks]
        if numbers != list(range(1, EXPECTED_CHECKS + 1)):
            raise ValueError(f"Release must contain checks 1..{EXPECTED_CHECKS}; observed={numbers}")
        failed = [row for row in self.checks if row["status"] == "FAIL"]
        release_status = "VERIFIED_FOR_DOCUMENTATION" if not failed else "BLOCKED"
        generated = datetime.now(timezone.utc).isoformat()
        metrics = final_test["ranking_test_metrics"]

        official = {
            "schema_version": "3.1",
            "status": release_status,
            "official_v3_unchanged": frozen_ok,
            "dataset": {
                "source_rows": evidence_tables["source_rows"],
                "usable_historical_rows": evidence_tables["usable_historical_rows"],
                "eligible_rows": protocol["eligible_rows"],
                "eligible_builds": protocol["eligible_builds"],
                "features": EXPECTED_FEATURES,
            },
            "independent_test": {
                "rows": final_test["rows"]["test"],
                "builds": final_test["rows"]["test_builds"],
                **metrics,
                "grouped_bootstrap_ic95": final_test["ranking_grouped_bootstrap_ic95"],
            },
            "operational_policy": policy,
            "development_baselines": {
                "B0": baselines["B0"],
                "B3": baselines["B3"],
                "B2_status": "NOT_REQUIRED_NOT_EXECUTED",
            },
            "recommender": {
                "published_actions": recommender["action_distribution_published"],
                "publishable_upgrades": recommender["publishable_upgrades"],
                "weighted_monotonicity": recommender_audit["monotonicity"]["weighted_consistency_rate"],
            },
            "economics": {
                "status": anchored["status"],
                "mechanism": anchored["mechanism"],
                "break_even_coverage_times_reduction": anchored["break_even_coverage_times_reduction"],
                "annual_eligible_records_status": anchored["annual_eligible_records_status"],
            },
            "claims_summary": claims,
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        inventory = self._inventory(results_root, output_dir)
        self._write_csv(output_dir / "artifact_inventory_v3_1.csv", inventory)
        self._write_csv(output_dir / "frozen_v3_integrity_v3_1.csv", frozen_rows)
        (output_dir / "official_metrics_v3_1.json").write_text(
            json.dumps(official, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        reproducibility = {
            "schema_version": "3.1",
            "generated_at_utc": generated,
            "release_status": release_status,
            "checks_expected": EXPECTED_CHECKS,
            "checks_passed": EXPECTED_CHECKS - len(failed),
            "checks_failed": len(failed),
            "checks": self.checks,
            "test_suite": test_result,
            "scope_note": "B2 analyst interviews were an optional internal enhancement, not professor feedback; B0 and B3 are the required technical baselines.",
        }
        (output_dir / "reproducibility_check_v3_1.json").write_text(
            json.dumps(reproducibility, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        manifest = {
            "schema_version": "3.1",
            "release_status": release_status,
            "generated_at_utc": generated,
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
            "source_sha256": observed_source_hash,
            "test_build_set_sha256": expected_test_hash,
            "frozen_v3_files_verified": len(frozen_rows),
            "artifact_count": len(inventory),
            "official_metrics_file": "official_metrics_v3_1.json",
            "reproducibility_file": "reproducibility_check_v3_1.json",
            "inventory_file": "artifact_inventory_v3_1.csv",
            "integrity_file": "frozen_v3_integrity_v3_1.csv",
        }
        (output_dir / "release_manifest_v3_1.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        summary_lines = [
            "# Release v3.1 · resumen verificable",
            "",
            f"**Estado:** `{release_status}`",
            f"**Controles:** {EXPECTED_CHECKS - len(failed)}/{EXPECTED_CHECKS} aprobados",
            "",
            "## Resultado oficial conservado",
            "",
            f"- Test independiente: {final_test['rows']['test']} filas / {final_test['rows']['test_builds']} builds.",
            f"- ROC-AUC: {float(metrics['roc_auc']):.4f}.",
            f"- Recall@30: {float(metrics['recall_at_30']):.4f}.",
            f"- Lift@30: {float(metrics['lift_at_30']):.4f}.",
            "- Política: revisión humana total con asistencia de ranking.",
            "",
            "## Alcance de baselines",
            "",
            "- B0 aleatorio: ejecutado.",
            "- B3 tasa histórica por celda: ejecutado con GroupKFold por Build_Id.",
            "- B2 entrevistas: no requerido y no ejecutado.",
            "",
            "## Economía",
            "",
            "La evaluación económica es una proyección condicionada; no representa ahorro ni ROI realizado.",
        ]
        if failed:
            summary_lines.extend(["", "## Controles bloqueados", ""] + [f"- {row['number']}. {row['check']}: {row['evidence']}" for row in failed])
        (output_dir / "release_summary_v3_1.md").write_text("\n".join(summary_lines), encoding="utf-8")
        return {"manifest": manifest, "reproducibility": reproducibility, "official_metrics": official}
