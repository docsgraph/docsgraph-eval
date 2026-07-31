"""Retrieval quality benchmark stubs.

Will eventually measure search/retrieval quality (e.g. precision, recall,
and ranking metrics such as MRR/NDCG) against queries and relevance
judgments in ``fixtures/retrieval/``.
"""

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, unimplemented

AREA = "retrieval"


def run(cases: list[BenchmarkCase]) -> BenchmarkResult:
    """Run the retrieval quality benchmark.

    Args:
        cases: Cases pairing queries with golden relevant-document sets.

    Returns:
        Aggregate precision/recall/ranking results, once implemented.

    Raises:
        NotImplementedError: Retrieval benchmarking is not implemented yet.
    """
    unimplemented(AREA, cases)
