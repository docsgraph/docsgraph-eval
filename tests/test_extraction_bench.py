"""Tests for the extraction benchmark stub."""

import pytest

from docsgraph_eval.core import BenchmarkCase
from docsgraph_eval.extraction.bench import run


def test_run_raises_not_implemented() -> None:
    case = BenchmarkCase(
        case_id="sample-1",
        input_data="contract.pdf",
        expected_output={"party": "Acme Inc."},
    )
    with pytest.raises(NotImplementedError):
        run([case])
