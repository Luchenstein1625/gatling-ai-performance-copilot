from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from performance_decision_engine.infrastructure.configuration_training_v2 import eligibility_reason
from performance_decision_engine.infrastructure.model_selection_v3 import sha256_file, sha256_text
from performance_decision_engine.infrastructure.recommender_audit_v3_1 import (
    monotonicity_rows,
    summarize_monotonicity,
)
from performance_decision_engine.infrastructure.recommender_v3 import RecommenderV3, build_cell_stats


CONTEXT_FIELDS = ("pilar", "Tcomponente")
MIN_STRATUM_ROWS = 20
MIN_STRATUM_BUILDS = 5


def normalize_context(value: str) -> str:
    cleaned = value.strip()
    return cleaned if cleaned else "__MISSING__"


class RecommenderConfoundingV31:
    def __init__(self) -> None:
        self.recommender = RecommenderV3()

    @staticmethod
    def _load_assignments(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            return {row["build_id_sha256"]: row["partition"] for row in csv.DictReader(source)}

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        if not rows:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _pair_key(row: dict[str, Any]) -> tuple[str, str, str]:
        return (str(row["source_cell"]), str(row["target_cell"]), str(row["changed_parameter"]))

    def run(
        self,
        source_path: Path,
        protocol_path: Path,
        assignments_path: Path,
        governance_addendum_path: Path,
        recommender_audit_path: Path,
        output_dir: Path,
    ) -> dict[str, Any]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        addendum = json.loads(governance_addendum_path.read_text(encoding="utf-8"))
        recommender_audit = json.loads(recommender_audit_path.read_text(encoding="utf-8"))
        if sha256_file(source_path) != protocol.get("source_sha256"):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        if addendum.get("status") != "PRE_SPECIFIED_BEFORE_DIAGNOSTIC_EXECUTION":
            raise ValueError("Governance addendum is not pre-specified")
        if not any(item.get("id") == "A3" for item in addendum.get("registered_analyses", [])):
            raise ValueError("A3 diagnostic is not registered")
        if recommender_audit.get("test_status") != "NOT_ACCESSED_RECOMMENDER_AUDIT_TRAIN_DEV_ONLY":
            raise ValueError("A3 audit does not certify train+dev-only execution")

        assignments = self._load_assignments(assignments_path)
        source_rows = self.recommender.reader.read_fixed_width(source_path)
        eligible = [row for row in source_rows if eligibility_reason(row) == "trainable"]
        development = [
            row for row in eligible
            if assignments.get(sha256_text(row["Build_Id"])) in {"train", "dev"}
        ]
        if not development:
            raise ValueError("No train+dev rows available")
        missing_fields = [field for field in CONTEXT_FIELDS if field not in development[0]]
        if missing_fields:
            raise ValueError(f"Context fields not present in source rows: {missing_fields}")

        pooled_pairs = monotonicity_rows(build_cell_stats(development))
        pooled_by_key = {self._pair_key(row): row for row in pooled_pairs}
        support_rows: list[dict[str, Any]] = []
        stratified_rows: list[dict[str, Any]] = []
        pair_evidence: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)

        for field in CONTEXT_FIELDS:
            grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
            for row in development:
                grouped[normalize_context(row.get(field, ""))].append(row)
            for stratum, rows in sorted(grouped.items()):
                builds = len({row["Build_Id"] for row in rows})
                eligible_stratum = len(rows) >= MIN_STRATUM_ROWS and builds >= MIN_STRATUM_BUILDS
                stats = build_cell_stats(rows)
                pairs = monotonicity_rows(stats) if eligible_stratum else []
                support_rows.append({
                    "context_field": field,
                    "stratum": stratum,
                    "rows": len(rows),
                    "builds": builds,
                    "configuration_cells": len(stats),
                    "eligible_for_direction_diagnostic": eligible_stratum,
                    "pair_comparisons": len(pairs),
                })
                if not pairs:
                    continue
                summary = summarize_monotonicity(pairs)
                for item in summary:
                    stratified_rows.append({
                        "context_field": field,
                        "stratum": stratum,
                        "stratum_rows": len(rows),
                        "stratum_builds": builds,
                        **item,
                    })
                for pair in pairs:
                    pair_evidence[self._pair_key(pair)].append({
                        "context_field": field,
                        "stratum": stratum,
                        "rows": len(rows),
                        "support_weight": pair["support_weight"],
                        "consistent": bool(pair["consistent_with_more_demand_more_risk"]),
                        "delta": pair["delta_target_minus_source"],
                    })

        simpson_rows: list[dict[str, Any]] = []
        reversal_count = 0
        comparable_pairs = 0
        for key, pooled in sorted(pooled_by_key.items()):
            evidence = pair_evidence.get(key, [])
            total_weight = sum(int(item["support_weight"]) for item in evidence)
            consistent_weight = sum(
                int(item["support_weight"]) for item in evidence if bool(item["consistent"])
            )
            within_rate = consistent_weight / total_weight if total_weight else None
            pooled_consistent = bool(pooled["consistent_with_more_demand_more_risk"])
            reversal = bool(
                within_rate is not None
                and ((not pooled_consistent and within_rate > 0.5) or (pooled_consistent and within_rate < 0.5))
            )
            comparable_pairs += int(within_rate is not None)
            reversal_count += int(reversal)
            simpson_rows.append({
                "source_cell": key[0],
                "target_cell": key[1],
                "changed_parameter": key[2],
                "pooled_consistent": pooled_consistent,
                "pooled_delta": pooled["delta_target_minus_source"],
                "eligible_stratum_comparisons": len(evidence),
                "within_strata_support_weight": total_weight,
                "within_strata_consistency_rate": within_rate,
                "direction_reversal_flag": reversal,
            })

        eligible_all = [row for row in stratified_rows if row["parameter"] == "ALL"]
        aggregate_weight = sum(int(row["support_weight"]) for row in eligible_all)
        aggregate_consistent = sum(
            float(row["weighted_consistency_rate"]) * int(row["support_weight"])
            for row in eligible_all if row["weighted_consistency_rate"] not in (None, "")
        )
        stratified_weighted_rate = aggregate_consistent / aggregate_weight if aggregate_weight else None
        pooled_weighted_rate = float(recommender_audit["monotonicity"]["weighted_consistency_rate"])
        materially_higher = bool(
            stratified_weighted_rate is not None and stratified_weighted_rate >= pooled_weighted_rate + 0.10
        )
        if materially_higher or reversal_count > 0:
            finding = "CONTEXT_CONFOUNDING_COMPATIBLE"
            conclusion = (
                "Within-context diagnostics differ materially from the pooled result or show direction reversals. "
                "Context may confound the observational relation, but it is not added to the operational model."
            )
        else:
            finding = "NO_STRONG_CONTEXT_CONFOUNDING_EVIDENCE"
            conclusion = (
                "Stratification by Pilar and Tcomponente does not restore a robust monotonic relation. "
                "The negative directional result remains and no directional actions should be published."
            )
        report = {
            "schema_version": "3.1",
            "alert": "A3b",
            "status": "CONFOUNDING_DIAGNOSTIC_COMPLETE",
            "test_status": "NOT_ACCESSED_TRAIN_DEV_ONLY",
            "context_fields_used_for_diagnosis_only": list(CONTEXT_FIELDS),
            "context_fields_added_to_model": False,
            "minimum_stratum_support": {"rows": MIN_STRATUM_ROWS, "builds": MIN_STRATUM_BUILDS},
            "pooled_weighted_monotonicity": pooled_weighted_rate,
            "stratified_weighted_monotonicity": stratified_weighted_rate,
            "comparable_cell_pairs": comparable_pairs,
            "direction_reversal_pairs": reversal_count,
            "finding": finding,
            "official_recommender_changed": False,
            "conclusion": conclusion,
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        self._write_csv(output_dir / "context_support.csv", support_rows)
        self._write_csv(output_dir / "stratified_monotonicity.csv", stratified_rows)
        self._write_csv(output_dir / "simpson_pair_diagnostics.csv", simpson_rows)
        (output_dir / "recommender_confounding_audit_v3_1.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report

