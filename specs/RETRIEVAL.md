# LLM Wiki Hybrid Retrieval Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-RETRIEVAL-001`
> **Version**: `3.8.10`
> **Updated**: `2026-08-17`
> **Source**: Extracted from `spec.md` §9; source-aware retrieval is an opt-in extension
> **Status**: `LOCKED`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Compatibility target**: Baseline hybrid retrieval; Universal Source retrieval remains opt-in
> **Normative owner**: This document owns baseline retrieval algorithms, ranking and evidence bundles
> **Related documents**: `ARCHITECTURE.md`, `EPISTEMOLOGY.md`, `GRAPH-RETRIEVAL.md`, `UNIVERSAL-SOURCE-EXTENSION.md`

---

## 9. Hybrid Retrieval Pipeline & Formal Algorithms

The search pipeline is executed through the following eight layered steps:

The baseline pipeline retrieves Knowledge Objects. When the opt-in Universal
Source mode is selected, the same deterministic pipeline MAY retrieve Source,
Representation, Actor, Event and Experience records as distinct namespaces.
Source retrieval MUST NOT be treated as canonical knowledge retrieval.

```
 1. QUERY UNDERSTANDING  (Extracts intent, entities, explicit node IDs and parameters)
        │
        ▼
 2. SCOPE, FACET & VALIDITY PRE-FILTER (Pre-filtering on scope, object_type, domain, facets, status, confidence and validity)
        │
        ▼
 3. INITIAL SEED RETRIEVAL (BM25 lexical + vector search + ID lookup -> Top-K Seed Nodes)
        │
        ▼
 4. GRAPH EXPANSION      (BFS from seeds: max_depth, max_neighbors, visited_set, traverses canonical relations + inverse views)
        │
        ▼
 5. POST-FILTER          (Epistemic status, min_confidence, cross-scope security policy, redaction)
        │
        ▼
 6. HYBRID FUSION        (Lexical + vector + graph-subgraph fusion scoring via RRF)
        │
        ▼
 7. HYBRID RERANKING     (Domain cross-encoder with RRF fallback)
        │
        ▼
   EVIDENCE BUNDLE ──────► LLM ──────► GROUNDED ANSWER
```

### 9.1 Formal Hybrid Fusion via RRF & FinalScore

In step 6, the scores from BM25, vector and subgraph search are combined deterministically via **Reciprocal Rank Fusion (RRF)**:

$$
\operatorname{RRF}(d) = \sum_{m \in M_d} \frac{w_m}{k + \operatorname{rank}_m(d)}
$$

where

$$
M_d = \{ m \mid d \text{ occurs in search modality } m \}
$$

and modalities where d is absent contribute 0.

**Modality Admission & Fusion Invariants:**

> **Scope of items 2–4 (opt-in vector modality).** Item 1 governs baseline
> retrieval. Items 2, 3 and 4 apply **only** when the opt-in vector modality of
> `plans/90-OPT-IN-VECTOR-RETRIEVAL.md` is enabled. Baseline retrieval
> (lexical + graph) is vector-agnostic and its results MUST NOT change when the
> vector adapter is absent, per the extension-isolation rule in `specs/README.md`
> §2.6 and the exclusion of vector adapters in `plans/99-FUTURE-SCOPE.md`.
> `plans/90` remains `opt-in, deferred` and is not an active plan.

