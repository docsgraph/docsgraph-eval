import contextlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, NoReturn

import httpx
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


class BenchmarkSuite(BaseModel):
    """A collection of benchmark cases for a specific area.

    Attributes:
        area: Name of the benchmark area (e.g. ``"ocr"``).
        cases: List of benchmark cases.
    """

    area: str
    cases: list[BenchmarkCase] = Field(default_factory=list)


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


def load_suite(path: Path) -> BenchmarkSuite:
    """Load a benchmark suite from a JSON file.

    Args:
        path: Path to the suite JSON file.

    Returns:
        The loaded BenchmarkSuite.
    """
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return BenchmarkSuite.model_validate(data)


def load_suites_from_dir(path: Path) -> list[BenchmarkSuite]:
    """Load all benchmark suites from JSON files in a directory or a single file.

    Args:
        path: Path to a directory containing suite JSON files, or to a single file.

    Returns:
        A list of loaded BenchmarkSuites.
    """
    suites: list[BenchmarkSuite] = []
    if path.is_dir():
        for file_path in sorted(path.glob("*.json")):
            with contextlib.suppress(Exception):
                suites.append(load_suite(file_path))
    elif path.is_file() and path.suffix == ".json":
        with contextlib.suppress(Exception):
            suites.append(load_suite(path))
    return suites


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


def run_http_case(
    target_url: str,
    endpoint: str,
    method: str,
    input_data: Any,
    expected_output: Any,
    tolerance: float | None = None,
    eval_fn: Callable[[Any, Any, float | None], tuple[bool, float, dict[str, Any]]] | None = None,
) -> tuple[bool, float, dict[str, Any]]:
    """Execute a single case against the target instance and evaluate the response.

    Args:
        target_url: Base URL of the target instance.
        endpoint: API endpoint (e.g. "/api/v1/ocr").
        method: HTTP method (e.g. "POST", "GET").
        input_data: Input data to send.
        expected_output: Expected output to compare against.
        tolerance: Numeric tolerance/error threshold.
        eval_fn: Custom evaluation function taking (expected, actual, tolerance)
            and returning (passed, score, details).

    Returns:
        A tuple of (passed, score, details).
    """
    url = f"{target_url.rstrip('/')}{endpoint}"
    details: dict[str, Any] = {}

    try:
        if method.upper() == "POST":
            if isinstance(input_data, dict) and "file_path" in input_data:
                file_path = Path(input_data["file_path"])
                if not file_path.exists():
                    return False, 0.0, {"error": f"File not found: {file_path}"}
                with file_path.open("rb") as f:
                    response = httpx.post(url, files={"file": f}, timeout=10.0)
            elif isinstance(input_data, str) and input_data.startswith("file://"):
                file_path = Path(input_data[7:])
                if not file_path.exists():
                    return False, 0.0, {"error": f"File not found: {file_path}"}
                with file_path.open("rb") as f:
                    response = httpx.post(url, files={"file": f}, timeout=10.0)
            else:
                response = httpx.post(url, json=input_data, timeout=10.0)
        else:
            response = httpx.get(url, params=input_data, timeout=10.0)

        details["status_code"] = response.status_code
        if response.status_code != 200:
            details["error"] = f"HTTP error {response.status_code}: {response.text}"
            return False, 0.0, details

        actual_output = response.json()
        details["actual_output"] = actual_output

        if eval_fn:
            passed, score, eval_details = eval_fn(expected_output, actual_output, tolerance)
            details.update(eval_details)
            return passed, score, details

        passed = actual_output == expected_output
        score = 1.0 if passed else 0.0
        return passed, score, details

    except Exception as e:
        details["error"] = f"Request failed: {e}"
        return False, 0.0, details
