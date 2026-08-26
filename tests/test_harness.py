import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest
from typer.testing import CliRunner

from docsgraph_eval.cli import app
from docsgraph_eval.core import (
    BenchmarkCase,
    BenchmarkResult,
    BenchmarkSuite,
    load_suite,
    load_suites_from_dir,
    run_http_case,
)
from docsgraph_eval.runner import run_all_suites, run_suite

runner = CliRunner()


def test_load_suite_valid(tmp_path: Path) -> None:
    suite_file = tmp_path / "valid.json"
    data = {
        "area": "ocr",
        "cases": [
            {
                "case_id": "c1",
                "input_data": "doc.png",
                "expected_output": "hello",
                "tolerance": 0.05,
            }
        ],
    }
    suite_file.write_text(json.dumps(data), encoding="utf-8")

    suite = load_suite(suite_file)
    assert suite.area == "ocr"
    assert len(suite.cases) == 1
    assert suite.cases[0].case_id == "c1"
    assert suite.cases[0].input_data == "doc.png"
    assert suite.cases[0].expected_output == "hello"
    assert suite.cases[0].tolerance == 0.05


def test_load_suites_from_dir(tmp_path: Path) -> None:
    # Set up directory
    dir_path = tmp_path / "suites"
    dir_path.mkdir()

    # Valid suite
    suite1 = dir_path / "suite1.json"
    suite1.write_text(json.dumps({"area": "ocr", "cases": []}), encoding="utf-8")

    # Invalid JSON
    suite2 = dir_path / "suite2.json"
    suite2.write_text("invalid json", encoding="utf-8")

    # Not a json extension
    suite3 = dir_path / "suite3.txt"
    suite3.write_text(json.dumps({"area": "ocr", "cases": []}), encoding="utf-8")

    suites = load_suites_from_dir(dir_path)
    assert len(suites) == 1
    assert suites[0].area == "ocr"

    # Single file load
    single_load = load_suites_from_dir(suite1)
    assert len(single_load) == 1


@patch("httpx.post")
def test_run_http_case_post_json(mock_post: MagicMock) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"text": "hello"}
    mock_post.return_value = mock_response

    passed, score, details = run_http_case(
        target_url="http://localhost:8000",
        endpoint="/api/v1/ocr",
        method="POST",
        input_data={"param": 1},
        expected_output={"text": "hello"},
    )

    assert passed is True
    assert score == 1.0
    assert details["status_code"] == 200
    assert details["actual_output"] == {"text": "hello"}
    mock_post.assert_called_once_with(
        "http://localhost:8000/api/v1/ocr", json={"param": 1}, timeout=10.0
    )


@patch("httpx.post")
def test_run_http_case_post_file(mock_post: MagicMock, tmp_path: Path) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"text": "hello"}
    mock_post.return_value = mock_response

    dummy_file = tmp_path / "dummy.png"
    dummy_file.write_text("file_contents")

    # File path as dictionary key
    passed, score, details = run_http_case(
        target_url="http://localhost:8000",
        endpoint="/api/v1/ocr",
        method="POST",
        input_data={"file_path": str(dummy_file)},
        expected_output={"text": "hello"},
    )
    assert passed is True
    assert score == 1.0
    assert isinstance(details, dict)

    # File path as URL-like string
    passed2, score2, details2 = run_http_case(
        target_url="http://localhost:8000",
        endpoint="/api/v1/ocr",
        method="POST",
        input_data=f"file://{dummy_file}",
        expected_output={"text": "hello"},
    )
    assert passed2 is True
    assert score2 == 1.0
    assert isinstance(details2, dict)


@patch("httpx.post")
def test_run_http_case_file_not_found(mock_post: MagicMock) -> None:
    passed, score, details = run_http_case(
        target_url="http://localhost:8000",
        endpoint="/api/v1/ocr",
        method="POST",
        input_data={"file_path": "nonexistent.png"},
        expected_output={"text": "hello"},
    )
    assert passed is False
    assert score == 0.0
    assert "error" in details
    assert "File not found" in details["error"]


@patch("httpx.get")
def test_run_http_case_get(mock_get: MagicMock) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_get.return_value = mock_response

    passed, score, details = run_http_case(
        target_url="http://localhost:8000",
        endpoint="/api/v1/status",
        method="GET",
        input_data={"q": "test"},
        expected_output={"status": "ok"},
    )
    assert passed is True
    assert score == 1.0
    assert isinstance(details, dict)
    mock_get.assert_called_once_with(
        "http://localhost:8000/api/v1/status", params={"q": "test"}, timeout=10.0
    )


