from typing import Any

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, run_http_case

AREA = "permissions"


def run(cases: list[BenchmarkCase], target_url: str = "http://localhost:8000") -> BenchmarkResult:
    """Run the permissions benchmark.

    Args:
        cases: Cases pairing access-control scenarios with the expected
            allow/deny outcome.
        target_url: URL of the target docsgraph-server instance.

    Returns:
        Aggregate access-control correctness results.
    """
    total_cases = len(cases)
    passed = 0
    total_score = 0.0
    case_details = {}

    for case in cases:

        def eval_permissions(
            expected: Any, actual: Any, _tol: float | None
        ) -> tuple[bool, float, dict[str, Any]]:
            actual_allow = actual.get("allowed", False) if isinstance(actual, dict) else actual
            case_passed = bool(actual_allow) == bool(expected)
            score = 1.0 if case_passed else 0.0
            details: dict[str, Any] = {"actual_allowed": actual_allow}
            if not case_passed:
                details["error"] = (
                    f"Permission check failed: Expected access to be "
                    f"{'ALLOWED' if expected else 'DENIED'}, but got "
                    f"{'ALLOWED' if actual_allow else 'DENIED'}."
                )
            return case_passed, score, details

        case_passed, score, details = run_http_case(
            target_url=target_url,
            endpoint="/api/v1/permissions/check",
            method="POST",
            input_data=case.input_data,
            expected_output=case.expected_output,
            tolerance=case.tolerance,
            eval_fn=eval_permissions,
        )

        if case_passed:
            passed += 1
        total_score += score
        case_details[case.case_id] = {
            "passed": case_passed,
            "score": score,
            **details,
        }

    avg_score = total_score / total_cases if total_cases > 0 else 0.0
    return BenchmarkResult(
        area=AREA,
        total_cases=total_cases,
        passed=passed,
        score=avg_score,
        details={"cases": case_details},
    )
