"""Tests for the evidence attribution benchmark stub."""

import pytest

from docsgraph_eval.core import BenchmarkCase
from docsgraph_eval.evidence_attribution.bench import run


def test_run_raises_not_implemented() -> None:
    case = BenchmarkCase(
        case_id="sample-1",
        input_data="What is the notice period?",
        expected_output="doc-3#p12",
    )
    with pytest.raises(NotImplementedError):
        run([case])
