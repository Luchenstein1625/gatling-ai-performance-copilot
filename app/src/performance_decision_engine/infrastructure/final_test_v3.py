"""One-time evaluation of the frozen v3 protocol on the reserved test set."""

from __future__ import annotations

import csv
import json
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

from performance_decision_engine.infrastructure.calibration_decision_v3 import (
    CalibrationDecisionV3,
    expected_calibration_error,
    percentile_interval,
    wilson_interval,
)
from performance_decision_engine.infrastructure.configuration_training_v2 import (
    APPLIES,
    NOT_APPLIES,
    eligibility_reason,
    feature_row,
    technical_label,
)
from performance_decision_engine.infrastructure.fine_threshold_v3 import policy_counts
from performance_decision_engine.infrastructure.model_selection_v3 import (
    ModelSelectionV3,
    sha256_file,
    sha256_text,
)

RANDOM_STATE = 42


def require_confirmation(value: str) -> None:
    if value != "OPEN_TEST_ONCE":
        raise ValueError("Opening test requires --confirm-open-test OPEN_TEST_ONCE")


def assert_not_completed(output_dir: Path) -> None:
    if (output_dir / "final_test_evaluation_v3.json").exists():
        raise FileExistsError(
            "Final test report already exists. Do not reopen test or overwrite the result."
        )


def git_tag_commit(tag: str, repository: Path) -> str:
    result = subprocess.run(
        ["git", "rev-list", "-n", "1", tag],
        cwd=repository,
        capture_output=True,
        text=True,
        check=False,
    )
    commit = result.stdout.strip()
    if result.returncode != 0 or not commit:
        raise ValueError(f"Required frozen tag does not exist: {tag}")
    return commit


