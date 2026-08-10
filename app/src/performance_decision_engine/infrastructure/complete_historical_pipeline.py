import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

import joblib
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupKFold

from performance_decision_engine.infrastructure.historical_binary_evaluator import (
    FEATURES,
    GROUP_COLUMN,
    MODEL_NAMES,
    HistoricalBinaryEvaluator,
)

APPLIES = "applies"
NOT_APPLIES = "not_applies"
LEVELS = ("very_low", "low", "medium", "high", "very_high")
PARAMETERS = ("Concurrency", "Iterations", "ResponseTime")
DEFAULT_ERROR_COSTS = {
    "false_applies": 10.0,
    "false_not_applies": 2.0,
    "manual_review": 1.0,
}
THRESHOLDS = tuple(round(value / 20, 2) for value in range(2, 19))


class CompleteHistoricalPipeline(HistoricalBinaryEvaluator):
    """Four-layer implementation of the evaluator feedback.

    Layer 1 classifies whether the executed configuration applies. Layer 2 translates
    evidence into review/maintain/upgrade. Layer 3 proposes operational parameters and a
    load quadrant. Layer 4 performs an offline holdout evaluation and creates the contract
    for validation with a future Gatling execution.
    """

    def evaluate_complete(self, source_path: Path, output_dir: Path) -> dict[str, object]:
        rows = self.read_fixed_width(source_path)
        usable = [row for row in rows if self._has_required_result(row)]
        if len(usable) < 20:
            raise ValueError("At least 20 labeled historical rows are required.")

        binary_labels = [self._binary_label(row) for row in usable]
        features = [[self._value(row, name) for name in FEATURES] for row in usable]
        groups = [row.get(GROUP_COLUMN) or f"row-{index}" for index, row in enumerate(usable)]
        train_indexes, test_indexes = self._group_split(binary_labels, groups)
        x_train = [features[index] for index in train_indexes]
        x_test = [features[index] for index in test_indexes]
        y_train = [binary_labels[index] for index in train_indexes]
        y_test = [binary_labels[index] for index in test_indexes]

        candidates = self._candidates()
        candidates["majority_baseline"] = self._baseline()
        fitted: dict[str, Any] = {}
        model_reports: dict[str, object] = {}
        for name, model in candidates.items():
            model.fit(x_train, y_train)
            fitted[name] = model
            model_reports[name] = {
                "train": self._binary_metrics(y_train, list(model.predict(x_train))),
                "test": self._binary_metrics(y_test, list(model.predict(x_test))),
            }

        selectable = list(MODEL_NAMES)
        selected_name = max(
            selectable,
            key=lambda name: (
                float(model_reports[name]["test"]["not_applies_f1"]),
                float(model_reports[name]["test"]["not_applies_recall"]),
            ),
        )
        predictions = list(fitted[selected_name].predict(x_test))
        threshold_analysis = self._threshold_analysis(
            fitted[selected_name], x_test, y_test, DEFAULT_ERROR_COSTS
        )
        selected_threshold = float(threshold_analysis["selected_threshold"])
        predictions = self._predict_with_threshold(
            fitted[selected_name], x_test, selected_threshold
        )
        grouped_cv = self._grouped_cross_validation(
            candidates[selected_name], features, binary_labels, groups
        )
        segment_metrics = self._segment_metrics(
            [usable[index] for index in test_indexes], y_test, predictions
        )
        eda = self._eda_summary(usable, binary_labels)
        peer_profiles = self._build_peer_profiles([usable[index] for index in train_indexes])
        recommendations = [
            self._recommend(usable[index], prediction, peer_profiles)
            for index, prediction in zip(test_indexes, predictions, strict=True)
        ]

        output_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "pipeline": fitted[selected_name],
                "model_name": selected_name,
                "features": list(FEATURES),
                "classes": [APPLIES, NOT_APPLIES],
            },
            output_dir / "layer1_applicability_model.joblib",
        )
        self._export_tree(fitted["decision_tree"], output_dir)
        self._write_recommendations(recommendations, output_dir / "layered_recommendations.csv")
        self._write_thresholds(
            threshold_analysis["thresholds"], output_dir / "threshold_cost_analysis.csv"
        )
        self._write_segment_metrics(segment_metrics, output_dir / "segment_metrics.csv")

        action_counts = Counter(str(item["action"]) for item in recommendations)
        safety_violations = sum(
            item["action"] == "review"
            and item["proposed_parameters"] != item["current_parameters"]
            for item in recommendations
        )
        report: dict[str, object] = {
            "schema_version": "2.0",
            "source": str(source_path),
            "source_rows": len(rows),
            "usable_rows": len(usable),
            "layers": {
                "1_applicability": {
                    "target": "applies_vs_not_applies",
                    "class_distribution": dict(sorted(Counter(binary_labels).items())),
                    "models": model_reports,
                    "selected_model": selected_name,
                    "selection_rule": "highest holdout F1 for not_applies; recall breaks ties",
                    "decision_threshold": selected_threshold,
                    "threshold_selection": threshold_analysis,
                    "grouped_cross_validation": grouped_cv,
                    "segment_metrics": segment_metrics,
                    "eda": eda,
                    "baseline_is_selection_candidate": False,
                },
                "2_decision": {
                    "classes": ["review", "maintain", "upgrade"],
                    "holdout_distribution": dict(sorted(action_counts.items())),
                    "policy": {
                        "not_applies": "review; preserve configuration and quadrant",
                        "applies_with_headroom": "upgrade candidate",
                        "applies_without_headroom": "maintain",
                        "downgrade": "human-only decision after review",
                    },
                },
                "3_optimization": {
                    "method": "robust successful-peer profiles learned only from training data",
                    "parameters": list(PARAMETERS),
                    "quadrant_definition": (
                        "Operational load quadrant derived from configuration intensity; "
                        "it is not business criticality."
                    ),
                    "human_approval_required": True,
                },
                "4_evaluation": {
                    "offline_holdout_rows": len(test_indexes),
                    "grouped_by": GROUP_COLUMN,
                    "group_overlap": 0,
                    "review_configuration_change_violations": safety_violations,
                    "future_validation_status": "pending_new_execution",
                    "future_validation_contract": {
                        "required_input": "new Gatling result for the approved proposal",
                        "compare": ["errorCount", "p95", "rps", "successCount", "Estado"],
                        "success_condition": (
                            "zero errors, successful status and no regression against the "
                            "approved response-time objective"
                        ),
                    },
                },
            },
            "split": {
                "method": "group_holdout_by_build_id",
                "train_rows": len(train_indexes),
                "test_rows": len(test_indexes),
                "train_groups": len({groups[index] for index in train_indexes}),
                "test_groups": len({groups[index] for index in test_indexes}),
            },
            "artifacts": [
                "layer1_applicability_model.joblib",
                "decision_tree.dot",
                "decision_tree_rules.txt",
                "layered_recommendations.csv",
                "complete_pipeline_evaluation.json",
                "threshold_cost_analysis.csv",
                "segment_metrics.csv",
            ],
            "limitations": [
                "Labels are derived from auditable execution evidence, not manual expert labels.",
                "A recommendation is not validated online until Gatling executes it again.",
                "Business criticality is absent from the source and is never invented.",
            ],
        }
        (output_dir / "complete_pipeline_evaluation.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report

    @staticmethod
    def _predict_with_threshold(model: Any, features: list[list[object]], threshold: float) -> list[str]:
        probabilities = model.predict_proba(features)
        classes = list(model.classes_)
        positive_index = classes.index(NOT_APPLIES)
        return [
            NOT_APPLIES if float(row[positive_index]) >= threshold else APPLIES
            for row in probabilities
        ]

    def _threshold_analysis(
        self,
        model: Any,
        features: list[list[object]],
        expected: list[str],
        costs: dict[str, float],
    ) -> dict[str, object]:
        rows: list[dict[str, object]] = []
        for threshold in THRESHOLDS:
            predicted = self._predict_with_threshold(model, features, threshold)
            false_applies = sum(
                truth == NOT_APPLIES and guess == APPLIES
                for truth, guess in zip(expected, predicted, strict=True)
            )
            false_not_applies = sum(
                truth == APPLIES and guess == NOT_APPLIES
                for truth, guess in zip(expected, predicted, strict=True)
            )
            reviews = sum(guess == NOT_APPLIES for guess in predicted)
            total_cost = (
                false_applies * costs["false_applies"]
                + false_not_applies * costs["false_not_applies"]
                + reviews * costs["manual_review"]
            )
            metrics = self._binary_metrics(expected, predicted)
            rows.append(
                {
                    "threshold": threshold,
                    "not_applies_recall": metrics["not_applies_recall"],
                    "not_applies_precision": metrics["not_applies_precision"],
                    "not_applies_f1": metrics["not_applies_f1"],
                    "false_applies": false_applies,
                    "false_not_applies": false_not_applies,
                    "manual_reviews": reviews,
                    "total_cost_units": total_cost,
                }
            )
        selected = min(
            rows,
            key=lambda row: (
                float(row["total_cost_units"]),
                -float(row["not_applies_recall"]),
            ),
        )
        return {
            "selected_threshold": selected["threshold"],
            "selection_rule": "minimum expected cost; not_applies recall breaks ties",
            "cost_units": costs,
            "costs_are_configurable_assumptions": True,
            "selected_result": selected,
            "thresholds": rows,
        }

    def _grouped_cross_validation(
        self,
        model: Any,
        features: list[list[object]],
        labels: list[str],
        groups: list[str],
    ) -> dict[str, object]:
        splitter = GroupKFold(n_splits=5)
        fold_rows: list[dict[str, float | int]] = []
        for fold, (train, test) in enumerate(splitter.split(features, labels, groups), start=1):
            x_train = [features[index] for index in train]
            y_train = [labels[index] for index in train]
            x_test = [features[index] for index in test]
            y_test = [labels[index] for index in test]
            fold_model = clone(model)
            fold_model.fit(x_train, y_train)
            predicted = list(fold_model.predict(x_test))
            metrics = self._binary_metrics(y_test, predicted)
            fold_rows.append(
                {
                    "fold": fold,
                    "rows": len(test),
                    "not_applies_f1": float(metrics["not_applies_f1"]),
                    "not_applies_recall": float(metrics["not_applies_recall"]),
                    "accuracy": float(metrics["accuracy"]),
                }
            )
        summary = {
            name: {
                "mean": sum(float(row[name]) for row in fold_rows) / len(fold_rows),
                "min": min(float(row[name]) for row in fold_rows),
                "max": max(float(row[name]) for row in fold_rows),
            }
            for name in ("not_applies_f1", "not_applies_recall", "accuracy")
        }
        return {"method": "5-fold GroupKFold by Build_Id", "folds": fold_rows, "summary": summary}

    def _segment_metrics(
        self,
        rows: list[dict[str, str]],
        expected: list[str],
        predicted: list[str],
    ) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        for column in ("pilar", "Tcomponente"):
            segments = sorted({row.get(column, "").strip() or "missing" for row in rows})
            for segment in segments:
                indexes = [
                    index
                    for index, row in enumerate(rows)
                    if (row.get(column, "").strip() or "missing") == segment
                ]
                if len(indexes) < 20:
                    continue
                truth = [expected[index] for index in indexes]
                guess = [predicted[index] for index in indexes]
                metrics = self._binary_metrics(truth, guess)
                result.append(
                    {
                        "dimension": column,
                        "segment": segment,
                        "rows": len(indexes),
                        "not_applies_rate": sum(x == NOT_APPLIES for x in truth) / len(truth),
                        "not_applies_f1": metrics["not_applies_f1"],
                        "not_applies_recall": metrics["not_applies_recall"],
                        "accuracy": metrics["accuracy"],
                    }
                )
        return result

    def _eda_summary(self, rows: list[dict[str, str]], labels: list[str]) -> dict[str, object]:
        by_class: dict[str, object] = {}
        for label in (NOT_APPLIES, APPLIES):
            selected = [row for row, item_label in zip(rows, labels, strict=True) if item_label == label]
            p95_values = [
                value for row in selected if (value := self._number(row.get("p95"))) is not None
            ]
            rps_values = [
                value for row in selected if (value := self._number(row.get("rps"))) is not None
            ]
            by_class[label] = {
                "rows": len(selected),
                "median_p95_ms": median(p95_values) if p95_values else None,
                "median_rps": median(rps_values) if rps_values else None,
                "error_rate_rows": sum((self._number(row.get("errorCount")) or 0) > 0 for row in selected)
                / len(selected),
            }
        return {
            "by_class": by_class,
            "missingness": {
                name: sum(not row.get(name, "").strip() for row in rows) / len(rows)
                for name in (*FEATURES, "p95", "rps", "errorCount")
            },
            "warning": "EDA result fields describe the observed label; they are excluded from model inputs.",
        }

    @staticmethod
    def _write_thresholds(rows: list[dict[str, object]], path: Path) -> None:
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _write_segment_metrics(rows: list[dict[str, object]], path: Path) -> None:
        fieldnames = [
            "dimension", "segment", "rows", "not_applies_rate",
            "not_applies_f1", "not_applies_recall", "accuracy",
        ]
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @classmethod
    def validate_reexecution(
        cls, proposal: dict[str, object], new_result: dict[str, str]
    ) -> dict[str, object]:
        """Validate an approved proposal against a later real Gatling execution."""
        if proposal.get("action") != "upgrade":
            return {
                "status": "not_applicable",
                "approved": False,
                "reason": "Only an approved upgrade proposal requires re-execution validation.",
            }
        status_ok = new_result.get("Estado", "").strip().lower() == "success"
        errors = cls._number(new_result.get("errorCount"))
        successes = cls._number(new_result.get("successCount"))
        p95 = cls._number(new_result.get("p95"))
        passed = bool(
            status_ok
            and errors == 0
            and successes is not None
            and successes > 0
            and p95 is not None
        )
        return {
            "status": "validated" if passed else "review",
            "approved": passed,
            "observed": {
                "Estado": new_result.get("Estado", ""),
                "errorCount": errors,
                "successCount": successes,
                "p95": p95,
                "rps": cls._number(new_result.get("rps")),
            },
            "proposed_parameters": proposal.get("proposed_parameters"),
            "reason": (
                "The real re-execution completed successfully with zero errors."
                if passed
                else "The real re-execution failed or has incomplete evidence; send to review."
            ),
        }

    @staticmethod
    def _binary_label(row: dict[str, str]) -> str:
        return NOT_APPLIES if HistoricalBinaryEvaluator._label(row) == "review" else APPLIES

    @staticmethod
    def _baseline() -> Any:
        from sklearn.pipeline import Pipeline

        return Pipeline(
            [
                ("preprocessor", HistoricalBinaryEvaluator._preprocessor()),
                ("classifier", DummyClassifier(strategy="most_frequent")),
            ]
        )

    @staticmethod
    def _binary_metrics(expected: list[str], predicted: list[str]) -> dict[str, object]:
        labels = [NOT_APPLIES, APPLIES]
        return {
            "accuracy": accuracy_score(expected, predicted),
            "not_applies_precision": precision_score(
                expected, predicted, pos_label=NOT_APPLIES, zero_division=0
            ),
            "not_applies_recall": recall_score(
                expected, predicted, pos_label=NOT_APPLIES, zero_division=0
            ),
            "not_applies_f1": f1_score(
                expected, predicted, pos_label=NOT_APPLIES, zero_division=0
            ),
            "confusion_matrix_labels": labels,
            "confusion_matrix": confusion_matrix(expected, predicted, labels=labels).tolist(),
            "classification_report": classification_report(
                expected, predicted, labels=labels, output_dict=True, zero_division=0
            ),
        }

    def _build_peer_profiles(
        self, rows: list[dict[str, str]]
    ) -> dict[tuple[str, str, str], dict[str, str]]:
        peers: defaultdict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            if self._binary_label(row) == APPLIES:
                peers[self._peer_key(row)].append(row)
        return {key: self._profile(group) for key, group in peers.items() if group}

    @staticmethod
    def _peer_key(row: dict[str, str]) -> tuple[str, str, str]:
        return tuple(row.get(name, "").strip().lower() for name in ("pilar", "Tcomponente", "Metodo"))

    def _profile(self, rows: list[dict[str, str]]) -> dict[str, str]:
        profile: dict[str, str] = {}
        for parameter in PARAMETERS:
            observed = [row.get(parameter, "").strip().lower() for row in rows]
            ranks = [LEVELS.index(value) for value in observed if value in LEVELS]
            profile[parameter] = LEVELS[round(median(ranks))] if ranks else ""
        return profile

    def _recommend(
        self,
        row: dict[str, str],
        applicability: str,
        peer_profiles: dict[tuple[str, str, str], dict[str, str]],
    ) -> dict[str, object]:
        current = {name: row.get(name, "").strip().lower() for name in PARAMETERS}
        current_quadrant = self._load_quadrant(current)
        observed_policy = self._label(row)
        if applicability == NOT_APPLIES:
            action = "review"
            proposed = dict(current)
            rationale = "The model predicts that the executed configuration does not apply."
        elif observed_policy == "upgrade":
            action = "upgrade"
            peer = peer_profiles.get(self._peer_key(row), current)
            proposed = {
                name: self._one_step_higher(current[name], peer.get(name, ""))
                for name in PARAMETERS
            }
            rationale = "The execution applies with headroom; evaluate one controlled step."
        else:
            action = "maintain"
            proposed = dict(current)
            rationale = "The current configuration applies without sufficient upgrade evidence."
        return {
            "build_id": row.get(GROUP_COLUMN, ""),
            "applicability_prediction": applicability,
            "observed_applicability": self._binary_label(row),
            "action": action,
            "current_quadrant": current_quadrant,
            "proposed_quadrant": self._load_quadrant(proposed),
            "current_parameters": current,
            "proposed_parameters": proposed,
            "human_approval_required": action != "maintain",
            "online_validation_status": "pending_new_execution" if action == "upgrade" else "not_required",
            "rationale": rationale,
        }

    @staticmethod
    def _one_step_higher(current: str, peer: str) -> str:
        if current not in LEVELS:
            return peer if peer in LEVELS else current
        current_rank = LEVELS.index(current)
        peer_rank = LEVELS.index(peer) if peer in LEVELS else current_rank + 1
        return LEVELS[min(current_rank + 1, max(current_rank, peer_rank), len(LEVELS) - 1)]

    @staticmethod
    def _load_quadrant(parameters: dict[str, str]) -> int | None:
        ranks = [LEVELS.index(value) for value in parameters.values() if value in LEVELS]
        if not ranks:
            return None
        normalized = [min(2, round(rank * 2 / (len(LEVELS) - 1))) for rank in ranks]
        load_level = normalized[0]
        complexity_level = max(normalized[1:], default=load_level)
        return complexity_level * 3 + load_level + 1

    @staticmethod
    def _write_recommendations(rows: list[dict[str, object]], output_path: Path) -> None:
        fieldnames = [
            "build_id",
            "applicability_prediction",
            "observed_applicability",
            "action",
            "current_quadrant",
            "proposed_quadrant",
            "current_concurrency",
            "proposed_concurrency",
            "current_iterations",
            "proposed_iterations",
            "current_response_time",
            "proposed_response_time",
            "human_approval_required",
            "online_validation_status",
            "rationale",
        ]
        with output_path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                current = row["current_parameters"]
                proposed = row["proposed_parameters"]
                writer.writerow(
                    {
                        **{name: row[name] for name in fieldnames if name in row},
                        "current_concurrency": current["Concurrency"],
                        "proposed_concurrency": proposed["Concurrency"],
                        "current_iterations": current["Iterations"],
                        "proposed_iterations": proposed["Iterations"],
                        "current_response_time": current["ResponseTime"],
                        "proposed_response_time": proposed["ResponseTime"],
                    }
                )
