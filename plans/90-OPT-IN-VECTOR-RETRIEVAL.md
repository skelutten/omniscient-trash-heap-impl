# Plan 90 — Opt-in vector retrieval

> **Status:** opt-in, deferred
> **Prerequisite:** `02-DETERMINISTIC-CORE.md` green
> **Dependency:** embedding model and vector index must be explicitly selected. Cross-encoder reranking remains excluded (D83).

## Scope

Define a stable optional adapter interface, corpus/policy hashing, invalidation, reproducible ranking, multi-chunk passage attribution, and degraded fallback to baseline retrieval. Keep vector dependencies outside the core install and ensure retrieval remains 100% offline and deterministic.

## Phased Implementation Roadmap (D79–D84)

### Phase V1 — Seam & Deterministic Double (D79)
- Define `Embedder` protocol, `EmbeddingIdentity`, cosine similarity, and index fingerprint (`CANON-003`).
- Implement `DeterministicDouble` for testing.
- **Rule (Honest Modality):** The test double is *strictly forbidden* from claiming the vector modality (`EmbeddingIdentity.is_double = True`). In bundles, `modalities_for()` reports vector as `absent`, identical to having no embedder configured.
- AST-based tests assert that the core package contains no network imports or remote connection parameters (`endpoint`, `api_key`).

### Phase V2 — Offline Provider & Multi-Chunk Object Model (D80, D81)
- Support offline embedding providers (e.g. local ONNX / `all-MiniLM-L6-v2`, 384 dimensions, unit norm).
- **Multi-Chunk Representation:** For objects spanning multiple chunks (e.g. 512 words), an object is an ordered sequence of chunk vectors scored via **max-over-chunks aggregation** ($\max_{c} \operatorname{cosine}(q, d_c)$).
  - *Design hypothesis — UNMEASURED (SCALE-001):* Max-aggregation is expected to outperform mean-pooling because it prevents relevant passages from being diluted across long articles. A calibration figure previously cited here (129 articles / 16,512 pairs; 58% paraphrase recall vs 42% for mean-pooling) has **no benchmark artifact, dataset, reproduction script or review source anywhere in this repository**, and is therefore withdrawn as evidence. Per **SCALE-001** it MUST NOT be presented as conformance evidence; it is carried as an open hypothesis with the same status as the NFR-2 design budgets (see `PRD.md` §5 and commit `b0c8de4`). The Gate below ("paraphrase ranking proof") is where this hypothesis is to be settled by measurement.
  - Returns `Hit(node_id, score, chunk_index)` allowing passage-level attribution in evidence bundles.
- **Frontmatter Stripping:** YAML frontmatter MUST be stripped before computing text embeddings; structured metadata is queried via Step 2 pre-filters.
- **Defensive Store Validation:** Validate provider record keys, payload, dimensions, and unit norm fail-closed.
- **Ephemeral Provisioning:** Ensure provisioning contexts support clean `--cleanup` to prevent context accumulation.

### Phase V3 — Hybrid RRF Fusion & Honest Evidence Bundles (D81, D82)
- Integrate vector hits into Reciprocal Rank Fusion with weights `0.4` (BM25), `0.4` (vector), `0.2` (graph).
- **No Arbitrary Score Floor:** Do not apply arbitrary cutoffs (such as 0.75). Retrieval relies on candidate rank cut (`seed_top_k: 10`, `max_results: 20`) and RRF fusion, with only a `0.0` sign-convention floor (discarding negative cosine similarity).
- **Governance Pre-Filter:** Vector hits MUST pass through scope/governance pre-filters; a newly added modality cannot bypass admission boundaries.
- **Self-Describing Bundles:** `modalities_available` and `modalities_absent` are derived from the `EmbeddingIdentity` that actually executed. Unspent modalities report `null` raw scores, never `0.0`.

### Phase V4 — Cross-Encoder Exclusion (D83)
- Cross-encoder reranking is **explicitly excluded**:
  1. Bi-encoders (e.g. MiniLM) cannot act as cross-encoders.
  2. Model weights are not reachable offline.
  3. Putting a model call on the query path destroys offline determinism and violates `RET-002`.
- `FinalScore` defaults strictly to `RRF(d)`. Reversal requires offline-reachable weights and measured evidence of RRF ordering defects.

### Phase V5 — CLI Scoping & Degraded Fallback (D84)
- Maintain transparent, degraded fallback to baseline lexical+graph retrieval when vector dependencies or indexes are absent.
- Ensure index staleness is reported with exact reasons (corpus change, model change, or policy change).

## Gate

Do not enable by default. Mark blocked/degraded when dependencies are unavailable. Acceptance requires deterministic fixtures, baseline compatibility, multi-chunk max-aggregation tests, and paraphrase ranking proof.

## Source material

- `../specs/RETRIEVAL.md`, `GRAPH-RETRIEVAL.md`
- `threshold_policy.yaml` (D81, D83, D93, D94)
