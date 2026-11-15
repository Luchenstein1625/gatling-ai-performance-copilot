from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.model_selection import GroupKFold

from performance_decision_engine.infrastructure.configuration_training_v2 import (
    APPLIES,
    eligibility_reason,
    technical_label,
)
from performance_decision_engine.infrastructure.model_selection_v3 import sha256_file, sha256_text
from performance_decision_engine.infrastructure.recommender_v3 import (
    FEATURES,
    LEVELS,
    MIN_ACTION_STABILITY,
    REAL_VALUES,
    RecommenderV3,
    apply_stability_guardrail,
    build_cell_stats,
    cell_id,
    evaluate_fold,
    recommendation,
    stricter_neighbors,
)


RANDOM_STATE = 42
EXPECTED_ORDER = {
    "Concurrency": ("very_low", "low", "medium", "high", "very_high"),
    "Iterations": ("low", "medium", "high"),
    "ResponseTime": ("very_high", "high", "medium", "low"),
}
EXPECTED_REAL_VALUES = {
    "Concurrency": {"very_low": 5, "low": 20, "medium": 40, "high": 60, "very_high": 80},
    "Iterations": {"low": 5, "medium": 7, "high": 10},
    "ResponseTime": {"very_high": 15000, "high": 8000, "medium": 5000, "low": 3000},
}


def percentile(values: list[float], probability: float) -> float | None:
    return None if not values else float(np.quantile(values, probability))


