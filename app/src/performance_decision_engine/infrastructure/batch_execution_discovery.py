from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExecutionFiles:
    """Filesystem inputs required to normalize one historical execution."""

    execution_id: str
    performance: Path
    parameters: Path
    results: Path
    assertions: Path | None


class BatchExecutionDiscovery:
    """Discover historical execution bundles below a source directory."""

    def discover(self, source: Path) -> list[ExecutionFiles]:
        if not source.exists() or not source.is_dir():
            raise ValueError(f"Batch source directory does not exist: {source}")

        results_files = sorted(source.rglob("global_stats.json"))
        if not results_files:
            raise ValueError("No global_stats.json files were found in the batch source.")

        performance_files = sorted(source.rglob("performance.yaml"))
        assertion_files = sorted(source.rglob("assertions.json"))
        shared_parameters = sorted(source.rglob("parametricConfigurationValues.yaml"))
        if len(shared_parameters) > 1:
            raise ValueError("More than one shared parametricConfigurationValues.yaml was found.")
        shared_parameter = shared_parameters[0] if shared_parameters else None

        executions: list[ExecutionFiles] = []
        for results in results_files:
            performance = self._best_match(
                results,
                performance_files,
                "performance.yaml",
            )
            if performance is None:
                raise ValueError(f"No performance.yaml could be associated with {results}.")
            assertions = self._best_match(
                results,
                assertion_files,
                "assertions.json",
                required=False,
            )
            parameters = shared_parameter

            if parameters is None:
                raise ValueError(
                    "No parametricConfigurationValues.yaml could be associated " f"with {results}."
                )

            execution_id = results.parent.relative_to(source).as_posix()
            executions.append(
                ExecutionFiles(
                    execution_id=execution_id,
                    performance=performance,
                    parameters=parameters,
                    results=results,
                    assertions=assertions,
                )
            )

        return executions

    @classmethod
    def _best_match(
        cls,
        reference: Path,
        candidates: list[Path],
        filename: str,
        *,
        required: bool = True,
    ) -> Path | None:
        if not candidates:
            if required:
                raise ValueError(f"No {filename} files were found in the batch source.")
            return None

        ranked = sorted(
            (
                cls._directory_distance(reference.parent, candidate.parent),
                candidate,
            )
            for candidate in candidates
        )
        best_distance = ranked[0][0]
        best_candidates = [candidate for distance, candidate in ranked if distance == best_distance]

        if len(best_candidates) > 1:
            options = ", ".join(str(candidate) for candidate in best_candidates)
            raise ValueError(f"Ambiguous {filename} association for {reference}: {options}")

        return best_candidates[0]

    @staticmethod
    def _directory_distance(left: Path, right: Path) -> int:
        left_parts = left.resolve().parts
        right_parts = right.resolve().parts
        common_length = 0

        for left_part, right_part in zip(left_parts, right_parts, strict=False):
            if left_part.casefold() != right_part.casefold():
                break
            common_length += 1

        return len(left_parts) - common_length + len(right_parts) - common_length
