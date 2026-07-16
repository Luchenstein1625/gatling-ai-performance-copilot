import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from performance_decision_engine.infrastructure.decision_tree_training_backend import (
    DecisionTreeTrainingBackend,
)
from performance_decision_engine.interfaces.cli.main import app

runner = CliRunner()


def test_explain_model_command_exports_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = tmp_path / "model.joblib"
    output = tmp_path / "model_explanation.json"
    model.write_bytes(b"trusted test artifact")

    payload: dict[str, object] = {
        "schema_version": "1",
        "model_type": "DecisionTreeClassifier",
        "classes": ["maintain", "review"],
        "transformed_feature_columns": ["numeric__error_rate_percent"],
        "feature_importance": [
            {
                "feature": "numeric__error_rate_percent",
                "importance": 1.0,
            }
        ],
        "decision_rules": "tree",
    }

    def fake_explain(
        self: DecisionTreeTrainingBackend,
        model_path: Path,
        output_path: Path,
    ) -> dict[str, object]:
        assert model_path == model.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        return payload

    monkeypatch.setattr(
        DecisionTreeTrainingBackend,
        "explain",
        fake_explain,
    )

    result = runner.invoke(
        app,
        [
            "explain-model",
            "--model",
            str(model),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert "H9 model explanation completed" in result.stdout
    assert "DecisionTreeClassifier" in result.stdout
    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8")) == payload


def test_explain_model_command_rejects_missing_model(tmp_path: Path) -> None:
    missing_model = tmp_path / "missing.joblib"
    output = tmp_path / "explanation.json"

    result = runner.invoke(
        app,
        [
            "explain-model",
            "--model",
            str(missing_model),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 2
    assert "Invalid value for '--model'" in result.stderr
    assert not output.exists()


def test_explain_model_command_reports_backend_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = tmp_path / "model.joblib"
    output = tmp_path / "model_explanation.json"
    model.write_bytes(b"incompatible test artifact")

    def fail_explanation(
        self: DecisionTreeTrainingBackend,
        model_path: Path,
        output_path: Path,
    ) -> dict[str, object]:
        raise ValueError("Model artifact is incompatible with H8.")

    monkeypatch.setattr(
        DecisionTreeTrainingBackend,
        "explain",
        fail_explanation,
    )

    result = runner.invoke(
        app,
        [
            "explain-model",
            "--model",
            str(model),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 2
    assert "Error:" in result.stdout
    assert "incompatible with H8" in result.stdout
    assert not output.exists()


def test_explain_model_help_is_available() -> None:
    result = runner.invoke(app, ["explain-model", "--help"])

    assert result.exit_code == 0
    assert "--model" in result.stdout
    assert "--output" in result.stdout
