"""Create and freeze the grouped train/dev/test protocol for the final project."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from sklearn.model_selection import StratifiedGroupKFold

from performance_decision_engine.infrastructure.configuration_training_v2 import (
    FEATURES,
    ConfigurationTrainingV2,
    eligibility_reason,
    technical_label,
)

RANDOM_STATE = 42
PROTOCOL_VERSION = "3.0"
PARTITIONS = ("train", "dev", "test")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def partition_digest(build_ids: set[str]) -> str:
    return sha256_text("\n".join(sorted(build_ids)))


class FrozenProtocolV3:
    def __init__(self) -> None:
        self.training = ConfigurationTrainingV2()

    @staticmethod
    def _indexes_from_split(
        indexes: list[int], labels: list[str], groups: list[str], n_splits: int, seed: int
    ) -> tuple[list[int], list[int]]:
        local_labels = [labels[index] for index in indexes]
        local_groups = [groups[index] for index in indexes]
        splitter = StratifiedGroupKFold(
            n_splits=n_splits, shuffle=True, random_state=seed
        )
        local_train, local_holdout = next(
            splitter.split(indexes, local_labels, local_groups)
        )
        return (
            [indexes[int(position)] for position in local_train],
            [indexes[int(position)] for position in local_holdout],
        )

    def split(
        self, labels: list[str], groups: list[str]
    ) -> dict[str, list[int]]:
        indexes = list(range(len(labels)))
        train_dev, test = self._indexes_from_split(
            indexes, labels, groups, n_splits=5, seed=RANDOM_STATE
        )
        train, dev = self._indexes_from_split(
            train_dev, labels, groups, n_splits=8, seed=RANDOM_STATE + 1
        )
        partitions = {"train": train, "dev": dev, "test": test}
        expected_classes = set(labels)
        for name, values in partitions.items():
            if set(labels[index] for index in values) != expected_classes:
                raise ValueError(f"Partition {name} does not contain every class")
        build_sets = {
            name: {groups[index] for index in values}
            for name, values in partitions.items()
        }
        if build_sets["train"] & build_sets["dev"]:
            raise ValueError("Build_Id leakage between train and dev")
        if build_sets["train"] & build_sets["test"]:
            raise ValueError("Build_Id leakage between train and test")
        if build_sets["dev"] & build_sets["test"]:
            raise ValueError("Build_Id leakage between dev and test")
        return partitions

    @staticmethod
    def _partition_summary(
        name: str,
        indexes: list[int],
        labels: list[str],
        groups: list[str],
        total_rows: int,
    ) -> dict[str, object]:
        builds = {groups[index] for index in indexes}
        counts = Counter(labels[index] for index in indexes)
        return {
            "partition": name,
            "rows": len(indexes),
            "row_fraction": len(indexes) / total_rows,
            "builds": len(builds),
            "class_distribution": dict(sorted(counts.items())),
            "not_applies_prevalence": counts.get("not_applies", 0) / len(indexes),
            "build_id_set_sha256": partition_digest(builds),
        }

    def run(self, source_path: Path, output_dir: Path) -> dict[str, object]:
        rows = self.training.read_fixed_width(source_path)
        usable = [row for row in rows if eligibility_reason(row) == "trainable"]
        labels = [technical_label(row) for row in usable]
        groups = [row["Build_Id"] for row in usable]
        partitions = self.split(labels, groups)
        summaries = {
            name: self._partition_summary(
                name, indexes, labels, groups, len(usable)
            )
            for name, indexes in partitions.items()
        }

        build_to_partition: dict[str, str] = {}
        for name, indexes in partitions.items():
            for index in indexes:
                build = groups[index]
                previous = build_to_partition.setdefault(build, name)
                if previous != name:
                    raise ValueError(f"Build_Id assigned twice: {build}")

        protocol: dict[str, object] = {
            "protocol_version": PROTOCOL_VERSION,
            "status": "frozen_before_final_model_selection",
            "source_sha256": sha256_file(source_path),
            "unit_of_analysis": "one executed Gatling configuration record",
            "grouping_unit": "Build_Id",
            "eligible_rows": len(usable),
            "eligible_builds": len(set(groups)),
            "target": "applies_vs_not_applies_from_measured_execution_evidence",
            "allowed_features": list(FEATURES),
            "forbidden_features": [
                "Is_In_Prod",
                "ambiente",
                "Performance",
                "CpruebasCarga",
                "CpruebasAcep",
                "pilar",
                "Tcomponente",
                "Metodo",
                "Estado",
                "errorCount",
                "successCount",
                "p95",
                "rps",
            ],
            "abstention": [
                "Performance is not 1",
                "configuration is incomplete",
                "result evidence is incomplete during offline labeling",
            ],
            "split_method": {
                "outer": "first fold of StratifiedGroupKFold(n_splits=5)",
                "inner": (
                    "first fold of StratifiedGroupKFold(n_splits=8) over outer train+dev"
                ),
                "random_state_outer": RANDOM_STATE,
                "random_state_inner": RANDOM_STATE + 1,
                "target_proportions": {"train": 0.70, "dev": 0.10, "test": 0.20},
                "note": "Exact row proportions vary because complete Build_Id groups stay together.",
            },
            "partitions": summaries,
            "model_selection": {
                "train": "fit candidate models and internal grouped CV",
                "dev": "select hyperparameters, model, calibration and threshold",
                "test": "open once after the final model is frozen",
                "primary_metric": "ROC-AUC",
                "tie_breaker": "macro-F1",
                "ranking_metrics": ["recall_at_30", "precision_at_30", "lift_at_30"],
                "uncertainty": "bootstrap in Build_Id clusters",
            },
            "threshold_policy": {
                "selection_set": "dev",
                "costs": {
                    "false_applies": 10,
                    "applies_reviewed": 2,
                    "manual_review": 1,
                },
                "guardrail": "no automatic release; human approval remains mandatory",
            },
            "preregistered_hypotheses": {
                "H1": (
                    "A tuned boosting model improves ROC-AUC over Random Forest; superiority "
                    "requires a paired 95% interval for the difference excluding zero."
                ),
                "H2": (
                    "The final ranking exceeds random ordering at equal review capacity."
                ),
                "H3": (
                    "The selected policy has lower expected cost than review-all under more "
                    "than half of the registered economic scenarios."
                ),
            },
            "test_lock": {
                "opened_for_model_selection": False,
                "test_build_set_sha256": summaries["test"]["build_id_set_sha256"],
                "instruction": (
                    "Do not calculate test model metrics until model-final is tagged."
                ),
            },
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "frozen_protocol_v3.json").write_text(
            json.dumps(protocol, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        with (output_dir / "build_partition_hashes_v3.csv").open(
            "w", encoding="utf-8", newline=""
        ) as target:
            writer = csv.DictWriter(
                target, fieldnames=["build_id_sha256", "partition"]
            )
            writer.writeheader()
            for build, partition in sorted(build_to_partition.items()):
                writer.writerow(
                    {"build_id_sha256": sha256_text(build), "partition": partition}
                )
        return protocol
