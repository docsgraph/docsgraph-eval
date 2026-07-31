"""Smoke test: the package installs, imports, and its CLI runs.

Placeholder until real benchmark implementations land — deliberately not
testing per-module stub behavior, since there is no real logic yet.
"""

from typer.testing import CliRunner

from docsgraph_eval.cli import app

runner = CliRunner()


def test_cli_help_runs() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
