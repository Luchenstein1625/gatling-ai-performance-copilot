from __future__ import annotations

import csv
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree

import numpy as np


FORBIDDEN_RULES = (
    {
        "rule_id": "L-001",
        "pattern": r"\b(confirma|confirmamos|confirmado)\b.{0,80}\b(señal|valor|prioriz)",
        "message": "Use lenguaje de evidencia acotada; el conjunto de métricas no confirma utilidad general.",
    },
    {
        "rule_id": "L-002",
        "pattern": r"\bvalor demostrado\b",
        "message": "Reemplazar por evidencia observada o hipótesis compatible, según el registro.",
    },
    {
        "rule_id": "L-003",
        "pattern": r"(?<!proyección de )(?<!proyección condicionada de )\bahorro(?:s)?\b",
        "message": "Todo ahorro económico debe rotularse explícitamente como proyección condicionada.",
    },
    {
        "rule_id": "L-004",
        "pattern": r"\b(libera|liberación automática segura|automatiza la liberación)\b",
        "message": "La política oficial revisa todos los casos; no se certificó liberación automática.",
    },
    {
        "rule_id": "L-005",
        "pattern": r"\brecomienda(?:r)? (?:un |los |las )?(?:upgrade|ajuste|cambio)",
        "message": "No existen upgrades publicables; describir candidatos experimentales o abstención.",
    },
)


def percentile_summary(values: Iterable[float]) -> dict[str, float]:
    data = list(values)
    if not data:
        raise ValueError("Cannot summarize an empty distribution")
    return {
        "point_or_mean": float(np.mean(data)),
        "lower_95": float(np.quantile(data, 0.025)),
        "upper_95": float(np.quantile(data, 0.975)),
    }


def additional_cases(rows_reviewed: int, precision: float, prevalence: float) -> float:
    return rows_reviewed * (precision - prevalence)


def evidence_level(lower: float, null_value: float, upper: float) -> str:
    return "No concluyente" if lower <= null_value <= upper else "Demostrado"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Required artifact not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def _interval(report: dict[str, Any], metric: str) -> tuple[float, float]:
    item = report["ranking_grouped_bootstrap_ic95"][metric]
    return float(item["lower_95"]), float(item["upper_95"])


