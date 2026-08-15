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

```bash
uv run docsgraph-eval --help
uv run docsgraph-eval run ocr
uv run docsgraph-eval run all
```

## Benchmark areas

- **ocr** — OCR accuracy against ground-truth transcriptions (character/word error rate).
- **extraction** — structured field/clause extraction quality.
- **retrieval** — search/retrieval quality (precision/recall, ranking metrics).
- **evidence_attribution** — whether answers correctly cite the source passage they came from.
- **graph_generation** — quality of the generated knowledge graph (entity/relation correctness).
- **permissions** — whether permission/access-control decisions match expected outcomes.
- **sync** — whether the sync protocol converges correctly across simulated clients.
- **offline_consistency** — whether data stays consistent across offline/online transitions and reconnects.

Each area lives in `src/docsgraph_eval/<area>/` as a skeleton: a
`BenchmarkCase` type (shared, defined in `src/docsgraph_eval/core.py`) and a
`run()` stub that will grow into the real benchmark implementation. Sample
documents and golden answers will live in `fixtures/<area>/`.

## Status

Early scaffold. Benchmark logic is not implemented yet — `run()` in each
area currently raises `NotImplementedError`.

## License

MIT — see [LICENSE](LICENSE).
