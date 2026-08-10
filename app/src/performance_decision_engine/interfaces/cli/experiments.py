import json
from collections import Counter
from collections.abc import Mapping
from datetime import datetime
import csv
import hashlib
import math
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from performance_decision_engine.application.use_cases.analyze_dataset import (
    AnalyzeDataset,
)
from performance_decision_engine.application.use_cases.evaluate_evolution import (
    EvaluateEvolution,
    EvolutionObservation,
    load_evolution_history,
)
from performance_decision_engine.application.use_cases.normalize_execution import (
    NormalizeExecution,
)
from performance_decision_engine.application.use_cases.train_model import TrainModel
from performance_decision_engine.application.use_cases.plan_quadrant_action import (
    PlanQuadrantAction,
)
from performance_decision_engine.application.use_cases.predict_execution import (
    PredictExecution,
)
from performance_decision_engine.application.use_cases.recommend_execution import (
    RecommendExecution,
)
from performance_decision_engine.domain.entities.recommendation import Recommendation
from performance_decision_engine.infrastructure.decision_tree_training_backend import (
    DecisionTreeTrainingBackend,
)
from performance_decision_engine.application.use_cases.explain_model import ExplainModel
from performance_decision_engine.application.use_cases.generate_dataset import (
    GenerateDatasetRow,
)
from performance_decision_engine.infrastructure.batch_execution_discovery import (
    BatchExecutionDiscovery,
    ExecutionFiles,
)
from performance_decision_engine.infrastructure.model_evaluator import ModelEvaluator
from performance_decision_engine.infrastructure.parsers.gatling_metrics_reader import (
    GatlingMetricsReader,
)
from performance_decision_engine.infrastructure.parsers.yaml_configuration_reader import (
    YamlConfigurationReader,
)


