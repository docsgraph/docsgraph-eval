"""Tests for shared benchmark case/result types."""

import pytest

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, unimplemented


def test_benchmark_case_defaults() -> None:
    case = BenchmarkCase(case_id="c1", input_data=1, expected_output=2)
    assert case.case_id == "c1"
    assert case.tolerance is None
    assert case.metadata == {}


def test_benchmark_case_with_tolerance_and_metadata() -> None:
    case = BenchmarkCase(
        case_id="c2",
        input_data="a",
        expected_output="b",
        tolerance=0.1,
        metadata={"source": "unit-test"},
    )
    assert case.tolerance == 0.1
    assert case.metadata == {"source": "unit-test"}


def test_benchmark_result_defaults() -> None:
    result = BenchmarkResult(area="ocr")
    assert result.total_cases == 0
    assert result.passed == 0
    assert result.score is None
    assert result.details == {}


def test_unimplemented_raises_with_case_count() -> None:
    cases = [BenchmarkCase(case_id="c1", input_data=1, expected_output=1)]
    with pytest.raises(NotImplementedError, match=r"ocr.*1 case"):
        unimplemented("ocr", cases)
