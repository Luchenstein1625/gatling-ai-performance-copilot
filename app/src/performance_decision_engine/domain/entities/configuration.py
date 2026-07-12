from pydantic import BaseModel, Field


class ResolvedTriplet(BaseModel):
    concurrency_level: str
    concurrency_value: int | None = None
    iterations_level: str
    iterations_value: int | None = None
    response_time_level: str
    response_time_ms: int | None = None


class EndpointConfiguration(BaseModel):
    name: str
    feature_reference: str
    enabled: bool
    reason: str | None = None
    reason_detail: str | None = None
    triplet: ResolvedTriplet


class PerformanceConfiguration(BaseModel):
    load_type: str | None = None
    endpoints: list[EndpointConfiguration] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
