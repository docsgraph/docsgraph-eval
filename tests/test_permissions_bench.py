"""Tests for the permissions benchmark stub."""

import pytest

from docsgraph_eval.core import BenchmarkCase
from docsgraph_eval.permissions.bench import run


def test_run_raises_not_implemented() -> None:
    case = BenchmarkCase(
        case_id="sample-1",
        input_data={"user": "alice", "resource": "doc-1", "action": "read"},
        expected_output="allow",
    )
    with pytest.raises(NotImplementedError):
        run([case])
