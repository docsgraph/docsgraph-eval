"""Shared types used by every benchmark subpackage.

Each capability area (``ocr``, ``extraction``, ``retrieval``, ...) builds its
benchmark cases and results on top of :class:`BenchmarkCase` and
:class:`BenchmarkResult` so that reporting and CLI plumbing can stay generic.
"""

from typing import Any, NoReturn

from pydantic import BaseModel, Field


class BenchmarkCase(BaseModel):
    """A single benchmark test case.

    Attributes:
        case_id: Unique identifier for this case within its benchmark area.
        input_data: The input fed to the system under test (e.g. a document
            path or payload). Shape is area-specific.
        expected_output: The expected/gold output for this case. Shape is
            area-specific.
        tolerance: Optional numeric tolerance for approximate matching
            (e.g. an allowed error rate). ``None`` means exact match.
        metadata: Arbitrary extra context about the case (source, difficulty,
            tags, etc.).
    """

    case_id: str
    input_data: Any
    expected_output: Any
    tolerance: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BenchmarkResult(BaseModel):
    """Aggregate result of running a set of benchmark cases for one area.

    Attributes:
        area: Name of the benchmark area (e.g. ``"ocr"``).
        total_cases: Number of cases that were run.
        passed: Number of cases that passed.
        score: Overall score in ``[0, 1]``, if the area defines one.
        details: Per-case or summary details, area-specific.
    """

    area: str
    total_cases: int = 0
    passed: int = 0
    score: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)


def unimplemented(area: str, cases: list[BenchmarkCase]) -> NoReturn:
    """Raise a consistent, informative error for a not-yet-implemented benchmark.

    Args:
        area: Name of the benchmark area (e.g. ``"ocr"``).
        cases: The cases that were passed to the area's ``run()``.

    Raises:
        NotImplementedError: Always. Benchmark logic for the area has not
            been written yet.
    """
    msg = f"{area} benchmark is not implemented yet ({len(cases)} case(s) given)."
    raise NotImplementedError(msg)
