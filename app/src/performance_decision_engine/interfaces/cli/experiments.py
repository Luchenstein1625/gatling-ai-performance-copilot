import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from performance_decision_engine.application.use_cases.analyze_dataset import (
    AnalyzeDataset,
)
from performance_decision_engine.application.use_cases.evaluate_evolution import (
    EvaluateEvolution,
    load_evolution_history,
)
from performance_decision_engine.application.use_cases.normalize_execution import (
    NormalizeExecution,
)
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
from performance_decision_engine.infrastructure.model_evaluator import ModelEvaluator
from performance_decision_engine.infrastructure.parsers.gatling_metrics_reader import (
    GatlingMetricsReader,
)
from performance_decision_engine.infrastructure.parsers.yaml_configuration_reader import (
    YamlConfigurationReader,
)


def _write_json(output: Path, payload: dict[str, object]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


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
        ] = 10,
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