1. **Graph Modality Condition (D93):** The graph modality $m = \text{graph}$ participates in $M_d$ **only if graph expansion reached at least one node beyond seeds** (`depth > 0`, `graph_reached = True`). When `max_depth = 0` (or when expansion reaches zero neighbors), all candidate nodes sit at depth 0 with an identical score of $1.0$. Because tie-breaking is lexicographic by $\operatorname{node\_id}\ \text{ASC}$, including depth-0 scores in the RRF sum would degenerate into an unintended alphabetical reordering of results. When no depth > 0 node is reached, the graph term is excluded from the sum.
2. **Vector Modality Ranking & Floor (D81):** Query-to-document vector search does **not** apply an arbitrary similarity threshold (such as `GRAPH-SEMANTIC-SIMILARITY: 0.75` in `threshold_policy.yaml`, which is strictly reserved for inter-object graph edge inference). Query-document similarity distributions are expected to overlap with noise on technical corpora; **no calibration artifact, dataset or reproduction script exists in this repository**, so this sentence is design rationale and MUST NOT be cited as measured evidence (**SCALE-001**). Vector search relies on rank-capping (`seed_top_k`, default 10) and RRF fusion, with only a **0.0** sign-convention floor (discarding negative cosine similarity).
3. **Multi-Chunk Max-Over-Chunks Aggregation (D81):** For multi-chunk Knowledge Objects, vector scoring uses **max-over-chunks aggregation** ($\operatorname{score}_{\text{vector}}(q, d) = \max_{c} \operatorname{cosine}(q, d_c)$). Max-aggregation is specified in preference to mean-pooling because it prevents relevant passages from being diluted across long articles. **The magnitude of that preference is unmeasured**: a previously cited calibration figure (129 articles / 16,512 pairs; 58% vs 42% paraphrase recall) has no supporting artifact in this repository and is recorded as an open hypothesis in `plans/90-OPT-IN-VECTOR-RETRIEVAL.md` Phase V2, to be settled by that plan's "paraphrase ranking proof" gate (**SCALE-001**). Hits carry passage attribution: $\operatorname{Hit}(\operatorname{node\_id}, \operatorname{score}, \operatorname{chunk\_index})$.
4. **Frontmatter Stripping for Embeddings:** YAML frontmatter MUST be stripped from Knowledge Objects prior to generating vector embeddings. Frontmatter metadata is queried deterministically via Step 2 pre-filters; embedding raw YAML would corrupt semantic similarity with schema keywords and structural boilerplate.

**Established parameters:**
- k = 60
- w_bm25 = 0.4
- w_vector = 0.4
- w_graph = 0.2

**Final score computation (FinalScore):**

$$
\operatorname{FinalScore}(d) =
\begin{cases}
\operatorname{reranker}(d) & \text{if an offline cross-encoder model score exists} \\
\operatorname{RRF}(d) & \text{otherwise (default baseline)}
\end{cases}
$$

*Note on Reranking (D83):* Transformer cross-encoders remain an opt-in extension requiring offline-reachable weights. Query-path model calls MUST NOT jeopardize offline determinism or `RET-002`. In baseline retrieval, `FinalScore` defaults to `RRF(d)`.

**Tie-breaking** is performed strictly according to:

$$
\operatorname{FinalScore}(d)\ \text{DESC} \quad \rightarrow \quad \operatorname{node\_id}\ \text{ASC}
$$

---

### 9.2 Deterministic Selection Rule for Graph Neighbors

If a node has more relations than `max_neighbors_per_node`, they are sorted deterministically before pruning using the key function:

$$
\operatorname{key}(r) = \bigl( \operatorname{priority}(\operatorname{category}(r)),\ \operatorname{type}(r),\ \operatorname{target}(r) \bigr)
$$

**Explicit integer values for `priority(category)`:**

| Category | Priority |
|---|---|
| structural | 1 |
| dependency | 2 |
| engineering | 3 |
| evolution | 4 |
| derivation | 5 |
| verification | 6 |
| epistemic | 7 |
| procedural | 8 |
| documentation | 9 |
| semantic | 10 |

On equal category, sorting is lexicographic on `type` and thereafter `target` in ascending order.

---

### 9.3 N-Way Conflict Cluster & Lexicographic Epistemic Ranking

When two or more nodes (N ≥ 2) are part of a mutual `CONTRADICTS` cluster (the maximal connected component in the undirected graph spanned by `CONTRADICTS` edges), each node is evaluated independently.