@patch("httpx.get")
def test_run_http_case_http_error(mock_get: MagicMock) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_response.text = "Internal error"
    mock_get.return_value = mock_response

    passed, score, details = run_http_case(
        target_url="http://localhost:8000",
        endpoint="/api/v1/status",
        method="GET",
        input_data={},
        expected_output={},
    )
    assert passed is False
    assert score == 0.0
    assert details["status_code"] == 500
    assert "error" in details


@patch("httpx.get")
def test_run_http_case_exception(mock_get: MagicMock) -> None:
    mock_get.side_effect = httpx.ConnectTimeout("Timeout")

    passed, score, details = run_http_case(
        target_url="http://localhost:8000",
        endpoint="/api/v1/status",
        method="GET",
        input_data={},
        expected_output={},
    )
    assert passed is False
    assert score == 0.0
    assert "error" in details


@patch("httpx.post")
def test_ocr_benchmark(mock_post: MagicMock) -> None:
    from docsgraph_eval.ocr import bench as ocr_bench

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"text": "hello word"}
    mock_post.return_value = mock_response

    cases = [
        BenchmarkCase(
            case_id="case1",
            input_data="doc1.png",
            expected_output="hello world",
            tolerance=0.1,
        )
    ]
    result = ocr_bench.run(cases, target_url="http://localhost:8000")
    assert result.area == "ocr"
    assert result.total_cases == 1
    assert result.passed == 1
    assert result.score is not None
    assert result.score > 0.9


@patch("httpx.post")
def test_extraction_benchmark(mock_post: MagicMock) -> None:
    from docsgraph_eval.extraction import bench as extraction_bench

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"extracted_fields": {"amount": 100.5, "currency": "USD"}}
    mock_post.return_value = mock_response

    cases = [
        BenchmarkCase(
            case_id="case1",
            input_data="invoice.pdf",
            expected_output={"amount": 100.49, "currency": "USD"},
            tolerance=0.02,
        )
    ]
    result = extraction_bench.run(cases, target_url="http://localhost:8000")
    assert result.area == "extraction"
    assert result.passed == 1
    assert result.score == 1.0


@patch("httpx.post")
def test_retrieval_benchmark(mock_post: MagicMock) -> None:
    from docsgraph_eval.retrieval import bench as retrieval_bench

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": ["doc1", "doc2"]}
    mock_post.return_value = mock_response

    cases = [
        BenchmarkCase(
            case_id="case1",
            input_data="query",
            expected_output=["doc1", "doc3"],
            tolerance=0.5,
        )
    ]
    result = retrieval_bench.run(cases, target_url="http://localhost:8000")
    assert result.area == "retrieval"
    assert result.passed == 1


@patch("httpx.post")
def test_evidence_attribution_benchmark(mock_post: MagicMock) -> None:
    from docsgraph_eval.evidence_attribution import bench as ea_bench

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"evidence": "Passage 1 contains the details."}
    mock_post.return_value = mock_response

    cases = [
        BenchmarkCase(
            case_id="case1",
            input_data="question",
            expected_output="Passage 1",
        )
    ]
    result = ea_bench.run(cases, target_url="http://localhost:8000")
    assert result.area == "evidence_attribution"
    assert result.passed == 1
    assert result.score == 1.0


@patch("httpx.post")
def test_graph_generation_benchmark(mock_post: MagicMock) -> None:
    from docsgraph_eval.graph_generation import bench as gg_bench

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"nodes": ["A", "B"], "edges": [["A", "B"]]}
    mock_post.return_value = mock_response

    cases = [
        BenchmarkCase(
            case_id="case1",
            input_data="text",
            expected_output={"nodes": ["A", "B", "C"], "edges": [["A", "B"]]},
            tolerance=0.4,
        )
    ]
    result = gg_bench.run(cases, target_url="http://localhost:8000")
    assert result.area == "graph_generation"
    assert result.passed == 1


@patch("httpx.post")
def test_permissions_benchmark(mock_post: MagicMock) -> None:
    from docsgraph_eval.permissions import bench as perm_bench

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"allowed": True}
    mock_post.return_value = mock_response

    cases = [
        BenchmarkCase(
            case_id="case1",
            input_data={"user": "alice", "doc": "d1"},
            expected_output=True,
        )
    ]
    result = perm_bench.run(cases, target_url="http://localhost:8000")
    assert result.area == "permissions"
    assert result.passed == 1
    assert result.score == 1.0


