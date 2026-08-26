import contextlib
import importlib
from collections.abc import Callable

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, BenchmarkSuite


def run_suite(suite: BenchmarkSuite, target_url: str) -> BenchmarkResult:
    """Run a single benchmark suite against a configured target instance.

    Args:
        suite: The benchmark suite to run.
        target_url: URL of the target docsgraph-server instance.

    Returns:
        The benchmark result.
    """
    area = suite.area
    try:
        module = importlib.import_module(f"docsgraph_eval.{area}.bench")
        run_func: Callable[[list[BenchmarkCase], str], BenchmarkResult] = getattr(module, "run")  # noqa: B009
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Unknown or unimplemented benchmark area: {area}") from e

    return run_func(suite.cases, target_url)


def run_all_suites(suites: list[BenchmarkSuite], target_url: str) -> list[BenchmarkResult]:
    """Run a list of benchmark suites against a configured target instance.

    Args:
        suites: List of benchmark suites to run.
        target_url: URL of the target docsgraph-server instance.

    Returns:
        A list of benchmark results.
    """
    results = []
    for suite in suites:
        with contextlib.suppress(ValueError):
            results.append(run_suite(suite, target_url))
    return results
