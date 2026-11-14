"""Generate the Gate 0 label-cause audit from the fixed-width historical export."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = APP_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from performance_decision_engine.infrastructure.historical_binary_evaluator import (  # noqa: E402
    HistoricalBinaryEvaluator,
)
from performance_decision_engine.infrastructure.label_audit import (  # noqa: E402
    build_label_audit,
    write_label_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit why historical rows are labeled applies/not_applies."
    )
    parser.add_argument("--source", required=True, type=Path, help="Fixed-width historical file.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Artifact directory.")
    args = parser.parse_args()

    rows = HistoricalBinaryEvaluator.read_fixed_width(args.source)
    report = build_label_audit(rows)
    write_label_audit(report, args.output_dir)

    print(f"Source rows: {report['source_rows']}")
    print(f"Usable rows: {report['usable_rows']}")
    print(f"Distinct Build_Id: {report['distinct_builds']}")
    for item in report["cause_distribution"]:
        print(
            f"- {item['cause']}: {item['rows']} rows, "
            f"{item['builds']} builds, {item['percentage_rows']:.2%}"
        )
    print(f"Created: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

