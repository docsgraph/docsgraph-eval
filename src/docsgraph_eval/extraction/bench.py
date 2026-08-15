"""Structured extraction benchmark stubs.

Will eventually measure how accurately structured fields and clauses are
extracted from documents against golden annotations in
``fixtures/extraction/``.
"""

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, unimplemented

AREA = "extraction"


def run(cases: list[BenchmarkCase]) -> BenchmarkResult:
    """Run the structured extraction benchmark.

    Args:
        cases: Cases pairing documents with golden field/clause extractions.

    Returns:
        Aggregate extraction accuracy results, once implemented.

    Raises:
        NotImplementedError: Extraction benchmarking is not implemented yet.
    """
    unimplemented(AREA, cases)
