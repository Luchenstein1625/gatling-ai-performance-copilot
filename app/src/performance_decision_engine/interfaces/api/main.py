import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

from performance_decision_engine import __version__
from performance_decision_engine.application.use_cases.recommend_execution import (
    RecommendExecution,
)
from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation
from performance_decision_engine.domain.services.quadrant_service import resolve_quadrant

app = FastAPI(
    title="Performance Decision Engine",
    version=__version__,
)

OUTPUT_BASE = Path("examples/output")
RUNS_INDEX_PATH = OUTPUT_BASE / "runs_index.json"
RUNS_COMPARISON_PATH = OUTPUT_BASE / "runs_comparison_latest.json"


def _read_json_object(path: Path) -> dict[str, object]:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Invalid JSON file: {path}") from exc

    if not isinstance(loaded, dict):
        raise HTTPException(status_code=500, detail=f"Expected JSON object in: {path}")
    return loaded


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": __version__}


@app.get("/quadrants/{criticality}/{complexity}")
def quadrant(criticality: str, complexity: str) -> dict[str, int | str]:
    try:
        result = resolve_quadrant(criticality, complexity)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "quadrant": result.number,
        "criticality": result.criticality,
        "complexity": result.complexity,
    }


@app.post("/recommendations", response_model=Recommendation)
def recommendation(execution: NormalizedExecution) -> Recommendation:
    """Generate a baseline recommendation from a normalized execution."""
    return RecommendExecution().execute(execution)


@app.get("/runs/index")
def runs_index() -> dict[str, object]:
    """Return the central index of automatic evaluation runs."""
    return _read_json_object(RUNS_INDEX_PATH)


@app.get("/runs/comparison")
def runs_comparison() -> dict[str, object]:
    """Return the latest consolidated runs comparison."""
    return _read_json_object(RUNS_COMPARISON_PATH)


@app.get("/runs/top")
def runs_top(limit: int = 5) -> dict[str, object]:
    """Return top runs ranked by operational_core_macro_f1."""
    if limit < 1 or limit > 50:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 50")

    comparison = _read_json_object(RUNS_COMPARISON_PATH)
    top_value = comparison.get("top_operational_runs")
    top = top_value if isinstance(top_value, list) else []
    selected = [item for item in top if isinstance(item, dict)][:limit]
    return {
        "total_available": len(top),
        "limit": limit,
        "top_runs": selected,
        "latest_overfit_risk": comparison.get("latest_overfit_risk"),
        "latest_overfit_gap": comparison.get("latest_overfit_gap"),
    }