The ranking is computed by maximizing the formal vector key:

$$
K(d) = \bigl(
  V(d),\
  A(d),\
  C(d),\
  E(d),\
  \operatorname{Conf}(d),\
  \operatorname{Date}(d),\
  -\operatorname{ASCII}(\operatorname{ID}(d))
\bigr)
$$

**Explicit integer scales** (normative owner: `schemas/registry/epistemic_registry.yaml` / `EPISTEMOLOGY.md` §5.2 — the values below
SHALL be identical with that registry):
- $V(d)$ (verification): `formal_proof = 4`, `peer_verified = 3`, `self_verified = 2`, `unverified = 1`, `falsified = 0`
- $A(d)$ (authority): `normative = 4`, `authoritative = 3`, `informative = 2`, `advisory = 1`, `deprecated = 0`
- $C(d)$ (consensus): `accepted = 2`, `proposed = 1`, `contested = 0`
- $E(d)$ (evidence): `observed = 3`, `derived = 2`, `inferred = 1`, `postulated = 0`
- $\operatorname{Conf}(d)$: Float in the interval [0.0, 1.0]
- $\operatorname{Date}(d)$: `last_verified` in ISO format (latest date wins; `null` sorts lowest)
- $-\operatorname{ASCII}(\operatorname{ID}(d))$: Lowest Node-ID wins the last tie-breaker

The winning node is defined as:

$$
d^* = \arg\max_{d \in C} K(d)
$$

where C is the conflict cluster. d* is placed in `evidence_bundle`. The remaining N-1 nodes are placed in `suppressed_nodes` with the reason `conflict_lower_epistemic_rank`.

---

## 9.4 Retrieval Configuration & Operator Knobs (THRESH-001–THRESH-003)

### Operator Knobs & Threshold Invariants
* **THRESH-001 (Normalized Signals):** All relevance, graph, and lexical signals SHALL be normalized to `[0.0, 1.0]` before fusion.
* **THRESH-002 (Internal Defaults):** Internal cutoffs are owned by
  `schemas/registry/threshold_policy.yaml`. The values currently used by this
  specification (`max_depth=2`, `max_neighbors_per_node=25`, `k=60`) are
  policy defaults, not calibration claims. Derived retrieval artifacts MUST
  carry the policy ID and version; implementations MUST NOT introduce a new
  internal cut-off outside that registry.
* **THRESH-003 (Operator Knob Budget):** The operator-facing knob budget is strictly capped at **two**:
  1. `min_confidence` (provenance threshold, default `0.0`)
  2. `min_relevance` (normalized composite score cutoff, default `0.0`)
* **Parameter Precedence & Origin Tracking (D94):** Parameters are resolved with strict per-parameter precedence:
  $$\text{CLI flag} \quad > \quad \text{config file (\texttt{retrieval:} block)} \quad > \quad \text{\S 9.4 default}$$
  The system MUST report the resolution source of each non-default parameter in `parameters_origin` alongside `parameters_used` in the evidence bundle.
* **Modality Nullability & Honest Availability (D82, D93):**
  - If a search modality is not active (e.g. no vector adapter configured), its score in the evidence bundle MUST report `null`, NEVER `0.0` (which would falsely state semantic search returned zero similarity). Unspent weights remain unspent rather than renormalised.
  - `modalities_available` and `modalities_absent` MUST be derived from what *actually ran* (`EmbeddingIdentity`). An index built with a deterministic test-double is forbidden from claiming the vector modality as available (`is_double = True` reports vector as `absent`).
  - `graph`: If `max_depth == 0`, graph is reported as `absent` (`graph_consulted = False`). If `max_depth > 0` but no edges exist or were reached, graph is reported as `available` but contributes no term to RRF (`graph_reached = False`).

### Default parameters

