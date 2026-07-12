from pydantic import BaseModel, Field

from performance_decision_engine.domain.entities.configuration import PerformanceConfiguration


class ExecutionMetrics(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate_percent: float
    min_response_time_ms: int | None = None
    mean_response_time_ms: int | None = None
    max_response_time_ms: int | None = None
    p95_response_time_ms: int | None = None
    p99_response_time_ms: int | None = None
    requests_per_second: float | None = None


class NormalizedExecution(BaseModel):
    configuration: PerformanceConfiguration
    global_metrics: ExecutionMetrics
    warnings: list[str] = Field(default_factory=list)
