import csv
import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from performance_decision_engine.application.use_cases.explain_model import ExplainModel
from performance_decision_engine.application.use_cases.generate_dataset import (
    GenerateDatasetRow,
)
from performance_decision_engine.application.use_cases.normalize_execution import (
    NormalizeExecution,
)
from performance_decision_engine.application.use_cases.recommend_execution import (
    RecommendExecution,
)
from performance_decision_engine.application.use_cases.run_pipeline import RunPipeline
from performance_decision_engine.application.use_cases.train_model import TrainModel
from performance_decision_engine.infrastructure.decision_tree_training_backend import (
    DecisionTreeTrainingBackend,
)
from performance_decision_engine.infrastructure.parsers.gatling_metrics_reader import (
    GatlingMetricsReader,
)
from performance_decision_engine.infrastructure.parsers.yaml_configuration_reader import (
    YamlConfigurationReader,
)
from performance_decision_engine.infrastructure.reporting.html_report_generator import (
    HtmlReportGenerator,
)


def _append_dataset_row(
    output: Path,
    row: dict[str, str | int | float | bool | None],
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


def register_pipeline_command(app: typer.Typer, console: Console) -> None:
    """Register the H10 command without increasing the size of main.py further."""

    @app.command("pipeline")
    def pipeline(
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
        output_dir: Annotated[
            Path,
            typer.Option(
                "--output-dir",
                file_okay=False,
                dir_okay=True,
                resolve_path=True,
                help="Directory for all H10 artifacts.",
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
        train: Annotated[
            bool,
            typer.Option(
                "--train",
                help="Attempt H8 training and H9 model explanation.",
            ),
        ] = False,
    ) -> None:
        """Run the local H10 end-to-end proof of concept."""
        output_dir.mkdir(parents=True, exist_ok=True)

        execution_path = output_dir / "execution_summary.json"
        recommendation_path = output_dir / "recommendation.json"
        dataset_path = output_dir / "dataset.csv"
        model_path = output_dir / "model.joblib"
        training_report_path = output_dir / "training_report.json"
        explanation_path = output_dir / "model_explanation.json"
        report_path = output_dir / "report.html"
        summary_path = output_dir / "pipeline_summary.json"

        use_case = RunPipeline(
            normalization=NormalizeExecution(
                configuration_reader=YamlConfigurationReader(),
                metrics_reader=GatlingMetricsReader(),
            ),
            recommendation=RecommendExecution(),
            dataset=GenerateDatasetRow(),
        )

        try:
            result = use_case.execute(
                performance_path=performance,
                parameters_path=parameters,
                results_path=results,
                assertions_path=assertions,
            )
            execution_path.write_text(
                result.execution.model_dump_json(indent=2),
                encoding="utf-8",
            )
            recommendation_path.write_text(
                result.recommendation.model_dump_json(indent=2),
                encoding="utf-8",
            )
            _append_dataset_row(
                dataset_path,
                result.dataset_row,
                result.dataset_fieldnames,
            )
        except (OSError, ValueError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=2) from exc

        training_status: dict[str, object] = {"status": "not_requested"}
        model_explanation: dict[str, object] | None = None

        if train:
            backend = DecisionTreeTrainingBackend()
            try:
                training_result = TrainModel(backend).execute(
                    dataset_path,
                    model_path,
                    training_report_path,
                )
                training_status = {
                    "status": "completed",
                    "report": training_result,
                }
                model_explanation = ExplainModel(backend).execute(
                    model_path,
                    explanation_path,
                )
            except (OSError, ValueError) as exc:
                training_status = {
                    "status": "skipped",
                    "reason": str(exc),
                }

        HtmlReportGenerator().generate(
            result.execution,
            result.recommendation,
            report_path,
            training_status=training_status,
            model_explanation=model_explanation,
        )

        summary = {
            "schema_version": "1",
            "mode": "local_poc",
            "recommendation_action": result.recommendation.action,
            "training": training_status,
            "artifacts": {
                "execution_summary": str(execution_path),
                "recommendation": str(recommendation_path),
                "dataset": str(dataset_path),
                "model": str(model_path) if model_path.exists() else None,
                "training_report": (
                    str(training_report_path) if training_report_path.exists() else None
                ),
                "model_explanation": (str(explanation_path) if explanation_path.exists() else None),
                "html_report": str(report_path),
            },
            "limitations": [
                "Local proof of concept only.",
                "No integration with bank platforms.",
                "Training is optional and may be skipped when H8 safeguards reject the dataset.",
            ],
        }
        summary_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        console.print("[bold green]H10 local pipeline completed[/bold green]")
        console.print(f"Recommendation: [bold]{result.recommendation.action}[/bold]")
        console.print(f"Training: {training_status['status']}")
        console.print(f"[green]Output directory:[/green] {output_dir}")
        console.print(f"[green]HTML report:[/green] {report_path}")
