from typing import Any

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, run_http_case

AREA = "evidence_attribution"


def run(cases: list[BenchmarkCase], target_url: str = "http://localhost:8000") -> BenchmarkResult:
    """Run the evidence attribution benchmark.

    Args:
        cases: Cases pairing answers with the golden source passage(s) they
            should cite.
        target_url: URL of the target docsgraph-server instance.

    Returns:
        Aggregate citation-correctness results.
    """
    total_cases = len(cases)
    passed = 0
    total_score = 0.0
    case_details = {}

    for case in cases:

        def eval_attribution(
            expected: Any, actual: Any, _tol: float | None
        ) -> tuple[bool, float, dict[str, Any]]:
            actual_attribution = actual.get("evidence", "") if isinstance(actual, dict) else actual

            expected_str = str(expected)
            actual_str = str(actual_attribution)

            case_passed = expected_str in actual_str or actual_str in expected_str
            score = 1.0 if case_passed else 0.0
            return case_passed, score, {"actual_attribution": actual_str}

        case_passed, score, details = run_http_case(
            target_url=target_url,
            endpoint="/api/v1/evidence",
            method="POST",
            input_data=case.input_data,
            expected_output=case.expected_output,
            tolerance=case.tolerance,
            eval_fn=eval_attribution,
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
