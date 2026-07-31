"""Tests for the CLI entrypoint."""

from typer.testing import CliRunner

from docsgraph_eval.cli import BENCHMARK_AREAS, app

runner = CliRunner()


def test_help_lists_run_command() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output


def test_run_help_lists_every_area() -> None:
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    for area in BENCHMARK_AREAS:
        assert area.replace("_", "-") in result.output


def test_run_ocr_reports_not_implemented() -> None:
    result = runner.invoke(app, ["run", "ocr"])
    assert result.exit_code == 0
    assert "[ocr] not yet implemented" in result.output


def test_run_all_covers_every_area() -> None:
    result = runner.invoke(app, ["run", "all"])
    assert result.exit_code == 0
    for area in BENCHMARK_AREAS:
        assert f"[{area}] not yet implemented" in result.output
