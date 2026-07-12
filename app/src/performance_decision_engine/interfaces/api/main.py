from fastapi import FastAPI, HTTPException

from performance_decision_engine import __version__
from performance_decision_engine.domain.services.quadrant_service import resolve_quadrant

app = FastAPI(
    title="Performance Decision Engine",
    version=__version__,
)


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
