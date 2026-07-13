from pydantic import BaseModel

from performance_decision_engine.domain.value_objects.load_level import LoadLevel


class RecommendedTriplet(BaseModel):
    concurrency_level: LoadLevel
    iterations_level: LoadLevel
    response_time_level: LoadLevel
    concurrency_value: int | None = None
    iterations_value: int | None = None
    response_time_ms: int | None = None