| Parameter | Type | Default | Description | Range |
|---|---|---|---|---|
| `seed_top_k` | int | 10 | Number of seed nodes from initial search | 1-50 |
| `max_depth` | int | 2 | Max depth in graph expansion | 0-5 |
| `max_neighbors_per_node` | int | 25 | Max neighbors per node | 1-100 |
| `max_expanded_nodes` | int | 200 | Max total nodes in subgraph | 1-500 |
| `max_results` | int | 20 | Number of results in evidence bundle | 1-100 |
| `min_confidence` | float | 0.0 | Operator Knob 1: Min confidence for inclusion | 0.0-1.0 |
| `min_relevance` | float | 0.0 | Operator Knob 2: Min normalized relevance score | 0.0-1.0 |

### Search modules

#### BM25 (Lexical Search)
- Standard TF-IDF based search using the Okapi BM25 algorithm ($k_1=1.5, b=0.75$).
- Returns ranked results based on term frequency and field weighting.

#### Vector Search (Semantic)

> **Opt-in modality.** This entire subsection is scoped to the deferred opt-in
> vector track (`plans/90-OPT-IN-VECTOR-RETRIEVAL.md`) and is excluded from the
> core sequence by `plans/99-FUTURE-SCOPE.md`. None of the requirements below
> apply to baseline retrieval, which MUST produce identical results whether or
> not a vector adapter is installed.

- Uses dense embeddings (e.g. `text-embedding-3-small` or local BGE) for semantic similarity.
- HNSW index backend with cosine similarity scoring.
- **Passage Granularity & Chunking:** Coarse chunks (e.g. fixed 512 words) are expected to dilute answers and flatten similarity distributions; no measurement of the effect exists in this repository (**SCALE-001**), so the expectation is design rationale, not evidence. Chunk size MUST be configurable with finer passage boundaries (e.g. 128–256 tokens or Markdown section boundaries) for high-precision retrieval. The configurability requirement stands independently of the unmeasured magnitude.
- **Structured Content & Technical Data Caution:** General prose-trained sentence models (e.g. `MiniLM`) are expected to yield noisy, false-positive similarities on structured YAML definitions or code; this is likewise unmeasured here (**SCALE-001**). Exact technical identifiers (e.g. protocol fields, acronyms) therefore rely on the BM25 lexical modality. YAML frontmatter MUST be stripped before embedding prose.
- **Air-Gap & Locality:** Local inference adapters MUST document exact model weight paths and run with zero network egress.

#### Graph Search (Topological & Personalized PageRank)
- Traverses knowledge graphs via relations, respecting `dag` and `symmetric` registry properties.
- **Resource Constraints (Fail-Safe):**
  - Maximum visited node cap: $N_{\text{max}} = 2,000$ nodes.
  - Hard traversal timeout: $T_{\text{max}} = 150\text{ ms}$ (aborts expansion and falls back to seeds if exceeded).
  - Memory budget: Adjacency matrices for subgraph walks MUST NOT exceed 64 MB resident memory per query.

### Fusion & Reranking

#### RRF Fusion (Reciprocal Rank Fusion)
- Combines ranks from BM25, Vector, and Graph modules: $RRF(d) = \sum_{m \in M} \frac{w_m}{k + r_m(d)}$ where $k=60$.
- Scale-free fusion guarantees deterministic results without calibration drift.

#### Cross-Encoder Reranking
- Uses a transformer-based cross-encoder (e.g. `bge-reranker-large` / `ms-marco-MiniLM-L-6-v2`).
- **Execution Budget & Constraints:**
  - Candidates restricted to top-$K \le 10$ from RRF output to avoid token/latency explosion.
  - Document text scoring window: naïve leading-only truncation (e.g. cutting at leading 512 tokens) is vulnerable to the *Truncation Trap* (severing trailing conclusion and hedging sections, which empirically degraded answer accuracy by 14.5 points). Implementations SHOULD employ section-aware scoring (including document overview and conclusion/findings sections) or configure context windows up to 1,024–2,048 tokens where execution budget permits.
  - Fallback: If Cross-Encoder model is unavailable or latency exceeds 200 ms, system falls back transparently to raw RRF scores.

