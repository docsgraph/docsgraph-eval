# Fixtures

Sample documents and golden (expected) answers used by the benchmarks in
`src/docsgraph_eval/` live here, one subdirectory per benchmark area:

- `ocr/` — scanned/source documents and ground-truth transcriptions.
- `extraction/` — documents and golden structured field/clause extractions.
- `retrieval/` — document corpora, queries, and relevance judgments.
- `evidence_attribution/` — question/answer pairs with golden source passages.
- `graph_generation/` — documents with golden entity/relation graphs.
- `permissions/` — access-control scenarios and expected allow/deny outcomes.
- `sync/` — simulated client operation logs and expected converged state.
- `offline_consistency/` — offline/online transition scenarios and expected
  final state.

These directories are currently empty placeholders (tracked via `.gitkeep`)
until real fixtures are added alongside the corresponding benchmark
implementations in `src/docsgraph_eval/<area>/`.
