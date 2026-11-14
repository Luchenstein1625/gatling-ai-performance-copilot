"""Auditable configuration recommender trained and backtested on train+dev only."""

from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from sklearn.model_selection import GroupKFold

from performance_decision_engine.infrastructure.calibration_decision_v3 import (
    wilson_interval,
)
from performance_decision_engine.infrastructure.configuration_training_v2 import (
    APPLIES,
    NOT_APPLIES,
    eligibility_reason,
    technical_label,
)
from performance_decision_engine.infrastructure.model_selection_v3 import (
    sha256_file,
    sha256_text,
)

RANDOM_STATE = 42
FEATURES = ("Concurrency", "Iterations", "ResponseTime")
CONCURRENCY_LEVELS = ("very_low", "low", "medium", "high", "very_high")
ITERATION_LEVELS = ("low", "medium", "high")
# Ascending test strictness: smaller allowed latency is more demanding.
RESPONSE_TIME_LEVELS = ("very_high", "high", "medium", "low")
LEVELS = {
    "Concurrency": CONCURRENCY_LEVELS,
    "Iterations": ITERATION_LEVELS,
    "ResponseTime": RESPONSE_TIME_LEVELS,
}
REAL_VALUES = {
    "Concurrency": {"very_low": 5, "low": 20, "medium": 40, "high": 60, "very_high": 80},
    "Iterations": {"low": 5, "medium": 7, "high": 10},
    "ResponseTime": {"low": 3000, "medium": 5000, "high": 8000, "very_high": 15000},
}
P_MIN_VALUES = (0.70, 0.80, 0.90)
P_REVIEW_VALUES = (0.40, 0.50, 0.60)
MIN_ROWS_VALUES = (20, 30, 50)
MIN_BUILDS = 5
MIN_ACTION_STABILITY = 0.80


Cell = tuple[str, str, str]


