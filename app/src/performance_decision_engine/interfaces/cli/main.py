import csv
import hashlib
import json
import platform
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from performance_decision_engine import __version__
from performance_decision_engine.application.use_cases.generate_dataset import (
    GenerateDatasetRow,
)
from performance_decision_engine.application.use_cases.normalize_execution import (
    NormalizeExecution,
)
from performance_decision_engine.application.use_cases.recommend_execution import (
    RecommendExecution,
)
from performance_decision_engine.application.use_cases.train_model import TrainModel
from performance_decision_engine.domain.services.quadrant_service import resolve_quadrant
from performance_decision_engine.infrastructure.batch_execution_discovery import (
    BatchExecutionDiscovery,
    ExecutionFiles,
)
from performance_decision_engine.infrastructure.decision_tree_training_backend import (
    DecisionTreeTrainingBackend,
)
from performance_decision_engine.infrastructure.parsers.gatling_metrics_reader import (
    GatlingMetricsReader,
)
from performance_decision_engine.infrastructure.parsers.yaml_configuration_reader import (
    YamlConfigurationReader,
)
from performance_decision_engine.infrastructure.repositories.json_execution_repository import (
    JsonExecutionRepository,
)

app = typer.Typer(help="Performance Decision Engine")
console = Console()


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    show_version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show application version.",
        ),
    ] = False,
) -> None:
    """Performance Decision Engine CLI."""
    if show_version:
        console.print(__version__)
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@app.command()
def doctor() -> None:
    """Validate the local execution environment."""
    console.print("[bold green]Performance Decision Engine[/bold green]")
    console.print(f"Version: {__version__}")
    console.print(f"Python: {sys.version.split()[0]}")
    console.print(f"Platform: {platform.platform()}")
    console.print("[green]Environment ready[/green]")


@app.command()
def quadrant(
    criticality: Annotated[
        str,
        typer.Option(
            "--criticality",
            help="Criticality level: low, medium or high.",
        ),
    ],
    complexity: Annotated[
        str,
        typer.Option(
            "--complexity",
            help="Complexity level: low, medium or high.",
        ),
    ],
) -> None:
    """Resolve the matrix quadrant from criticality and complexity."""
    try:
        result = resolve_quadrant(criticality, complexity)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    console.print(f"Quadrant: {result.number}")


@app.command()
def normalize(
    performance: Annotated[
        Path,
        typer.Option(
            "--performance",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to performance.yaml.",
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
            help="Path to parametricConfigurationValues.yaml.",
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
            help="Path to global_stats.json.",
        ),
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Output JSON path.",
        ),
    ],
) -> None:
    """Normalize one performance-test execution into a JSON document."""
    try:
        use_case = NormalizeExecution(
            configuration_reader=YamlConfigurationReader(),
            metrics_reader=GatlingMetricsReader(),
        )

        execution = use_case.execute(
            performance_path=performance,
            parameters_path=parameters,
            results_path=results,
        )

        JsonExecutionRepository().save(execution, output)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    console.print(f"[green]Created:[/green] {output}")


@app.command()
def recommend(
    performance: Annotated[
        Path,
        typer.Option(
            "--performance",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to performance.yaml.",
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
            help="Path to parametricConfigurationValues.yaml.",
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
            help="Path to global_stats.json.",
        ),
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
            help="Optional path to assertions.json.",
        ),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Optional recommendation JSON output path.",
        ),
    ] = None,
) -> None:
    """Normalize an execution and generate its baseline recommendation."""
    try:
        normalize_use_case = NormalizeExecution(
            configuration_reader=YamlConfigurationReader(),
            metrics_reader=GatlingMetricsReader(),
        )
        execution = normalize_use_case.execute(
            performance_path=performance,
            parameters_path=parameters,
            results_path=results,
            assertions_path=assertions,
        )
        recommendation = RecommendExecution().execute(execution)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    console.print(f"Recommendation: [bold]{recommendation.action}[/bold]")
    console.print(recommendation.explanation)

    if output is None:
        console.print(recommendation.model_dump_json(indent=2))
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(recommendation.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"[green]Created:[/green] {output}")


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


@app.command()
def dataset(
    performance: Annotated[
        Path,
        typer.Option(
            "--performance",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to performance.yaml.",
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
            help="Path to parametricConfigurationValues.yaml.",
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
            help="Path to global_stats.json.",
        ),
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Dataset CSV output path.",
        ),
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
            help="Optional path to assertions.json.",
        ),
    ] = None,
) -> None:
    """Append one normalized execution and its H6 decision to a CSV dataset."""
    try:
        normalize_use_case = NormalizeExecution(
            configuration_reader=YamlConfigurationReader(),
            metrics_reader=GatlingMetricsReader(),
        )
        execution = normalize_use_case.execute(
            performance_path=performance,
            parameters_path=parameters,
            results_path=results,
            assertions_path=assertions,
        )
        recommendation = RecommendExecution().execute(execution)
        dataset_use_case = GenerateDatasetRow()
        row = dataset_use_case.execute(execution, recommendation)
        _append_dataset_row(output, row, dataset_use_case.fieldnames)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    console.print(f"[green]Appended:[/green] {output}")