def _coerce_float(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _std(values: list[float], mean_value: float) -> float:
    variance = sum((value - mean_value) ** 2 for value in values) / len(values)
    return math.sqrt(variance)


def _confidence_interval_95(mean_value: float, std_value: float, n: int) -> dict[str, float]:
    margin = 1.96 * std_value / math.sqrt(n)
    return {
        "low": mean_value - margin,
        "high": mean_value + margin,
        "margin": margin,
    }


def _extract_split_metric_series(
    evaluation_payload: dict[str, object],
    variant_name: str,
    metric_name: str,
) -> list[float]:
    variants_value = evaluation_payload.get("variants")
    if not isinstance(variants_value, dict):
        return []

    variant = variants_value.get(variant_name)
    if not isinstance(variant, dict):
        return []

    splits_value = variant.get("splits")
    if not isinstance(splits_value, list):
        return []

    values: list[float] = []
    for split in splits_value:
        if not isinstance(split, dict):
            continue
        metrics_value = split.get("metrics")
        if not isinstance(metrics_value, dict):
            continue
        metric = _coerce_float(metrics_value.get(metric_name))
        if metric is not None:
            values.append(metric)
    return values


def _paired_delta_report(
    baseline_name: str,
    challenger_name: str,
    baseline_values: list[float],
    challenger_values: list[float],
) -> dict[str, object]:
    n = min(len(baseline_values), len(challenger_values))
    if n < 2:
        return {
            "baseline": baseline_name,
            "challenger": challenger_name,
            "paired_splits": n,
            "status": "insufficient_data",
        }

    deltas = [baseline_values[index] - challenger_values[index] for index in range(n)]
    mean_delta = _mean(deltas)
    std_delta = _std(deltas, mean_delta)
    ci95 = _confidence_interval_95(mean_delta, std_delta, n)
    includes_zero = ci95["low"] <= 0 <= ci95["high"]

    if includes_zero:
        evidence = "inconclusive"
    elif abs(mean_delta) >= 0.20:
        evidence = "strong"
    elif abs(mean_delta) >= 0.10:
        evidence = "moderate"
    else:
        evidence = "weak"

    return {
        "baseline": baseline_name,
        "challenger": challenger_name,
        "paired_splits": n,
        "mean_delta": mean_delta,
        "std_delta": std_delta,
        "ci95": ci95,
        "includes_zero": includes_zero,
        "evidence": evidence,
        "interpretation": (
            "Difference is not statistically clear at 95% CI."
            if includes_zero
            else "Difference is statistically directional at 95% CI."
        ),
    }


def _build_statistical_validity_report(
    evaluation_payload: dict[str, object],
    *,
    focus_metric: str = "macro_f1",
) -> dict[str, object]:
    variants = (
        "all_features",
        "without_assertions",
        "operational_core",
    )
    per_variant: dict[str, object] = {}

    for variant_name in variants:
        values = _extract_split_metric_series(evaluation_payload, variant_name, focus_metric)
        if len(values) < 2:
            per_variant[variant_name] = {
                "split_count": len(values),
                "status": "insufficient_data",
            }
            continue

        mean_value = _mean(values)
        std_value = _std(values, mean_value)
        per_variant[variant_name] = {
            "split_count": len(values),
            "mean": mean_value,
            "std": std_value,
            "ci95": _confidence_interval_95(mean_value, std_value, len(values)),
            "min": min(values),
            "max": max(values),
        }

    all_features_values = _extract_split_metric_series(
        evaluation_payload,
        "all_features",
        focus_metric,
    )
    without_assertions_values = _extract_split_metric_series(
        evaluation_payload,
        "without_assertions",
        focus_metric,
    )
    operational_values = _extract_split_metric_series(
        evaluation_payload,
        "operational_core",
        focus_metric,
    )

    all_vs_operational = _paired_delta_report(
        "all_features",
        "operational_core",
        all_features_values,
        operational_values,
    )
    woa_vs_operational = _paired_delta_report(
        "without_assertions",
        "operational_core",
        without_assertions_values,
        operational_values,
    )

    conclusion = "insufficient_data"
    if isinstance(all_vs_operational.get("evidence"), str):
        conclusion = all_vs_operational["evidence"]

    return {
        "schema_version": "1",
        "focus_metric": focus_metric,
        "per_variant": per_variant,
        "paired_comparisons": {
            "all_features_vs_operational_core": all_vs_operational,
            "without_assertions_vs_operational_core": woa_vs_operational,
        },
        "conclusion": {
            "evidence_level": conclusion,
            "summary": (
                "Operational core behaves similarly to proxy-rich variants."
                if conclusion in {"weak", "inconclusive"}
                else "Proxy-rich variants outperform operational core with statistically directional gap."
            ),
        },
    }


def _metric_mean(
    evaluation_payload: dict[str, object],
    variant_name: str,
    metric_name: str,
) -> float | None:
    variants_value = evaluation_payload.get("variants")
    if not isinstance(variants_value, dict):
        return None

    variant = variants_value.get(variant_name)
    if not isinstance(variant, dict):
        return None

    metrics_value = variant.get("metrics")
    if not isinstance(metrics_value, dict):
        return None

    metric = metrics_value.get(metric_name)
    if not isinstance(metric, dict):
        return None

    return _coerce_float(metric.get("mean"))


def _read_json_dict(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(loaded, dict):
        return loaded
    raise ValueError(f"Invalid JSON object in {path}.")


def _created_at_from_run_id(run_id: str) -> str:
    prefix = "run_"
    if not run_id.startswith(prefix):
        return datetime.now().isoformat(timespec="seconds")

    timestamp = run_id[len(prefix) :]
    main_part = timestamp.split("_")
    if len(main_part) < 2:
        return datetime.now().isoformat(timespec="seconds")

    candidate = f"{main_part[0]}_{main_part[1]}"
    try:
        parsed = datetime.strptime(candidate, "%Y%m%d_%H%M%S")
    except ValueError:
        return datetime.now().isoformat(timespec="seconds")
    return parsed.isoformat(timespec="seconds")


def _build_run_record(
    *,
    run_directory: Path,
    source: Path,
    seeds: int,
    feature_profile: str,
    batch_import: dict[str, object],
    dataset_quality: dict[str, object],
    training_result: dict[str, object],
    evaluation_payload: dict[str, object],
) -> dict[str, object]:
    training_metrics_value = training_result.get("metrics")
    training_metrics = (
        training_metrics_value if isinstance(training_metrics_value, dict) else {}
    )

    return {
        "run_id": run_directory.name,
        "run_directory": str(run_directory),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source": str(source),
        "seeds": seeds,
        "feature_profile": feature_profile,
        "dataset_rows": dataset_quality.get("rows"),
        "class_distribution": dataset_quality.get("class_distribution"),
        "duplicate_rows": dataset_quality.get("duplicate_rows"),
        "imported_this_run": batch_import.get("imported_this_run"),
        "failed_this_run": batch_import.get("failed_this_run"),
        "training_metrics": {
            "accuracy": _coerce_float(training_metrics.get("accuracy")),
            "balanced_accuracy": _coerce_float(training_metrics.get("balanced_accuracy")),
            "macro_f1": _coerce_float(training_metrics.get("macro_f1")),
        },
        "multiseed_metrics_mean": {
            "all_features_macro_f1": _metric_mean(
                evaluation_payload,
                "all_features",
                "macro_f1",
            ),
            "without_assertions_macro_f1": _metric_mean(
                evaluation_payload,
                "without_assertions",
                "macro_f1",
            ),
            "operational_core_macro_f1": _metric_mean(
                evaluation_payload,
                "operational_core",
                "macro_f1",
            ),
        },
    }


def _build_run_record_from_directory(run_directory: Path) -> dict[str, object] | None:
    summary_path = run_directory / "auto_evaluation_summary.json"
    if not summary_path.exists():
        return None

    try:
        summary = _read_json_dict(summary_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None

    source_value = summary.get("source")
    source = source_value if isinstance(source_value, str) else ""
    seeds_value = summary.get("seeds")
    seeds = int(seeds_value) if isinstance(seeds_value, int) else 0
    feature_profile_value = summary.get("feature_profile")
    feature_profile = feature_profile_value if isinstance(feature_profile_value, str) else ""

    batch_import_value = summary.get("batch_import")
    batch_import = batch_import_value if isinstance(batch_import_value, dict) else {}
    dataset_quality_value = summary.get("dataset_quality")
    dataset_quality = dataset_quality_value if isinstance(dataset_quality_value, dict) else {}
    training_value = summary.get("training")
    training = training_value if isinstance(training_value, dict) else {}
    training_metrics_value = training.get("metrics")
    training_metrics = training_metrics_value if isinstance(training_metrics_value, dict) else {}

    artifacts_value = summary.get("artifacts")
    artifacts = artifacts_value if isinstance(artifacts_value, dict) else {}
    multiseed_eval_value = artifacts.get("multiseed_evaluation")
    evaluation_payload: dict[str, object] = {}
    if isinstance(multiseed_eval_value, str):
        evaluation_path = Path(multiseed_eval_value)
        if evaluation_path.exists():
            try:
                evaluation_payload = _read_json_dict(evaluation_path)
            except (OSError, ValueError, json.JSONDecodeError):
                evaluation_payload = {}

    return {
        "run_id": run_directory.name,
        "run_directory": str(run_directory),
        "created_at": _created_at_from_run_id(run_directory.name),
        "source": source,
        "seeds": seeds,
        "feature_profile": feature_profile,
        "dataset_rows": dataset_quality.get("rows"),
        "class_distribution": dataset_quality.get("class_distribution"),
        "duplicate_rows": dataset_quality.get("duplicate_rows"),
        "imported_this_run": batch_import.get("imported_this_run"),
        "failed_this_run": batch_import.get("failed_this_run"),
        "training_metrics": {
            "accuracy": _coerce_float(training_metrics.get("accuracy")),
            "balanced_accuracy": _coerce_float(training_metrics.get("balanced_accuracy")),
            "macro_f1": _coerce_float(training_metrics.get("macro_f1")),
        },
        "multiseed_metrics_mean": {
            "all_features_macro_f1": _metric_mean(
                evaluation_payload,
                "all_features",
                "macro_f1",
            ),
            "without_assertions_macro_f1": _metric_mean(
                evaluation_payload,
                "without_assertions",
                "macro_f1",
            ),
            "operational_core_macro_f1": _metric_mean(
                evaluation_payload,
                "operational_core",
                "macro_f1",
            ),
        },
    }


def _discover_run_records(output_base: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for entry in sorted(output_base.iterdir()):
        if not entry.is_dir() or not entry.name.startswith("run_"):
            continue
        record = _build_run_record_from_directory(entry)
        if record is not None:
            records.append(record)
    return records


def _update_runs_index(
    index_path: Path,
    run_record: dict[str, object],
    output_base: Path,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = _discover_run_records(output_base)
    if index_path.exists():
        loaded = _read_json_dict(index_path)
        previous_records = loaded.get("runs")
        if isinstance(previous_records, list):
            records.extend(dict(item) for item in previous_records if isinstance(item, dict))

    run_id = run_record.get("run_id")
    deduped: dict[str, dict[str, object]] = {}
    for item in records:
        item_run_id = item.get("run_id")
        if isinstance(item_run_id, str):
            deduped[item_run_id] = item
    if isinstance(run_id, str):
        deduped[run_id] = run_record
    records = list(deduped.values())
    records.sort(key=lambda item: str(item.get("run_id", "")))

    payload = {
        "schema_version": "1",
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "runs": records,
    }
    _write_json(index_path, payload)
    return records


def _build_runs_comparison(
    runs: list[dict[str, object]],
) -> dict[str, object]:
    if not runs:
        return {
            "schema_version": "1",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "total_runs": 0,
            "message": "No runs available.",
            "runs": [],
        }

    best_operational = None
    best_all_features = None

    for run in runs:
        means_value = run.get("multiseed_metrics_mean")
        means = means_value if isinstance(means_value, dict) else {}

        operational = _coerce_float(means.get("operational_core_macro_f1"))
        all_features = _coerce_float(means.get("all_features_macro_f1"))

        if operational is not None:
            if best_operational is None or operational > best_operational["score"]:
                best_operational = {
                    "run_id": run.get("run_id"),
                    "score": operational,
                }

        if all_features is not None:
            if best_all_features is None or all_features > best_all_features["score"]:
                best_all_features = {
                    "run_id": run.get("run_id"),
                    "score": all_features,
                }

    latest_run = max(runs, key=lambda item: str(item.get("run_id", "")))
    previous_run = None
    if len(runs) >= 2:
        previous_run = sorted(runs, key=lambda item: str(item.get("run_id", "")))[-2]

    latest_means_value = latest_run.get("multiseed_metrics_mean")
    latest_means = latest_means_value if isinstance(latest_means_value, dict) else {}
    previous_means: dict[str, object] = {}
    if previous_run is not None:
        previous_means_value = previous_run.get("multiseed_metrics_mean")
        if isinstance(previous_means_value, dict):
            previous_means = previous_means_value

    latest_operational = _coerce_float(latest_means.get("operational_core_macro_f1"))
    previous_operational = _coerce_float(previous_means.get("operational_core_macro_f1"))

    operational_delta = None
    if latest_operational is not None and previous_operational is not None:
        operational_delta = latest_operational - previous_operational

    latest_all_features = _coerce_float(latest_means.get("all_features_macro_f1"))
    overfit_gap = None
    if latest_all_features is not None and latest_operational is not None:
        overfit_gap = latest_all_features - latest_operational

    overfit_risk = "unknown"
    if overfit_gap is not None:
        if overfit_gap >= 0.25:
            overfit_risk = "high"
        elif overfit_gap >= 0.10:
            overfit_risk = "medium"
        else:
            overfit_risk = "low"

    leaderboard = sorted(
        runs,
        key=lambda item: (
            _coerce_float(
                (
                    item.get("multiseed_metrics_mean", {})
                    if isinstance(item.get("multiseed_metrics_mean"), dict)
                    else {}
                ).get("operational_core_macro_f1")
            )
            or -1.0
        ),
        reverse=True,
    )

    top_operational_runs = [
        {
            "rank": rank,
            "run_id": run.get("run_id"),
            "operational_core_macro_f1": _coerce_float(
                (
                    run.get("multiseed_metrics_mean", {})
                    if isinstance(run.get("multiseed_metrics_mean"), dict)
                    else {}
                ).get("operational_core_macro_f1")
            ),
            "all_features_macro_f1": _coerce_float(
                (
                    run.get("multiseed_metrics_mean", {})
                    if isinstance(run.get("multiseed_metrics_mean"), dict)
                    else {}
                ).get("all_features_macro_f1")
            ),
            "seeds": run.get("seeds"),
        }
        for rank, run in enumerate(leaderboard[:5], start=1)
    ]

    return {
        "schema_version": "1",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_runs": len(runs),
        "latest_run": latest_run,
        "previous_run": previous_run,
        "best_operational_core_macro_f1": best_operational,
        "best_all_features_macro_f1": best_all_features,
        "operational_core_delta_vs_previous": operational_delta,
        "latest_overfit_gap": overfit_gap,
        "latest_overfit_risk": overfit_risk,
        "top_operational_runs": top_operational_runs,
        "runs": runs,
    }


def _write_json(output: Path, payload: dict[str, object]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _append_dataset_row(
    output: Path,
    row: Mapping[str, object],
    fieldnames: tuple[str, ...],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists() and output.stat().st_size > 0:
        with output.open("r", encoding="utf-8", newline="") as source:
            existing_header = next(csv.reader(source), [])
        if tuple(existing_header) != fieldnames:
            raise ValueError("The existing dataset header is incompatible with schema version 1.")

    write_header = not output.exists() or output.stat().st_size == 0
    with output.open("a", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def _build_run_directory(base_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = base_dir / f"run_{timestamp}"
    suffix = 1
    while candidate.exists():
        candidate = base_dir / f"run_{timestamp}_{suffix:02d}"
        suffix += 1
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def _batch_fingerprint(files: ExecutionFiles) -> str:
    digest = hashlib.sha256()
    for path in (
        files.performance,
        files.parameters,
        files.results,
        files.assertions,
    ):
        if path is None:
            digest.update(b"<missing>")
            continue
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _component_id_from_execution_id(execution_id: str) -> str:
    normalized = execution_id.strip("/")
    if not normalized:
        return "unknown_component"
    return normalized.split("/", 1)[0]


def _build_evolution_observation(
    component_id: str,
    recommendation_action: str,
    execution,
    target_ms: int | None,
) -> EvolutionObservation | None:
    p95 = execution.global_metrics.p95_response_time_ms
    if p95 is None or target_ms is None or target_ms <= 0:
        return None

    assertions = execution.global_metrics.assertions
    return EvolutionObservation(
        component_id=component_id,
        recommendation_action=recommendation_action,
        p95_response_time_ms=p95,
        response_time_target_ms=target_ms,
        error_rate_percent=execution.global_metrics.error_rate_percent,
        assertions_all_passed=(assertions is None or assertions.all_passed),
    )


def _import_batch_dataset(
    source: Path,
    output: Path,
    report: Path,
) -> dict[str, object]:
    discovery = BatchExecutionDiscovery()
    normalize_use_case = NormalizeExecution(
        configuration_reader=YamlConfigurationReader(),
        metrics_reader=GatlingMetricsReader(),
    )
    dataset_use_case = GenerateDatasetRow()

    imported = 0
    skipped = 0
    failed = 0
    class_distribution: Counter[str] = Counter()
    entries: list[dict[str, object]] = []
    fingerprints: set[str] = set()
    evolution_evaluator = EvaluateEvolution()
    history_by_component: dict[str, list[EvolutionObservation]] = {}

    executions = discovery.discover(source)
    for files in executions:
        component_id = _component_id_from_execution_id(files.execution_id)
        fingerprint = _batch_fingerprint(files)
        if fingerprint in fingerprints:
            skipped += 1
            continue

        try:
            execution = normalize_use_case.execute(
                performance_path=files.performance,
                parameters_path=files.parameters,
                results_path=files.results,
                assertions_path=files.assertions,
            )
            baseline_recommendation = RecommendExecution().execute(execution)
            recommendation = evolution_evaluator.execute(
                component_id,
                baseline_recommendation,
                history_by_component.get(component_id, []),
            )
            row = dataset_use_case.execute(execution, recommendation)
            _append_dataset_row(output, row, dataset_use_case.fieldnames)

            baseline_target_raw = baseline_recommendation.evidence.get("expected_response_time_ms")
            baseline_target = baseline_target_raw if isinstance(baseline_target_raw, int) else None
            observation = _build_evolution_observation(
                component_id,
                baseline_recommendation.action,
                execution,
                baseline_target,
            )
            if observation is not None:
                history_by_component.setdefault(component_id, []).append(observation)
        except (OSError, ValueError) as exc:
            failed += 1
            entries.append(
                {
                    "component_id": component_id,
                    "execution_id": files.execution_id,
                    "fingerprint": fingerprint,
                    "status": "failed",
                    "error": str(exc),
                }
            )
            continue

        imported += 1
        class_distribution[recommendation.action] += 1
        fingerprints.add(fingerprint)
        entries.append(
            {
                "component_id": component_id,
                "execution_id": files.execution_id,
                "fingerprint": fingerprint,
                "status": "imported",
                "recommendation_action": recommendation.action,
                "baseline_recommendation_action": baseline_recommendation.action,
                "performance": str(files.performance),
                "parameters": str(files.parameters),
                "results": str(files.results),
                "assertions": str(files.assertions) if files.assertions is not None else None,
            }
        )

    payload = {
        "schema_version": "1",
        "source": str(source),
        "output": str(output),
        "discovered": len(executions),
        "imported_this_run": imported,
        "skipped_this_run": skipped,
        "failed_this_run": failed,
        "class_distribution_this_run": dict(sorted(class_distribution.items())),
        "executions": entries,
    }
    _write_json(report, payload)
    return payload


def _write_seed_reports(
    output_dir: Path,
    comparison_payload: dict[str, object],
) -> list[str]:
    variants_value = comparison_payload.get("variants")
    if not isinstance(variants_value, dict):
        return []

    variants: dict[str, dict[str, object]] = {
        name: value
        for name, value in variants_value.items()
        if isinstance(name, str) and isinstance(value, dict)
    }

    split_ids: set[int] = set()
    for variant in variants.values():
        splits_value = variant.get("splits")
        if not isinstance(splits_value, list):
            continue
        for split in splits_value:
            if isinstance(split, dict) and isinstance(split.get("split_id"), int):
                split_ids.add(split["split_id"])

    output_dir.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for split_id in sorted(split_ids):
        per_variant: dict[str, object] = {}
        for variant_name, variant in variants.items():
            splits_value = variant.get("splits")
            if not isinstance(splits_value, list):
                continue
            split = next(
                (
                    item
                    for item in splits_value
                    if isinstance(item, dict) and item.get("split_id") == split_id
                ),
                None,
            )
            if split is not None:
                per_variant[variant_name] = split

        seed_payload = {
            "schema_version": "1",
            "seed": split_id,
            "test_size": comparison_payload.get("test_size"),
            "split_random_state": comparison_payload.get("split_random_state"),
            "variants": per_variant,
        }
        filename = f"seed_{split_id:02d}.json"
        target = output_dir / filename
        _write_json(target, seed_payload)
        created.append(filename)
    return created


def register_experiment_commands(app: typer.Typer, console: Console) -> None:
    """Register post-H10 commands used to strengthen the academic PoC."""

    @app.command("data-quality")
    def data_quality(
        dataset: Annotated[
            Path,
            typer.Option(
                "--dataset",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
                help="Path to the H7 dataset CSV.",
            ),
        ],
        output: Annotated[
            Path,
            typer.Option("--output", resolve_path=True, help="Quality report JSON path."),
        ],
    ) -> None:
        """Analyze completeness, duplicates and class distribution."""
        try:
            result = AnalyzeDataset().execute(dataset)
            _write_json(output, result)
        except (OSError, ValueError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=2) from exc
        console.print("[bold green]Dataset quality analysis completed[/bold green]")
        console.print(f"Rows: {result['rows']}")
        console.print(f"Empty columns: {result['completely_empty_columns']}")
        console.print(f"Duplicate rows: {result['duplicate_rows']}")
        console.print(f"[green]Report:[/green] {output}")

    @app.command("evaluate-model")
    def evaluate_model(
        dataset: Annotated[
            Path,
            typer.Option(
                "--dataset",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
                help="Path to the H7 dataset CSV.",
            ),
        ],
        output: Annotated[
            Path,
            typer.Option("--output", resolve_path=True, help="Evaluation report JSON path."),
        ],
        seeds: Annotated[
            int,
            typer.Option("--seeds", min=2, max=100, help="Repeated holdout splits."),
        ] = 30,
    ) -> None:
        """Compare the complete H8 model with an assertion-free ablation."""
        try:
            result = ModelEvaluator().evaluate(dataset, output, seeds=seeds)
        except (OSError, ValueError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=2) from exc
        variants = result["variants"]
        if not isinstance(variants, dict):
            raise typer.Exit(code=2)
        console.print("[bold green]Model comparison completed[/bold green]")
        for name, value in variants.items():
            if isinstance(value, dict):
                metrics = value.get("metrics")
                if isinstance(metrics, dict):
                    macro_f1 = metrics.get("macro_f1")
                    if isinstance(macro_f1, dict):
                        console.print(f"{name} macro F1: {macro_f1['mean']:.4f}")
        console.print(f"[green]Report:[/green] {output}")

    @app.command("predict")
    def predict(
        model: Annotated[
            Path,
            typer.Option(
                "--model",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
            ),
        ],
        performance: Annotated[
            Path,
            typer.Option(
                "--performance",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
            ),
        ],
        parameters: Annotated[
            Path,
            typer.Option(
                "--parameters",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
            ),
        ],
        results: Annotated[
            Path,
            typer.Option(
                "--results",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
            ),
        ],
        output: Annotated[
            Path,
            typer.Option("--output", resolve_path=True, help="Prediction JSON path."),
        ],
        assertions: Annotated[
            Path | None,
            typer.Option(
                "--assertions",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
            ),
        ] = None,
    ) -> None:
        """Predict one execution and compare H8 with deterministic H6."""
        try:
            execution = NormalizeExecution(
                configuration_reader=YamlConfigurationReader(),
                metrics_reader=GatlingMetricsReader(),
            ).execute(performance, parameters, results, assertions)
            recommendation = RecommendExecution().execute(execution)
            prediction = PredictExecution(DecisionTreeTrainingBackend()).execute(
                model,
                execution,
                recommendation,
            )
            _write_json(output, prediction)
        except (OSError, ValueError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=2) from exc
        console.print("[bold green]Individual prediction completed[/bold green]")
        console.print(f"Prediction: {prediction['prediction']}")
        console.print(f"H6 recommendation: {prediction['rule_based_recommendation']}")
        console.print(f"Agreement: {prediction['agreement']}")
        console.print(f"[green]Output:[/green] {output}")

    @app.command("plan-quadrant")
    def plan_quadrant(
        recommendation_path: Annotated[
            Path,
            typer.Option(
                "--recommendation",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
            ),
        ],
        current_quadrant: Annotated[
            int,
            typer.Option("--current-quadrant", min=1, max=9),
        ],
        output: Annotated[
            Path,
            typer.Option("--output", resolve_path=True, help="Action plan JSON path."),
        ],
    ) -> None:
        """Link an H6 recommendation to a controlled quadrant action."""
        try:
            recommendation = Recommendation.model_validate_json(
                recommendation_path.read_text(encoding="utf-8")
            )
            plan = PlanQuadrantAction().execute(recommendation, current_quadrant)
            _write_json(output, plan)
        except (OSError, ValueError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=2) from exc
        console.print("[bold green]Quadrant action plan completed[/bold green]")
        console.print(f"Action: {plan['action']}")
        console.print(f"Human validation: {plan['human_validation_required']}")
        console.print(f"[green]Output:[/green] {output}")

    @app.command("evaluate-evolution")
    def evaluate_evolution(
        recommendation_path: Annotated[
            Path,
            typer.Option(
                "--recommendation",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
            ),
        ],
        history_path: Annotated[
            Path,
            typer.Option(
                "--history",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
                help="Comparable component history CSV, oldest row first.",
            ),
        ],
        component_id: Annotated[
            str,
            typer.Option("--component-id", min=1, help="Stable component identifier."),
        ],
        output: Annotated[
            Path,
            typer.Option("--output", resolve_path=True, help="Evaluated recommendation JSON."),
        ],
    ) -> None:
        """Evaluate whether a compliant component can evolve its load."""
        try:
            recommendation = Recommendation.model_validate_json(
                recommendation_path.read_text(encoding="utf-8")
            )
            history = load_evolution_history(history_path)
            evaluated = EvaluateEvolution().execute(
                component_id,
                recommendation,
                history,
            )
            _write_json(output, evaluated.model_dump())
        except (OSError, ValueError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=2) from exc
        console.print("[bold green]Evolution evaluation completed[/bold green]")
        console.print(f"Component: {component_id}")
        console.print(f"Recommendation: {evaluated.action}")
        console.print(f"[green]Output:[/green] {output}")

    @app.command("auto-evaluate")
    def auto_evaluate(
        source: Annotated[
            Path,
            typer.Option(
                "--source",
                exists=True,
                file_okay=False,
                dir_okay=True,
                readable=True,
                resolve_path=True,
                help="Directory containing historical performance executions.",
            ),
        ] = Path("examples/input/sources"),
        output_base: Annotated[
            Path,
            typer.Option(
                "--output-base",
                file_okay=False,
                dir_okay=True,
                resolve_path=True,
                help="Base directory where a timestamped run folder will be created.",
            ),
        ] = Path("examples/output"),
        seeds: Annotated[
            int,
            typer.Option(
                "--seeds",
                min=2,
                max=100,
                help="Repeated holdout splits for multiseed evaluation.",
            ),
        ] = 30,
        feature_profile: Annotated[
            str,
            typer.Option(
                "--feature-profile",
                help="Feature profile for training: all_features or operational_core.",
            ),
        ] = "operational_core",
    ) -> None:
        """Run full automatic historical evaluation with general and per-seed artifacts."""
        run_dir = _build_run_directory(output_base)
        runs_index_path = output_base / "runs_index.json"
        runs_comparison_path = output_base / "runs_comparison_latest.json"

        dataset_path = run_dir / "historical_dataset.csv"
        import_report_path = run_dir / "historical_batch_report.json"
        quality_report_path = run_dir / "dataset_quality.json"
        model_path = run_dir / "historical_decision_tree.joblib"
        model_report_path = run_dir / "historical_model_report.json"
        model_explanation_path = run_dir / "historical_model_explanation.json"
        evaluation_path = run_dir / "multiseed_evaluation.json"
        statistical_validity_path = run_dir / "statistical_validity_report.json"
        seed_reports_dir = run_dir / "seed_reports"
        summary_path = run_dir / "auto_evaluation_summary.json"

        try:
            batch_import = _import_batch_dataset(source, dataset_path, import_report_path)
            dataset_quality = AnalyzeDataset().execute(dataset_path)
            _write_json(quality_report_path, dataset_quality)

            backend = DecisionTreeTrainingBackend()
            training_result = TrainModel(backend).execute(
                dataset_path,
                model_path,
                model_report_path,
                feature_profile=feature_profile,
            )
            model_explanation = ExplainModel(backend).execute(
                model_path,
                model_explanation_path,
            )

            evaluation_payload = ModelEvaluator().evaluate(
                dataset_path,
                evaluation_path,
                seeds=seeds,
            )
            statistical_validity = _build_statistical_validity_report(evaluation_payload)
            _write_json(statistical_validity_path, statistical_validity)
            seed_files = _write_seed_reports(seed_reports_dir, evaluation_payload)
        except (OSError, ValueError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            console.print(f"[yellow]Run directory (partial):[/yellow] {run_dir}")
            raise typer.Exit(code=2) from exc

        summary = {
            "schema_version": "1",
            "source": str(source),
            "run_directory": str(run_dir),
            "seeds": seeds,
            "feature_profile": feature_profile,
            "batch_import": batch_import,
            "dataset_quality": {
                "rows": dataset_quality.get("rows"),
                "class_distribution": dataset_quality.get("class_distribution"),
                "duplicate_rows": dataset_quality.get("duplicate_rows"),
            },
            "training": {
                "dataset_rows": training_result.get("dataset_rows"),
                "metrics": training_result.get("metrics"),
            },
            "artifacts": {
                "historical_dataset": str(dataset_path),
                "historical_batch_report": str(import_report_path),
                "dataset_quality": str(quality_report_path),
                "historical_model": str(model_path),
                "historical_model_report": str(model_report_path),
                "historical_model_explanation": str(model_explanation_path),
                "multiseed_evaluation": str(evaluation_path),
                "multiseed_evaluation_splits": str(
                    evaluation_path.with_name(f"{evaluation_path.stem}_splits.csv")
                ),
                "statistical_validity_report": str(statistical_validity_path),
                "seed_reports_dir": str(seed_reports_dir),
                "seed_reports": seed_files,
            },
            "model_explanation": {
                "model_type": model_explanation.get("model_type"),
                "classes": model_explanation.get("classes"),
            },
            "statistical_validity": {
                "evidence_level": (
                    statistical_validity.get("conclusion", {})
                    if isinstance(statistical_validity.get("conclusion"), dict)
                    else {}
                ).get("evidence_level"),
                "summary": (
                    statistical_validity.get("conclusion", {})
                    if isinstance(statistical_validity.get("conclusion"), dict)
                    else {}
                ).get("summary"),
            },
        }
        _write_json(summary_path, summary)

        run_record = _build_run_record(
            run_directory=run_dir,
            source=source,
            seeds=seeds,
            feature_profile=feature_profile,
            batch_import=batch_import,
            dataset_quality=dataset_quality,
            training_result=training_result,
            evaluation_payload=evaluation_payload,
        )
        runs = _update_runs_index(runs_index_path, run_record, output_base)
        comparison = _build_runs_comparison(runs)
        _write_json(runs_comparison_path, comparison)
        _write_json(run_dir / "runs_comparison_snapshot.json", comparison)

        console.print("[bold green]Automatic historical evaluation completed[/bold green]")
        console.print(f"Run directory: {run_dir}")
        console.print(f"Imported executions: {batch_import['imported_this_run']}")
        console.print(f"Seed reports: {len(seed_files)}")
        console.print(f"Runs index: {runs_index_path}")
        console.print(f"Runs comparison: {runs_comparison_path}")
        console.print(
            f"Overfit risk (latest): {comparison.get('latest_overfit_risk')} "
            f"(gap={comparison.get('latest_overfit_gap')})"
        )
        top_runs = comparison.get("top_operational_runs")
        if isinstance(top_runs, list):
            for row in top_runs[:3]:
                if isinstance(row, dict):
                    console.print(
                        "Top "
                        f"#{row.get('rank')}: {row.get('run_id')} "
                        f"operational_core_macro_f1={row.get('operational_core_macro_f1')}"
                    )
        conclusion_value = statistical_validity.get("conclusion")
        if isinstance(conclusion_value, dict):
            console.print(
                "Statistical validity: "
                f"{conclusion_value.get('evidence_level')} "
                f"- {conclusion_value.get('summary')}"
            )
        console.print(f"[green]Summary:[/green] {summary_path}")

    @app.command("compare-runs")
    def compare_runs(
        output_base: Annotated[
            Path,
            typer.Option(
                "--output-base",
                exists=True,
                file_okay=False,
                dir_okay=True,
                readable=True,
                resolve_path=True,
                help="Base directory where run folders and runs_index.json are stored.",
            ),
        ] = Path("examples/output"),
        output: Annotated[
            Path | None,
            typer.Option(
                "--output",
                resolve_path=True,
                help="Optional explicit output path for consolidated comparison JSON.",
            ),
        ] = None,
    ) -> None:
        """Generate consolidated comparison from the central runs index."""
        index_path = output_base / "runs_index.json"
        if index_path.exists():
            try:
                index_payload = _read_json_dict(index_path)
            except ValueError as exc:
                console.print(f"[red]Error:[/red] {exc}")
                raise typer.Exit(code=2) from exc

            runs_value = index_payload.get("runs")
            if not isinstance(runs_value, list):
                console.print(f"[red]Error:[/red] Invalid runs list in {index_path}")
                raise typer.Exit(code=2)
            runs = [dict(item) for item in runs_value if isinstance(item, dict)]
        else:
            runs = _discover_run_records(output_base)
            rebuilt_index = {
                "schema_version": "1",
                "updated_at": datetime.now().isoformat(timespec="seconds"),
                "runs": runs,
            }
            _write_json(index_path, rebuilt_index)

        comparison = _build_runs_comparison(runs)
        target = output if output is not None else (output_base / "runs_comparison_latest.json")
        _write_json(target, comparison)

        console.print("[bold green]Runs comparison generated[/bold green]")
        console.print(f"Runs analyzed: {comparison['total_runs']}")
        console.print(f"[green]Output:[/green] {target}")
