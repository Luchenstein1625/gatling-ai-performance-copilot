from pathlib import Path
import platform
import sys

import typer
from rich.console import Console

from performance_decision_engine import __version__
from performance_decision_engine.adapters.execution_builder import build_execution_summary
from performance_decision_engine.storage.json_store import save_model_json

app = typer.Typer(help="Performance Decision Engine")
console = Console()


@app.command()
def version() -> None:
    """Show application version."""
    console.print(__version__)


@app.command()
def doctor() -> None:
    """Validate the local execution environment."""
    console.print("[bold green]Performance Decision Engine[/bold green]")
    console.print(f"Version: {__version__}")
    console.print(f"Python: {sys.version.split()[0]}")
    console.print(f"Platform: {platform.platform()}")
    console.print("[green]Environment ready[/green]")


@app.command()
def normalize(
    performance: Path = typer.Option(..., exists=True, readable=True),
    parameters: Path = typer.Option(..., exists=True, readable=True),
    gatling: Path = typer.Option(..., exists=True, readable=True),
    output: Path = typer.Option(...),
) -> None:
    """Normalize one execution into a JSON document."""
    summary = build_execution_summary(
        performance_path=performance,
        parameters_path=parameters,
        gatling_path=gatling,
    )
    save_model_json(summary, output)
    console.print(f"[green]Created:[/green] {output}")


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    show_version: bool = typer.Option(
        False,
        "--version",
        help="Show application version.",
    ),
) -> None:
    if show_version:
        console.print(__version__)
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
