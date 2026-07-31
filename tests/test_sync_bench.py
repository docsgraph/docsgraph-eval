"""Tests for the sync benchmark stub."""

import pytest

from docsgraph_eval.core import BenchmarkCase
from docsgraph_eval.sync.bench import run


def test_run_raises_not_implemented() -> None:
    case = BenchmarkCase(
        case_id="sample-1",
        input_data=["client-a: edit doc-1", "client-b: edit doc-1"],
        expected_output={"doc-1": "merged"},
    )
    with pytest.raises(NotImplementedError):
        run([case])
