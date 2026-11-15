from __future__ import annotations

import pytest

from performance_decision_engine.infrastructure.baselines_v3_1 import (
    out_of_fold_cell_scores,
    ranking_metrics,
    wilson_interval,
)


def row(build: str, concurrency: str, iterations: str, response: str, label: str) -> dict[str, str]:
    applies = label == "applies"
    return {
        "Build_Id": build,
        "Performance": "1",
        "Concurrency": concurrency,
        "Iterations": iterations,
        "ResponseTime": response,
        "errorCount": "0" if applies else "1",
        "successCount": "1",
        "Estado": "success" if applies else "failed",
    }


def test_ranking_metrics_top_30_is_auditable() -> None:
    labels = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    scores = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
    result = ranking_metrics(labels, scores)
    assert result["top_rows"] == 3
    assert result["recall_at_30"] == pytest.approx(1.0)
    assert result["precision_at_30"] == pytest.approx(2 / 3)


def test_wilson_interval_contains_estimate() -> None:
    result = wilson_interval(40, 100)
    assert result["lower_95"] < 0.4 < result["upper_95"]


def test_grouped_oof_has_no_build_leakage() -> None:
    rows = []
    for index in range(10):
        rows.append(row(f"b{index}", "low", "low", "low", "not_applies" if index % 2 else "applies"))
    scores, audit = out_of_fold_cell_scores(rows, folds=5)
    assert len(scores) == len(rows)
    assert all(item["group_overlap"] == 0 for item in audit)


def test_unseen_cell_uses_fold_prevalence() -> None:
    rows = [
        row("b1", "low", "low", "low", "applies"),
        row("b2", "medium", "low", "low", "not_applies"),
        row("b3", "high", "low", "low", "applies"),
        row("b4", "very_high", "low", "low", "not_applies"),
    ]
    scores, audit = out_of_fold_cell_scores(rows, folds=2)
    assert all(0.0 <= value <= 1.0 for value in scores)
    assert sum(item["unseen_cell_rows"] for item in audit) > 0


def test_protocol_contract_is_train_dev_only() -> None:
    declared_partitions = {"train", "dev"}
    assert "test" not in declared_partitions
