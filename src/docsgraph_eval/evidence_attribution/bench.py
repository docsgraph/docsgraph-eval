"""Evidence attribution benchmark stubs.

Will eventually measure whether answers correctly cite the source passage
they were derived from, against golden citations in
``fixtures/evidence_attribution/``.
"""

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, unimplemented

AREA = "evidence_attribution"


def run(cases: list[BenchmarkCase]) -> BenchmarkResult:
    """Run the evidence attribution benchmark.

    Args:
        cases: Cases pairing answers with the golden source passage(s) they
            should cite.

    Returns:
        Aggregate citation-correctness results, once implemented.

    Raises:
        NotImplementedError: Evidence attribution benchmarking is not
            implemented yet.
    """
    unimplemented(AREA, cases)
