"""Offline consistency benchmark stubs.

Will eventually measure whether data stays consistent across offline/online
transitions and reconnects, using the scenarios in
``fixtures/offline_consistency/``.
"""

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, unimplemented

AREA = "offline_consistency"


def run(cases: list[BenchmarkCase]) -> BenchmarkResult:
    """Run the offline consistency benchmark.

    Args:
        cases: Cases pairing offline/online transition scenarios with the
            expected final state.

    Returns:
        Aggregate consistency results, once implemented.

    Raises:
        NotImplementedError: Offline consistency benchmarking is not
            implemented yet.
    """
    unimplemented(AREA, cases)