@patch("httpx.post")
def test_sync_benchmark(mock_post: MagicMock) -> None:
    from docsgraph_eval.sync import bench as sync_bench

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"converged": True}
    mock_post.return_value = mock_response

    cases = [
        BenchmarkCase(
            case_id="case1",
            input_data={"ops": []},
            expected_output={"converged": True},
        )
    ]
    result = sync_bench.run(cases, target_url="http://localhost:8000")
    assert result.area == "sync"
    assert result.passed == 1


@patch("httpx.post")
def test_offline_consistency_benchmark(mock_post: MagicMock) -> None:
    from docsgraph_eval.offline_consistency import bench as oc_bench

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"consistent": True}
    mock_post.return_value = mock_response

    cases = [
        BenchmarkCase(
            case_id="case1",
            input_data={"transitions": []},
            expected_output={"consistent": True},
        )
    ]
    result = oc_bench.run(cases, target_url="http://localhost:8000")
    assert result.area == "offline_consistency"
    assert result.passed == 1


def test_runner_suite_execution() -> None:
    suite = BenchmarkSuite(
        area="ocr",
        cases=[
            BenchmarkCase(
                case_id="c1",
                input_data="doc.png",
                expected_output="txt",
            )
        ],
    )

    with patch("docsgraph_eval.ocr.bench.run") as mock_run:
        mock_run.return_value = BenchmarkResult(area="ocr", total_cases=1, passed=1)
        res = run_suite(suite, "http://localhost:8000")
        assert res.area == "ocr"
        mock_run.assert_called_once()

    # Invalid area
    invalid_suite = BenchmarkSuite(area="invalid", cases=[])
    with pytest.raises(ValueError, match="Unknown or unimplemented"):
        run_suite(invalid_suite, "http://localhost:8000")

    # Run all suites
    with patch("docsgraph_eval.ocr.bench.run") as mock_run:
        mock_run.return_value = BenchmarkResult(area="ocr", total_cases=1, passed=1)
        res_list = run_all_suites([suite, invalid_suite], "http://localhost:8000")
        assert len(res_list) == 1
        assert res_list[0].area == "ocr"


