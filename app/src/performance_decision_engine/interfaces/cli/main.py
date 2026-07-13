import platform
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from performance_decision_engine import __version__
from performance_decision_engine.application.use_cases.normalize_execution import (
    NormalizeExecution,
)
from performance_decision_engine.domain.services.quadrant_service import resolve_quadrant
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
