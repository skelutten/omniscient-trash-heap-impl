# LLM Wiki Graph-Enhanced Retrieval Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-GRAPH-RETRIEVAL-001`
> **Document family ID**: `LLM-WIKI-KG-DELTA-001`
> **Version**: `1.0.0`
> **Updated**: `2026-08-17`
> **Source**: Extracted from `LLM-WIKI-KG-DELTA-001` §8–§9
> **Status**: `PROPOSED`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Compatibility target**: Additive, isolated, opt-in (Phase 3+)
> **Base specification**: `RETRIEVAL.md` §9 (Layer 7 hybrid retrieval)
> **Companion documents**: `GRAPH-INTELLIGENCE.md` (delta core), `DISCOVERY.md`
> **Normative owner**: This document owns opt-in graph-enhanced retrieval behavior
> **Related documents**: `RETRIEVAL.md`, `GRAPH-INTELLIGENCE.md`, `DISCOVERY.md`

---

## 8. Delta graph-feature and edge-strength policy

The Delta MUST NOT create a second retrieval pipeline. This section defines versioned graph-feature calculations consumed by the existing Layer 7 graph modality and RRF fusion when `retrieval_mode: graph_enhanced` is explicitly selected. The default Layer 7 retrieval pipeline, including its existing epistemic post-filter and conflict-resolution behavior, remains authoritative.

The initial edge-strength policy MUST use explicit normalized topology/content weights. Epistemic metadata MUST NOT be converted into a scalar edge-strength or graph-ranking component because the base EPI-001 contract keeps those dimensions orthogonal. Epistemic metadata may be used by the existing retrieval filters and conflict resolver only.

```yaml
version: "1.0.0"
weights:
  explicit_canonical_edge: 0.50
  semantic_similarity: 0.20
  contextual_proximity: 0.15
  cooccurrence_frequency: 0.15
thresholds:
  min_edge_strength: 0.15
  semantic_similarity_cutoff: 0.75
  contextual_cooccurrence_min_chunks: 2
```

The score is:

```text
S(u,v) = clamp(
  w1*canonical
  + w2*similarity
  + w3*proximity
  + w4*cooccurrence,
  0.0,
  1.0
)
```

Definitions:

- `canonical` is `1.0` only when the canonical relation exists, otherwise `0.0`;
- `similarity` is cosine similarity, clipped to `0.0` below the configured cutoff;
- `shared_documents` is the count of distinct normalized `provenance.source_refs` values shared by both nodes. Missing references contribute zero. It does not mean Markdown files, taxonomy directories, or raw source files unless those are explicitly represented as the same normalized provenance reference;
- `provenance.source_refs` normalization lowercases each string, strips leading/trailing whitespace, and collapses internal whitespace. URI prefixes such as `doi:` and `isbn:` are preserved while being case-normalized. Empty values are treated as missing;
- `proximity(s,c) = min(1.0, |shared_provenance_refs(s) ∩ shared_provenance_refs(c)| / 5)`;
- `cooccurrence_count(s,c)` is the number of distinct normalized text chunks in which both canonical node IDs or their indexed aliases occur. It is computed from the same deterministic chunking policy recorded in the manifest; it is not a count of shared relation targets, directories, or source files. Missing or empty chunk indexes produce zero;
- `cooccurrence = min(1.0, cooccurrence_count / 10)`. **Implementation note:** the
  index SHALL be built by tokenising each chunk once and looking up candidate node
  IDs/aliases by first token. Matching every alias against every chunk is quadratic;
  measured prior art records 107 s versus 0.49 s at 5,000 documents, and notes that
  collapsing all aliases into one regex alternation is *"quadratic behaviour wearing a
  linear disguise"* (`research/critiques-and-community-feedback.md` L3);
The four epistemic dimensions MUST remain separate metadata fields; they are not averaged or otherwise collapsed by Delta. The four active weights above sum to `1.0`; adding a future component requires a new policy version and a revised normalization contract.

All policy values require schema validation, range validation, and a policy version.

## 9. Graph-enhanced retrieval

All internal graph-retrieval cut-offs are declared in
`schemas/registry/threshold_policy.yaml`; the inline values below are
descriptive projections and MUST remain synchronized with that registry.

Graph-enhanced retrieval is opt-in and must not replace baseline retrieval. The `phi` values below are named feature components for the existing Layer 7 graph modality, not an independent ranking or fusion pipeline.

The initial implementation SHOULD use only deterministic canonical-graph features:

For candidate `c` and seed set `S_Q`, the baseline definitions are:

```text
phi1(c) = max over s in S_Q of 1 / (1 + dist_canon(s,c))
         = 0 when no canonical path exists

phi2(c) = max over p in Paths_canon(S_Q,c) of Product over (u,v) in p of edge_weight(u,v)
         = 0 when no canonical path exists

phi3(c) = max over s in S_Q of proximity(s,c)
         = 0 when S_Q is empty

phi4(c) = 1 when c and at least one seed belong to the same enabled community,
          otherwise 0; when community detection is disabled, phi4(c) = 0

phi5(c) = PPR(c | S_Q), with alpha=0.85, only when the optional PPR stage is enabled;
          otherwise 0

phi6(c) = min(1.0, total_degree(c) / degree_normalization)
         where total_degree = in_degree + out_degree over canonical edges
```

