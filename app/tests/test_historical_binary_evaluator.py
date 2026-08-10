from pathlib import Path

from performance_decision_engine.infrastructure.historical_binary_evaluator import (
    HistoricalBinaryEvaluator,
)


def _dataset(path: Path, count: int = 40) -> None:
    names = [
        "Performance",
        "Build_Id",
        "CpruebasCarga",
        "CpruebasAcep",
        "Is_In_Prod",
        "pilar",
        "Tcomponente",
        "Metodo",
        "Concurrency",
        "Iterations",
        "ResponseTime",
        "ambiente",
        "Estado",
        "successCount",
        "errorCount",
        "p95",
    ]
    widths = [20] * len(names)
    header = " ".join(name.ljust(width) for name, width in zip(names, widths, strict=True))
    separator = " ".join("-" * width for width in widths)
    rows = [header, separator]
    for index in range(count):
        review = index % 3 == 0
        upgrade = index % 3 == 1
        values = {
            "Performance": "0" if review else "1",
            "Build_Id": str(index // 2),
            "CpruebasCarga": "3",
            "CpruebasAcep": "2",
            "Is_In_Prod": "1",
            "pilar": "OSS",
            "Tcomponente": "OSS-Team-Backend",
            "Metodo": "GET",
            "Concurrency": "high",
            "Iterations": "medium",
            "ResponseTime": "high",
            "ambiente": "cert",
            "Estado": "Failed" if review else "Success",
            "successCount": "0" if review else "1000",
            "errorCount": "10" if review else "0",
            "p95": "1200" if upgrade else "1900",
        }
        rows.append(
            " ".join(values[name].ljust(width) for name, width in zip(names, widths, strict=True))
        )
    path.write_text("\n".join(rows), encoding="utf-8")


def test_evaluates_three_models_and_exports_tree(tmp_path: Path) -> None:
    source = tmp_path / "historical.txt"
    output = tmp_path / "results"
    _dataset(source)

    report = HistoricalBinaryEvaluator().evaluate(source, output)

    assert report["problem_type"] == "multiclass_recommendation"
    assert set(report["models"]) == {"decision_tree", "logistic_regression", "random_forest"}
    assert report["positive_class"] == "review"
    assert report["split"]["group_overlap"] == 0
    assert (output / "historical_recommendation_evaluation.json").exists()
    assert (output / "historical_recommendation_model.joblib").exists()
    assert (output / "historical_recommendation_dataset.csv").exists()
    assert (output / "decision_tree.dot").exists()
    assert (output / "decision_tree_rules.txt").exists()


def test_fixed_width_reader_normalizes_null(tmp_path: Path) -> None:
    source = tmp_path / "historical.txt"
    _dataset(source, count=20)
    text = source.read_text(encoding="utf-8").replace("cert        ", "NULL        ", 1)
    source.write_text(text, encoding="utf-8")

    rows = HistoricalBinaryEvaluator.read_fixed_width(source)

    assert rows[0]["ambiente"] == ""
