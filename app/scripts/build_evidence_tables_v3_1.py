from __future__ import annotations

import argparse
from pathlib import Path

from performance_decision_engine.infrastructure.evidence_tables_v3_1 import EvidenceTablesV31


def main() -> None:
    parser = argparse.ArgumentParser(description="Build F8/F1 cause, impact and data-flow evidence tables")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = EvidenceTablesV31().run(args.source, args.protocol, args.output_dir)
    print(f"Status: {report['status']}")
    print(f"Source rows: {report['source_rows']}")
    print(f"Usable historical rows: {report['usable_historical_rows']}")
    print(f"Eligible model rows: {report['eligible_model_rows']}")
    print(f"Eligible model builds: {report['eligible_model_builds']}")
    print(f"Flow reconciled: {report['integrity']['flow_reconciled']}")
    print(f"Official v3 changed: {report['integrity']['official_v3_changed']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()
