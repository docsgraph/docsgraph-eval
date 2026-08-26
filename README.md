# docsgraph-eval

Independent benchmark and testing suite for OCR, extraction, retrieval,
evidence attribution, graph generation, permissions, synchronization, and
offline consistency.

`docsgraph-eval` is the quality-assurance layer for docsgraph, a
local-first document/contract management platform built from
[`docsgraph`](https://github.com/docsgraph/docsgraph) (the client) and
[`docsgraph-server`](https://github.com/docsgraph/docsgraph-server) (the
self-hostable backend). This repo independently benchmarks whether those
two actually work correctly.

## Development setup

This project uses [`uv`](https://docs.astral.sh/uv/) for packaging,
[`ruff`](https://docs.astral.sh/ruff/) for linting and formatting,
[`mypy`](https://mypy-lang.org/) (strict mode) for typing, and
[`pytest`](https://docs.pytest.org/) for tests.

```bash
uv sync --all-extras --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

Install the git hooks with [`pre-commit`](https://pre-commit.com/) so these
checks run automatically before each commit:

```bash
uv run pre-commit install
```

## CLI

Run benchmarks using the Typer CLI:

```bash
# Get help and list available subcommands
uv run docsgraph-eval --help

# Run a specific benchmark area with optional target server and output options
uv run docsgraph-eval run ocr --target-url http://localhost:8000 --fixtures-dir fixtures --format json --output report.json

# Run all implemented benchmark suites
uv run docsgraph-eval run all --target-url http://localhost:8000 --fixtures-dir fixtures --format markdown
```

### CLI Options

The following options are supported across all `run` subcommands:
- `--target-url`: Base URL of the running target `docsgraph-server` instance (default: `http://localhost:8000`).
- `--fixtures-dir`: Directory containing benchmark suites partitioned by area (default: `fixtures`).
- `--format`: Format of the generated report (`json` or `markdown`, default: `json`).
- `--output`: File path to save the generated report. If omitted, results are printed to standard output.

## Benchmark areas

- **ocr** — OCR accuracy against ground-truth transcriptions (character/word error rate).
- **extraction** — structured field/clause extraction quality.
- **retrieval** — search/retrieval quality (precision/recall, ranking metrics).
- **evidence_attribution** — whether answers correctly cite the source passage they came from.
- **graph_generation** — quality of the generated knowledge graph (entity/relation correctness).
- **permissions** — whether permission/access-control decisions match expected outcomes.
- **sync** — whether the sync protocol converges correctly across simulated clients.
- **offline_consistency** — whether data stays consistent across offline/online transitions and reconnects.

## Adding a New Benchmark Suite

To add a new benchmark suite for an existing area (e.g., `ocr`):

1. **Define the suite JSON file**:
   Create a JSON file inside the area's fixtures directory (e.g., `fixtures/ocr/invoice_suite.json`). The file must adhere to the `BenchmarkSuite` schema:
   ```json
   {
     "area": "ocr",
     "cases": [
       {
         "case_id": "ocr_invoice_001",
         "input_data": "file://fixtures/ocr/invoice_001.png",
         "expected_output": "INVOICE #12345\nDate: 2026-08-26\nTotal: $150.00",
         "tolerance": 0.05,
         "metadata": {
           "difficulty": "easy",
           "source": "scanned_invoice"
         }
       }
     ]
   }
   ```

2. **Place target files if necessary**:
   If the test case uploads a file, place it in the same fixtures folder (e.g., `fixtures/ocr/invoice_001.png`). In `input_data`, specify the relative path to the file using `"file://fixtures/ocr/invoice_001.png"` or `{"file_path": "fixtures/ocr/invoice_001.png"}`.

3. **Run the suite**:
   Execute the benchmark harness via the CLI pointing to the server instance and the fixtures directory:
   ```bash
   uv run docsgraph-eval run ocr --fixtures-dir fixtures --target-url http://localhost:8000
   ```

## Adding a New Capability Area

To introduce a completely new benchmarking area:

1. **Add the area subfolder**:
   Create `src/docsgraph_eval/<new_area>/` and add `__init__.py` and `bench.py`.
2. **Implement `run()`**:
   In `bench.py`, define the `run(cases: list[BenchmarkCase], target_url: str) -> BenchmarkResult` function. You can use `docsgraph_eval.core.run_http_case` to execute HTTP calls against the server and evaluate the outputs.
3. **Register the command**:
   In `src/docsgraph_eval/cli.py`, add the new area to `FOLDER_MAP` and register the corresponding subcommand with `@run_app.command("<new-area>")`.
4. **Create fixtures**:
   Create a folder `fixtures/<new_area>/` with the input suites.

## Status

Active development. The modular harness supports all 8 capability areas and dynamic suite loading, execution against the target server API, and structured reporting.

## License

MIT — see [LICENSE](LICENSE).
