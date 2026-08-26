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
        case_passed, score, details = run_http_case(
            target_url=target_url,
            endpoint="/api/v1/sync/consistency",
            method="POST",
            input_data=case.input_data,
            expected_output=case.expected_output,
            tolerance=case.tolerance,
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
