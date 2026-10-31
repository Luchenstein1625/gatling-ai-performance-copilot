import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

import joblib
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
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
PARAMETERS = ("Concurrency", "Iterations", "ResponseTime")
PARAMETER_INTENSITY_LEVELS = {
    "Concurrency": ("very_low", "low", "medium", "high", "very_high"),
    "Iterations": ("low", "medium", "high"),
    # A smaller allowed response time is stricter.  The order below therefore
    # follows test intensity, not the numeric milliseconds in the YAML.
    "ResponseTime": ("very_high", "high", "medium", "low"),
}
RESPONSE_TIME_MS = {"low": 3_000, "medium": 5_000, "high": 8_000, "very_high": 15_000}
DEFAULT_ERROR_COSTS = {
    "false_applies": 10.0,
    "false_not_applies": 2.0,
    "manual_review": 1.0,
}
THRESHOLDS = tuple(round(value / 20, 2) for value in range(2, 19))
REFERENCE_THRESHOLD = 0.50
ANNUAL_ATTENTIONS = 144
AVERAGE_ATTENTION_COST_CLP = 224_000
ECONOMIC_COVERAGE_RATES = (0.25, 0.50, 0.75)
ECONOMIC_EFFORT_REDUCTION_RATES = (0.50, 0.75)
MONTHLY_CLOUD_COST_USD = 100.0
MONTHLY_AI_COST_USD = 10.0
BUDGET_USD_CLP = 982.0
PAIRED_BOOTSTRAP_REPETITIONS = 1_000


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
        train_groups = [groups[index] for index in train_indexes]
        test_groups = [groups[index] for index in test_indexes]

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

        model_selection: dict[str, dict[str, object]] = {}
        oof_cache: dict[str, tuple[list[str], list[float]]] = {}
        for name in MODEL_NAMES:
            oof_predictions, oof_probabilities = self._grouped_oof_predictions(
                candidates[name], x_train, y_train, train_groups
            )
            oof_cache[name] = (oof_predictions, oof_probabilities)
            model_selection[name] = self._binary_metrics(y_train, oof_predictions)

        selectable = list(MODEL_NAMES)
        selected_name = max(
            selectable,
            key=lambda name: (
                float(model_selection[name]["not_applies_f1"]),
                float(model_selection[name]["not_applies_recall"]),
            ),
        )
        threshold_analysis = self._threshold_analysis_from_probabilities(
            oof_cache[selected_name][1],
            y_train,
            DEFAULT_ERROR_COSTS,
            evaluation_set="train_oof_groupkfold",
        )
        selected_threshold = float(threshold_analysis["selected_threshold"])
        holdout_probabilities = self._not_applies_probabilities(fitted[selected_name], x_test)
        holdout_threshold_analysis = self._threshold_analysis_from_probabilities(
            holdout_probabilities,
            y_test,
            DEFAULT_ERROR_COSTS,
            evaluation_set="untouched_holdout",
            selected_threshold=selected_threshold,
        )
        predictions = self._predict_with_threshold(
            fitted[selected_name], x_test, selected_threshold
        )
        grouped_cv = self._grouped_cross_validation(
            candidates[selected_name], features, binary_labels, groups
        )
        paired_model_comparison = self._paired_model_comparison(
            fitted["random_forest"],
            fitted["logistic_regression"],
            x_test,
            y_test,
            test_groups,
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
                "decision_threshold": selected_threshold,
                "features": list(FEATURES),
                "classes": [APPLIES, NOT_APPLIES],
            },
            output_dir / "layer1_applicability_model.joblib",
        )
        self._export_tree(fitted["decision_tree"], output_dir)
        self._write_recommendations(recommendations, output_dir / "layered_recommendations.csv")
        self._write_thresholds(
            holdout_threshold_analysis["thresholds"],
            output_dir / "threshold_cost_analysis.csv",
        )
        self._write_thresholds(
            threshold_analysis["thresholds"], output_dir / "threshold_oof_analysis.csv"
        )
        threshold_comparison = self._threshold_comparison(
            holdout_threshold_analysis["thresholds"], selected_threshold
        )
        self._write_rows(threshold_comparison, output_dir / "threshold_comparison.csv")
        self._write_rows(
            paired_model_comparison["bootstrap_rows"],
            output_dir / "paired_model_comparison.csv",
        )
        economic_sensitivity = self._economic_sensitivity()
        self._write_rows(economic_sensitivity, output_dir / "economic_sensitivity.csv")
        self._write_segment_metrics(segment_metrics, output_dir / "segment_metrics.csv")

        action_counts = Counter(str(item["action"]) for item in recommendations)
        safety_violations = sum(
            item["action"] == "review" and item["proposed_parameters"] != item["current_parameters"]
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
                    "selection_rule": (
                        "highest grouped out-of-fold F1 for not_applies on training data; "
                        "recall breaks ties"
                    ),
                    "model_selection_train_oof": model_selection,
                    "decision_threshold": selected_threshold,
                    "threshold_selection": threshold_analysis,
                    "threshold_holdout_evaluation": holdout_threshold_analysis,
                    "paired_random_forest_vs_logistic_regression": {
                        key: value
                        for key, value in paired_model_comparison.items()
                        if key != "bootstrap_rows"
                    },
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
                    "method": (
                        "one controlled parameter step, using parameter-specific intensity "
                        "orders and successful-peer profiles from training data"
                    ),
                    "parameters": list(PARAMETERS),
                    "quadrant_definition": (
                        "Internal 1-9 summary derived from configuration intensity. It is "
                        "not an official QA matrix and each parameter remains auditable."
                    ),
                    "parameter_intensity_levels": PARAMETER_INTENSITY_LEVELS,
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
            "economic_evaluation": {
                "current_process": (
                    "QA expert judgement, considering downstream dependencies such as "
                    "databases, Tuxedo, external services and other microservices; no "
                    "reproducible quantitative ranking is currently used."
                ),
                "annual_attentions": ANNUAL_ATTENTIONS,
                "average_attention_cost_clp": AVERAGE_ATTENTION_COST_CLP,
                "annual_current_cost_clp": ANNUAL_ATTENTIONS * AVERAGE_ATTENTION_COST_CLP,
                "base_case": {
                    "coverage_rate": 0.50,
                    "effort_reduction_rate": 0.75,
                    "gross_benefit_potential_clp": 12_096_000,
                    "annual_operating_cost_usd": (MONTHLY_CLOUD_COST_USD + MONTHLY_AI_COST_USD)
                    * 12,
                    "annual_operating_cost_clp": self._annual_operating_cost_clp(),
                    "net_benefit_potential_clp": (12_096_000 - self._annual_operating_cost_clp()),
                    "projected_roi": (
                        (12_096_000 - self._annual_operating_cost_clp())
                        / self._annual_operating_cost_clp()
                    ),
                    "projected_payback_months": (
                        self._annual_operating_cost_clp() / 12_096_000 * 12
                    ),
                },
                "interpretation": (
                    "Costs are budget estimates supplied by the project. Benefit, ROI and "
                    "payback remain scenario projections until the operational pilot."
                ),
                "cost_basis": {
                    "monthly_cloud_usd": MONTHLY_CLOUD_COST_USD,
                    "monthly_ai_usd": MONTHLY_AI_COST_USD,
                    "internal_development_incremental_clp": 0,
                    "budget_usd_clp": BUDGET_USD_CLP,
                },
            },
            "artifacts": [
                "layer1_applicability_model.joblib",
                "decision_tree.dot",
                "decision_tree_rules.txt",
                "layered_recommendations.csv",
                "complete_pipeline_evaluation.json",
                "threshold_cost_analysis.csv",
                "threshold_oof_analysis.csv",
                "threshold_comparison.csv",
                "paired_model_comparison.csv",
                "economic_sensitivity.csv",
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
    def _predict_with_threshold(
        model: Any, features: list[list[object]], threshold: float
    ) -> list[str]:
        probabilities = CompleteHistoricalPipeline._not_applies_probabilities(model, features)
        return [
            NOT_APPLIES if probability >= threshold else APPLIES for probability in probabilities
        ]

    @staticmethod
    def _not_applies_probabilities(model: Any, features: list[list[object]]) -> list[float]:
        probabilities = model.predict_proba(features)
        positive_index = list(model.classes_).index(NOT_APPLIES)
        return [float(row[positive_index]) for row in probabilities]

    def _grouped_oof_predictions(
        self,
        model: Any,
        features: list[list[object]],
        expected: list[str],
        groups: list[str],
    ) -> tuple[list[str], list[float]]:
        splitter = GroupKFold(n_splits=5)
        predictions = [""] * len(expected)
        probabilities = [0.0] * len(expected)
        for train, validation in splitter.split(features, expected, groups):
            fold_model = clone(model)
            fold_model.fit(
                [features[index] for index in train],
                [expected[index] for index in train],
            )
            validation_features = [features[index] for index in validation]
            fold_predictions = list(fold_model.predict(validation_features))
            fold_probabilities = self._not_applies_probabilities(fold_model, validation_features)
            for position, prediction, probability in zip(
                validation, fold_predictions, fold_probabilities, strict=True
            ):
                predictions[int(position)] = str(prediction)
                probabilities[int(position)] = float(probability)
        return predictions, probabilities

    def _threshold_analysis_from_probabilities(
        self,
        probabilities: list[float],
        expected: list[str],
        costs: dict[str, float],
        evaluation_set: str,
        selected_threshold: float | None = None,
    ) -> dict[str, object]:
        rows: list[dict[str, object]] = []
        for threshold in THRESHOLDS:
            predicted = [
                NOT_APPLIES if probability >= threshold else APPLIES
                for probability in probabilities
            ]
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
        if selected_threshold is None:
            selected = min(
                rows,
                key=lambda row: (
                    float(row["total_cost_units"]),
                    -float(row["not_applies_recall"]),
                ),
            )
        else:
            selected = next(row for row in rows if float(row["threshold"]) == selected_threshold)
        return {
            "selected_threshold": selected["threshold"],
            "selection_rule": "minimum expected cost; not_applies recall breaks ties",
            "evaluation_set": evaluation_set,
            "cost_units": costs,
            "costs_are_configurable_assumptions": True,
            "selected_result": selected,
            "thresholds": rows,
        }

    @staticmethod
    def _threshold_comparison(
        rows: list[dict[str, object]], selected_threshold: float
    ) -> list[dict[str, object]]:
        by_threshold = {float(row["threshold"]): row for row in rows}
        reference = by_threshold[REFERENCE_THRESHOLD]
        selected = by_threshold[selected_threshold]
        reference_cost = float(reference["total_cost_units"])
        selected_cost = float(selected["total_cost_units"])

        comparison: list[dict[str, object]] = []
        for scenario, row in (("reference", reference), ("selected", selected)):
            comparison.append(
                {
                    "scenario": scenario,
                    "threshold": row["threshold"],
                    "not_applies_recall": row["not_applies_recall"],
                    "not_applies_precision": row["not_applies_precision"],
                    "not_applies_f1": row["not_applies_f1"],
                    "false_applies": row["false_applies"],
                    "false_not_applies": row["false_not_applies"],
                    "manual_reviews": row["manual_reviews"],
                    "total_cost_units": row["total_cost_units"],
                    "cost_difference_vs_reference": float(row["total_cost_units"]) - reference_cost,
                    "cost_reduction_vs_reference_pct": (
                        (reference_cost - float(row["total_cost_units"])) / reference_cost
                    ),
                }
            )
        if selected_cost > reference_cost:
            raise ValueError("Selected threshold must not cost more than the reference threshold.")
        return comparison

    @staticmethod
    def _economic_sensitivity() -> list[dict[str, object]]:
        annual_cost = ANNUAL_ATTENTIONS * AVERAGE_ATTENTION_COST_CLP
        operating_cost = CompleteHistoricalPipeline._annual_operating_cost_clp()
        rows: list[dict[str, object]] = []
        for coverage in ECONOMIC_COVERAGE_RATES:
            for reduction in ECONOMIC_EFFORT_REDUCTION_RATES:
                addressable = annual_cost * coverage
                benefit = addressable * reduction
                rows.append(
                    {
                        "coverage_rate": coverage,
                        "effort_reduction_rate": reduction,
                        "annual_current_cost_clp": annual_cost,
                        "addressable_cost_clp": addressable,
                        "gross_benefit_potential_clp": benefit,
                        "residual_annual_cost_clp": annual_cost - benefit,
                        "annual_operating_cost_clp": operating_cost,
                        "net_benefit_potential_clp": benefit - operating_cost,
                        "projected_roi": (benefit - operating_cost) / operating_cost,
                        "projected_payback_months": (
                            operating_cost / benefit * 12 if benefit > 0 else None
                        ),
                        "is_base_case": coverage == 0.50 and reduction == 0.75,
                    }
                )
        return rows

    @staticmethod
    def _annual_operating_cost_clp() -> float:
        return (MONTHLY_CLOUD_COST_USD + MONTHLY_AI_COST_USD) * 12 * BUDGET_USD_CLP

    def _paired_model_comparison(
        self,
        random_forest: Any,
        logistic_regression: Any,
        features: list[list[object]],
        expected: list[str],
        groups: list[str],
    ) -> dict[str, object]:
        rf_probabilities = self._not_applies_probabilities(random_forest, features)
        lr_probabilities = self._not_applies_probabilities(logistic_regression, features)
        rf_predictions = list(random_forest.predict(features))
        lr_predictions = list(logistic_regression.predict(features))
        truth = [1 if value == NOT_APPLIES else 0 for value in expected]

        def metrics(indexes: list[int]) -> dict[str, float]:
            subset_truth = [truth[index] for index in indexes]
            subset_expected = [expected[index] for index in indexes]
            return {
                "rf_macro_f1": float(
                    f1_score(
                        subset_expected,
                        [rf_predictions[index] for index in indexes],
                        average="macro",
                    )
                ),
                "lr_macro_f1": float(
                    f1_score(
                        subset_expected,
                        [lr_predictions[index] for index in indexes],
                        average="macro",
                    )
                ),
                "rf_roc_auc": float(
                    roc_auc_score(subset_truth, [rf_probabilities[index] for index in indexes])
                ),
                "lr_roc_auc": float(
                    roc_auc_score(subset_truth, [lr_probabilities[index] for index in indexes])
                ),
                "rf_pr_auc": float(
                    average_precision_score(
                        subset_truth, [rf_probabilities[index] for index in indexes]
                    )
                ),
                "lr_pr_auc": float(
                    average_precision_score(
                        subset_truth, [lr_probabilities[index] for index in indexes]
                    )
                ),
            }

        point = metrics(list(range(len(expected))))
        group_indexes: defaultdict[str, list[int]] = defaultdict(list)
        for index, group in enumerate(groups):
            group_indexes[group].append(index)
        unique_groups = sorted(group_indexes)
        generator = random.Random(42)
        bootstrap_rows: list[dict[str, object]] = []
        for repetition in range(1, PAIRED_BOOTSTRAP_REPETITIONS + 1):
            sampled_groups = [generator.choice(unique_groups) for _ in unique_groups]
            indexes = [index for group in sampled_groups for index in group_indexes[group]]
            if len({truth[index] for index in indexes}) < 2:
                continue
            values = metrics(indexes)
            for metric in ("macro_f1", "roc_auc", "pr_auc"):
                rf_value = values[f"rf_{metric}"]
                lr_value = values[f"lr_{metric}"]
                bootstrap_rows.append(
                    {
                        "repetition": repetition,
                        "metric": metric,
                        "random_forest": rf_value,
                        "logistic_regression": lr_value,
                        "difference_rf_minus_logistic": rf_value - lr_value,
                    }
                )

        summary: dict[str, object] = {}
        for metric in ("macro_f1", "roc_auc", "pr_auc"):
            differences = sorted(
                float(row["difference_rf_minus_logistic"])
                for row in bootstrap_rows
                if row["metric"] == metric
            )
            lower_index = int(0.025 * (len(differences) - 1))
            upper_index = int(0.975 * (len(differences) - 1))
            summary[metric] = {
                "random_forest": point[f"rf_{metric}"],
                "logistic_regression": point[f"lr_{metric}"],
                "difference": point[f"rf_{metric}"] - point[f"lr_{metric}"],
                "difference_ci95_build_bootstrap": [
                    differences[lower_index],
                    differences[upper_index],
                ],
            }
        return {
            "method": "paired bootstrap by Build_Id on untouched holdout",
            "repetitions": PAIRED_BOOTSTRAP_REPETITIONS,
            "metrics": summary,
            "bootstrap_rows": bootstrap_rows,
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
            selected = [
                row for row, item_label in zip(rows, labels, strict=True) if item_label == label
            ]
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
                "error_rate_rows": sum(
                    (self._number(row.get("errorCount")) or 0) > 0 for row in selected
                )
                / len(selected),
            }
        return {
            "by_class": by_class,
            "missingness": {
                name: sum(not row.get(name, "").strip() for row in rows) / len(rows)
                for name in (*FEATURES, "p95", "rps", "errorCount")
            },
            "warning": (
                "EDA result fields describe the observed label; "
                "they are excluded from model inputs."
            ),
        }

    @staticmethod
    def _write_thresholds(rows: list[dict[str, object]], path: Path) -> None:
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _write_rows(rows: list[dict[str, object]], path: Path) -> None:
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _write_segment_metrics(rows: list[dict[str, object]], path: Path) -> None:
        fieldnames = [
            "dimension",
            "segment",
            "rows",
            "not_applies_rate",
            "not_applies_f1",
            "not_applies_recall",
            "accuracy",
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
        proposed_parameters = proposal.get("proposed_parameters", {})
        response_time_level = (
            proposed_parameters.get("ResponseTime", "")
            if isinstance(proposed_parameters, dict)
            else ""
        )
        response_time_limit = RESPONSE_TIME_MS.get(str(response_time_level).lower())
        passed = bool(
            status_ok
            and errors == 0
            and successes is not None
            and successes > 0
            and p95 is not None
            and response_time_limit is not None
            and p95 <= response_time_limit
        )
        return {
            "status": "validated" if passed else "review",
            "approved": passed,
            "observed": {
                "Estado": new_result.get("Estado", ""),
                "errorCount": errors,
                "successCount": successes,
                "p95": p95,
                "response_time_limit_ms": response_time_limit,
                "rps": cls._number(new_result.get("rps")),
            },
            "proposed_parameters": proposed_parameters,
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
            "not_applies_f1": f1_score(expected, predicted, pos_label=NOT_APPLIES, zero_division=0),
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
        return tuple(
            row.get(name, "").strip().lower() for name in ("pilar", "Tcomponente", "Metodo")
        )

    def _profile(self, rows: list[dict[str, str]]) -> dict[str, str]:
        profile: dict[str, str] = {}
        for parameter in PARAMETERS:
            observed = [row.get(parameter, "").strip().lower() for row in rows]
            levels = PARAMETER_INTENSITY_LEVELS[parameter]
            ranks = [levels.index(value) for value in observed if value in levels]
            profile[parameter] = levels[round(median(ranks))] if ranks else ""
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
            peer = peer_profiles.get(self._peer_key(row), current)
            proposed, changed_parameter = self._propose_one_controlled_step(current, peer)
            if changed_parameter is None:
                action = "maintain"
                rationale = (
                    "The execution applies, but every configurable parameter is already at "
                    "the maximum defined test intensity."
                )
            else:
                action = "upgrade"
                rationale = (
                    f"The execution applies with headroom; increase only {changed_parameter} "
                    "by one controlled intensity level and validate with a new Gatling run."
                )
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
            "changed_parameter": (
                next(
                    (name for name in PARAMETERS if current.get(name) != proposed.get(name)),
                    None,
                )
            ),
            "human_approval_required": action != "maintain",
            "online_validation_status": (
                "pending_new_execution" if action == "upgrade" else "not_required"
            ),
            "rationale": rationale,
        }

    @staticmethod
    def _one_step_higher(parameter: str, current: str) -> str:
        levels = PARAMETER_INTENSITY_LEVELS[parameter]
        if current not in levels:
            return current
        return levels[min(levels.index(current) + 1, len(levels) - 1)]

    @classmethod
    def _propose_one_controlled_step(
        cls,
        current: dict[str, str],
        peer: dict[str, str],
    ) -> tuple[dict[str, str], str | None]:
        """Increase exactly one dimension of test intensity.

        Peer profiles decide which dimension has evidence of additional headroom. If no
        peer dimension is higher, concurrency is tried first because it raises load while
        keeping iterations and the response-time objective unchanged.
        """
        proposed = dict(current)
        candidates: list[tuple[bool, str]] = []
        for parameter in PARAMETERS:
            levels = PARAMETER_INTENSITY_LEVELS[parameter]
            value = current.get(parameter, "")
            peer_value = peer.get(parameter, "")
            if value not in levels or levels.index(value) >= len(levels) - 1:
                continue
            peer_has_headroom = peer_value in levels and levels.index(peer_value) > levels.index(
                value
            )
            candidates.append((peer_has_headroom, parameter))
        if not candidates:
            return proposed, None
        candidates.sort(key=lambda item: (not item[0], PARAMETERS.index(item[1])))
        parameter = candidates[0][1]
        proposed[parameter] = cls._one_step_higher(parameter, proposed[parameter])
        return proposed, parameter

    @staticmethod
    def _load_quadrant(parameters: dict[str, str]) -> int | None:
        normalized: list[int] = []
        for parameter in PARAMETERS:
            levels = PARAMETER_INTENSITY_LEVELS[parameter]
            value = parameters.get(parameter, "")
            if value not in levels:
                normalized.append(0)
                continue
            normalized.append(round(levels.index(value) * 2 / (len(levels) - 1)))
        if not any(parameters.get(parameter) for parameter in PARAMETERS):
            return None
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
            "changed_parameter",
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