@app.command("train-model")
def train_model(
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
    model: Annotated[
        Path,
        typer.Option(
            "--model",
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Output path for the trusted joblib model artifact.",
        ),
    ],
    report: Annotated[
        Path,
        typer.Option(
            "--report",
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Output path for the JSON evaluation report.",
        ),
    ],
) -> None:
    """Train and evaluate the H8 Decision Tree baseline."""
    try:
        result = TrainModel(DecisionTreeTrainingBackend()).execute(
            dataset,
            model,
            report,
        )
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    metrics = result["metrics"]
    if not isinstance(metrics, dict):
        raise typer.Exit(code=2)

    console.print("[bold green]H8 Machine Learning baseline completed[/bold green]")
    console.print(f"Dataset rows: {result['dataset_rows']}")
    console.print(f"Accuracy: {metrics['accuracy']:.4f}")
    console.print(f"Balanced accuracy: {metrics['balanced_accuracy']:.4f}")
    console.print(f"Macro F1: {metrics['macro_f1']:.4f}")
    console.print(f"[green]Model:[/green] {model}")
    console.print(f"[green]Report:[/green] {report}")


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


@app.command("dataset-batch")
def dataset_batch(
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
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Dataset CSV output path.",
        ),
    ],
    report: Annotated[
        Path,
        typer.Option(
            "--report",
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Batch import JSON report path.",
        ),
    ],
    replace: Annotated[
        bool,
        typer.Option(
            "--replace",
            help="Replace the dataset and report before importing.",
        ),
    ] = False,
) -> None:
    """Import historical executions into the H7 dataset."""
    if replace:
        output.unlink(missing_ok=True)
        report.unlink(missing_ok=True)

    previous: dict[str, object] = {}
    if report.exists():
        try:
            loaded = json.loads(report.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            console.print(f"[red]Error:[/red] Invalid existing batch report: {exc}")
            raise typer.Exit(code=2) from exc
        if isinstance(loaded, dict):
            previous = loaded

    processed_entries_value = previous.get("executions", [])
    processed_entries = processed_entries_value if isinstance(processed_entries_value, list) else []
    previous_fingerprints = {
        entry["fingerprint"]
        for entry in processed_entries
        if isinstance(entry, dict) and isinstance(entry.get("fingerprint"), str)
    }

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
    entries: list[dict[str, object]] = [
        dict(entry) for entry in processed_entries if isinstance(entry, dict)
    ]

    try:
        executions = discovery.discover(source)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    for files in executions:
        fingerprint = _batch_fingerprint(files)
        if fingerprint in previous_fingerprints:
            skipped += 1
            continue

        try:
            execution = normalize_use_case.execute(
                performance_path=files.performance,
                parameters_path=files.parameters,
                results_path=files.results,
                assertions_path=files.assertions,
            )
            recommendation = RecommendExecution().execute(execution)
            row = dataset_use_case.execute(execution, recommendation)
            _append_dataset_row(output, row, dataset_use_case.fieldnames)
        except (OSError, ValueError) as exc:
            failed += 1
            entries.append(
                {
                    "execution_id": files.execution_id,
                    "fingerprint": fingerprint,
                    "status": "failed",
                    "error": str(exc),
                }
            )
            continue

        imported += 1
        class_distribution[recommendation.action] += 1
        previous_fingerprints.add(fingerprint)
        entries.append(
            {
                "execution_id": files.execution_id,
                "fingerprint": fingerprint,
                "status": "imported",
                "recommendation_action": recommendation.action,
                "performance": str(files.performance),
                "parameters": str(files.parameters),
                "results": str(files.results),
                "assertions": (str(files.assertions) if files.assertions is not None else None),
            }
        )

    report_payload = {
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
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        json.dumps(report_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    console.print("[bold green]Historical dataset import completed[/bold green]")
    console.print(f"Discovered: {len(executions)}")
    console.print(f"Imported: {imported}")
    console.print(f"Skipped: {skipped}")
    console.print(f"Failed: {failed}")
    console.print(f"Classes: {dict(sorted(class_distribution.items()))}")
    console.print(f"[green]Dataset:[/green] {output}")
    console.print(f"[green]Report:[/green] {report}")

    if failed > 0:
        raise typer.Exit(code=1)
