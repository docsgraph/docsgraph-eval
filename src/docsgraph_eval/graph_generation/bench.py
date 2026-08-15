"""Graph generation quality benchmark stubs.

Will eventually measure the quality of the generated knowledge graph
(entity/relation correctness) against golden graphs in
``fixtures/graph_generation/``.
"""

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, unimplemented

AREA = "graph_generation"


def run(cases: list[BenchmarkCase]) -> BenchmarkResult:
    """Run the graph generation quality benchmark.

    Args:
        cases: Cases pairing documents with golden entity/relation graphs.

    Returns:
        Aggregate entity/relation correctness results, once implemented.

    Raises:
        NotImplementedError: Graph generation benchmarking is not
            implemented yet.
    """
    unimplemented(AREA, cases)