---

## 9.5 Evidence Bundle Schema

See [`examples/evidence_bundle.json`](../examples/evidence_bundle.json) for the complete JSON schema.

### Bundle Structure

```json
{
  "query": "string",
  "retrieval_version": "1.0.0",
  "ranking_policy_version": "1.0.0",
  "relation_registry_version": "3.8.10",
  "modalities_available": ["bm25", "graph", "vector"],
  "modalities_absent": [],
  "parameters_used": { ... },
  "parameters_origin": { ... },
  "candidate_count": 2,
  "returned_count": 1,
  "suppressed_count": 1,
  "cross_scope_redactions_applied": false,
  "evidence_bundle": [ ... ],
  "suppressed_nodes": [ ... ]
}
```

### Retrieval Signals

Each node in evidence_bundle contains:

```json
{
  "node_id": "ENG-CLM-2026-0039",
  "title": "...",
  "matched_by": ["vector", "bm25"],
  "score_components": {
    "bm25_raw": 0.81,
    "vector_raw": 0.89,
    "graph_raw": 0.50,
    "rrf_score": 0.0161836,
    "reranker_score": 0.92,
    "final": 0.92
  },
  "retrieval_signals": {
    "bm25": {"raw_score": 0.81, "rank": 2, "rrf_contribution": 0.0064516},
    "vector": {"raw_score": 0.89, "rank": 1, "rrf_contribution": 0.0065574, "chunk_index": 3},
    "graph": {"raw_score": 0.50, "rank": 3, "rrf_contribution": 0.0031746}
  }
}
```

### Conflict detection

When `CONTRADICTS` relations are detected:

```json
{
  "conflict_detected": true,
  "conflicting_node_id": "ENG-CLM-2026-0042",
  "conflicting_relation_type": "CONTRADICTS",
  "conflict_resolution": "epistemic_then_confidence"
}
```

### 9.5.1 Full-Content Access, Body Excerpts & Draft Visibility

1. **Body Excerpt Boundedness & Synthesis Warning:** In Evidence Bundles, `body_excerpt` is strictly bounded ($\le 250$ characters) to preserve LLM context budget during multi-node candidate routing. Because arbitrary front-end truncation risks discarding conclusions and epistemic hedging clauses, callers performing answer synthesis MUST NOT rely solely on `body_excerpt`. Downstream agents SHALL resolve complete markdown text via `"path"` or request `--include-body`.
2. **Direct Filesystem Path:** Each bundle node entry SHALL contain a `"path"` field with the canonical repository-relative filesystem location of the Knowledge Object (e.g. `personal/02_formella_vetenskaper_matematik/PERS-CON-0001.md`), preventing local host path leakage in exported or agent-bound evidence bundles.
3. **Full Text Retrieval:** Complete object markdown text MUST be accessible via the non-truncating CLI command `trashheap show <node_id|file_path>` or through the `--include-body` flag on `trashheap query`.
4. **Draft Status Invariant:** Canonical retrieval filters `status: draft` objects by default. When querying unpromoted or migrated legacy articles, callers MUST explicitly supply `--include-drafts`.
5. **Multi-Target Citation Parsing:** When extracting or verifying citation brackets from synthesized answers (e.g. `[NODE-1, NODE-2]`), parsers MUST match bracket boundaries and split comma/semicolon delimited IDs, validating every referenced ID against the evidence bundle path set to prevent multi-citation safety leakage.

---

## 9.6 Two-Stage Refusal Architecture (Topological Aboutness vs. Propositional Truth)

A central epistemic finding is that **graph path certification evaluates topological admissibility, NOT assertion truth**. Empirical evaluation reveals that topological path connectivity between concepts predicts propositional correctness at chance ($\text{AUROC} \approx 0.50$), because a graph edge establishes that concepts are co-studied or related, regardless of whether the specific claim is supported, contradicted, or inconclusive.

