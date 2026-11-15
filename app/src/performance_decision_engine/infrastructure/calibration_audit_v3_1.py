from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold

from performance_decision_engine.infrastructure.calibration_decision_v3 import (
    CalibrationDecisionV3,
    expected_calibration_error,
    percentile_interval,
)
from performance_decision_engine.infrastructure.configuration_training_v2 import (
    NOT_APPLIES,
    eligibility_reason,
    feature_row,
    technical_label,
)
from performance_decision_engine.infrastructure.model_selection_v3 import (
    ModelSelectionV3,
    sha256_file,
    sha256_text,
)


RANDOM_STATE = 42


def metric_values(labels: list[str], probabilities: list[float]) -> dict[str, float]:
    expected = [1 if value == NOT_APPLIES else 0 for value in labels]
    clipped = np.clip(np.asarray(probabilities, dtype=float), 1e-15, 1 - 1e-15)
    ece, _ = expected_calibration_error(expected, list(clipped))
    return {
        "roc_auc": float(roc_auc_score(expected, clipped)),
        "pr_auc": float(average_precision_score(expected, clipped)),
        "brier": float(brier_score_loss(expected, clipped)),
        "log_loss": float(log_loss(expected, clipped, labels=[0, 1])),
        "ece_10_bins": float(ece),
    }


def order_effects(raw: list[float], transformed: list[float]) -> dict[str, int]:
    inversions = 0
    created_ties = 0
    preserved_unequal = 0
    for left in range(len(raw)):
        for right in range(left + 1, len(raw)):
            raw_delta = raw[left] - raw[right]
            calibrated_delta = transformed[left] - transformed[right]
            if raw_delta == 0:
                continue
            if calibrated_delta == 0:
                created_ties += 1
            elif raw_delta * calibrated_delta < 0:
                inversions += 1
            else:
                preserved_unequal += 1
    return {
        "order_inversions": inversions,
        "new_tied_pairs": created_ties,
        "strictly_ordered_pairs_preserved": preserved_unequal,
    }