def monotonicity_rows(stats: dict[Any, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source, source_stats in sorted(stats.items()):
        for feature, target in stricter_neighbors(source):
            target_stats = stats.get(target)
            if target_stats is None:
                continue
            consistent = target_stats.applies_rate <= source_stats.applies_rate
            rows.append({
                "source_cell": cell_id(source),
                "target_cell": cell_id(target),
                "changed_parameter": feature,
                "source_rows": source_stats.rows,
                "target_rows": target_stats.rows,
                "source_builds": source_stats.builds,
                "target_builds": target_stats.builds,
                "source_applies_rate": source_stats.applies_rate,
                "target_applies_rate": target_stats.applies_rate,
                "delta_target_minus_source": target_stats.applies_rate - source_stats.applies_rate,
                "consistent_with_more_demand_more_risk": consistent,
                "support_weight": min(source_stats.rows, target_stats.rows),
            })
    return rows


def summarize_monotonicity(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for feature in FEATURES:
        selected = [row for row in rows if row["changed_parameter"] == feature]
        consistent = sum(bool(row["consistent_with_more_demand_more_risk"]) for row in selected)
        weight = sum(int(row["support_weight"]) for row in selected)
        weighted = sum(
            int(row["support_weight"]) * int(bool(row["consistent_with_more_demand_more_risk"]))
            for row in selected
        )
        output.append({
            "parameter": feature,
            "comparisons": len(selected),
            "consistent": consistent,
            "consistency_rate": consistent / len(selected) if selected else None,
            "weighted_consistency_rate": weighted / weight if weight else None,
            "support_weight": weight,
        })
    all_consistent = sum(bool(row["consistent_with_more_demand_more_risk"]) for row in rows)
    all_weight = sum(int(row["support_weight"]) for row in rows)
    all_weighted = sum(
        int(row["support_weight"]) * int(bool(row["consistent_with_more_demand_more_risk"]))
        for row in rows
    )
    output.append({
        "parameter": "ALL",
        "comparisons": len(rows),
        "consistent": all_consistent,
        "consistency_rate": all_consistent / len(rows) if rows else None,
        "weighted_consistency_rate": all_weighted / all_weight if all_weight else None,
        "support_weight": all_weight,
    })
    return output


class RecommenderAuditV31:
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

    def _bootstrap(
        self,
        development: list[dict[str, str]],
        cells: list[Any],
        full_actions: dict[Any, str],
        rules: dict[str, Any],
        repetitions: int,
    ) -> tuple[list[dict[str, Any]], dict[str, list[float]]]:
        by_build: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in development:
            by_build[row["Build_Id"]].append(row)
        builds = sorted(by_build)
        generator = random.Random(RANDOM_STATE)
        agreements: Counter[Any] = Counter()
        counts: dict[Any, Counter[str]] = {cell: Counter() for cell in cells}
        monotonic_rates: dict[str, list[float]] = defaultdict(list)
        for repetition in range(repetitions):
            sampled: list[dict[str, str]] = []
            for draw, build in enumerate(generator.choice(builds) for _ in builds):
                for original in by_build[build]:
                    copied = dict(original)
                    copied["Build_Id"] = f"{build}#bootstrap_{repetition}_{draw}"
                    sampled.append(copied)
            stats = build_cell_stats(sampled)
            summary = summarize_monotonicity(monotonicity_rows(stats))
            for row in summary:
                if row["consistency_rate"] is not None:
                    monotonic_rates[str(row["parameter"])].append(float(row["consistency_rate"]))
            for cell in cells:
                action = str(recommendation(
                    cell, stats, float(rules["p_min"]), float(rules["p_review"]),
                    int(rules["min_rows"]), int(rules["min_builds"])
                )["action"])
                counts[cell][action] += 1
                agreements[cell] += int(action == full_actions[cell])
        stability = []
        for cell in cells:
            stability.append({
                "cell": cell_id(cell),
                "full_action": full_actions[cell],
                "agreement_rate": agreements[cell] / repetitions,
                "bootstrap_repetitions": repetitions,
                **{f"count_{action}": counts[cell][action] for action in ("abstain", "review", "maintain", "upgrade")},
            })
        return stability, monotonic_rates

    def _oos_cell_calibration(self, development: list[dict[str, str]]) -> list[dict[str, Any]]:
        groups = [row["Build_Id"] for row in development]
        labels = [technical_label(row) for row in development]
        splitter = GroupKFold(n_splits=5)
        predictions: dict[str, list[tuple[float, int]]] = defaultdict(list)
        for fold, (train, validation) in enumerate(splitter.split(development, labels, groups), start=1):
            stats = build_cell_stats([development[int(index)] for index in train])
            for index in validation:
                row = development[int(index)]
                cell = tuple(row[name].strip().lower().replace("-", "_").replace(" ", "_") for name in FEATURES)
                cell_stats = stats.get(cell)
                if cell_stats is None:
                    continue
                observed = int(technical_label(row) == APPLIES)
                predictions[cell_id(cell)].append((cell_stats.applies_rate, observed))
        output = []
        for cell, values in sorted(predictions.items()):
            output.append({
                "cell": cell,
                "oos_rows": len(values),
                "mean_predicted_applies_rate": float(np.mean([value[0] for value in values])),
                "observed_applies_rate": float(np.mean([value[1] for value in values])),
                "absolute_gap": abs(float(np.mean([value[0] for value in values])) - float(np.mean([value[1] for value in values]))),
                "folds": 5,
            })
        return output

    @staticmethod
    def _baseline_comparison(development: list[dict[str, str]], rules: dict[str, Any]) -> list[dict[str, Any]]:
        groups = [row["Build_Id"] for row in development]
        labels = [technical_label(row) for row in development]
        splitter = GroupKFold(n_splits=5)
        aggregates: dict[str, list[float]] = defaultdict(list)
        coverage: dict[str, list[float]] = defaultdict(list)
        for train, validation in splitter.split(development, labels, groups):
            training_rows = [development[int(index)] for index in train]
            validation_rows = [development[int(index)] for index in validation]
            result = evaluate_fold(training_rows, validation_rows, float(rules["p_min"]), float(rules["p_review"]), int(rules["min_rows"]))
            aggregates["recommender"].append(float(result["decision_success_rate"]))
            coverage["recommender"].append(float(result["coverage"]))
            observed = [technical_label(row) for row in validation_rows]
            applies_rate = sum(label == APPLIES for label in observed) / len(observed)
            aggregates["always_maintain"].append(applies_rate)
            aggregates["always_review"].append(1 - applies_rate)
            aggregates["random_binary_action"].append(0.5)
            for name in ("always_maintain", "always_review", "random_binary_action"):
                coverage[name].append(1.0)
        output = []
        for strategy in ("recommender", "always_maintain", "always_review", "random_binary_action"):
            values = aggregates[strategy]
            output.append({
                "strategy": strategy,
                "folds": len(values),
                "mean_decision_success": float(np.mean(values)),
                "minimum": float(np.min(values)),
                "maximum": float(np.max(values)),
                "mean_coverage": float(np.mean(coverage[strategy])),
                "interpretation": "descriptive grouped CV; strategies have different operational meanings",
            })
        output.append({
            "strategy": "analyst_rule",
            "folds": 0,
            "mean_decision_success": None,
            "minimum": None,
            "maximum": None,
            "mean_coverage": None,
            "interpretation": "pending two analyst interviews; not invented from data",
        })
        return output

    def run(
        self,
        source_path: Path,
        protocol_path: Path,
        assignments_path: Path,
        governance_addendum_path: Path,
        recommender_report_path: Path,
        output_dir: Path,
        bootstrap_repetitions: int = 2000,
    ) -> dict[str, Any]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        addendum = json.loads(governance_addendum_path.read_text(encoding="utf-8"))
        original_report = json.loads(recommender_report_path.read_text(encoding="utf-8"))
        if addendum.get("status") != "PRE_SPECIFIED_BEFORE_DIAGNOSTIC_EXECUTION" or not any(
            item.get("id") == "A3" for item in addendum.get("registered_analyses", [])
        ):
            raise ValueError("A3 is not pre-registered")
        if sha256_file(source_path) != protocol.get("source_sha256"):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        if original_report.get("test_status") != "NOT_ACCESSED_RECOMMENDER_TRAIN_DEV_ONLY":
            raise ValueError("Original recommender report indicates test access")

        order_rows = []
        order_correct = True
        for feature in FEATURES:
            actual = tuple(LEVELS[feature])
            expected = EXPECTED_ORDER[feature]
            matches = actual == expected
            order_correct &= matches
            for rank, level in enumerate(actual):
                order_rows.append({
                    "parameter": feature,
                    "strictness_rank_low_to_high": rank,
                    "level": level,
                    "real_value": REAL_VALUES[feature][level],
                    "expected_real_value": EXPECTED_REAL_VALUES[feature][level],
                    "direction": "higher load is stricter" if feature != "ResponseTime" else "lower allowed milliseconds is stricter",
                    "order_matches_specification": matches,
                })

        assignments = self._load_assignments(assignments_path)
        source_rows = self.recommender.reader.read_fixed_width(source_path)
        eligible = [row for row in source_rows if eligibility_reason(row) == "trainable"]
        development = [
            row for row in eligible
            if assignments.get(sha256_text(row["Build_Id"])) in {"train", "dev"}
        ]
        rules = original_report["selected_rules"]
        stats = build_cell_stats(development)
        cells = sorted(stats)
        estimated_cards = [
            recommendation(cell, stats, float(rules["p_min"]), float(rules["p_review"]), int(rules["min_rows"]), int(rules["min_builds"]))
            for cell in cells
        ]
        full_actions = {cell: str(card["action"]) for cell, card in zip(cells, estimated_cards, strict=True)}
        stability, monotonic_bootstrap = self._bootstrap(development, cells, full_actions, rules, bootstrap_repetitions)
        stability_by_cell = {str(row["cell"]): float(row["agreement_rate"]) for row in stability}
        guarded_cards = [apply_stability_guardrail(card, stability_by_cell[str(card["cell"])]) for card in estimated_cards]

        pair_rows = monotonicity_rows(stats)
        summary = summarize_monotonicity(pair_rows)
        for row in summary:
            values = monotonic_bootstrap[str(row["parameter"])]
            row["bootstrap_repetitions"] = len(values)
            row["lower_95"] = percentile(values, 0.025)
            row["upper_95"] = percentile(values, 0.975)

        transitions = []
        for card in guarded_cards:
            transitions.append({
                "cell": card["cell"],
                "estimated_action": card["action_estimated"],
                "stability": card["action_stability"],
                "stability_guardrail": card["minimum_action_stability"],
                "published_action": card["action_published"],
                "estimation_reason": card["reason"],
                "publication_reason": card["publication_reason"],
                "experimental_candidate": card["experimental_candidate"],
                "changed_parameter": card["changed_parameter"],
                "from_level": card["from_level"],
                "to_level": card["to_level"],
                "to_real_value": card["to_real_value"],
            })

        cell_rows = [{
            "cell": cell_id(cell), "concurrency": cell[0], "iterations": cell[1], "response_time": cell[2], **vars(value)
        } for cell, value in sorted(stats.items())]
        oos = self._oos_cell_calibration(development)
        baselines = self._baseline_comparison(development, rules)
        overall = next(row for row in summary if row["parameter"] == "ALL")
        estimated_distribution = Counter(str(card["action_estimated"]) for card in guarded_cards)
        published_distribution = Counter(str(card["action_published"]) for card in guarded_cards)
        conclusion = (
            "The ResponseTime strictness order was already correct; the 44.9% monotonicity result is not caused by inverted latency encoding. "
            "The data do not support robust directional recommendations with only the three configuration variables, so unstable actions remain abstentions."
            if order_correct else
            "An order-encoding defect was confirmed. A corrected recommender must be generated using the same pre-registered guardrails."
        )
        report = {
            "schema_version": "3.1",
            "alert": "A3",
            "status": "RECOMMENDER_AUDIT_COMPLETE",
            "test_status": "NOT_ACCESSED_RECOMMENDER_AUDIT_TRAIN_DEV_ONLY",
            "order_encoding_correct": order_correct,
            "response_time_direction": "very_high 15000 -> high 8000 -> medium 5000 -> low 3000 milliseconds; lower is stricter",
            "correction_required": not order_correct,
            "guardrails_changed": False,
            "bootstrap_repetitions": bootstrap_repetitions,
            "monotonicity": {
                "comparisons": overall["comparisons"],
                "consistency_rate": overall["consistency_rate"],
                "weighted_consistency_rate": overall["weighted_consistency_rate"],
                "lower_95": overall["lower_95"],
                "upper_95": overall["upper_95"],
            },
            "action_distribution_estimated": dict(sorted(estimated_distribution.items())),
            "action_distribution_published": dict(sorted(published_distribution.items())),
            "publishable_upgrades": published_distribution["upgrade"],
            "conclusion": conclusion,
            "next_action": "Keep v3 official recommendations unchanged and report the negative directional result." if order_correct else "Generate recommender_v3_1 with corrected ordering.",
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "order_encoding_check.json").write_text(json.dumps({"correct": order_correct, "rows": order_rows}, indent=2, ensure_ascii=False), encoding="utf-8")
        (output_dir / "recommender_audit_v3_1.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        self._write_csv(output_dir / "monotonicity_pairs.csv", pair_rows)
        self._write_csv(output_dir / "monotonicity_by_parameter.csv", summary)
        self._write_csv(output_dir / "action_transitions.csv", transitions)
        self._write_csv(output_dir / "cell_support.csv", cell_rows)
        self._write_csv(output_dir / "cell_calibration_oos.csv", oos)
        self._write_csv(output_dir / "baseline_comparison.csv", baselines)
        self._write_csv(output_dir / "recommender_stability_2000.csv", stability)
        return report