To prevent hallucinations while maintaining high answer coverage, retrieval and synthesis MUST execute as a **Two-Stage Refusal Architecture**:

```text
User Question
      │
      ▼
[Stage 1: Structural Refusal (Graph Gates - Deterministic)]
      ├── 1. Ontology Grounding: Question maps to registered descriptors / taxonomy?
      ├── 2. Path Admissibility: Valid path connects grounded concepts (direct / bridge)?
      ├── 3. Terminal Validity: Connected nodes possess quotable body text?
      └── 4. Retraction / Supersession: Reject if evidence is superseded or invalidated.
      │   (If any structural gate fails -> REFUSE with deterministic refusal reason)
      ▼
[Candidate Evidence Passages]
      │
      ▼
[Stage 2: Propositional Refusal (Epistemic / Confidence Gates)]
      ├── 1. Claim Entailment: Cited passage entails the atomic claim (neutrality < tau)?
      └── 2. Calibrated Confidence: Model confidence over answer tokens clears threshold?
          (If propositional gate fails -> ABSTAIN with INSUFFICIENT_EVIDENCE)
```

---

## 9.7 Constrained Logit Decoding & Posterior Calibration

Unconstrained natural language generation evaluated with heuristic regular expressions (such as `\b(yes|no|maybe)\b`) introduces brittle parser failure modes—for example, treating epistemic hedges ("there is no definitive evidence that...") as negative assertions. Furthermore, free-text generation produces point predictions rather than calibrated confidence distributions.

To maintain epistemic rigour:
1. **Constrained Vocabulary Decoding:** Classification and decision gates over discrete response sets (e.g. `{yes, no, maybe}`, `{approve, reject, revise}`) SHALL extract token logits directly at the decision position (`logits_to_keep=1`), computing a normalized softmax posterior over the candidate token IDs (**RET-008**).
2. **Prior-Calibrated Decision Rule:** Systems MAY apply class-bias corrections fitted strictly on a held-out development set (DEV split) to adjust for model prior skew before emitting a discrete label.
3. **Calibrated Abstention:** The maximum class posterior $\max_y P(y)$ SHALL serve as the primary epistemic confidence score. When $\max_y P(y) < \tau_{\text{abstain}}$, the system SHALL emit an `EPISTEMIC_ABSTENTION` refusal.

---

## 9.8 The RCVA Protocol (Retrieve, Constrain, Verify, Abstain)

