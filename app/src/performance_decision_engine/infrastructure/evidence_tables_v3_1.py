from __future__ import annotations

import csv
import hashlib
import html
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from performance_decision_engine.infrastructure.configuration_training_v2 import (
    eligibility_reason,
)
from performance_decision_engine.infrastructure.label_audit import build_label_audit


CAUSE_LABELS = {
    "applies_complete": "Conforme con evidencia completa",
    "not_applies_execution_error": "Ejecutado con error técnico",
    "not_applies_multiple_causes": "No aplica por causas múltiples",
    "not_applies_not_executed": "No ejecutado",
    "not_applies_incomplete_evidence": "Evidencia incompleta",
    "not_applies_other_policy": "Otra regla histórica",
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_data_flow(source_rows: int, usable_rows: int, reasons: Counter[str]) -> list[dict[str, Any]]:
    steps = [
        ("source_export", source_rows, 0, "Filas leídas desde el export histórico"),
        (
            "usable_historical_rows",
            usable_rows,
            source_rows - usable_rows,
            "Se excluyen filas sin identificador/resultado mínimo utilizable",
        ),
    ]
    current = usable_rows
    for code, reason_key, description in (
        ("exclude_not_executed", "not_executed", "Performance=0: la prueba no se ejecutó"),
        (
            "exclude_incomplete_result_evidence",
            "incomplete_result_evidence",
            "Falta estado, errorCount o successCount para construir la etiqueta técnica",
        ),
        (
            "exclude_incomplete_configuration",
            "incomplete_configuration",
            "Falta Concurrency, Iterations o ResponseTime",
        ),
    ):
        removed = int(reasons[reason_key])
        current -= removed
        steps.append((code, current, removed, description))
    return [
        {
            "step": index,
            "stage": code,
            "rows_remaining": remaining,
            "rows_removed_at_step": removed,
            "description": description,
        }
        for index, (code, remaining, removed, description) in enumerate(steps, start=1)
    ]


def validate_data_flow(flow: list[dict[str, Any]], eligible_rows: int) -> None:
    if int(flow[-1]["rows_remaining"]) != eligible_rows:
        raise ValueError(
            f"Data flow ends in {flow[-1]['rows_remaining']} rows; frozen protocol expects {eligible_rows}"
        )
    for previous, current in zip(flow, flow[1:], strict=False):
        expected = int(previous["rows_remaining"]) - int(current["rows_removed_at_step"])
        if expected != int(current["rows_remaining"]):
            raise ValueError("Data-flow arithmetic is inconsistent")


def evidence_completeness(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for label in ("applies", "not_applies", "ALL"):
        selected = records if label == "ALL" else [row for row in records if row["binary_label"] == label]
        for field in ("p95", "rps", "error_count"):
            missing = sum(not str(row.get(field, "")).strip() for row in selected)
            output.append({
                "binary_label": label,
                "field": "errorCount" if field == "error_count" else field,
                "rows": len(selected),
                "missing_rows": missing,
                "missing_rate": missing / len(selected) if selected else 0.0,
                "complete_rows": len(selected) - missing,
            })
    return output


def flow_svg(path: Path, flow: list[dict[str, Any]]) -> None:
    width, height = 1280, 360
    box_width, gap, start = 210, 35, 35
    colours = ["#073b66", "#087f8c", "#3b8d99", "#4d9d91", "#009e95"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="35" y="42" font-family="Arial" font-size="26" font-weight="700" fill="#073b66">Flujo auditable de datos</text>',
    ]
    for index, row in enumerate(flow):
        x = start + index * (box_width + gap)
        remaining = int(row["rows_remaining"])
        removed = int(row["rows_removed_at_step"])
        parts.extend([
            f'<rect x="{x}" y="90" width="{box_width}" height="145" rx="16" fill="{colours[index]}"/>',
            f'<text x="{x + box_width/2}" y="145" text-anchor="middle" font-family="Arial" font-size="30" font-weight="700" fill="white">{remaining:,}</text>',
            f'<text x="{x + box_width/2}" y="177" text-anchor="middle" font-family="Arial" font-size="15" fill="white">filas</text>',
            f'<text x="{x + box_width/2}" y="210" text-anchor="middle" font-family="Arial" font-size="14" fill="white">{"inicio" if removed == 0 else f"−{removed:,} en este paso"}</text>',
        ])
        if index < len(flow) - 1:
            arrow_x = x + box_width + 8
            parts.append(f'<text x="{arrow_x}" y="168" font-family="Arial" font-size="32" fill="#6b7c8f">→</text>')
    parts.extend([
        '<text x="35" y="285" font-family="Arial" font-size="17" fill="#17324d">6.444 filas históricas utilizables → se excluyen 1.591 no ejecutadas, 57 con evidencia insuficiente y 407 con configuración incompleta → 4.389 elegibles.</text>',
        '<text x="35" y="320" font-family="Arial" font-size="15" fill="#56697a">La unidad del modelo es un registro ejecutado; Build_Id se conserva como unidad de agrupación para evitar leakage.</text>',
        '</svg>',
    ])
    path.write_text("\n".join(parts), encoding="utf-8")


def composition_svg(path: Path, causes: list[dict[str, Any]]) -> None:
    width, height = 1200, 420
    palette = ["#009e95", "#245a86", "#7895a8", "#a8b5bf", "#58727f", "#385566"]
    total = sum(int(row["rows"]) for row in causes)
    x0, y, bar_width, bar_height = 50, 90, 1100, 70
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="50" y="45" font-family="Arial" font-size="26" font-weight="700" fill="#073b66">Composición del histórico por causa operacional</text>',
    ]
    cursor = x0
    for index, row in enumerate(causes):
        fraction = int(row["rows"]) / total
        segment = bar_width * fraction
        colour = palette[index % len(palette)]
        parts.append(f'<rect x="{cursor:.1f}" y="{y}" width="{segment:.1f}" height="{bar_height}" fill="{colour}"/>')
        if segment > 75:
            parts.append(f'<text x="{cursor + segment/2:.1f}" y="{y+43}" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="white">{100*fraction:.1f}%</text>')
        cursor += segment
    for index, row in enumerate(causes):
        column = index % 2
        line = index // 2
        x = 60 + column * 565
        ly = 215 + line * 62
        colour = palette[index % len(palette)]
        label = html.escape(str(row["display_name"]))
        parts.extend([
            f'<rect x="{x}" y="{ly-18}" width="20" height="20" rx="3" fill="{colour}"/>',
            f'<text x="{x+32}" y="{ly}" font-family="Arial" font-size="17" fill="#17324d">{label}: {int(row["rows"]):,} filas · {100*float(row["percentage_rows"]):.1f}%</text>',
        ])
    parts.extend([
        '<text x="50" y="390" font-family="Arial" font-size="14" fill="#56697a">Los builds pueden contener registros de más de una causa; por eso los conteos de builds por causa no son aditivos.</text>',
        '</svg>',
    ])
    path.write_text("\n".join(parts), encoding="utf-8")


class EvidenceTablesV31:
    def __init__(self) -> None:
        from performance_decision_engine.infrastructure.configuration_training_v2 import ConfigurationTrainingV2

        self.reader = ConfigurationTrainingV2()

    def run(self, source_path: Path, protocol_path: Path, output_dir: Path) -> dict[str, Any]:
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        if protocol["source_sha256"] != sha256_file(source_path):
            raise ValueError("Dataset SHA-256 differs from frozen protocol")
        rows = self.reader.read_fixed_width(source_path)
        audit = build_label_audit(rows)
        records = audit["records"]
        if not isinstance(records, list):
            raise ValueError("Label-audit records are missing")
        reasons = Counter(eligibility_reason(row) for row in rows)
        flow = build_data_flow(len(rows), int(audit["usable_rows"]), reasons)
        validate_data_flow(flow, int(protocol["eligible_rows"]))

        causes = []
        for row in audit["cause_distribution"]:
            item = dict(row)
            item["display_name"] = CAUSE_LABELS.get(str(item["cause"]), str(item["cause"]))
            item["denominator_rows"] = audit["usable_rows"]
            item["build_count_note"] = "non_additive_across_causes"
            causes.append(item)

        build_accumulator: dict[str, Counter[str]] = defaultdict(Counter)
        for record in records:
            build_id = str(record["build_id"])
            if build_id:
                build_accumulator[build_id][str(record["primary_cause"])] += 1
                build_accumulator[build_id]["total_rows"] += 1
        cause_names = sorted({str(record["primary_cause"]) for record in records})
        build_rows = []
        for build_id, counts in sorted(build_accumulator.items()):
            build_rows.append({
                "build_id_sha256": sha256_text(build_id),
                "total_rows": counts["total_rows"],
                "distinct_causes": sum(counts[name] > 0 for name in cause_names),
                **{f"rows_{name}": counts[name] for name in cause_names},
            })

        impact_rows = []
        for item in causes:
            impact_rows.append({
                "indicator": item["cause"],
                "display_name": item["display_name"],
                "rows": item["rows"],
                "percentage_of_usable_history": item["percentage_rows"],
                "builds_with_at_least_one_record": item["builds"],
                "evidence_type": "measured_historical_composition",
                "business_interpretation": (
                    "Historical workload/problem composition; it is not a realized monetary saving."
                ),
            })
        technical_issue_rows = sum(
            int(item["rows"])
            for item in causes
            if item["cause"] in {"not_applies_execution_error", "not_applies_multiple_causes"}
        )
        impact_rows.append({
            "indicator": "executed_with_observed_technical_issue",
            "display_name": "Ejecutado con evidencia de problema técnico (incluye causas múltiples)",
            "rows": technical_issue_rows,
            "percentage_of_usable_history": technical_issue_rows / int(audit["usable_rows"]),
            "builds_with_at_least_one_record": "not_additive_requires_union",
            "evidence_type": "derived_historical_composition",
            "business_interpretation": "Describes historical review demand; no causal or monetary claim.",
        })

        definitions = [
            {
                "term": "p95",
                "definition": "Percentil 95 del tiempo de respuesta: el 95% de las solicitudes observadas terminó en un tiempo menor o igual a este valor.",
                "unit": "milisegundos cuando el reporte Gatling de origen está expresado en ms",
                "not_equivalent_to": "promedio, máximo, SLA o probabilidad de falla",
                "use_in_project": "evidencia posterior a la ejecución; se usa para auditoría/etiqueta, nunca como predictor ex ante",
            },
            {
                "term": "RPS",
                "definition": "Solicitudes procesadas por segundo durante la prueba.",
                "unit": "requests/second",
                "not_equivalent_to": "usuarios concurrentes",
                "use_in_project": "evidencia posterior a la ejecución; no es feature del modelo v3",
            },
            {
                "term": "registro",
                "definition": "Una configuración ejecutada y registrada en el export histórico.",
                "unit": "fila",
                "not_equivalent_to": "Build_Id ni atención operativa",
                "use_in_project": "unidad de clasificación/ranking",
            },
            {
                "term": "Build_Id",
                "definition": "Identificador que agrupa registros relacionados de una misma build/ejecución.",
                "unit": "grupo",
                "not_equivalent_to": "fila individual",
                "use_in_project": "unidad de separación, validación y bootstrap para evitar leakage",
            },
        ]

        completeness = evidence_completeness(records)
        report = {
            "schema_version": "3.1",
            "status": "EVIDENCE_TABLES_COMPLETE",
            "source_rows": len(rows),
            "usable_historical_rows": audit["usable_rows"],
            "distinct_builds": audit["distinct_builds"],
            "eligible_model_rows": protocol["eligible_rows"],
            "eligible_model_builds": protocol["eligible_builds"],
            "eligibility_distribution": dict(sorted(reasons.items())),
            "data_flow": flow,
            "cause_distribution": causes,
            "definitions": definitions,
            "integrity": {
                "flow_reconciled": True,
                "final_rows_match_frozen_protocol": True,
                "model_metrics_recomputed": False,
                "official_v3_changed": False,
            },
            "allowed_claim": "The historical export contains measurable non-execution, technical-error and conformity workloads.",
            "prohibited_claim": "These historical proportions are realized savings or causal effects of the model.",
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        _write_csv(output_dir / "label_cause_tables.csv", causes)
        _write_csv(output_dir / "label_cause_by_build.csv", build_rows)
        _write_csv(output_dir / "evidence_completeness.csv", completeness)
        _write_csv(output_dir / "problem_impact_inputs.csv", impact_rows)
        _write_csv(output_dir / "data_flow.csv", flow)
        _write_csv(output_dir / "metric_definitions.csv", definitions)
        flow_svg(output_dir / "data_flow_v3_1.svg", flow)
        composition_svg(output_dir / "problem_composition_v3_1.svg", causes)
        (output_dir / "evidence_tables_v3_1.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report
