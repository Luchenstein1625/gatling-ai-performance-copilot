from pathlib import Path

import pytest

from performance_decision_engine.infrastructure.final_test_v3 import (
    assert_not_completed,
    require_confirmation,
)


def test_confirmation_is_explicit() -> None:
    require_confirmation("OPEN_TEST_ONCE")
    with pytest.raises(ValueError):
        require_confirmation("yes")


def test_completed_report_cannot_be_overwritten(tmp_path: Path) -> None:
    assert_not_completed(tmp_path)
    (tmp_path / "final_test_evaluation_v3.json").write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError):
        assert_not_completed(tmp_path)


def test_incomplete_marker_does_not_silently_replace_completed_rule(tmp_path: Path) -> None:
    (tmp_path / "test_opened_v3.json").write_text(
        '{"status":"OPENED_IN_PROGRESS"}', encoding="utf-8"
    )
    assert_not_completed(tmp_path)