class FinalTestV3:
    def __init__(self) -> None:
        self.selection = ModelSelectionV3()
        self.calibration = CalibrationDecisionV3()

    @staticmethod
    def _load_assignments(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8", newline="") as source:
            return {
                row["build_id_sha256"]: row["partition"]
                for row in csv.DictReader(source)
            }

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _group_samples(groups: list[str], repetitions: int) -> list[list[int]]:
        by_group: dict[str, list[int]] = {}
        for index, group in enumerate(groups):
            by_group.setdefault(group, []).append(index)
        names = sorted(by_group)
        generator = random.Random(RANDOM_STATE)
        return [
            [index for name in (generator.choice(names) for _ in names) for index in by_group[name]]
            for _ in range(repetitions)
        ]

    def _grouped_bootstrap(
        self,
        labels: list[str],
        groups: list[str],
        probabilities: list[float],
        repetitions: int,
    ) -> tuple[list[dict[str, object]], dict[str, dict[str, float]]]:
        rows: list[dict[str, object]] = []
        for repetition, indexes in enumerate(
            self._group_samples(groups, repetitions), start=1
        ):
            sampled_labels = [labels[index] for index in indexes]
            if len(set(sampled_labels)) < 2:
                continue
            sampled_probabilities = [probabilities[index] for index in indexes]
            metrics = self.selection.metrics(sampled_labels, sampled_probabilities, 0.5)
            rows.append({
                "repetition": repetition,
                "roc_auc": metrics["roc_auc"],
                "pr_auc": metrics["pr_auc"],
                "recall_at_30": metrics["recall_at_30"],
                "precision_at_30": metrics["precision_at_30"],
                "lift_at_30": metrics["lift_at_30"],
            })
        summary = {
            metric: percentile_interval([float(row[metric]) for row in rows])
            for metric in (
                "roc_auc",
                "pr_auc",
                "recall_at_30",
                "precision_at_30",
                "lift_at_30",
            )
        }
        return rows, summary

    @staticmethod
    def _curves(labels: list[str], probabilities: list[float]) -> tuple[list[dict[str, float]], list[dict[str, float]]]:
        expected = [1 if label == NOT_APPLIES else 0 for label in labels]
        false_positive, true_positive, roc_thresholds = roc_curve(expected, probabilities)
        precision, recall, pr_thresholds = precision_recall_curve(expected, probabilities)
        roc_rows = [
            {
                "false_positive_rate": float(fpr),
                "true_positive_rate": float(tpr),
                "threshold": None if not np.isfinite(threshold) else float(threshold),
            }
            for fpr, tpr, threshold in zip(
                false_positive, true_positive, roc_thresholds, strict=True
            )
        ]
        pr_rows: list[dict[str, float]] = []
        for index, (precision_value, recall_value) in enumerate(
            zip(precision, recall, strict=True)
        ):
            threshold = float(pr_thresholds[index]) if index < len(pr_thresholds) else None
            pr_rows.append({
                "recall": float(recall_value),
                "precision": float(precision_value),
                "threshold": threshold,
            })
        return roc_rows, pr_rows

    @staticmethod
    def _curve_svg(
        path: Path,
        roc_rows: list[dict[str, float]],
        pr_rows: list[dict[str, float]],
        roc_auc: float,
        pr_auc: float,
        prevalence: float,
    ) -> None:
        width, height = 1040, 470
        panel_w, panel_h = 390, 330
        top, left_roc, left_pr = 65, 85, 600

        def points(rows: list[dict[str, float]], x_key: str, y_key: str, left: int) -> str:
            return " ".join(
                f"{left + float(row[x_key]) * panel_w:.1f},{top + (1-float(row[y_key])) * panel_h:.1f}"
                for row in rows
            )

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="white"/>',
            '<style>text{font-family:Arial;fill:#263746}.title{font-size:18px;font-weight:bold}.label{font-size:13px}</style>',
            f'<text x="{left_roc}" y="30" class="title">ROC · test final · AUC {roc_auc:.3f}</text>',
            f'<text x="{left_pr}" y="30" class="title">Precision–Recall · PR-AUC {pr_auc:.3f}</text>',
        ]
        for left in (left_roc, left_pr):
            parts.extend([
                f'<rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="#f7fafb" stroke="#a8b5bf"/>',
                f'<text x="{left-5}" y="{top+panel_h+28}" class="label">0</text>',
                f'<text x="{left+panel_w-5}" y="{top+panel_h+28}" class="label">1</text>',
                f'<text x="{left-25}" y="{top+5}" class="label">1</text>',
                f'<text x="{left-25}" y="{top+panel_h+5}" class="label">0</text>',
            ])
        parts.extend([
            f'<line x1="{left_roc}" y1="{top+panel_h}" x2="{left_roc+panel_w}" y2="{top}" stroke="#8e9ba6" stroke-dasharray="6 6"/>',
            f'<polyline points="{points(roc_rows, "false_positive_rate", "true_positive_rate", left_roc)}" fill="none" stroke="#008f83" stroke-width="3"/>',
            f'<line x1="{left_pr}" y1="{top+(1-prevalence)*panel_h:.1f}" x2="{left_pr+panel_w}" y2="{top+(1-prevalence)*panel_h:.1f}" stroke="#8e9ba6" stroke-dasharray="6 6"/>',
            f'<polyline points="{points(pr_rows, "recall", "precision", left_pr)}" fill="none" stroke="#073b66" stroke-width="3"/>',
            f'<text x="{left_roc+125}" y="{height-18}" class="label">False positive rate</text>',
            f'<text x="{left_pr+165}" y="{height-18}" class="label">Recall</text>',
            f'<text x="{left_pr+8}" y="{top+(1-prevalence)*panel_h-8:.1f}" class="label">Prevalencia {prevalence:.3f}</text>',
            '</svg>',
        ])
        path.write_text("\n".join(parts), encoding="utf-8")

    def run(
        self,
        source_path: Path,
        protocol_path: Path,
        assignments_path: Path,
        calibration_report_path: Path,
        fine_threshold_report_path: Path,
        output_dir: Path,
        repository: Path,
        required_tag: str,
        confirmation: str,
        bootstrap_repetitions: int = 2000,
    ) -> dict[str, object]:
        require_confirmation(confirmation)
        assert_not_completed(output_dir)
        frozen_commit = git_tag_commit(required_tag, repository)
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        calibration_report = json.loads(calibration_report_path.read_text(encoding="utf-8"))
        fine_report = json.loads(fine_threshold_report_path.read_text(encoding="utf-8"))
        if protocol["source_sha256"] != sha256_file(source_path):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        if protocol["test_lock"]["opened_for_model_selection"] is not False:
            raise ValueError("Test was opened during model selection")
        if calibration_report["test_status"] != "LOCKED_NOT_EVALUATED":
            raise ValueError("Calibration report does not preserve the test lock")
        if fine_report["test_status"] != "LOCKED_NOT_EVALUATED":
            raise ValueError("Fine-threshold report does not preserve the test lock")
        if fine_report["recommended_policy"] != "review_all_with_ranking_assistance":
            raise ValueError("Frozen operational policy differs from expected safe policy")

        output_dir.mkdir(parents=True, exist_ok=True)
        opened_at = datetime.now(timezone.utc).isoformat()
        marker = {
            "status": "OPENED_IN_PROGRESS",
            "opened_at_utc": opened_at,
            "required_tag": required_tag,
            "frozen_commit": frozen_commit,
            "source_sha256": protocol["source_sha256"],
            "test_build_set_sha256": protocol["test_lock"]["test_build_set_sha256"],
            "rule": "No model, calibration, feature, threshold or policy selection is permitted after this point.",
        }
        (output_dir / "test_opened_v3.json").write_text(
            json.dumps(marker, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        assignments = self._load_assignments(assignments_path)
        source_rows = self.selection.reader.read_fixed_width(source_path)
        usable = [row for row in source_rows if eligibility_reason(row) == "trainable"]
        partitions: dict[str, list[dict[str, str]]] = {"train": [], "dev": [], "test": []}
        for row in usable:
            partition = assignments.get(sha256_text(row["Build_Id"]))
            if partition is None:
                raise ValueError("Eligible Build_Id is absent from frozen assignments")
            partitions[partition].append(row)
        development = partitions["train"] + partitions["dev"]
        test = partitions["test"]
        if len(test) != int(protocol["partitions"]["test"]["rows"]):
            raise ValueError("Test rows differ from frozen protocol")

        x_development = [feature_row(row) for row in development]
        y_development = [technical_label(row) for row in development]
        g_development = [row["Build_Id"] for row in development]
        x_test = [feature_row(row) for row in test]
        y_test = [technical_label(row) for row in test]
        g_test = [row["Build_Id"] for row in test]

        model_name = str(calibration_report["selected_model"])
        parameters = dict(calibration_report["selected_parameters"])
        calibration_method = str(calibration_report["selected_calibration"])
        oof = self.calibration._oof_probabilities(
            model_name, parameters, x_development, y_development, g_development
        )
        calibrator = self.calibration._fit_calibrator(
            calibration_method, oof, y_development
        )
        model = self.selection.build_model(model_name, parameters).fit(
            x_development, y_development
        )
        raw_test = self.selection._probabilities(model, x_test)
        probabilities = self.calibration._apply_calibrator(
            calibrator, calibration_method, raw_test
        )

        ranking_metrics = self.selection.metrics(y_test, probabilities, 0.5)
        expected_binary = [1 if label == NOT_APPLIES else 0 for label in y_test]
        ece, reliability = expected_calibration_error(expected_binary, probabilities)
        calibration_metrics = {
            "brier": float(brier_score_loss(expected_binary, probabilities)),
            "ece_10_bins": float(ece),
        }
        bootstrap_rows, bootstrap_summary = self._grouped_bootstrap(
            y_test, g_test, probabilities, bootstrap_repetitions
        )
        diagnostic_threshold = 0.01
        diagnostic_policy = policy_counts(y_test, probabilities, diagnostic_threshold)
        released_risk = wilson_interval(
            int(diagnostic_policy["false_applies"]),
            int(diagnostic_policy["released_rows"]),
        )
        roc_rows, pr_rows = self._curves(y_test, probabilities)

        self._write_csv(output_dir / "final_test_grouped_bootstrap_v3.csv", bootstrap_rows)
        self._write_csv(output_dir / "final_test_reliability_bins_v3.csv", reliability)
        self._write_csv(output_dir / "final_test_roc_curve_v3.csv", roc_rows)
        self._write_csv(output_dir / "final_test_pr_curve_v3.csv", pr_rows)
        self._curve_svg(
            output_dir / "final_test_roc_pr_curves_v3.svg",
            roc_rows,
            pr_rows,
            float(ranking_metrics["roc_auc"]),
            float(ranking_metrics["pr_auc"]),
            float(ranking_metrics["prevalence_not_applies"]),
        )
        joblib.dump({
            "pipeline": model,
            "model_name": model_name,
            "parameters": parameters,
            "calibration_method": calibration_method,
            "calibrator": calibrator,
            "features": ["Concurrency", "Iterations", "ResponseTime"],
            "operational_policy": "review_all_with_ranking_assistance",
            "automatic_release_enabled": False,
            "frozen_tag": required_tag,
            "frozen_commit": frozen_commit,
            "status": "final_model_test_evaluated_once",
        }, output_dir / "final_model_v3.joblib")

        report: dict[str, object] = {
            "schema_version": "3.0",
            "experiment": "one_time_independent_test_evaluation",
            "test_status": "OPENED_ONCE_EVALUATION_COMPLETE",
            "opened_at_utc": opened_at,
            "frozen_tag": required_tag,
            "frozen_commit": frozen_commit,
            "source_sha256": protocol["source_sha256"],
            "test_build_set_sha256": protocol["test_lock"]["test_build_set_sha256"],
            "rows": {
                "development_train_plus_dev": len(development),
                "test": len(test),
                "test_builds": len(set(g_test)),
            },
            "final_model": {
                "name": model_name,
                "parameters": parameters,
                "features": ["Concurrency", "Iterations", "ResponseTime"],
                "calibration": calibration_method,
            },
            "selection_changes_after_test": False,
            "ranking_test_metrics": {
                key: ranking_metrics[key]
                for key in (
                    "roc_auc", "pr_auc", "prevalence_not_applies",
                    "recall_at_30", "precision_at_30", "lift_at_30",
                )
            },
            "ranking_grouped_bootstrap_ic95": bootstrap_summary,
            "calibration_test_metrics": calibration_metrics,
            "operational_policy": {
                "name": "review_all_with_ranking_assistance",
                "automatic_release_enabled": False,
                "meaning": "QA reviews every case; score only orders the queue.",
            },
            "diagnostic_threshold_not_operational": {
                **diagnostic_policy,
                "released_risk_wilson_95": released_risk,
            },
            "baselines": {
                "random_ranking": {
                    "roc_auc": 0.5,
                    "expected_recall_at_30": 0.30,
                    "expected_precision_at_30": ranking_metrics["prevalence_not_applies"],
                    "expected_lift_at_30": 1.0,
                }
            },
            "interpretation_rule": (
                "Report the independent test result exactly as observed. Do not retune or replace the model using test evidence."
            ),
        }
        (output_dir / "final_test_evaluation_v3.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        marker["status"] = "OPENED_ONCE_EVALUATION_COMPLETE"
        marker["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        (output_dir / "test_opened_v3.json").write_text(
            json.dumps(marker, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report
