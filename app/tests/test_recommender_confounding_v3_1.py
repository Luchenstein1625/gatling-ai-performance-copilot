from performance_decision_engine.infrastructure.recommender_confounding_v3_1 import normalize_context


def test_blank_context_is_explicitly_missing() -> None:
    assert normalize_context("   ") == "__MISSING__"


def test_context_value_is_not_used_as_model_feature() -> None:
    assert normalize_context("  OSS  ") == "OSS"


def test_diagnostic_context_fields_are_fixed() -> None:
    from performance_decision_engine.infrastructure.recommender_confounding_v3_1 import CONTEXT_FIELDS
    assert CONTEXT_FIELDS == ("pilar", "Tcomponente")

