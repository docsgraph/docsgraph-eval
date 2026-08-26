"""Command-line interface for docsgraph-eval.

Provides one ``run`` subcommand per benchmark area, plus a ``run all``
command that runs every area.
"""

import importlib
from pathlib import Path
from typing import Annotated

import typer

from docsgraph_eval.core import BenchmarkCase, load_suites_from_dir
from docsgraph_eval.report import to_json, to_markdown, write_json, write_markdown

app = typer.Typer(
    name="docsgraph-eval",
    help=(
        "Independent benchmark and testing suite for docsgraph: ocr, "
        "extraction, retrieval, evidence_attribution, graph_generation, "
        "permissions, sync, and offline_consistency."
    ),
)
run_app = typer.Typer(help="Run a benchmark for a specific area, or `all` areas.")
app.add_typer(run_app, name="run")

FOLDER_MAP = {
    "ocr": "ocr",
    "extraction": "extraction",
    "retrieval": "retrieval",
    "evidence-attribution": "evidence_attribution",
    "graph-generation": "graph_generation",
    "permissions": "permissions",
    "sync": "sync",
    "offline-consistency": "offline_consistency",
}


def run_benchmark(
    area: str,
    target_url: str,
    fixtures_dir: Path,
    output: Path | None,
    output_format: str,
) -> None:
    """Load fixtures for the given area, run the benchmark, and output the report."""
    folder = FOLDER_MAP.get(area, area)
    area_dir = fixtures_dir / folder
    if not area_dir.exists():
        typer.echo(f"Fixtures directory {area_dir} does not exist.")
        raise typer.Exit(code=1)

    suites = load_suites_from_dir(area_dir)
    if not suites:
        typer.echo(f"No benchmark suites found in {area_dir}")
        raise typer.Exit(code=1)

    cases: list[BenchmarkCase] = []
    for suite in suites:
        cases.extend(suite.cases)

    if not cases:
        typer.echo(f"No test cases found in suites for {area}")
        raise typer.Exit(code=1)

    try:
        module = importlib.import_module(f"docsgraph_eval.{folder}.bench")
        run_func = module.run
    except (ImportError, AttributeError) as e:
        typer.echo(f"Error loading benchmark implementation for {area}: {e}")
        raise typer.Exit(code=1) from e

    try:
        result = run_func(cases, target_url=target_url)
    except Exception as e:
        typer.echo(f"Error running benchmark for {area}: {e}")
        raise typer.Exit(code=1) from e

    report_str = to_markdown(result) if output_format == "markdown" else to_json(result)

    if output:
        try:
            if output_format == "markdown":
                write_markdown(result, output)
            else:
                write_json(result, output)
            typer.echo(f"Report written to {output}")
        except Exception as e:
            typer.echo(f"Error writing report to {output}: {e}")
            raise typer.Exit(code=1) from e
    else:
        typer.echo(report_str)


# Common options helper type aliases
TargetUrlOpt = Annotated[
    str,
    typer.Option(help="URL of the docsgraph-server instance"),
]
FixturesDirOpt = Annotated[
    Path,
    typer.Option(help="Directory containing benchmark fixtures"),
]
OutputOpt = Annotated[
    Path | None,
    typer.Option(help="File path to write the report to"),
]
FormatOpt = Annotated[
    str,
    typer.Option("--format", help="Format of the report (json or markdown)"),
]


@run_app.command("ocr")
def run_ocr(
    target_url: TargetUrlOpt = "http://localhost:8000",
    fixtures_dir: FixturesDirOpt = Path("fixtures"),
    output: OutputOpt = None,
    output_format: FormatOpt = "json",
) -> None:
    """Run the OCR accuracy benchmark."""
    run_benchmark("ocr", target_url, fixtures_dir, output, output_format)


@run_app.command("extraction")
def run_extraction(
    target_url: TargetUrlOpt = "http://localhost:8000",
    fixtures_dir: FixturesDirOpt = Path("fixtures"),
    output: OutputOpt = None,
    output_format: FormatOpt = "json",
) -> None:
    """Run the structured extraction benchmark."""
    run_benchmark("extraction", target_url, fixtures_dir, output, output_format)


@run_app.command("retrieval")
def run_retrieval(
    target_url: TargetUrlOpt = "http://localhost:8000",
    fixtures_dir: FixturesDirOpt = Path("fixtures"),
    output: OutputOpt = None,
    output_format: FormatOpt = "json",
) -> None:
    """Run the retrieval quality benchmark."""
    run_benchmark("retrieval", target_url, fixtures_dir, output, output_format)


@run_app.command("evidence-attribution")
def run_evidence_attribution(
    target_url: TargetUrlOpt = "http://localhost:8000",
    fixtures_dir: FixturesDirOpt = Path("fixtures"),
    output: OutputOpt = None,
    output_format: FormatOpt = "json",
) -> None:
    """Run the evidence attribution benchmark."""
    run_benchmark("evidence-attribution", target_url, fixtures_dir, output, output_format)


@run_app.command("graph-generation")
def run_graph_generation(
    target_url: TargetUrlOpt = "http://localhost:8000",
    fixtures_dir: FixturesDirOpt = Path("fixtures"),
    output: OutputOpt = None,
    output_format: FormatOpt = "json",
) -> None:
    """Run the knowledge graph generation quality benchmark."""
    run_benchmark("graph-generation", target_url, fixtures_dir, output, output_format)


@run_app.command("permissions")
def run_permissions(
    target_url: TargetUrlOpt = "http://localhost:8000",
    fixtures_dir: FixturesDirOpt = Path("fixtures"),
    output: OutputOpt = None,
    output_format: FormatOpt = "json",
) -> None:
    """Run the permissions/access-control benchmark."""
    run_benchmark("permissions", target_url, fixtures_dir, output, output_format)


@run_app.command("sync")
def run_sync(
    target_url: TargetUrlOpt = "http://localhost:8000",
    fixtures_dir: FixturesDirOpt = Path("fixtures"),
    output: OutputOpt = None,
    output_format: FormatOpt = "json",
) -> None:
    """Run the sync protocol convergence benchmark."""
    run_benchmark("sync", target_url, fixtures_dir, output, output_format)


@run_app.command("offline-consistency")
def run_offline_consistency(
    target_url: TargetUrlOpt = "http://localhost:8000",
    fixtures_dir: FixturesDirOpt = Path("fixtures"),
    output: OutputOpt = None,
    output_format: FormatOpt = "json",
) -> None:
    """Run the offline/online consistency benchmark."""
    run_benchmark("offline-consistency", target_url, fixtures_dir, output, output_format)


@run_app.command("all")
def run_all(
    target_url: TargetUrlOpt = "http://localhost:8000",
    fixtures_dir: FixturesDirOpt = Path("fixtures"),
    output_format: FormatOpt = "json",
) -> None:
    """Run every benchmark area."""
    for area in FOLDER_MAP:
        typer.echo(f"=== Running benchmark: {area} ===")
        try:
            run_benchmark(area, target_url, fixtures_dir, None, output_format)
        except typer.Exit as e:
            if e.exit_code != 0:
                typer.echo(f"Failed to run benchmark for {area}")
        typer.echo("")


if __name__ == "__main__":
    app()
