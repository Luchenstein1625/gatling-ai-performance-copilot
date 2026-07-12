from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ResolvedTriplet(BaseModel):
    concurrency_level: str
    concurrency_value: int | None = None
    iterations_level: str
    iterations_value: int | None = None
    response_time_level: str
    response_time_ms: int | None = None


class FeatureConfiguration(BaseModel):
    name: str
    feature: str
    performance: bool
    reason: str | None = None
    reason_detail: str | None = None
    triplet: ResolvedTriplet


class GatlingGlobalMetrics(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    min_response_time_ms: int | None = None
    mean_response_time_ms: int | None = None
    max_response_time_ms: int | None = None
    p95_response_time_ms: int | None = None
    p99_response_time_ms: int | None = None
    requests_per_second: float | None = None


class ExecutionSummary(BaseModel):
    load_type: str | None = None
    features: list[FeatureConfiguration] = Field(default_factory=list)
    gatling_global: GatlingGlobalMetrics
    assertions: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
