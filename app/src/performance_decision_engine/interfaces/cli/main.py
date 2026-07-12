from pathlib import Path
import platform
import sys

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
    show_version: bool = typer.Option(False, "--version"),
) -> None:
    if show_version:
        console.print(__version__)
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@app.command()
def doctor() -> None:
    console.print("[bold green]Performance Decision Engine[/bold green]")
    console.print(f"Version: {__version__}")
    console.print(f"Python: {sys.version.split()[0]}")
    console.print(f"Platform: {platform.platform()}")
    console.print("[green]Environment ready[/green]")


@app.command()
def quadrant(
    criticality: str = typer.Option(...),
    complexity: str = typer.Option(...),
) -> None:
    result = resolve_quadrant(criticality, complexity)
    console.print(f"Quadrant: {result.number}")


@app.command()
def normalize(
    performance: Path = typer.Option(..., exists=True, readable=True),
    parameters: Path = typer.Option(..., exists=True, readable=True),
    results: Path = typer.Option(..., exists=True, readable=True),
    output: Path = typer.Option(...),
) -> None:
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
    console.print(f"[green]Created:[/green] {output}")
