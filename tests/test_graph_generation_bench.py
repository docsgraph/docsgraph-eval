"""Tests for the graph generation benchmark stub."""

import pytest

from docsgraph_eval.core import BenchmarkCase
from docsgraph_eval.graph_generation.bench import run


def test_run_raises_not_implemented() -> None:
    case = BenchmarkCase(
        case_id="sample-1",
        input_data="contract.pdf",
        expected_output={"entities": ["Acme Inc."], "relations": []},
    )
    with pytest.raises(NotImplementedError):
        run([case])
