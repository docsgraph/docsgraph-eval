"""Tests for the report writer."""

import json
from pathlib import Path

from docsgraph_eval.core import BenchmarkResult
from docsgraph_eval.report import to_json, to_markdown, write_json, write_markdown


def _sample_result() -> BenchmarkResult:
    return BenchmarkResult(area="ocr", total_cases=2, passed=1, score=0.5)


def test_to_json_round_trips() -> None:
    data = json.loads(to_json(_sample_result()))
    assert data["area"] == "ocr"
    assert data["total_cases"] == 2
    assert data["passed"] == 1
    assert data["score"] == 0.5


def test_to_markdown_contains_area_and_metrics() -> None:
    md = to_markdown(_sample_result())
    assert "# Benchmark report: ocr" in md
    assert "| passed | 1 |" in md
    assert "| score | 0.5 |" in md


def test_to_markdown_handles_missing_score() -> None:
    md = to_markdown(BenchmarkResult(area="sync"))
    assert "| score | n/a |" in md


def test_write_json(tmp_path: Path) -> None:
    dest = tmp_path / "result.json"
    write_json(_sample_result(), dest)
    data = json.loads(dest.read_text())
    assert data["passed"] == 1


def test_write_markdown(tmp_path: Path) -> None:
    dest = tmp_path / "result.md"
    write_markdown(_sample_result(), dest)
    assert "ocr" in dest.read_text()
