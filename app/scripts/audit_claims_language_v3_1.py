from argparse import ArgumentParser
import csv
import json
from pathlib import Path

from performance_decision_engine.infrastructure.claims_v3_1 import audit_language


def main() -> None:
    parser = ArgumentParser(description="Audit language in README, report and deck against v3.1 rules.")
    parser.add_argument("--document", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    missing = [str(path) for path in args.document if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Documents not found: {missing}")
    findings = audit_language(args.document)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields = ["document", "rule_id", "matched_text", "context", "required_correction"]
    with (args.output_dir / "language_audit_v3_1.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(findings)
    report = {
        "schema_version": "3.1", "status": "PASS" if not findings else "REQUIRES_CORRECTION",
        "documents": [str(path) for path in args.document], "violations": len(findings),
    }
    (args.output_dir / "language_audit_v3_1.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Status: {report['status']}")
    print(f"Documents: {len(args.document)}")
    print(f"Violations: {len(findings)}")
    print(f"Created: {args.output_dir}")
    raise SystemExit(0 if not findings else 1)


if __name__ == "__main__":
    main()