def test_cli_commands(tmp_path: Path) -> None:
    ocr_fixtures = tmp_path / "ocr"
    ocr_fixtures.mkdir()
    suite_file = ocr_fixtures / "suite.json"
    suite_file.write_text(
        json.dumps(
            {
                "area": "ocr",
                "cases": [
                    {
                        "case_id": "c1",
                        "input_data": "doc.png",
                        "expected_output": "hello",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    # Test run specific command
    with patch("docsgraph_eval.ocr.bench.run") as mock_run:
        mock_run.return_value = BenchmarkResult(
            area="ocr", total_cases=1, passed=1, score=1.0, details={}
        )
        result = runner.invoke(
            app,
            [
                "run",
                "ocr",
                "--fixtures-dir",
                str(tmp_path),
                "--target-url",
                "http://localhost:8000",
            ],
        )
        assert result.exit_code == 0
        assert "ocr" in result.output

    # Test run all command
    with patch("docsgraph_eval.ocr.bench.run") as mock_run:
        mock_run.return_value = BenchmarkResult(
            area="ocr", total_cases=1, passed=1, score=1.0, details={}
        )
        result = runner.invoke(
            app,
            [
                "run",
                "all",
                "--fixtures-dir",
                str(tmp_path),
                "--target-url",
                "http://localhost:8000",
            ],
        )
        assert result.exit_code == 0
        assert "=== Running benchmark: ocr ===" in result.output


@patch("httpx.post")
def test_real_fixtures_ocr(mock_post: MagicMock) -> None:
    from docsgraph_eval.core import load_suites_from_dir
    from docsgraph_eval.ocr import bench as ocr_bench

    suites = load_suites_from_dir(Path("fixtures/ocr"))
    assert len(suites) == 1
    suite = suites[0]
    assert suite.area == "ocr"
    assert len(suite.cases) == 1
    case = suite.cases[0]

    # Verify input_data references the real sample file
    file_path = case.input_data.get("file_path")
    assert file_path == "fixtures/ocr/sample_agreement.txt"
    assert Path(file_path).exists()

    # 2. Mock HTTP post to simulate slightly imperfect OCR text (e.g. one character typo)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "text": case.expected_output.replace("AGREEMENT", "AGREENENT")
    }
    mock_post.return_value = mock_response

    result = ocr_bench.run(suite.cases, target_url="http://localhost:8000")
    assert result.area == "ocr"
    assert result.total_cases == 1
    assert result.passed == 1
    assert result.score is not None
    assert 0.99 < result.score < 1.0


@patch("httpx.post")
def test_real_fixtures_extraction(mock_post: MagicMock) -> None:
    from docsgraph_eval.core import load_suites_from_dir
    from docsgraph_eval.extraction import bench as extraction_bench

    suites = load_suites_from_dir(Path("fixtures/extraction"))
    assert len(suites) == 1
    suite = suites[0]
    assert suite.area == "extraction"
    assert len(suite.cases) == 1
    case = suite.cases[0]

    # Verify input_data references the real sample file
    file_path = case.input_data.get("file_path")
    assert file_path == "fixtures/extraction/sample_contract.txt"
    assert Path(file_path).exists()

    # 2. Mock HTTP post to simulate 4/5 matched fields (one mismatch on monthly_fees)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "extracted_fields": {
            "effective_date": "October 1, 2026",
            "provider": "DevCorp Solutions",
            "client": "MegaRetail Inc",
            "monthly_fees": 12000.0,
            "governing_law": "State of New York",
        }
    }
    mock_post.return_value = mock_response

    result = extraction_bench.run(suite.cases, target_url="http://localhost:8000")
    assert result.area == "extraction"
    assert result.total_cases == 1
    assert result.passed == 0
    assert result.score == 0.8


@patch("httpx.post")
def test_real_fixtures_retrieval(mock_post: MagicMock) -> None:
    from docsgraph_eval.core import load_suites_from_dir
    from docsgraph_eval.retrieval import bench as retrieval_bench

    suites = load_suites_from_dir(Path("fixtures/retrieval"))
    assert len(suites) == 1
    suite = suites[0]
    assert suite.area == "retrieval"
    assert len(suite.cases) == 2

    def post_side_effect(url: str, json: Any, *args: Any, **kwargs: Any) -> MagicMock:
        res = MagicMock(spec=httpx.Response)
        res.status_code = 200
        if json.get("query") == "billing terms":
            res.json.return_value = {
                "results": ["doc_billing_003", "doc_billing_001", "doc_billing_002"]
            }
        else:
            res.json.return_value = {"results": ["doc_other", "doc_other2"]}
        return res

    mock_post.side_effect = post_side_effect

    result = retrieval_bench.run(suite.cases, target_url="http://localhost:8000")
    assert result.area == "retrieval"
    assert result.total_cases == 2
    assert result.passed == 1

    assert result.details is not None
    assert result.details["mrr"] == 0.25
    assert result.details["cases"]["retrieval_case_billing"]["passed"] is True
    assert result.details["cases"]["retrieval_case_billing"]["reciprocal_rank"] == 0.5
    assert result.details["cases"]["retrieval_case_termination"]["passed"] is False
    assert result.details["cases"]["retrieval_case_termination"]["reciprocal_rank"] == 0.0


@patch("httpx.post")
def test_real_fixtures_evidence_attribution(mock_post: MagicMock) -> None:
    from docsgraph_eval.core import load_suites_from_dir
    from docsgraph_eval.evidence_attribution import bench as evidence_bench

    suites = load_suites_from_dir(Path("fixtures/evidence_attribution"))
    assert len(suites) == 1
    suite = suites[0]
    assert suite.area == "evidence_attribution"
    assert len(suite.cases) == 2

    def post_side_effect(url: str, json: Any, *args: Any, **kwargs: Any) -> MagicMock:
        res = MagicMock(spec=httpx.Response)
        res.status_code = 200
        if json.get("query") == "What is the interest rate on late payments?":
            res.json.return_value = {
                "evidence": "Interest on late payments shall accrue at a rate of 5% per annum."
            }
        else:
            res.json.return_value = {"evidence": ""}
        return res

    mock_post.side_effect = post_side_effect

    result = evidence_bench.run(suite.cases, target_url="http://localhost:8000")
    assert result.area == "evidence_attribution"
    assert result.total_cases == 2
    assert result.passed == 1
    assert result.details is not None
    assert result.details["cases"]["attribution_case_late_payment"]["passed"] is True
    assert result.details["cases"]["attribution_case_notices"]["passed"] is False
    assert (
        "No valid supporting citation"
        in result.details["cases"]["attribution_case_notices"]["error"]
    )


@patch("httpx.post")
def test_real_fixtures_graph_generation(mock_post: MagicMock) -> None:
    from docsgraph_eval.core import load_suites_from_dir
    from docsgraph_eval.graph_generation import bench as graph_bench

    suites = load_suites_from_dir(Path("fixtures/graph_generation"))
    assert len(suites) == 1
    suite = suites[0]
    assert suite.area == "graph_generation"
    assert len(suite.cases) == 1

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "nodes": [
            {"id": "doc_001", "type": "document", "label": "Service Agreement"},
            {"id": "party_001", "type": "party", "label": "Acme Corp"},
            {"id": "party_002", "type": "party", "label": "Beta LLC"},
            {"id": "extra_node", "type": "party", "label": "Extra Entity"},
        ],
        "edges": [
            {"source": "doc_001", "target": "party_001", "type": "HAS_SIGNATORY"},
            {"source": "doc_001", "target": "party_002", "type": "HAS_SIGNATORY"},
            {"source": "doc_001", "target": "extra_node", "type": "HAS_SIGNATORY"},
        ],
    }
    mock_post.return_value = mock_response

    result = graph_bench.run(suite.cases, target_url="http://localhost:8000")
    assert result.area == "graph_generation"
    assert result.total_cases == 1
    assert result.passed == 0
    assert result.score is not None
    assert 0.70 < result.score < 0.71

    # Check precision/recall reporting on relationships
    details = result.details["cases"]["graph_case_service_agreement"]
    assert details["passed"] is False
    assert details["node_precision"] == 0.75
    assert details["node_recall"] == 0.75
    assert 0.66 < details["relationship_precision"] < 0.67
    assert 0.66 < details["relationship_recall"] < 0.67


@patch("httpx.post")
def test_real_fixtures_permissions(mock_post: MagicMock) -> None:
    from docsgraph_eval.core import load_suites_from_dir
    from docsgraph_eval.permissions import bench as permissions_bench

    suites = load_suites_from_dir(Path("fixtures/permissions"))
    assert len(suites) == 1
    suite = suites[0]
    assert suite.area == "permissions"
    assert len(suite.cases) == 5

    def post_side_effect(url: str, json: Any, *args: Any, **kwargs: Any) -> MagicMock:
        res = MagicMock(spec=httpx.Response)
        res.status_code = 200
        user_id = json.get("user_id")
        action = json.get("action")

        if user_id == "user_admin_org_a":
            res.json.return_value = {"allowed": True}
        elif user_id == "user_viewer_org_a":
            if action == "read":
                res.json.return_value = {"allowed": True}
            else:
                res.json.return_value = {"allowed": False}
        else:
            res.json.return_value = {"allowed": False}
        return res

    mock_post.side_effect = post_side_effect

    result = permissions_bench.run(suite.cases, target_url="http://localhost:8000")
    assert result.area == "permissions"
    assert result.total_cases == 5
    assert result.passed == 4

    details = result.details["cases"]
    assert details["permissions_admin_same_org_write"]["passed"] is True
    assert details["permissions_admin_cross_org_write"]["passed"] is False
    assert (
        "Permission check failed: Expected access to be DENIED, but got ALLOWED"
        in details["permissions_admin_cross_org_write"]["error"]
    )
    assert details["permissions_viewer_same_org_read"]["passed"] is True
    assert details["permissions_viewer_same_org_write"]["passed"] is True
    assert details["permissions_user_cross_org_read"]["passed"] is True


@patch("httpx.post")
def test_real_fixtures_offline_consistency(mock_post: MagicMock) -> None:
    from docsgraph_eval.core import load_suites_from_dir
    from docsgraph_eval.offline_consistency import bench as offline_bench

    suites = load_suites_from_dir(Path("fixtures/offline_consistency"))
    assert len(suites) == 1
    suite = suites[0]
    assert suite.area == "offline_consistency"
    assert len(suite.cases) == 2

    def post_side_effect(url: str, json: Any, *args: Any, **kwargs: Any) -> MagicMock:
        res = MagicMock(spec=httpx.Response)
        res.status_code = 200
        document_id = json.get("document_id")

        if document_id == "doc_001":
            res.json.return_value = {
                "state": {"title": "Client 1 Draft", "content": "Client 2 Content"},
                "data_loss": False,
            }
        else:
            res.json.return_value = {"state": {"title": "Title B"}, "data_loss": True}
        return res

    mock_post.side_effect = post_side_effect

    result = offline_bench.run(suite.cases, target_url="http://localhost:8000")
    assert result.area == "offline_consistency"
    assert result.total_cases == 2
    assert result.passed == 1

    details = result.details["cases"]
    assert details["offline_consistency_merge_non_conflicting"]["passed"] is True
    assert details["offline_consistency_resolve_conflicting_lww"]["passed"] is False
    assert (
        "Silent data loss detected"
        in details["offline_consistency_resolve_conflicting_lww"]["error"]
    )