Canonical path edge weights MUST be read from a versioned relation-weight policy. The initial default assigns `1.0` to every traversable canonical edge; relation-specific weighting is optional and MUST be explicitly configured. Consequently, under the initial default, `phi2(c)` is a bounded reachability indicator: it is `1.0` when at least one allowed canonical path exists within the configured limits and `0.0` otherwise. It does not decay with hop count until a relation-weight policy assigns weights below `1.0`. A future policy MAY add an explicit per-hop decay factor, but implementations MUST NOT introduce one implicitly. Paths are bounded by the pipeline's maximum depth and expanded-node limits. `S_Q` is the set of canonical seed node IDs returned by baseline retrieval.

The default graph-score weights are:

```yaml
version: "1.0.0"
alpha:
  phi1_distance: 0.30
  phi2_path_score: 0.20
  phi3_proximity: 0.15
  phi4_community: 0.10
  phi5_ppr: 0.15
  phi6_degree: 0.10
degree_normalization: 50
```

`degree_normalization` is an integer policy value with minimum `1`; `50` is an intentionally arbitrary baseline ceiling, not a corpus-derived constant. Policy loading MUST reject zero, negative, fractional, or non-finite values. The alpha values MUST be non-negative and sum to `1.0`. Missing modalities contribute zero; the configured weights are not silently renormalized. Candidates are ordered by:

`phi6` is a topological retrieval signal only. A high-degree or central node is structurally connected, not thereby more authoritative, more trustworthy, or epistemically better supported.

```text
(-graph_feature_score, node_id)
```

The resulting feature vector is passed to the existing Layer 7 graph modality and its existing RRF fusion only when `retrieval_mode: graph_enhanced` is explicit. The evidence bundle MUST identify the mode, policy version, feature values, and graph-modality rank. Delta MUST NOT introduce a second RRF implementation.

Delta features MUST NOT alter the deterministic neighbor-selection order defined by base graph expansion §9.2 of `RETRIEVAL.md` (`priority(category)`, then `type`, then `target`). They affect only the scoring of nodes already selected by the base BFS; they MUST NOT be used as traversal or neighbor-pruning tie-breakers.

### 9.1 Graph retrieval and graph reasoning

Graph retrieval answers which canonical or explicitly enabled derived records are relevant. Graph reasoning interprets the paths, claims, evidence, and derivation metadata connecting those records. Graph retrieval and graph reasoning MUST remain separate contracts: a retrieved path is not itself an asserted explanation, and a reasoning result MUST retain the supporting node IDs and evidence-unit IDs. For example, “Which functions call ProcessOrder?” MAY return a deterministic node list, while “Why is ProcessOrder architecturally critical?” requires synthesis; an LLM MUST NOT be inserted solely to restate a deterministic node/edge lookup.

### 9.2 Community memory and reports

> **On the reference implementation.** The hierarchical-community and community-report
> ideas originate in Microsoft GraphRAG, which is now **in maintenance mode** (no new
> features), is described by its authors as a demonstration rather than a supported
> offering, carries an explicit indexing-cost warning, and depends on prompt tuning for
> acceptable quality. That is independent support for keeping this stage optional and
> late rather than adopting it early; it is not an upstream to track. See
> `research/related-implementations.md` §3.

Community detection is an optional later analytical stage. It MAY produce a hierarchical community structure of derived memberships and community reports at levels `L0`, `L1`, and higher. A community report MUST include:

- a stable community ID, hierarchy level, and parent community where applicable;
- corpus hash, algorithm/version, scope, and determinism level;
- sorted member node IDs and source-node hashes;
- key relation IDs or derived-edge IDs used in the report;
- evidence-unit references for claims or excerpts;
- report status and invalidation metadata.

Community reports MUST be stored as derived retrieval artifacts and MUST NOT become canonical Knowledge Objects. Community membership MUST NOT modify taxonomy_path, taxonomy_id, scope, taxonomy_registry.yaml, or canonical relations. Community centrality, degree, or membership MUST NOT be interpreted as epistemic confidence or authority. Hierarchical reports MAY support `global` retrieval and context compression only after their schema, provenance, invalidation, and source-grounding contracts are implemented and tested.

When optional PPR or community signals are disabled, their components remain zero and the maximum possible graph-feature score is reduced by their configured alpha weights. This is intentional and deterministic; weights MUST NOT be silently renormalized.

---

**End of LLM Wiki Graph-Enhanced Retrieval Specification v1.0.0**

See also: `RETRIEVAL.md` (baseline Layer 7), `GRAPH-INTELLIGENCE.md` (delta core).