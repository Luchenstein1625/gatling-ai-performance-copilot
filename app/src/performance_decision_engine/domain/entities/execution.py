from pydantic import BaseModel, Field, model_validator

from performance_decision_engine.domain.entities.configuration import PerformanceConfiguration


class AssertionResult(BaseModel):
    """Normalized result of one Gatling assertion."""

    path: str | None = None
    target: str | None = None
    condition: str | None = None
    expected: str | int | float | bool | None = None
    actual: str | int | float | bool | None = None
    successful: bool
    message: str | None = None


class AssertionSummary(BaseModel):
    """Summary of all assertions evaluated by Gatling."""

    total: int = Field(ge=0)
    successful: int = Field(ge=0)
    failed: int = Field(ge=0)
    all_passed: bool
    results: list[AssertionResult] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_counts(self) -> "AssertionSummary":
        if self.total != self.successful + self.failed:
            raise ValueError(
                "Assertion counts are inconsistent: "
                "total must equal successful plus failed"
            )

        if self.total != len(self.results):
            raise ValueError(
                "Assertion counts are inconsistent: "
                "total must equal the number of results"
            )

        if self.all_passed != (self.failed == 0):
            raise ValueError(
                "Assertion status is inconsistent with the failed count"
            )

        return self


class ExecutionMetrics(BaseModel):
    """Normalized global metrics extracted from Gatling results."""

    total_requests: int = Field(ge=0)
    successful_requests: int = Field(ge=0)
    failed_requests: int = Field(ge=0)
    error_rate_percent: float = Field(ge=0.0, le=100.0)

    min_response_time_ms: int | None = Field(default=None, ge=0)
    mean_response_time_ms: int | None = Field(default=None, ge=0)
    max_response_time_ms: int | None = Field(default=None, ge=0)

    p50_response_time_ms: int | None = Field(default=None, ge=0)
    p75_response_time_ms: int | None = Field(default=None, ge=0)
    p95_response_time_ms: int | None = Field(default=None, ge=0)
    p99_response_time_ms: int | None = Field(default=None, ge=0)

    requests_per_second: float | None = Field(default=None, ge=0.0)
    assertions: AssertionSummary | None = None

    @model_validator(mode="after")
    def validate_request_counts(self) -> "ExecutionMetrics":
        if self.total_requests != self.successful_requests + self.failed_requests:
            raise ValueError(
                "Request counts are inconsistent: "
                "total_requests must equal successful_requests plus failed_requests"
            )
        return self


class NormalizedExecution(BaseModel):
    configuration: PerformanceConfiguration
    global_metrics: ExecutionMetrics
    warnings: list[str] = Field(default_factory=list)
