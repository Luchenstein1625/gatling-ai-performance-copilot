from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from performance_decision_engine.infrastructure.historical_binary_evaluator import (
    HistoricalBinaryEvaluator,
)
from performance_decision_engine.infrastructure.complete_historical_pipeline import (
    CompleteHistoricalPipeline,
)


def register_historical_command(app: typer.Typer, console: Console) -> None:
    @app.command("evaluate-historical")
    def evaluate_historical(
        source: Annotated[
            Path,
            typer.Option(
                "--source",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
                help="Fixed-width historical Gatling export.",
            ),
        ],
        output_dir: Annotated[
            Path,
            typer.Option(
                "--output-dir",
                file_okay=False,
                dir_okay=True,
                resolve_path=True,
                help="Directory for evaluation artifacts.",
            ),
        ],
    ) -> None:
        """Compare three review/maintain/upgrade recommendation models."""
        try:
            report = HistoricalBinaryEvaluator().evaluate(source, output_dir)
        except ValueError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=2) from exc
        console.print(f"Rows evaluated: {report['labeled_rows']}")
        console.print(f"Selected model: [bold]{report['selected_model']}[/bold]")
        console.print(f"[green]Created:[/green] {output_dir}")

    @app.command("evaluate-complete")
    def evaluate_complete(
        source: Annotated[
            Path,
            typer.Option("--source", exists=True, file_okay=True, dir_okay=False),
        ],
        output_dir: Annotated[
            Path,
            typer.Option("--output-dir", file_okay=False, dir_okay=True),
        ],
    ) -> None:
        """Run all four layers requested in the evaluator feedback."""
        try:
            report = CompleteHistoricalPipeline().evaluate_complete(source, output_dir)
        except ValueError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=2) from exc
        layer1 = report["layers"]["1_applicability"]
        console.print(f"Rows evaluated: {report['usable_rows']}")
        console.print(f"Selected model: [bold]{layer1['selected_model']}[/bold]")
        console.print("Future online validation: pending new Gatling execution")
        console.print(f"[green]Created:[/green] {output_dir}")
