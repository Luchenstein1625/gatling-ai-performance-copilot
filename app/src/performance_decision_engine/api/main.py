from fastapi import FastAPI

from performance_decision_engine import __version__

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
