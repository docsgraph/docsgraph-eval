"""Command-line interface for docsgraph-eval.

Provides one ``run`` subcommand per benchmark area, plus a ``run all``
command that runs every area. Each command currently reports that the
corresponding benchmark is not yet implemented.
"""

import typer

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

BENCHMARK_AREAS: tuple[str, ...] = (
    "ocr",
    "extraction",
    "retrieval",
    "evidence_attribution",
    "graph_generation",
    "permissions",
    "sync",
    "offline_consistency",
)


def _not_implemented(area: str) -> None:
    """Report that a benchmark area has no runnable implementation yet.

    Args:
        area: Name of the benchmark area.
    """
    typer.echo(f"[{area}] not yet implemented")


@run_app.command("ocr")
def run_ocr() -> None:
    """Run the OCR accuracy benchmark."""
    _not_implemented("ocr")


@run_app.command("extraction")
def run_extraction() -> None:
    """Run the structured extraction benchmark."""
    _not_implemented("extraction")


@run_app.command("retrieval")
def run_retrieval() -> None:
    """Run the retrieval quality benchmark."""
    _not_implemented("retrieval")


@run_app.command("evidence-attribution")
def run_evidence_attribution() -> None:
    """Run the evidence attribution benchmark."""
    _not_implemented("evidence_attribution")


@run_app.command("graph-generation")
def run_graph_generation() -> None:
    """Run the knowledge graph generation quality benchmark."""
    _not_implemented("graph_generation")


@run_app.command("permissions")
def run_permissions() -> None:
    """Run the permissions/access-control benchmark."""
    _not_implemented("permissions")


@run_app.command("sync")
def run_sync() -> None:
    """Run the sync protocol convergence benchmark."""
    _not_implemented("sync")


@run_app.command("offline-consistency")
def run_offline_consistency() -> None:
    """Run the offline/online consistency benchmark."""
    _not_implemented("offline_consistency")


@run_app.command("all")
def run_all() -> None:
    """Run every benchmark area."""
    for area in BENCHMARK_AREAS:
        _not_implemented(area)


if __name__ == "__main__":
    app()
