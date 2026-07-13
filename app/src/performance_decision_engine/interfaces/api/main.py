from fastapi import FastAPI, HTTPException

from performance_decision_engine import __version__
from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation
from performance_decision_engine.domain.services.quadrant_service import resolve_quadrant
from performance_decision_engine.interfaces.dependencies import build_generate_recommendation

app = FastAPI(title="Performance Decision Engine", version=__version__)


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
def create_recommendation(execution: NormalizedExecution) -> Recommendation:
    try:
        return build_generate_recommendation().execute(execution)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
