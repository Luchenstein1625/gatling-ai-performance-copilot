from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupKFold

from performance_decision_engine.infrastructure.configuration_training_v2 import (
    FEATURES,
    eligibility_reason,
    technical_label,
)


NOT_APPLIES = "not_applies"
RANDOM_STATE = 42
TOP_FRACTION = 0.30


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> dict[str, float | int]:
    if total <= 0:
        return {"successes": successes, "total": total, "estimate": 0.0, "lower_95": 0.0, "upper_95": 0.0}
    estimate = successes / total
    denominator = 1.0 + z * z / total
    centre = (estimate + z * z / (2.0 * total)) / denominator
    radius = z * math.sqrt(estimate * (1.0 - estimate) / total + z * z / (4.0 * total * total)) / denominator
    return {
        "successes": successes,
        "total": total,
        "estimate": estimate,
        "lower_95": max(0.0, centre - radius),
        "upper_95": min(1.0, centre + radius),
    }


def percentile_summary(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("At least one value is required")
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "lower_95": float(np.quantile(values, 0.025)),
        "upper_95": float(np.quantile(values, 0.975)),
    }


def ranking_metrics(labels: list[int], scores: list[float], top_fraction: float = TOP_FRACTION) -> dict[str, float | int]:
    if len(labels) != len(scores) or not labels:
        raise ValueError("Labels and scores must be non-empty and have equal length")
    top_rows = max(1, round(len(labels) * top_fraction))
    ranking = sorted(range(len(scores)), key=lambda index: (-scores[index], index))
    selected = ranking[:top_rows]
    positives = sum(labels)
    captured = sum(labels[index] for index in selected)
    prevalence = positives / len(labels)
    precision = captured / top_rows
    return {
        "rows": len(labels),
        "not_applies": positives,
        "prevalence_not_applies": prevalence,
        "top_fraction": top_fraction,
        "top_rows": top_rows,
        "recall_at_30": captured / positives if positives else 0.0,
        "precision_at_30": precision,
        "lift_at_30": precision / prevalence if prevalence else 0.0,
        "roc_auc": float(roc_auc_score(labels, scores)) if len(set(labels)) == 2 else float("nan"),
        "pr_auc": float(average_precision_score(labels, scores)) if len(set(labels)) == 2 else float("nan"),
    }


def cell_key(row: dict[str, str]) -> tuple[str, str, str]:
    return tuple(row[name] for name in FEATURES)  # type: ignore[return-value]


def out_of_fold_cell_scores(rows: list[dict[str, str]], folds: int = 5) -> tuple[list[float], list[dict[str, Any]]]:
    labels_text = [technical_label(row) for row in rows]
    labels = [1 if label == NOT_APPLIES else 0 for label in labels_text]
    groups = [row["Build_Id"] for row in rows]
    scores = [0.0] * len(rows)
    audit: list[dict[str, Any]] = []
    splitter = GroupKFold(n_splits=folds)
    for fold, (train, validation) in enumerate(splitter.split(rows, labels, groups), start=1):
        train_groups = {groups[int(index)] for index in train}
        validation_groups = {groups[int(index)] for index in validation}
        if train_groups & validation_groups:
            raise ValueError("Build_Id overlap detected inside GroupKFold")
        totals: Counter[tuple[str, str, str]] = Counter()
        positives: Counter[tuple[str, str, str]] = Counter()
        for index in train:
            key = cell_key(rows[int(index)])
            totals[key] += 1
            positives[key] += labels[int(index)]
        fallback = sum(labels[int(index)] for index in train) / len(train)
        unseen = 0
        for index in validation:
            key = cell_key(rows[int(index)])
            if totals[key]:
                scores[int(index)] = positives[key] / totals[key]
            else:
                scores[int(index)] = fallback
                unseen += 1
        audit.append({
            "fold": fold,
            "train_rows": len(train),
            "validation_rows": len(validation),
            "train_builds": len(train_groups),
            "validation_builds": len(validation_groups),
            "group_overlap": 0,
            "unseen_cell_rows": unseen,
            "fallback_prevalence": fallback,
        })
    return scores, audit


