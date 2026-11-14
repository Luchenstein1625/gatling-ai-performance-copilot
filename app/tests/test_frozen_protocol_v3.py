from performance_decision_engine.infrastructure.frozen_protocol_v3 import (
    FrozenProtocolV3,
    partition_digest,
    sha256_text,
)


def test_hash_is_stable() -> None:
    assert sha256_text("build-1") == sha256_text("build-1")
    assert len(sha256_text("build-1")) == 64


def test_partition_digest_is_order_independent() -> None:
    assert partition_digest({"b", "a"}) == partition_digest({"a", "b"})


def test_split_has_no_group_overlap_and_all_classes() -> None:
    labels: list[str] = []
    groups: list[str] = []
    for group_index in range(80):
        for row_index in range(4):
            groups.append(f"build-{group_index}")
            labels.append("not_applies" if (group_index + row_index) % 3 == 0 else "applies")
    partitions = FrozenProtocolV3().split(labels, groups)
    build_sets = {
        name: {groups[index] for index in indexes}
        for name, indexes in partitions.items()
    }
    assert build_sets["train"].isdisjoint(build_sets["dev"])
    assert build_sets["train"].isdisjoint(build_sets["test"])
    assert build_sets["dev"].isdisjoint(build_sets["test"])
    for indexes in partitions.values():
        assert {labels[index] for index in indexes} == {"applies", "not_applies"}


def test_split_is_reproducible() -> None:
    labels = ["applies", "not_applies"] * 100
    groups = [f"build-{index // 2}" for index in range(200)]
    first = FrozenProtocolV3().split(labels, groups)
    second = FrozenProtocolV3().split(labels, groups)
    assert first == second
