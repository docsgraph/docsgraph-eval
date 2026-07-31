"""Tests for the offline consistency benchmark stub."""

import pytest

from docsgraph_eval.core import BenchmarkCase
from docsgraph_eval.offline_consistency.bench import run


def test_run_raises_not_implemented() -> None:
    case = BenchmarkCase(
        case_id="sample-1",
        input_data={"offline_edits": ["rename doc-1"], "reconnect_order": ["client-a"]},
        expected_output={"doc-1": "renamed"},
    )
    with pytest.raises(NotImplementedError):
        run([case])