def grouped_bootstrap(
    labels: list[int], scores: list[float], groups: list[str], repetitions: int, seed: int = RANDOM_STATE
) -> list[dict[str, float | int]]:
    by_group: dict[str, list[int]] = defaultdict(list)
    for index, group in enumerate(groups):
        by_group[group].append(index)
    unique_groups = sorted(by_group)
    generator = random.Random(seed)
    output: list[dict[str, float | int]] = []
    for repetition in range(1, repetitions + 1):
        selected = [generator.choice(unique_groups) for _ in unique_groups]
        sampled_indexes = [index for group in selected for index in by_group[group]]
        sampled_labels = [labels[index] for index in sampled_indexes]
        if len(set(sampled_labels)) < 2:
            continue
        metrics = ranking_metrics(sampled_labels, [scores[index] for index in sampled_indexes])
        output.append({"repetition": repetition, **metrics})
    if not output:
        raise ValueError("No valid grouped bootstrap repetitions")
    return output


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class BaselinesV31:
    def __init__(self) -> None:
        from performance_decision_engine.infrastructure.configuration_training_v2 import ConfigurationTrainingV2

        self.reader = ConfigurationTrainingV2()

    @staticmethod
    def _assignments(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8", newline="") as source:
            return {row["build_id_sha256"]: row["partition"] for row in csv.DictReader(source)}

    def run(
        self,
        source_path: Path,
        protocol_path: Path,
        assignments_path: Path,
        governance_addendum_path: Path,
        baseline_protocol_path: Path,
        output_dir: Path,
        bootstrap_repetitions: int = 2000,
        random_repetitions: int = 2000,
    ) -> dict[str, Any]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        governance = json.loads(governance_addendum_path.read_text(encoding="utf-8"))
        baseline_protocol = json.loads(baseline_protocol_path.read_text(encoding="utf-8"))
        if protocol["source_sha256"] != sha256_file(source_path):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        if not governance["integrity"]["official_final_test_is_immutable"]:
            raise ValueError("Official v3 is not protected by governance")
        if baseline_protocol.get("status") != "PRE_SPECIFIED_BEFORE_BASELINE_EXECUTION":
            raise ValueError("B0/B3 protocol was not frozen before execution")
        if {item.get("id") for item in baseline_protocol.get("analyses", [])} != {"B0", "B3"}:
            raise ValueError("Frozen baseline protocol must contain exactly B0 and B3")
        if any(item.get("test_use") != "none" for item in baseline_protocol.get("analyses", [])):
            raise ValueError("B0/B3 must not access the independent test")

        assignments = self._assignments(assignments_path)
        source_rows = self.reader.read_fixed_width(source_path)
        usable = [row for row in source_rows if eligibility_reason(row) == "trainable"]
        development = [
            row for row in usable
            if assignments.get(sha256_text(row["Build_Id"])) in {"train", "dev"}
        ]
        expected = int(protocol["partitions"]["train"]["rows"]) + int(protocol["partitions"]["dev"]["rows"])
        if len(development) != expected:
            raise ValueError("Development rows differ from frozen protocol")
        if any(assignments.get(sha256_text(row["Build_Id"])) == "test" for row in development):
            raise ValueError("Independent test leaked into baseline development data")

        labels = [1 if technical_label(row) == NOT_APPLIES else 0 for row in development]
        groups = [row["Build_Id"] for row in development]
        prevalence = sum(labels) / len(labels)
        top_rows = max(1, round(len(labels) * TOP_FRACTION))

        generator = random.Random(RANDOM_STATE)
        random_draws: list[dict[str, Any]] = []
        indexes = list(range(len(labels)))
        for repetition in range(1, random_repetitions + 1):
            selected = generator.sample(indexes, top_rows)
            captured = sum(labels[index] for index in selected)
            precision = captured / top_rows
            random_draws.append({
                "repetition": repetition,
                "top_rows": top_rows,
                "captured_not_applies": captured,
                "recall_at_30": captured / sum(labels),
                "precision_at_30": precision,
                "lift_at_30": precision / prevalence,
            })

        b3_scores, fold_audit = out_of_fold_cell_scores(development)
        b3_point = ranking_metrics(labels, b3_scores)
        b3_bootstrap = grouped_bootstrap(labels, b3_scores, groups, bootstrap_repetitions)

        b0_summary = {
            "roc_auc": {"mean": 0.5, "median": 0.5, "lower_95": 0.5, "upper_95": 0.5},
            "pr_auc": {"mean": prevalence, "median": prevalence, "lower_95": prevalence, "upper_95": prevalence},
            "recall_at_30": percentile_summary([float(row["recall_at_30"]) for row in random_draws]),
            "precision_at_30": percentile_summary([float(row["precision_at_30"]) for row in random_draws]),
            "lift_at_30": percentile_summary([float(row["lift_at_30"]) for row in random_draws]),
        }
        b3_summary = {
            metric: percentile_summary([float(row[metric]) for row in b3_bootstrap])
            for metric in ("roc_auc", "pr_auc", "recall_at_30", "precision_at_30", "lift_at_30")
        }

        comparison: list[dict[str, Any]] = []
        for baseline, summary, point in (
            ("B0_random", b0_summary, None),
            ("B3_cell_not_applies_rate_oof", b3_summary, b3_point),
        ):
            for metric in ("roc_auc", "pr_auc", "recall_at_30", "precision_at_30", "lift_at_30"):
                values = summary[metric]
                comparison.append({
                    "baseline": baseline,
                    "population": "frozen_train_plus_dev",
                    "evaluation": "random simulation" if baseline == "B0_random" else "5-fold grouped OOF plus grouped bootstrap",
                    "metric": metric,
                    "point": values["mean"] if point is None else point[metric],
                    "bootstrap_mean": values["mean"],
                    "lower_95": values["lower_95"],
                    "upper_95": values["upper_95"],
                    "test_accessed": False,
                })

        cell_counts: dict[tuple[str, str, str], dict[str, Any]] = {}
        for row, label in zip(development, labels, strict=True):
            key = cell_key(row)
            value = cell_counts.setdefault(key, {"rows": 0, "not_applies": 0, "builds": set()})
            value["rows"] += 1
            value["not_applies"] += label
            value["builds"].add(row["Build_Id"])
        cell_rows = []
        for key, value in sorted(cell_counts.items()):
            interval = wilson_interval(int(value["not_applies"]), int(value["rows"]))
            cell_rows.append({
                "cell": "|".join(key),
                "Concurrency": key[0],
                "Iterations": key[1],
                "ResponseTime": key[2],
                "rows": value["rows"],
                "builds": len(value["builds"]),
                "not_applies": value["not_applies"],
                "not_applies_rate": interval["estimate"],
                "lower_95_wilson": interval["lower_95"],
                "upper_95_wilson": interval["upper_95"],
            })

        report = {
            "schema_version": "3.1",
            "status": "BASELINES_B0_B3_COMPLETE",
            "population": {
                "rows": len(development),
                "builds": len(set(groups)),
                "not_applies": sum(labels),
                "prevalence_not_applies": prevalence,
                "partitions": ["train", "dev"],
            },
            "test_status": "NOT_ACCESSED_BASELINES_TRAIN_DEV_ONLY",
            "baseline_protocol": {
                "path": str(baseline_protocol_path),
                "sha256": sha256_file(baseline_protocol_path),
                "status": baseline_protocol["status"],
            },
            "B0": b0_summary,
            "B3": {
                "point": b3_point,
                "grouped_bootstrap": b3_summary,
                "cells": len(cell_rows),
                "unseen_oof_rows": sum(int(row["unseen_cell_rows"]) for row in fold_audit),
            },
            "interpretation": "B0 quantifies chance ranking. B3 tests whether configuration-cell history has out-of-sample ranking signal without fitting the final model.",
            "decision_effect": "descriptive only; official v3 model, threshold and test metrics remain unchanged",
            "official_v3_changed": False,
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        _write_csv(output_dir / "baseline_comparison.csv", comparison)
        _write_csv(output_dir / "baseline_b0_random_draws.csv", random_draws)
        _write_csv(output_dir / "baseline_b3_grouped_bootstrap.csv", b3_bootstrap)
        _write_csv(output_dir / "baseline_b3_fold_audit.csv", fold_audit)
        _write_csv(output_dir / "cell_not_applies_rates.csv", cell_rows)
        (output_dir / "baselines_b0_b3_v3_1.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report
