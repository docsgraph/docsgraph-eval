"""Tests for the OCR benchmark stub."""

import pytest

from docsgraph_eval.core import BenchmarkCase
from docsgraph_eval.ocr.bench import run


def test_run_raises_not_implemented() -> None:
    case = BenchmarkCase(case_id="sample-1", input_data="scan.png", expected_output="hello world")
    with pytest.raises(NotImplementedError):
        run([case])
