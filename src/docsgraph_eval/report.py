"""Benchmark report writer.

Turns a :class:`~docsgraph_eval.core.BenchmarkResult` into a JSON or
Markdown report. This is intentionally minimal for now -- enough structure
to build on once real benchmark implementations start producing results
worth reporting on.
"""

import json
from pathlib import Path

from docsgraph_eval.core import BenchmarkResult


def to_json(result: BenchmarkResult) -> str:
    """Serialize a benchmark result to a JSON string.

    Args:
        result: The benchmark result to serialize.

    Returns:
        A JSON-formatted string representation of the result.
    """
    return result.model_dump_json(indent=2)


def to_markdown(result: BenchmarkResult) -> str:
    """Render a benchmark result as a minimal Markdown summary table.

    Args:
        result: The benchmark result to render.

    Returns:
        A Markdown-formatted summary of the result.
    """
    score = "n/a" if result.score is None else f"{result.score}"
    lines = [
        f"# Benchmark report: {result.area}",
        "",
        "| metric | value |",
        "| --- | --- |",
        f"| total_cases | {result.total_cases} |",
        f"| passed | {result.passed} |",
        f"| score | {score} |",
    ]
    return "\n".join(lines) + "\n"


def write_json(result: BenchmarkResult, path: Path) -> None:
    """Write a benchmark result to disk as JSON.

    Args:
        result: The benchmark result to write.
        path: Destination file path.
    """
    path.write_text(json.dumps(json.loads(to_json(result)), indent=2) + "\n")


def write_markdown(result: BenchmarkResult, path: Path) -> None:
    """Write a benchmark result to disk as Markdown.

    Args:
        result: The benchmark result to write.
        path: Destination file path.
    """
    path.write_text(to_markdown(result))
