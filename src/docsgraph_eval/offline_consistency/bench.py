from typing import Any

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, run_http_case

AREA = "offline_consistency"


def run(cases: list[BenchmarkCase], target_url: str = "http://localhost:8000") -> BenchmarkResult:
    """Run the offline consistency benchmark.

    Args:
        cases: Cases pairing offline/online transition scenarios with the
            expected final state.
        target_url: URL of the target docsgraph-server instance.

    Returns:
        Aggregate consistency results.
    """
    total_cases = len(cases)
    passed = 0
    total_score = 0.0
    case_details = {}

    for case in cases:

        def eval_consistency(
            expected: Any, actual: Any, _tol: float | None
        ) -> tuple[bool, float, dict[str, Any]]:
            if not isinstance(expected, dict) or not isinstance(actual, dict):
                return False, 0.0, {"error": "Invalid output formats"}

            actual_state = actual.get("state", {})
            actual_lost = actual.get("data_loss", False)

            expected_state = expected.get("state", {})
            expected_lost = expected.get("data_loss", False)

            state_match = actual_state == expected_state
            # Silent data loss check (fail if data_loss is True)
            no_data_loss = (
                not actual_lost and not expected_lost if expected_lost else not actual_lost
            )

            case_passed = state_match and no_data_loss
            score = 1.0 if case_passed else 0.0

            details = {
                "state_match": state_match,
                "no_data_loss": no_data_loss,
                "actual_state": actual_state,
            }
            if not state_match:
                details["error"] = (
                    f"Final state inconsistent. Expected: {expected_state}, Got: {actual_state}"
                )
            elif not no_data_loss:
                details["error"] = "Silent data loss detected in final state."

            return case_passed, score, details

        case_passed, score, details = run_http_case(
            target_url=target_url,
            endpoint="/api/v1/sync/consistency",
            method="POST",
            input_data=case.input_data,
            expected_output=case.expected_output,
            tolerance=case.tolerance,
            eval_fn=eval_consistency,
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
