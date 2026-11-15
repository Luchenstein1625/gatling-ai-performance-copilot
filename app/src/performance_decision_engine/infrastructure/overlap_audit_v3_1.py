from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import joblib

from performance_decision_engine.infrastructure.calibration_decision_v3 import CalibrationDecisionV3
from performance_decision_engine.infrastructure.configuration_stability_v2 import ConfigurationStabilityV2
from performance_decision_engine.infrastructure.configuration_training_v2 import (
    ConfigurationTrainingV2,
    eligibility_reason,
    feature_row,
    technical_label,
)
from performance_decision_engine.infrastructure.final_test_v3 import FinalTestV3
from performance_decision_engine.infrastructure.model_selection_v3 import ModelSelectionV3, sha256_file, sha256_text


RANDOM_STATE = 42
STABILITY_SPLITS = 20


def pairwise_overlap(name_a: str, values_a: set[str], name_b: str, values_b: set[str]) -> dict[str, Any]:
    overlap = values_a & values_b
    union = values_a | values_b
    return {
        "partition_a": name_a,
        "partition_b": name_b,
        "builds_a": len(values_a),
        "builds_b": len(values_b),
        "overlap_builds": len(overlap),
        "overlap_pct_of_a": len(overlap) / len(values_a) if values_a else None,
        "overlap_pct_of_b": len(overlap) / len(values_b) if values_b else None,
        "jaccard": len(overlap) / len(union) if union else None,
    }