def build_claims_register(
    final_test_path: Path,
    bootstrap_path: Path,
    fine_threshold_path: Path,
    recommender_path: Path,
    economics_path: Path,
    calibration_audit_path: Path,
    recommender_audit_path: Path,
    confounding_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    final = _read_json(final_test_path)
    bootstrap = _read_csv(bootstrap_path)
    threshold = _read_json(fine_threshold_path)
    recommender = _read_json(recommender_path)
    economics = _read_json(economics_path)
    calibration = _read_json(calibration_audit_path)
    recommender_audit = _read_json(recommender_audit_path)
    confounding = _read_json(confounding_path)

    if final.get("test_status") != "OPENED_ONCE_EVALUATION_COMPLETE":
        raise ValueError("Official independent test is not complete")
    metrics = final["ranking_test_metrics"]
    baselines = final["baselines"]["random_ranking"]
    test_rows = int(final["rows"]["test"])
    top_rows = int(round(test_rows * 0.30))
    point_additional = additional_cases(
        top_rows, float(metrics["precision_at_30"]), float(metrics["prevalence_not_applies"])
    )
    additional_distribution = [
        additional_cases(
            top_rows,
            float(row["precision_at_30"]),
            float(row["precision_at_30"]) / float(row["lift_at_30"])
            if float(row["lift_at_30"]) else 0.0,
        )
        for row in bootstrap
    ]
    additional_ic = percentile_summary(additional_distribution)
    roc_low, roc_high = _interval(final, "roc_auc")
    recall_low, recall_high = _interval(final, "recall_at_30")
    lift_low, lift_high = _interval(final, "lift_at_30")
    diagnostic = final["diagnostic_threshold_not_operational"]
    risk = diagnostic["released_risk_wilson_95"]
    break_even = float(economics["break_even"]["minimum_coverage_times_effort_reduction"])

    rows: list[dict[str, Any]] = [
        {
            "claim_id": "C-001", "topic": "discriminacion_test", "claim": "El test independiente observa discriminación por encima del azar.",
            "metric": "ROC-AUC", "estimate": float(metrics["roc_auc"]), "lower_95": roc_low, "upper_95": roc_high,
            "null_reference": float(baselines["roc_auc"]), "evidence_level": evidence_level(roc_low, 0.5, roc_high),
            "allowed_wording": "Señal de discriminación débil pero distinguible del azar en el test independiente.",
            "prohibited_wording": "El test confirma una señal predictiva útil.", "source": str(final_test_path),
        },
        {
            "claim_id": "C-002", "topic": "priorizacion_recall", "claim": "Revisar el 30% superior captura más not_applies que un ranking aleatorio.",
            "metric": "Recall@30", "estimate": float(metrics["recall_at_30"]), "lower_95": recall_low, "upper_95": recall_high,
            "null_reference": float(baselines["expected_recall_at_30"]), "evidence_level": evidence_level(recall_low, 0.30, recall_high),
            "allowed_wording": "El beneficio de priorización por Recall@30 es no concluyente.",
            "prohibited_wording": "El modelo prioriza mejor.", "source": str(final_test_path),
        },
        {
            "claim_id": "C-003", "topic": "priorizacion_lift", "claim": "La cola priorizada concentra más not_applies que la prevalencia.",
            "metric": "Lift@30", "estimate": float(metrics["lift_at_30"]), "lower_95": lift_low, "upper_95": lift_high,
            "null_reference": float(baselines["expected_lift_at_30"]), "evidence_level": evidence_level(lift_low, 1.0, lift_high),
            "allowed_wording": "El lift puntual es 1,31, pero su intervalo incluye 1; el resultado es no concluyente.",
            "prohibited_wording": "El ranking mejora la priorización en 31%.", "source": str(final_test_path),
        },
        {
            "claim_id": "C-004", "topic": "casos_adicionales", "claim": "Casos adicionales frente a selección aleatoria entre 264 revisados.",
            "metric": "casos adicionales en top 30%", "estimate": point_additional,
            "lower_95": additional_ic["lower_95"], "upper_95": additional_ic["upper_95"], "null_reference": 0.0,
            "evidence_level": evidence_level(additional_ic["lower_95"], 0.0, additional_ic["upper_95"]),
            "allowed_wording": "Diferencia puntual cercana a 35 casos, con intervalo que incluye cero.",
            "prohibited_wording": "Encuentra 35 casos más.", "source": str(bootstrap_path),
        },
        {
            "claim_id": "C-005", "topic": "liberacion_automatica", "claim": "La liberación automática cumple el guardrail de riesgo.",
            "metric": "límite superior 95% del error liberado", "estimate": float(diagnostic["released_error_rate"]),
            "lower_95": float(risk["lower"]), "upper_95": float(risk["upper"]), "null_reference": 0.05,
            "evidence_level": "No demostrado",
            "allowed_wording": "No se puede certificar liberación automática; la política mantiene revisión humana total.",
            "prohibited_wording": "El modelo libera casos con seguridad.", "source": str(final_test_path),
        },
        {
            "claim_id": "C-006", "topic": "recomendador", "claim": "Existen upgrades suficientemente estables para publicación.",
            "metric": "upgrades publicables", "estimate": int(recommender["publishable_upgrades"]), "lower_95": "", "upper_95": "",
            "null_reference": 1, "evidence_level": "No demostrado",
            "allowed_wording": "El recomendador se abstiene cuando la evidencia es inestable; no hay upgrades publicables.",
            "prohibited_wording": "El sistema recomienda ajustes de carga.", "source": str(recommender_path),
        },
        {
            "claim_id": "C-007", "topic": "monotonicidad", "claim": "Los parámetros presentan una relación direccional robusta.",
            "metric": "monotonicidad no ponderada", "estimate": float(recommender_audit["monotonicity"]["consistency_rate"]),
            "lower_95": float(recommender_audit["monotonicity"]["lower_95"]), "upper_95": float(recommender_audit["monotonicity"]["upper_95"]),
            "null_reference": 0.5, "evidence_level": "No demostrado",
            "allowed_wording": "La monotonicidad no ponderada es 44,9% [38,3%; 52,3%] y la ponderada descriptiva es 27,9%; los tres parámetros por sí solos no sostienen recomendaciones direccionales robustas.",
            "prohibited_wording": "Aumentar carga produce el cambio recomendado.", "source": str(recommender_audit_path),
        },
        {
            "claim_id": "C-008", "topic": "contexto", "claim": "El contexto explica causalmente la baja monotonicidad.",
            "metric": "monotonicidad ponderada estratificada", "estimate": float(confounding["stratified_weighted_monotonicity"]),
            "lower_95": "", "upper_95": "", "null_reference": float(confounding["pooled_weighted_monotonicity"]),
            "evidence_level": "Sugerido",
            "allowed_wording": "El resultado es compatible con confusión contextual; no demuestra causalidad.",
            "prohibited_wording": "Pilar y Tcomponente causan la baja monotonicidad.", "source": str(confounding_path),
        },
        {
            "claim_id": "C-009", "topic": "calibracion", "claim": "La calibración isotónica mejora de forma robusta la discriminación.",
            "metric": "auditoría cross-fit", "estimate": float(calibration["invariance_check"]["delta_isotonic_minus_raw"]),
            "lower_95": "", "upper_95": "", "null_reference": 0.0, "evidence_level": "No demostrado",
            "allowed_wording": "La mejora aparente de AUC proviene de empates; el beneficio de calibración no fue robusto en cross-fit.",
            "prohibited_wording": "La calibración mejora el ROC-AUC.", "source": str(calibration_audit_path),
        },
        {
            "claim_id": "C-010", "topic": "economia", "claim": "El proyecto genera un ahorro anual realizado.",
            "metric": "cobertura × reducción de esfuerzo de equilibrio", "estimate": break_even,
            "lower_95": "", "upper_95": "", "null_reference": break_even, "evidence_level": "No demostrado",
            "allowed_wording": "Proyección condicionada: supera el equilibrio si cobertura × reducción de esfuerzo es mayor que 4,02%.",
            "prohibited_wording": "Ahorro de $2,74 MM o ROI demostrado de 211%.", "source": str(economics_path),
        },
    ]
    summary = {
        "schema_version": "3.1", "alert": "A4", "status": "CLAIMS_REGISTER_COMPLETE",
        "test_recomputed": False, "frozen_bootstrap_reused": True,
        "top_30_rows": top_rows, "additional_cases_point": point_additional,
        "additional_cases_bootstrap": additional_ic,
        "claims": len(rows),
        "evidence_levels": {level: sum(row["evidence_level"] == level for row in rows) for level in ("Demostrado", "Sugerido", "No concluyente", "No demostrado")},
        "official_v3_changed": False,
    }
    return rows, summary


def _ooxml_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.endswith(".xml") and ("slides/slide" in name or "word/document" in name)]
        chunks: list[str] = []
        for name in names:
            root = ElementTree.fromstring(archive.read(name))
            chunks.extend(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
        return "\n".join(chunks)


def document_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".pptx", ".docx"}:
        return _ooxml_text(path)
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as error:
            raise RuntimeError("Install pypdf to audit PDF documents") from error
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    return path.read_text(encoding="utf-8", errors="replace")


def audit_language(paths: Iterable[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in paths:
        text = document_text(path)
        normalized = re.sub(r"\s+", " ", text)
        for rule in FORBIDDEN_RULES:
            for match in re.finditer(str(rule["pattern"]), normalized, flags=re.IGNORECASE):
                start = max(0, match.start() - 80)
                end = min(len(normalized), match.end() + 80)
                findings.append({
                    "document": str(path), "rule_id": str(rule["rule_id"]),
                    "matched_text": match.group(0), "context": normalized[start:end],
                    "required_correction": str(rule["message"]),
                })
    return findings

