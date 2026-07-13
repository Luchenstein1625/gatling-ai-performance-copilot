from enum import StrEnum


class RecommendationDecision(StrEnum):
    KEEP = "keep"
    INCREASE_LOAD = "increase_load"
    DECREASE_LOAD = "decrease_load"
    REVIEW = "review"
    INSUFFICIENT_DATA = "insufficient_data"