def build_exposure_rows(
    test_builds: set[str], fixed_holdout: set[str], repeated_holdouts: dict[str, set[str]]
) -> list[dict[str, Any]]:
    rows = []
    for build in sorted(test_builds):
        count = sum(build in values for values in repeated_holdouts.values())
        rows.append({
            "build_id_sha256": sha256_text(build),
            "seen_in_v2_fixed_holdout": build in fixed_holdout,
            "stability_holdouts_seen_count": count,
            "seen_in_any_v2_exploration_holdout": build in fixed_holdout or count > 0,
        })
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    fieldnames = fields or (list(rows[0]) if rows else ["status"])
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class OverlapAuditV31:
    def __init__(self) -> None:
        self.training = ConfigurationTrainingV2()
        self.stability = ConfigurationStabilityV2()
        self.selection = ModelSelectionV3()
        self.calibration = CalibrationDecisionV3()
        self.final_test = FinalTestV3()

    @staticmethod
    def _load_assignments(path: Path) -> dict[str, str]:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            return {row["build_id_sha256"]: row["partition"] for row in csv.DictReader(source)}

    def _sensitivity(
        self,
        name: str,
        rows: list[dict[str, str]],
        final_artifact: dict[str, Any],
        bootstrap: int,
    ) -> dict[str, Any]:
        if not rows:
            return {"subset": name, "status": "NOT_ESTIMABLE_EMPTY_SUBSET", "rows": 0, "builds": 0}
        labels = [technical_label(row) for row in rows]
        if len(set(labels)) < 2:
            return {
                "subset": name, "status": "NOT_ESTIMABLE_SINGLE_CLASS", "rows": len(rows),
                "builds": len({row["Build_Id"] for row in rows}),
            }
        features = [feature_row(row) for row in rows]
        groups = [row["Build_Id"] for row in rows]
        raw = self.selection._probabilities(final_artifact["pipeline"], features)
        probabilities = self.calibration._apply_calibrator(
            final_artifact["calibrator"], str(final_artifact["calibration_method"]), raw
        )
        metrics = self.selection.metrics(labels, probabilities, 0.5)
        _, interval = self.final_test._grouped_bootstrap(labels, groups, probabilities, bootstrap)
        return {
            "subset": name,
            "status": "DESCRIPTIVE_ONLY_COMPLETE",
            "rows": len(rows),
            "builds": len(set(groups)),
            "metrics": {
                key: metrics[key]
                for key in ("roc_auc", "pr_auc", "prevalence_not_applies", "recall_at_30", "precision_at_30", "lift_at_30")
            },
            "grouped_bootstrap_ic95": interval,
        }

    def run(
        self,
        source_path: Path,
        protocol_path: Path,
        assignments_path: Path,
        governance_addendum_path: Path,
        final_model_path: Path,
        final_test_report_path: Path,
        output_dir: Path,
        bootstrap_repetitions: int = 2000,
    ) -> dict[str, Any]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        addendum = json.loads(governance_addendum_path.read_text(encoding="utf-8"))
        final_report = json.loads(final_test_report_path.read_text(encoding="utf-8"))
        if sha256_file(source_path) != protocol.get("source_sha256"):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        if not any(item.get("id") == "A5" for item in addendum.get("registered_analyses", [])):
            raise ValueError("A5 diagnostic is not pre-registered")
        if final_report.get("selection_changes_after_test") is not False:
            raise ValueError("Final report does not preserve the no-selection-after-test rule")

        source_rows = self.training.read_fixed_width(source_path)
        eligible = [row for row in source_rows if eligibility_reason(row) == "trainable"]
        labels = [technical_label(row) for row in eligible]
        groups = [row["Build_Id"] for row in eligible]
        fixed_train_i, fixed_holdout_i = self.training._split(labels, groups)
        fixed_train = {groups[index] for index in fixed_train_i}
        fixed_holdout = {groups[index] for index in fixed_holdout_i}

        repeated_holdouts: dict[str, set[str]] = {}
        repeated_trains: dict[str, set[str]] = {}
        for number in range(STABILITY_SPLITS):
            seed = RANDOM_STATE + number
            train_i, holdout_i = self.stability._valid_group_split(labels, groups, seed)
            repeated_trains[f"v2_stability_{number + 1:02d}_train"] = {groups[index] for index in train_i}
            repeated_holdouts[f"v2_stability_{number + 1:02d}_holdout"] = {groups[index] for index in holdout_i}

        assignments = self._load_assignments(assignments_path)
        v3: dict[str, set[str]] = {"v3_train": set(), "v3_dev": set(), "v3_test": set()}
        rows_by_partition: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in eligible:
            partition = assignments.get(sha256_text(row["Build_Id"]))
            if partition not in {"train", "dev", "test"}:
                raise ValueError("Eligible Build_Id missing from frozen v3 assignments")
            v3[f"v3_{partition}"].add(row["Build_Id"])
            rows_by_partition[partition].append(row)

        core_sets = {
            "v2_fixed_train": fixed_train,
            "v2_fixed_holdout": fixed_holdout,
            **repeated_holdouts,
            **v3,
        }
        matrix = [
            pairwise_overlap(name_a, values_a, name_b, values_b)
            for name_a, values_a in core_sets.items()
            for name_b, values_b in core_sets.items()
        ]
        test_builds = v3["v3_test"]
        exposure = build_exposure_rows(test_builds, fixed_holdout, repeated_holdouts)
        test_seen_fixed = test_builds & fixed_holdout
        test_unseen_fixed = test_builds - fixed_holdout
        all_exploratory_holdouts = set().union(fixed_holdout, *repeated_holdouts.values())
        test_never_holdout = test_builds - all_exploratory_holdouts

        artifact = joblib.load(final_model_path)
        test_rows = rows_by_partition["test"]
        unseen_fixed_rows = [row for row in test_rows if row["Build_Id"] in test_unseen_fixed]
        never_holdout_rows = [row for row in test_rows if row["Build_Id"] in test_never_holdout]
        sensitivity = {
            "schema_version": "3.1",
            "alert": "A5",
            "status": "OVERLAP_SENSITIVITY_COMPLETE",
            "use": "descriptive_only_no_selection_or_retuning",
            "official_test_unchanged": True,
            "subsets": [
                self._sensitivity("test_not_in_v2_fixed_holdout", unseen_fixed_rows, artifact, bootstrap_repetitions),
                self._sensitivity("test_never_in_any_v2_holdout", never_holdout_rows, artifact, bootstrap_repetitions),
            ],
        }
        exposure_counts = Counter(
            "seen_fixed" if row["seen_in_v2_fixed_holdout"] else "not_seen_fixed" for row in exposure
        )
        report = {
            "schema_version": "3.1",
            "alert": "A5",
            "status": "OVERLAP_AUDIT_COMPLETE",
            "source_rows_eligible": len(eligible),
            "source_builds_eligible": len(set(groups)),
            "v3_test_builds": len(test_builds),
            "v3_test_builds_seen_in_v2_fixed_holdout": len(test_seen_fixed),
            "v3_test_builds_seen_in_v2_fixed_holdout_pct": len(test_seen_fixed) / len(test_builds),
            "v3_test_builds_not_seen_in_v2_fixed_holdout": len(test_unseen_fixed),
            "v3_test_builds_never_in_any_v2_holdout": len(test_never_holdout),
            "stability_splits_reconstructed": STABILITY_SPLITS,
            "test_reused_for_selection_in_v3": False,
            "historical_exposure_limitation": len(test_seen_fixed) > 0 or len(test_never_holdout) < len(test_builds),
            "decision_effect": "limitation_statement_only_no_retuning",
            "official_v3_changed": False,
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        _write_csv(output_dir / "build_overlap_matrix.csv", matrix)
        _write_csv(output_dir / "test_build_exposure.csv", exposure)
        (output_dir / "test_unseen_sensitivity.json").write_text(
            json.dumps(sensitivity, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (output_dir / "overlap_audit_v3_1.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        limitation = (
            f"De los {len(test_builds)} builds del test v3, {len(test_seen_fixed)} "
            f"({len(test_seen_fixed) / len(test_builds):.1%}) habían aparecido en el holdout exploratorio v2; "
            f"{len(test_unseen_fixed)} no habían aparecido allí. Además, los 20 splits exploratorios de estabilidad "
            "reutilizaron builds del universo histórico. El test v3 no se usó para ajustar hiperparámetros, calibración "
            "ni umbral, pero la familia de modelos y las variables se definieron tras exploraciones históricas; por ello, "
            "la evaluación se interpreta como confirmación interna y requiere validación prospectiva externa."
        )
        information_map = f"""# A5 · Mapa de información y decisiones

| Decisión | Información disponible | Uso del test v3 | Clasificación |
|---|---|---|---|
| Familia de modelos | Exploraciones v2 y estabilidad sobre el universo histórico | Algunos builds pudieron aparecer en holdouts previos | Exploratoria previa |
| Variables: Concurrency, Iterations, ResponseTime | Definidas antes del protocolo v3, apoyadas por análisis histórico | No se cambiaron después de abrir el test | Congelada con exposición histórica |
| Hiperparámetros | Train v3 | Ninguno | Selección interna válida |
| Calibración y threshold | OOF train + dev v3 | Ninguno | Selección interna válida |
| Política operacional | Train/dev y guardrails preinscritos | Test solo evaluación | Congelada |
| Métricas finales | Test v3 abierto una vez | Evaluación descriptiva | Oficial v3 |
| Sensibilidad sin builds del holdout fijo v2 | Subconjunto preinscrito del test | Diagnóstico post-hoc | No cambia selección |

## Frase de limitación

{limitation}

## Regla

El análisis A5 no autoriza reentrenar, cambiar variables, reemplazar el modelo ni seleccionar un resultado usando el test.
"""
        (output_dir / "decision_information_map.md").write_text(information_map, encoding="utf-8")
        return report

