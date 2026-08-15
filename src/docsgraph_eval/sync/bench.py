"""Sync convergence benchmark stubs.

Will eventually measure whether the sync protocol converges to a
consistent state across simulated clients, given the operation logs and
expected converged state in ``fixtures/sync/``.
"""

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, unimplemented

AREA = "sync"


def run(cases: list[BenchmarkCase]) -> BenchmarkResult:
    """Run the sync convergence benchmark.

    Args:
        cases: Cases pairing simulated multi-client operation sequences
            with the expected converged state.

    Returns:
        Aggregate convergence-correctness results, once implemented.

    Raises:
        NotImplementedError: Sync benchmarking is not implemented yet.
    """
    unimplemented(AREA, cases)
