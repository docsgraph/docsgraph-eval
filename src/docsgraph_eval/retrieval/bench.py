from typing import Any

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, run_http_case

AREA = "retrieval"


def run(cases: list[BenchmarkCase], target_url: str = "http://localhost:8000") -> BenchmarkResult:
    """Run the retrieval quality benchmark.

    Args:
        cases: Cases pairing queries with golden relevant-document sets.
        target_url: URL of the target docsgraph-server instance.

    Returns:
        Aggregate precision/recall/ranking results.
    """
    total_cases = len(cases)
    passed = 0
    total_score = 0.0
    case_details = {}

    for case in cases:

        def eval_retrieval(
            expected: Any, actual: Any, tol: float | None
        ) -> tuple[bool, float, dict[str, Any]]:
            actual_ids = actual.get("results", []) if isinstance(actual, dict) else actual
            if not isinstance(actual_ids, list) or not isinstance(expected, list):
                return False, 0.0, {"error": "Invalid output formats"}

            expected_set = set(expected)
            actual_set = set(actual_ids)

            if not expected_set:
                score = 1.0 if not actual_set else 0.0
                return score == 1.0, score, {"reciprocal_rank": score}

            intersection = expected_set.intersection(actual_set)
            recall = len(intersection) / len(expected_set)
            precision = len(intersection) / len(actual_set) if actual_set else 0.0

            score = (
                2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            )

            # Compute Reciprocal Rank (rank of first relevant document)
            rr = 0.0
            for rank, doc_id in enumerate(actual_ids, start=1):
                if doc_id in expected_set:
                    rr = 1.0 / rank
                    break

            limit = tol if tol is not None else 0.0
            case_passed = recall >= (1.0 - limit)
            return (
                case_passed,
                score,
                {
                    "precision": precision,
                    "recall": recall,
                    "f1_score": score,
                    "reciprocal_rank": rr,
                },
            )

        case_passed, score, details = run_http_case(
            target_url=target_url,
            endpoint="/api/v1/retrieval",
            method="POST",
            input_data=case.input_data,
            expected_output=case.expected_output,
            tolerance=case.tolerance,
            eval_fn=eval_retrieval,
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
    total_rr = sum(
        info.get("reciprocal_rank", 0.0) for info in case_details.values() if isinstance(info, dict)
    )
    mrr = total_rr / total_cases if total_cases > 0 else 0.0
    return BenchmarkResult(
        area=AREA,
        total_cases=total_cases,
        passed=passed,
        score=avg_score,
        details={"cases": case_details, "mrr": mrr},
    )