def normalize_level(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def row_cell(row: dict[str, str]) -> Cell:
    return tuple(normalize_level(row[name]) for name in FEATURES)  # type: ignore[return-value]


def cell_id(cell: Cell) -> str:
    return "|".join(cell)


def stricter_neighbors(cell: Cell) -> list[tuple[str, Cell]]:
    """Return valid one-level, one-parameter stricter configurations."""
    output: list[tuple[str, Cell]] = []
    values = list(cell)
    for position, feature in enumerate(FEATURES):
        levels = LEVELS[feature]
        if values[position] not in levels:
            continue
        index = levels.index(values[position])
        if index + 1 >= len(levels):
            continue
        candidate = list(values)
        candidate[position] = levels[index + 1]
        output.append((feature, tuple(candidate)))  # type: ignore[arg-type]
    return output


@dataclass(frozen=True)
class CellStats:
    rows: int
    builds: int
    applies: int
    not_applies: int
    applies_rate: float
    applies_lower_95: float
    applies_upper_95: float


def build_cell_stats(rows: Iterable[dict[str, str]]) -> dict[Cell, CellStats]:
    grouped: dict[Cell, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row_cell(row)].append(row)
    output: dict[Cell, CellStats] = {}
    for cell, values in grouped.items():
        labels = [technical_label(row) for row in values]
        applies = sum(label == APPLIES for label in labels)
        interval = wilson_interval(applies, len(labels))
        output[cell] = CellStats(
            rows=len(values),
            builds=len({row["Build_Id"] for row in values}),
            applies=applies,
            not_applies=len(values) - applies,
            applies_rate=applies / len(values),
            applies_lower_95=float(interval["lower"]),
            applies_upper_95=float(interval["upper"]),
        )
    return output


def supported(stats: CellStats | None, min_rows: int, min_builds: int = MIN_BUILDS) -> bool:
    return bool(stats and stats.rows >= min_rows and stats.builds >= min_builds)


def recommendation(
    cell: Cell,
    stats_by_cell: dict[Cell, CellStats],
    p_min: float,
    p_review: float,
    min_rows: int,
    min_builds: int = MIN_BUILDS,
) -> dict[str, object]:
    current = stats_by_cell.get(cell)
    base = {
        "cell": cell_id(cell),
        "concurrency": cell[0],
        "iterations": cell[1],
        "response_time": cell[2],
        "current_rows": 0 if current is None else current.rows,
        "current_builds": 0 if current is None else current.builds,
        "current_applies_rate": None if current is None else current.applies_rate,
        "current_applies_lower_95": None if current is None else current.applies_lower_95,
        "current_applies_upper_95": None if current is None else current.applies_upper_95,
        "target_cell": None,
        "changed_parameter": None,
        "from_level": None,
        "to_level": None,
        "to_real_value": None,
        "target_rows": None,
        "target_builds": None,
        "target_applies_rate": None,
        "target_applies_lower_95": None,
    }
    if not supported(current, min_rows, min_builds):
        return {**base, "action": "abstain", "reason": "insufficient_current_support"}

    assert current is not None
    if current.applies_upper_95 < p_review:
        return {**base, "action": "review", "reason": "current_success_upper_below_review_threshold"}

    candidates: list[tuple[float, int, int, str, Cell, CellStats]] = []
    for feature, target in stricter_neighbors(cell):
        target_stats = stats_by_cell.get(target)
        if not supported(target_stats, min_rows, min_builds):
            continue
        assert target_stats is not None
        if target_stats.applies_lower_95 >= p_min:
            candidates.append((
                target_stats.applies_lower_95,
                target_stats.builds,
                target_stats.rows,
                feature,
                target,
                target_stats,
            ))
    if candidates:
        _, _, _, feature, target, target_stats = max(
            candidates, key=lambda item: (item[0], item[1], item[2], item[3], item[4])
        )
        position = FEATURES.index(feature)
        return {
            **base,
            "action": "upgrade",
            "reason": "stricter_neighbor_passes_lower_confidence_guardrail",
            "target_cell": cell_id(target),
            "changed_parameter": feature,
            "from_level": cell[position],
            "to_level": target[position],
            "to_real_value": REAL_VALUES[feature][target[position]],
            "target_rows": target_stats.rows,
            "target_builds": target_stats.builds,
            "target_applies_rate": target_stats.applies_rate,
            "target_applies_lower_95": target_stats.applies_lower_95,
        }

    if current.applies_lower_95 >= p_review:
        return {**base, "action": "maintain", "reason": "current_supported_but_no_safe_stricter_neighbor"}
    return {**base, "action": "abstain", "reason": "current_uncertainty_crosses_review_threshold"}


def apply_stability_guardrail(
    card: dict[str, object], agreement_rate: float, minimum: float = MIN_ACTION_STABILITY
) -> dict[str, object]:
    """Separate the estimated action from the action safe to publish offline."""
    estimated = str(card["action"])
    if estimated == "abstain":
        published = "abstain"
        publication_reason = "estimated_abstention"
    elif agreement_rate < minimum:
        published = "abstain"
        publication_reason = "estimated_action_below_stability_guardrail"
    else:
        published = estimated
        publication_reason = "estimated_action_passes_stability_guardrail"
    return {
        **card,
        "action_estimated": estimated,
        "action_stability": agreement_rate,
        "minimum_action_stability": minimum,
        "action_published": published,
        # Backwards-compatible operational column: action is always the publishable action.
        "action": published,
        "publication_reason": publication_reason,
        "experimental_candidate": estimated if estimated != published else None,
    }


def evaluate_fold(
    training_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    p_min: float,
    p_review: float,
    min_rows: int,
) -> dict[str, object]:
    trained = build_cell_stats(training_rows)
    observed = build_cell_stats(validation_rows)
    source_rows_covered = 0
    evaluated_successes = 0
    evaluated_total = 0
    actions: Counter[str] = Counter()
    for cell, validation_stats in observed.items():
        decision = recommendation(cell, trained, p_min, p_review, min_rows)
        action = str(decision["action"])
        actions[action] += 1
        if action == "abstain":
            continue
        source_rows_covered += validation_stats.rows
        if action == "review":
            evaluated_successes += validation_stats.not_applies
            evaluated_total += validation_stats.rows
        elif action == "maintain":
            evaluated_successes += validation_stats.applies
            evaluated_total += validation_stats.rows
        elif action == "upgrade":
            target = tuple(str(decision["target_cell"]).split("|"))
            target_stats = observed.get(target)  # type: ignore[arg-type]
            if target_stats:
                evaluated_successes += target_stats.applies
                evaluated_total += target_stats.rows
    interval = wilson_interval(evaluated_successes, evaluated_total)
    return {
        "validation_rows": len(validation_rows),
        "validation_cells": len(observed),
        "covered_rows": source_rows_covered,
        "coverage": source_rows_covered / len(validation_rows),
        "evaluated_successes": evaluated_successes,
        "evaluated_total": evaluated_total,
        "decision_success_rate": interval["estimate"],
        "decision_success_lower_95": interval["lower"],
        "decision_success_upper_95": interval["upper"],
        **{f"action_{name}": actions[name] for name in ("abstain", "review", "maintain", "upgrade")},
    }


class RecommenderV3:
    def __init__(self) -> None:
        from performance_decision_engine.infrastructure.configuration_training_v2 import ConfigurationTrainingV2

        self.reader = ConfigurationTrainingV2()

    @staticmethod
    def _load_assignments(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8", newline="") as source:
            return {row["build_id_sha256"]: row["partition"] for row in csv.DictReader(source)}

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def _cv_search(self, rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict[str, object]]:
        groups = [row["Build_Id"] for row in rows]
        labels = [technical_label(row) for row in rows]
        splitter = GroupKFold(n_splits=5)
        grid_rows: list[dict[str, object]] = []
        for p_min in P_MIN_VALUES:
            for p_review in P_REVIEW_VALUES:
                for min_rows in MIN_ROWS_VALUES:
                    folds: list[dict[str, object]] = []
                    for fold, (train, validation) in enumerate(splitter.split(rows, labels, groups), start=1):
                        result = evaluate_fold(
                            [rows[int(i)] for i in train],
                            [rows[int(i)] for i in validation],
                            p_min,
                            p_review,
                            min_rows,
                        )
                        folds.append({"fold": fold, **result})
                    total_success = sum(int(row["evaluated_successes"]) for row in folds)
                    total_evaluated = sum(int(row["evaluated_total"]) for row in folds)
                    interval = wilson_interval(total_success, total_evaluated)
                    coverage = sum(int(row["covered_rows"]) for row in folds) / sum(int(row["validation_rows"]) for row in folds)
                    grid_rows.append({
                        "p_min": p_min,
                        "p_review": p_review,
                        "min_rows": min_rows,
                        "min_builds": MIN_BUILDS,
                        "folds": len(folds),
                        "coverage": coverage,
                        "evaluated_successes": total_success,
                        "evaluated_total": total_evaluated,
                        "decision_success_rate": interval["estimate"],
                        "decision_success_lower_95": interval["lower"],
                        "decision_success_upper_95": interval["upper"],
                        "mean_upgrade_cells": float(np.mean([row["action_upgrade"] for row in folds])),
                        "mean_abstain_cells": float(np.mean([row["action_abstain"] for row in folds])),
                    })
        eligible = [row for row in grid_rows if float(row["coverage"]) >= 0.20 and int(row["evaluated_total"]) > 0]
        pool = eligible or [row for row in grid_rows if int(row["evaluated_total"]) > 0]
        selected = max(
            pool,
            key=lambda row: (
                float(row["decision_success_lower_95"]),
                float(row["coverage"]),
                float(row["mean_upgrade_cells"]),
            ),
        )
        return grid_rows, selected

    @staticmethod
    def _monotonicity(stats: dict[Cell, CellStats]) -> dict[str, object]:
        comparisons = 0
        consistent = 0
        rows: list[dict[str, object]] = []
        for cell, current in stats.items():
            for feature, target in stricter_neighbors(cell):
                target_stats = stats.get(target)
                if not target_stats:
                    continue
                comparisons += 1
                is_consistent = target_stats.applies_rate <= current.applies_rate
                consistent += int(is_consistent)
                rows.append({
                    "source_cell": cell_id(cell),
                    "target_cell": cell_id(target),
                    "changed_parameter": feature,
                    "source_applies_rate": current.applies_rate,
                    "target_applies_rate": target_stats.applies_rate,
                    "monotonic_expected_direction": is_consistent,
                })
        return {
            "comparisons": comparisons,
            "consistent": consistent,
            "consistency_rate": consistent / comparisons if comparisons else None,
            "rows": rows,
        }

    def _bootstrap_stability(
        self,
        rows: list[dict[str, str]],
        cells: list[Cell],
        full_decisions: dict[Cell, str],
        parameters: dict[str, object],
        repetitions: int,
    ) -> list[dict[str, object]]:
        by_build: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            by_build[row["Build_Id"]].append(row)
        builds = sorted(by_build)
        generator = random.Random(RANDOM_STATE)
        agreements: dict[Cell, int] = Counter()
        action_counts: dict[Cell, Counter[str]] = {cell: Counter() for cell in cells}
        for _ in range(repetitions):
            selected = [generator.choice(builds) for _ in builds]
            sampled: list[dict[str, str]] = []
            for draw, build in enumerate(selected):
                for original in by_build[build]:
                    copied = dict(original)
                    copied["Build_Id"] = f"{build}#bootstrap_{draw}"
                    sampled.append(copied)
            stats = build_cell_stats(sampled)
            for cell in cells:
                action = str(recommendation(
                    cell,
                    stats,
                    float(parameters["p_min"]),
                    float(parameters["p_review"]),
                    int(parameters["min_rows"]),
                )["action"])
                action_counts[cell][action] += 1
                agreements[cell] += int(action == full_decisions[cell])
        output: list[dict[str, object]] = []
        for cell in cells:
            counts = action_counts[cell]
            output.append({
                "cell": cell_id(cell),
                "full_action": full_decisions[cell],
                "agreement_rate": agreements[cell] / repetitions,
                "bootstrap_repetitions": repetitions,
                **{f"count_{action}": counts[action] for action in ("abstain", "review", "maintain", "upgrade")},
            })
        return output

    def run(
        self,
        source_path: Path,
        protocol_path: Path,
        assignments_path: Path,
        output_dir: Path,
        bootstrap_repetitions: int = 500,
    ) -> dict[str, object]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        if protocol["source_sha256"] != sha256_file(source_path):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        assignments = self._load_assignments(assignments_path)
        source_rows = self.reader.read_fixed_width(source_path)
        usable = [row for row in source_rows if eligibility_reason(row) == "trainable"]
        development = [
            row for row in usable
            if assignments.get(sha256_text(row["Build_Id"])) in {"train", "dev"}
        ]
        expected_development = int(protocol["partitions"]["train"]["rows"]) + int(protocol["partitions"]["dev"]["rows"])
        if len(development) != expected_development:
            raise ValueError("Development rows differ from frozen protocol")

        grid_rows, selected = self._cv_search(development)
        stats = build_cell_stats(development)
        cells = sorted(stats)
        estimated_cards = [recommendation(
            cell,
            stats,
            float(selected["p_min"]),
            float(selected["p_review"]),
            int(selected["min_rows"]),
        ) for cell in cells]
        full_actions = {
            cell: str(card["action"])
            for cell, card in zip(cells, estimated_cards, strict=True)
        }
        stability = self._bootstrap_stability(
            development, cells, full_actions, selected, bootstrap_repetitions
        )
        stability_by_cell = {
            str(row["cell"]): float(row["agreement_rate"]) for row in stability
        }
        cards = [
            apply_stability_guardrail(card, stability_by_cell[str(card["cell"])])
            for card in estimated_cards
        ]
        monotonicity = self._monotonicity(stats)

        cell_rows = [{
            "cell": cell_id(cell),
            "concurrency": cell[0],
            "iterations": cell[1],
            "response_time": cell[2],
            **vars(value),
        } for cell, value in sorted(stats.items())]
        estimated_distribution = Counter(
            str(card["action_estimated"]) for card in cards
        )
        published_distribution = Counter(
            str(card["action_published"]) for card in cards
        )
        stable_cells = sum(float(row["agreement_rate"]) >= 0.80 for row in stability)

        output_dir.mkdir(parents=True, exist_ok=True)
        self._write_csv(output_dir / "cell_support_v3.csv", cell_rows)
        self._write_csv(output_dir / "recommendation_cards_v3.csv", cards)
        self._write_csv(output_dir / "recommender_cv_search_v3.csv", grid_rows)
        self._write_csv(output_dir / "recommender_stability_v3.csv", stability)
        self._write_csv(output_dir / "recommender_monotonicity_v3.csv", monotonicity["rows"])

        examples = {
            f"published_{action}": next(
                (card for card in cards if card["action_published"] == action), None
            )
            for action in ("abstain", "review", "maintain", "upgrade")
        }
        examples["experimental_upgrade_candidate"] = next(
            (card for card in cards if card["action_estimated"] == "upgrade"), None
        )
        upgrade_example = examples["experimental_upgrade_candidate"]
        upgrade_interpretation = (
            "No upgrade candidate was observed."
            if upgrade_example is None
            else (
                "The observed upgrade remains an experimental candidate because its "
                f"{float(upgrade_example['action_stability']):.1%} stability does not pass "
                f"the {MIN_ACTION_STABILITY:.0%} publication rule."
            )
        )
        (output_dir / "recommendation_examples_v3.json").write_text(
            json.dumps(examples, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        report: dict[str, object] = {
            "schema_version": "3.0",
            "experiment": "configuration_recommender_train_dev_grouped_cv",
            "test_status": "NOT_ACCESSED_RECOMMENDER_TRAIN_DEV_ONLY",
            "rows": len(development),
            "builds": len({row["Build_Id"] for row in development}),
            "cells": len(cells),
            "features": list(FEATURES),
            "selected_rules": {
                key: selected[key] for key in ("p_min", "p_review", "min_rows", "min_builds")
            },
            "selection_cv": selected,
            "stability_guardrail": {
                "minimum_action_stability": MIN_ACTION_STABILITY,
                "rule": "Any non-abstain estimated action below 80% bootstrap agreement is published as abstain.",
            },
            "action_distribution_estimated": dict(sorted(estimated_distribution.items())),
            "action_distribution_published": dict(sorted(published_distribution.items())),
            # Backwards-compatible alias now always refers to publishable actions.
            "action_distribution": dict(sorted(published_distribution.items())),
            "coverage_non_abstain_cells": 1 - published_distribution["abstain"] / len(cells),
            "experimental_upgrade_candidates": estimated_distribution["upgrade"],
            "publishable_upgrades": published_distribution["upgrade"],
            "stability": {
                "bootstrap_repetitions": bootstrap_repetitions,
                "cells_agreement_at_least_80_percent": stable_cells,
                "cells_total": len(cells),
                "fraction_stable": stable_cells / len(cells),
            },
            "monotonicity": {key: monotonicity[key] for key in ("comparisons", "consistent", "consistency_rate")},
            "interpretation": (
                "Offline observational recommendation by configuration cell. Every action must pass support, confidence and 80% bootstrap-stability guardrails. "
                + upgrade_interpretation
            ),
            "limitations": [
                "No causal effect is claimed.",
                "All records in the same configuration cell receive the same recommendation.",
                "Online Gatling validation remains future work.",
                "The independent test was not accessed for rule selection or backtesting.",
            ],
            "gate_status": "PASSED_WITH_CONSERVATIVE_STABILITY_FILTER",
            "next_gate": "Freeze the offline recommender and continue to economic evaluation; online Gatling validation remains future work.",
        }
        (output_dir / "recommender_v3.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report
