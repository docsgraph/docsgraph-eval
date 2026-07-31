"""Tests for the retrieval benchmark stub."""

import pytest

from docsgraph_eval.core import BenchmarkCase
from docsgraph_eval.retrieval.bench import run


def test_run_raises_not_implemented() -> None:
    case = BenchmarkCase(
        case_id="sample-1",
        input_data="termination clause",
        expected_output=["doc-1", "doc-7"],
    )
    with pytest.raises(NotImplementedError):
        run([case])
