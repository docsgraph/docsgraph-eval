from typing import Any

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, run_http_case

AREA = "ocr"


def run(cases: list[BenchmarkCase], target_url: str = "http://localhost:8000") -> BenchmarkResult:
    """Run the OCR accuracy benchmark.

    Args:
        cases: Cases pairing scanned/source documents with ground-truth
            transcriptions.
        target_url: URL of the target docsgraph-server instance.

    Returns:
        Aggregate CER/WER results.
    """
    total_cases = len(cases)
    passed = 0
    total_score = 0.0
    case_details = {}

    for case in cases:

        def eval_ocr(
            expected: Any, actual: Any, tol: float | None
        ) -> tuple[bool, float, dict[str, Any]]:
            actual_text = ""
            if isinstance(actual, dict):
                actual_text = actual.get("text", "")
            elif isinstance(actual, str):
                actual_text = actual

            ref = str(expected)
            hyp = str(actual_text)

            if not ref:
                cer = 0.0 if not hyp else 1.0
            else:
                d = [[0] * (len(hyp) + 1) for _ in range(len(ref) + 1)]
                for i in range(len(ref) + 1):
                    d[i][0] = i
                for j in range(len(hyp) + 1):
                    d[0][j] = j
                for i in range(1, len(ref) + 1):
                    for j in range(1, len(hyp) + 1):
                        if ref[i - 1] == hyp[j - 1]:
                            d[i][j] = d[i - 1][j - 1]
                        else:
                            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + 1)
                cer = d[len(ref)][len(hyp)] / len(ref)

            score = max(0.0, 1.0 - cer)
            limit = tol if tol is not None else 0.0
            case_passed = cer <= limit
            return case_passed, score, {"cer": cer, "actual_text": actual_text}

        case_passed, score, details = run_http_case(
            target_url=target_url,
            endpoint="/api/v1/ocr",
            method="POST",
            input_data=case.input_data,
            expected_output=case.expected_output,
            tolerance=case.tolerance,
            eval_fn=eval_ocr,
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
