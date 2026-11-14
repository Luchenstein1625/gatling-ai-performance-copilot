import argparse
from pathlib import Path

from performance_decision_engine.infrastructure.frozen_protocol_v3 import FrozenProtocolV3


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze final grouped train/dev/test protocol")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = FrozenProtocolV3().run(args.source, args.output_dir)
    print(f"Eligible rows: {report['eligible_rows']}")
    print(f"Eligible builds: {report['eligible_builds']}")
    for name in ("train", "dev", "test"):
        item = report["partitions"][name]
        print(
            f"- {name}: {item['rows']} rows ({item['row_fraction']:.2%}), "
            f"{item['builds']} builds, NA prevalence {item['not_applies_prevalence']:.2%}"
        )
    print(f"Test Build_Id set SHA-256: {report['test_lock']['test_build_set_sha256']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()
