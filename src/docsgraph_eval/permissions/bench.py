"""Permissions benchmark stubs.

Will eventually measure whether permission/access-control decisions match
expected allow/deny outcomes for scenarios in ``fixtures/permissions/``.
"""

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, unimplemented

AREA = "permissions"


def run(cases: list[BenchmarkCase]) -> BenchmarkResult:
    """Run the permissions benchmark.

    Args:
        cases: Cases pairing access-control scenarios with the expected
            allow/deny outcome.

    Returns:
        Aggregate access-control correctness results, once implemented.

    Raises:
        NotImplementedError: Permissions benchmarking is not implemented yet.
    """
    unimplemented(AREA, cases)