Grounded question answering, multi-hop reasoning, and automated knowledge synthesis workflows SHALL strictly adhere to the four-phase **RCVA Protocol**:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. RETRIEVE                                                 │
│    Hybrid Dense + BM25 Lexical + Graph BFS (RRF Fusion)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. CONSTRAIN                                                │
│    Metadata Domain Filtering + Document Card Line Budgeting │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. VERIFY                                                   │
│    Deterministic Claim Entailment + Exact Bracket Citations │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. ABSTAIN                                                  │
│    Posterior Mass Check (max P(y) < tau) -> Refusal         │
└─────────────────────────────────────────────────────────────┘
```

1. **Phase 1 — Retrieve:** Candidate evidence nodes are retrieved using deterministic hybrid fusion (dense vector search + BM25 lexical search + graph BFS traversal) combined via Reciprocal Rank Fusion (§9.1–§9.3).
2. **Phase 2 — Constrain:** Candidate contexts are strictly bounded against allocated token budgets. Non-relevant peripheral sections are pruned using Document Card line intervals (`RET-010`), and nodes outside valid temporal or domain boundaries are filtered.
3. **Phase 3 — Verify:** Every generated factual claim or relation MUST be verified against the cited source passage. Citations MUST use explicit bracketed provenance references (`[source:node_id#lines]`). If an atomic proposition cannot be entailed by the cited source text, the claim is rejected.
4. **Phase 4 — Abstain:** If the calibrated posterior mass clears below the confidence threshold ($\max_y P(y) < \tau_{\text{abstain}}$) or if verification fails to substantiate the core query, the system MUST halt generation and emit an `EPISTEMIC_ABSTENTION` refusal rather than speculative text (**RET-011**).

---

## Retrieval Invariants

Source-aware retrieval MUST distinguish `captured_at`, `observed_at`,
`occurred_at`, `published_at`, `modified_at`, `experienced_at`, validity
intervals and `derived_at`. A temporal query such as “what did we know then?”
MUST bind the selected representation and derivation timestamps rather than
silently returning the latest source revision.

| Invariant | Description | Error code |
|---|---|---|
| **RET-001** | Search results SHALL be deterministic. Fusion and conflict ranking SHALL execute the formal algorithms in §9.1–§9.3 | - |
| **RET-002** | The same query with the same parameters SHALL produce identical results | - |
| **RET-003** | The evidence bundle SHALL contain all necessary fields for LLM grounding | - |
| **RET-004** | Query execution SHALL be stateless and MUST NOT accumulate persistent contexts or search caches on disk | - |
| **RET-005** | Baseline retrieval (lexical + graph) SHALL operate 100% offline and air-gapped without external network calls | - |
| **RET-006** | Stage 1 graph gates SHALL execute as deterministic boolean predicates before generation, reporting explicit refusal reasons | - |
| **RET-007** | A non-empty graph path SHALL NOT be treated as verification of propositional claim truth; Stage 2 verification evaluates individual passage entailment | - |
| **RET-008** | Bounded decision gates over discrete classes SHALL use constrained logit decoding and normalized softmax posteriors rather than regex-parsed free text | - |
| **RET-009** | Text chunking and reranker scoring windows MUST NOT truncate trailing conclusion, hedging, or findings sections (Truncation Trap defense) | - |
| **RET-010** | For Knowledge Objects exceeding 1,000 words or 100 lines, retrieval tools MUST support section-targeted and line-interval reading (`--section`, `--lines`) using Document Cards to prevent context dilution | - |
| **RET-011** | Grounded question-answering and synthesis workflows SHALL strictly execute the four-phase Retrieve, Constrain, Verify, Abstain (RCVA) protocol in §9.8. Systems MUST abstain with `EPISTEMIC_ABSTENTION` if verification fails or confidence clears below $\tau_{\text{abstain}}$ | - |

---

## Implementation Notes

### Determinism Requirements

1. **Seed Selection**: Seed nodes SHALL be sorted deterministically before selection of top-k
2. **Graph Traversal**: BFS SHALL traverse neighbors in the order defined by §9.2
4. **Fusion Calculation**: The baseline implementation uses deterministic
   IEEE-754 binary64 arithmetic in a single-threaded code path. External vector and
   reranker adapters are themselves responsible for documenting model, index and
   version determinism.
5. **Tie-Breaking**: SHALL follow the explicit rule: FinalScore DESC → node_id ASC

On conflict, a selected node means **preferred evidence candidate**, not
"the truth". `suppressed_nodes` means lower priority in the current
retrieval strategy; suppression is not deletion, invalidation or an
assertion that the node is false.

### Performance Considerations

- Indexing of BM25 and vector embeddings SHALL happen asynchronously
- Graph expansion SHALL have a timeout mechanism
- In-process memoization of results MAY be used for repeated identical queries
  within a single run. It MUST NOT be persisted to disk: **RET-004** forbids
  accumulating persistent contexts or search caches on disk, and a persisted
  result cache would also break **RET-002** determinism once the corpus or the
  threshold policy changes underneath it. Any reuse across runs MUST go through
  a rebuildable derived index carrying **CANON-003** source markers, not a
  cached answer.

### Error Handling

- Missing nodes (broken links) SHALL be handled via the `soft_link` flag
- Invalid relations SHALL be logged but not stop retrieval
- Timeout in retrieval SHALL return partial results with a warning