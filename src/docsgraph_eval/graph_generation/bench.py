from typing import Any

from docsgraph_eval.core import BenchmarkCase, BenchmarkResult, run_http_case

AREA = "graph_generation"


def run(cases: list[BenchmarkCase], target_url: str = "http://localhost:8000") -> BenchmarkResult:
    """Run the graph generation quality benchmark.

    Args:
        cases: Cases pairing documents with golden entity/relation graphs.
        target_url: URL of the target docsgraph-server instance.

    Returns:
        Aggregate entity/relation correctness results.
    """
    total_cases = len(cases)
    passed = 0
    total_score = 0.0
    case_details = {}

    for case in cases:

        def eval_graph(
            expected: Any, actual: Any, tol: float | None
        ) -> tuple[bool, float, dict[str, Any]]:
            if not isinstance(expected, dict) or not isinstance(actual, dict):
                return False, 0.0, {"error": "Invalid output formats"}

            actual_nodes = actual.get("nodes", [])
            actual_edges = actual.get("edges", [])
            expected_nodes = expected.get("nodes", [])
            expected_edges = expected.get("edges", [])

            matched_nodes = 0
            for en in expected_nodes:
                if en in actual_nodes:
                    matched_nodes += 1
            node_recall = matched_nodes / len(expected_nodes) if expected_nodes else 1.0
            node_precision = (
                matched_nodes / len(actual_nodes)
                if actual_nodes
                else (1.0 if not expected_nodes else 0.0)
            )

            matched_edges = 0
            for ee in expected_edges:
                if ee in actual_edges:
                    matched_edges += 1
            edge_recall = matched_edges / len(expected_edges) if expected_edges else 1.0
            edge_precision = (
                matched_edges / len(actual_edges)
                if actual_edges
                else (1.0 if not expected_edges else 0.0)
            )

            edge_f1 = (
                2 * (edge_precision * edge_recall) / (edge_precision + edge_recall)
                if (edge_precision + edge_recall) > 0
                else 0.0
            )

            node_score = 0.5 * node_recall + 0.5 * node_precision
            score = 0.5 * node_score + 0.5 * edge_f1

            limit = tol if tol is not None else 0.0
            case_passed = score >= (1.0 - limit)
            return (
                case_passed,
                score,
                {
                    "node_precision": node_precision,
                    "node_recall": node_recall,
                    "relationship_precision": edge_precision,
                    "relationship_recall": edge_recall,
                    "relationship_f1": edge_f1,
                },
            )

        case_passed, score, details = run_http_case(
            target_url=target_url,
            endpoint="/api/v1/graph",
            method="POST",
            input_data=case.input_data,
            expected_output=case.expected_output,
            tolerance=case.tolerance,
            eval_fn=eval_graph,
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
