from typing import Any

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, run_http_case

AREA = "extraction"


def run(cases: list[BenchmarkCase], target_url: str = "http://localhost:8000") -> BenchmarkResult:
    """Run the structured extraction benchmark.

    Args:
        cases: Cases pairing documents with golden field/clause extractions.
        target_url: URL of the target docsgraph-server instance.

    Returns:
        Aggregate extraction accuracy results.
    """
    total_cases = len(cases)
    passed = 0
    total_score = 0.0
    case_details = {}

    for case in cases:

        def eval_extraction(
            expected: Any, actual: Any, tol: float | None
        ) -> tuple[bool, float, dict[str, Any]]:
            actual_fields = (
                actual.get("extracted_fields", {}) if isinstance(actual, dict) else actual
            )
            if not isinstance(actual_fields, dict) or not isinstance(expected, dict):
                return False, 0.0, {"error": "Invalid output formats"}

            matched_fields = 0
            total_fields = len(expected)
            if total_fields == 0:
                return True, 1.0, {}

            for k, expected_val in expected.items():
                actual_val = actual_fields.get(k)
                if actual_val == expected_val:
                    matched_fields += 1
                elif isinstance(expected_val, (int, float)) and isinstance(
                    actual_val, (int, float)
                ):
                    limit = tol if tol is not None else 1e-9
                    if abs(expected_val - actual_val) <= limit:
                        matched_fields += 1

            score = matched_fields / total_fields
            limit = tol if tol is not None else 0.0
            case_passed = score >= (1.0 - limit)
            return (
                case_passed,
                score,
                {
                    "matched_fields": matched_fields,
                    "total_fields": total_fields,
                },
            )

        case_passed, score, details = run_http_case(
            target_url=target_url,
            endpoint="/api/v1/extraction",
            method="POST",
            input_data=case.input_data,
            expected_output=case.expected_output,
            tolerance=case.tolerance,
            eval_fn=eval_extraction,
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
