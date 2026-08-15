"""OCR accuracy benchmark stubs.

Will eventually measure OCR output against ground-truth transcriptions
using metrics such as character error rate (CER) and word error rate
(WER) over the fixtures in ``fixtures/ocr/``.
"""

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, unimplemented

AREA = "ocr"


def run(cases: list[BenchmarkCase]) -> BenchmarkResult:
    """Run the OCR accuracy benchmark.

    Args:
        cases: Cases pairing scanned/source documents with ground-truth
            transcriptions.

    Returns:
        Aggregate CER/WER results, once implemented.

    Raises:
        NotImplementedError: OCR benchmarking is not implemented yet.
    """
    unimplemented(AREA, cases)
