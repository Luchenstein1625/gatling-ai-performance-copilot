from performance_decision_engine.infrastructure.overlap_audit_v3_1 import (
    OverlapAuditV31,
    build_exposure_rows,
    pairwise_overlap,
)


def test_pairwise_overlap_reports_both_denominators() -> None:
    result = pairwise_overlap("a", {"1", "2", "3"}, "b", {"3", "4"})
    assert result["overlap_builds"] == 1
    assert result["overlap_pct_of_a"] == 1 / 3
    assert result["overlap_pct_of_b"] == 1 / 2
    assert result["jaccard"] == 1 / 4


def test_exposure_counts_repeated_holdouts_without_raw_id_output() -> None:
    rows = build_exposure_rows(
        {"build-a", "build-b"},
        {"build-a"},
        {"split-1": {"build-a", "build-b"}, "split-2": {"build-b"}},
    )
    by_count = {row["stability_holdouts_seen_count"]: row for row in rows}
    assert by_count[1]["seen_in_v2_fixed_holdout"] is True
    assert by_count[2]["seen_in_v2_fixed_holdout"] is False
    assert all("build-a" not in row.values() and "build-b" not in row.values() for row in rows)


def test_empty_partition_overlap_is_safe() -> None:
    result = pairwise_overlap("empty", set(), "b", {"1"})
    assert result["overlap_builds"] == 0
    assert result["overlap_pct_of_a"] is None


def test_audit_uses_available_fixed_width_reader() -> None:
    audit = OverlapAuditV31()
    assert callable(audit.training.read_fixed_width)