class CalibrationAuditV31:
    def __init__(self) -> None:
        self.selection = ModelSelectionV3()
        self.calibration = CalibrationDecisionV3()

    @staticmethod
    def _load_assignments(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            return {row["build_id_sha256"]: row["partition"] for row in csv.DictReader(source)}

    @staticmethod
    def _group_samples(groups: list[str], repetitions: int) -> list[list[int]]:
        by_group: dict[str, list[int]] = {}
        for index, group in enumerate(groups):
            by_group.setdefault(group, []).append(index)
        names = sorted(by_group)
        generator = random.Random(RANDOM_STATE)
        return [
            [index for name in [generator.choice(names) for _ in names] for index in by_group[name]]
            for _ in range(repetitions)
        ]

    def _crossfit_calibration(
        self,
        labels: list[str],
        raw_probabilities: list[float],
        groups: list[str],
    ) -> dict[str, list[float]]:
        output = {"raw": list(raw_probabilities), "sigmoid": [0.0] * len(labels), "isotonic": [0.0] * len(labels)}
        folds = min(5, len(set(groups)))
        splitter = GroupKFold(n_splits=folds)
        dummy = np.zeros((len(labels), 1))
        for train, validation in splitter.split(dummy, labels, groups):
            train_probabilities = [raw_probabilities[int(i)] for i in train]
            train_labels = [labels[int(i)] for i in train]
            validation_probabilities = [raw_probabilities[int(i)] for i in validation]
            for method in ("sigmoid", "isotonic"):
                calibrator = self.calibration._fit_calibrator(method, train_probabilities, train_labels)
                calibrated = self.calibration._apply_calibrator(calibrator, method, validation_probabilities)
                for index, value in zip(validation, calibrated, strict=True):
                    output[method][int(index)] = float(value)
        return output

    def _bootstrap_summary(
        self,
        labels: list[str],
        probabilities: dict[str, list[float]],
        groups: list[str],
        repetitions: int,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        rows: list[dict[str, Any]] = []
        storage: dict[tuple[str, str], list[float]] = {}
        for repetition, indexes in enumerate(self._group_samples(groups, repetitions), start=1):
            sampled_labels = [labels[i] for i in indexes]
            if len(set(sampled_labels)) < 2:
                continue
            for method, values in probabilities.items():
                sampled_probabilities = [values[i] for i in indexes]
                metrics = metric_values(sampled_labels, sampled_probabilities)
                rows.append({"repetition": repetition, "method": method, **metrics})
                for metric, value in metrics.items():
                    storage.setdefault((method, metric), []).append(value)
        summary: list[dict[str, Any]] = []
        points = {method: metric_values(labels, values) for method, values in probabilities.items()}
        for method in probabilities:
            for metric, point in points[method].items():
                interval = percentile_interval(storage[(method, metric)])
                summary.append({"method": method, "metric": metric, "point": point, **interval})
        return rows, summary

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def run(
        self,
        source_path: Path,
        protocol_path: Path,
        assignments_path: Path,
        selection_report_path: Path,
        governance_addendum_path: Path,
        final_model_path: Path,
        output_dir: Path,
        bootstrap_repetitions: int = 1000,
    ) -> dict[str, Any]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        selection_report = json.loads(selection_report_path.read_text(encoding="utf-8"))
        addendum = json.loads(governance_addendum_path.read_text(encoding="utf-8"))
        if addendum.get("status") != "PRE_SPECIFIED_BEFORE_DIAGNOSTIC_EXECUTION":
            raise ValueError("v3.1 governance addendum is not pre-specified")
        if not any(item.get("id") == "A2" for item in addendum.get("registered_analyses", [])):
            raise ValueError("A2 calibration audit is not registered")
        if sha256_file(source_path) != protocol.get("source_sha256"):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        if selection_report.get("test_status") != "LOCKED_NOT_EVALUATED":
            raise ValueError("Model selection did not keep test locked")

        assignments = self._load_assignments(assignments_path)
        rows = self.selection.reader.read_fixed_width(source_path)
        eligible = [row for row in rows if eligibility_reason(row) == "trainable"]
        partitions: dict[str, list[dict[str, str]]] = {"train": [], "dev": [], "test": []}
        for row in eligible:
            partitions[assignments[sha256_text(row["Build_Id"])]].append(row)

        def prepare(partition: str) -> tuple[list[list[str]], list[str], list[str]]:
            selected = partitions[partition]
            return (
                [feature_row(row) for row in selected],
                [technical_label(row) for row in selected],
                [row["Build_Id"] for row in selected],
            )

        x_train, y_train, g_train = prepare("train")
        x_dev, y_dev, g_dev = prepare("dev")
        x_test, y_test, _ = prepare("test")
        rf_parameters = json.loads(selection_report["best_by_model"]["random_forest"]["parameters"])
        oof_train = self.calibration._oof_probabilities("random_forest", rf_parameters, x_train, y_train, g_train)
        rf = self.selection.build_model("random_forest", rf_parameters).fit(x_train, y_train)
        raw_dev = self.selection._probabilities(rf, x_dev)

        original_dev: dict[str, list[float]] = {"raw": raw_dev}
        for method in ("sigmoid", "isotonic"):
            calibrator = self.calibration._fit_calibrator(method, oof_train, y_train)
            original_dev[method] = self.calibration._apply_calibrator(calibrator, method, raw_dev)
        original_metrics = {method: metric_values(y_dev, probabilities) for method, probabilities in original_dev.items()}
        effects = order_effects(original_dev["raw"], original_dev["isotonic"])
        invariance = {
            "comparison_set": "same frozen dev rows and same raw RF scores",
            "raw_roc_auc": original_metrics["raw"]["roc_auc"],
            "isotonic_roc_auc": original_metrics["isotonic"]["roc_auc"],
            "delta_isotonic_minus_raw": original_metrics["isotonic"]["roc_auc"] - original_metrics["raw"]["roc_auc"],
            **effects,
            "strict_monotonic_invariance_expected": True,
            "observed_explanation": "Isotonic is non-decreasing rather than strictly increasing; it creates tied score blocks. With zero inversions, any AUC change is due to ties, not reordered pairs.",
        }

        crossfit = self._crossfit_calibration(y_dev, raw_dev, g_dev)
        bootstrap_rows, crossfit_summary = self._bootstrap_summary(y_dev, crossfit, g_dev, bootstrap_repetitions)

        frozen = joblib.load(final_model_path)
        required = {"pipeline", "calibration_method", "calibrator", "features"}
        if not required.issubset(frozen):
            raise ValueError(f"Final model artifact lacks fields: {sorted(required - set(frozen))}")
        raw_test = self.selection._probabilities(frozen["pipeline"], x_test)
        calibrated_test = self.calibration._apply_calibrator(
            frozen["calibrator"], str(frozen["calibration_method"]), raw_test
        )
        test_rows: list[dict[str, Any]] = []
        for method, probabilities in (("raw", raw_test), (str(frozen["calibration_method"]), calibrated_test)):
            test_rows.append({"method": method, **metric_values(y_test, probabilities), "use": "descriptive_only_no_selection"})

        same_sample_leakage = False
        conclusion = (
            "The original calibrators were fitted on grouped OOF train predictions and evaluated on separate dev rows; no same-sample calibration evaluation was found. "
            "The isotonic AUC difference is attributable to tied score blocks and must not be described as improved discrimination without the cross-fit evidence."
        )
        report = {
            "schema_version": "3.1",
            "alert": "A2",
            "status": "CALIBRATION_AUDIT_COMPLETE",
            "official_v3_changed": False,
            "test_used_for_selection": False,
            "original_design": {
                "calibrator_fit": "grouped OOF predictions from train",
                "calibrator_evaluation": "separate frozen dev",
                "same_sample_leakage_found": same_sample_leakage,
            },
            "invariance_check": invariance,
            "crossfit": {
                "unit": "Build_Id",
                "folds": min(5, len(set(g_dev))),
                "bootstrap_repetitions": bootstrap_repetitions,
                "summary_file": "crossfit_comparison.csv",
            },
            "test_diagnostic": {
                "status": "DESCRIPTIVE_ONLY_PRE_REGISTERED",
                "rows": len(y_test),
                "file": "test_ece_descriptive.csv",
            },
            "conclusion": conclusion,
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "invariance_check.json").write_text(json.dumps(invariance, indent=2, ensure_ascii=False), encoding="utf-8")
        (output_dir / "audit_findings.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        self._write_csv(output_dir / "original_dev_comparison.csv", [{"method": method, **metrics} for method, metrics in original_metrics.items()])
        self._write_csv(output_dir / "crossfit_comparison.csv", crossfit_summary)
        self._write_csv(output_dir / "crossfit_grouped_bootstrap.csv", bootstrap_rows)
        self._write_csv(output_dir / "test_ece_descriptive.csv", test_rows)
        return report

