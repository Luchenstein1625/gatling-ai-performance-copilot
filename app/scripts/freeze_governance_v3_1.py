from argparse import ArgumentParser
from pathlib import Path

from performance_decision_engine.infrastructure.governance_v3_1 import GovernanceV31


def main() -> None:
    parser = ArgumentParser(description="Freeze v3 hashes and preregister v3.1 diagnostic analyses.")
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = GovernanceV31().run(args.repository, args.results_root, args.source, args.output_dir)
    print(f"Gate: {report['gate']}")
    print(f"Frozen files: {report['files_frozen']}")
    print(f"Baseline manifest SHA-256: {report['baseline_manifest_sha256']}")
    print(f"Test Build_Id SHA-256: {report['test_build_set_sha256']}")
    print(f"Pre-registered decisions: {report['registered_decisions']}")
    print(f"Created: {args.output_dir}")


if __name__ == "__main__":
    main()

