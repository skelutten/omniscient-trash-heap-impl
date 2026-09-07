# LLM Wiki Graph Intelligence Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-GRAPH-INTELLIGENCE-001`
> **Document family ID**: `LLM-WIKI-KG-DELTA-001`
> **Version**: `1.0.0`
> **Updated**: `2026-08-17`
> **Source**: Extracted from `LLM-WIKI-KG-DELTA-001` §1–§5.1, §7, §11–§14
> **Status**: `PROPOSED`
> **Implementation status**: `UNIMPLEMENTED`
> **Compatibility target**: Additive, isolated, opt-in
> **Companion documents**: `GRAPH-RETRIEVAL.md` (§8–§9), `DISCOVERY.md` (§5.2, §6, §10)
> **Normative owner**: This document owns graph-intelligence delta algorithms, signals and error family `E201–E299`
> **Related documents**: `ARCHITECTURE.md`, `ONTOLOGY.md`, `RETRIEVAL.md`, `DISCOVERY.md`

---

## 1. Purpose and scope

This document defines a graph-intelligence extension above the canonical LLM Wiki knowledge graph. At the logical architecture level, the LLM Wiki is a Knowledge Library: Markdown and YAML remain the canonical human-readable source, while graph, index, community, and retrieval artifacts are rebuildable projections. The extension may calculate graph signals, derived metrics, semantic similarity, communities, anomaly indicators, duplicate candidates, and knowledge-gap candidates.

The extension MUST NOT silently change canonical knowledge, canonical registries, or the default retrieval result. Graph-enhanced retrieval is an explicit opt-in mode and is not part of baseline retrieval compatibility.

The extension is divided into:

1. **Canonical Graph** — reviewed Markdown knowledge objects and canonical registry-governed relations; this is the repository's Layer 6 graph.
2. **Derived indexes** — reproducible analytical artifacts calculated from a canonical snapshot and attached conceptually to Layer 6; they are not a second canonical graph.
3. **Discovery records** — non-canonical candidates stored outside the canonical graph and requiring review and governance before promotion; they are not traversable Layer 6 nodes until promotion.

The initial implementation MUST be dependency-light and deterministic. Leiden, PPR, embeddings, ANN indexes, and LLM extraction are optional later stages, not prerequisites for the first implementation slice.

The Delta may later provide a derived graph-memory layer inspired by community-based retrieval systems. This layer is a projection of canonical knowledge, not a replacement for the curated graph. Community membership, summaries, structural observations, and inferred relations MUST remain derived artifacts until an explicit governance workflow promotes a resulting assertion.

**Start here:** implement only the Phase 1 manifest described below. Sections 8–10 define later analytical policies and MUST NOT be interpreted as Phase 1 requirements.

The current base acceptance state is defined by `conformance_matrix.yaml`, not by this document or by historical review files. If the matrix is absent when Phase 1 begins, Phase 1 MUST create a minimal matrix recording the base validator's current state and open rows before generating the manifest. Phase 1 MUST record which base conformance rows were verified for the run and which open rows were accepted as non-blocking risk. The current matrix has `production_locked: false` and `W001-W011` marked as planned/not implemented; this remains a base limitation, not a Delta success claim.

### Phase 1 in ten lines

1. Read canonical Markdown objects and normative registries as read-only input.
2. Sort all input paths and canonical node IDs.
3. Validate the canonical objects with the existing base validator.
4. Compute SHA-256 hashes for every input and the sorted aggregate manifest.
5. Write one JSONL manifest record per canonical object and registry.
6. Write a manifest header containing schema, architecture, pipeline, and corpus versions.
7. Publish the output with temporary-file-then-atomic-rename.
8. Re-scan and verify that canonical input hashes did not change.
9. Do not calculate embeddings, communities, discovery candidates, or graph ranking.
10. Do not modify canonical files, registries, or default retrieval output.

## 2. Compatibility and immutability contract

### 2.1 Canonical input protection

A Delta pipeline MUST treat the canonical corpus and normative registries as read-only inputs. It MUST NOT:

- create, modify, delete, or overwrite canonical relations;
- change `relation_registry.yaml`, `taxonomy_registry.yaml`, `object_registry.yaml`, or `governance_policy.yaml`;
- change `taxonomy_path`, `taxonomy_id`, scope, or file placement;
- change epistemic fields, status, confidence, or lifecycle fields;
- write derived or discovery data into knowledge-object frontmatter.

The pipeline MUST calculate a canonical corpus manifest before processing and verify that canonical input hashes are unchanged after processing.

### 2.1.1 Hash calculation

All file hashes MUST be SHA-256 over the exact file bytes, before parsing or newline conversion, serialized as lowercase hexadecimal with the `sha256:` prefix. The aggregate `corpus_hash` MUST be SHA-256 over the UTF-8 bytes of the sorted manifest entries, where each entry is exactly `relative_posix_path + "\\0" + file_hash + "\\n"`. Paths MUST be repository-relative POSIX paths sorted by Unicode code point. `source_node_hashes` MUST use the same exact-byte hash of each canonical source file. Hashes MUST be verified before processing and again before manifest publication; a mismatch MUST abort publication and preserve the previous valid manifest.

### 2.2 Retrieval compatibility

The default retrieval mode MUST remain byte-for-byte/result-for-result compatible with the baseline implementation for the same corpus and configuration.

Graph-enhanced retrieval MUST be explicit and MUST use the existing Layer 7 hybrid retrieval pipeline:

```yaml
retrieval_mode: canonical        # default
# or
retrieval_mode: graph_enhanced   # opt-in
graph_features_enabled: true     # required when retrieval_mode is graph_enhanced
```

`retrieval_mode: graph_enhanced` is a versioned Layer 7 policy profile, not a second retrieval implementation. It enables Delta-derived graph features as additional inputs to the existing graph modality/RRF fusion. `retrieval_mode: canonical` MUST preserve the existing baseline pipeline and scores. Graph-enhanced output MUST carry a distinct retrieval policy version and MUST NOT overwrite baseline evidence bundles.

```text
Canonical graph
      │
      ▼
Delta-derived features and metrics
      │  (explicit graph_enhanced opt-in)
      ▼
Existing Layer 7 graph modality
      ├── BM25 / lexical
      ├── vector adapter (when configured)
      └── graph features
      ▼
Existing RRF fusion and reranking
      ▼
Evidence Bundle
```

Future retrieval extensions MAY be added as separate, explicit, versioned Layer 7 policies, but this version does not add new values to the base `retrieval_mode` enum. In particular, retrieval scope (`local` versus `global`) and exploration strategy (fixed versus adaptive/DRIFT-style) are orthogonal dimensions and MUST NOT be collapsed into one mode value. A future local/global profile MUST preserve canonical seed retrieval, bounded expansion, source-node references, and evidence-bundle provenance. A future adaptive/DRIFT-style policy is a DRIFT-style exploration policy and MUST define explicit limits for follow-up branches, depth, budget, and termination; it MUST NOT perform unbounded query generation or silently change the baseline retrieval mode. Any future profile MUST use the existing Layer 7 evidence-bundle and RRF contracts where ranking/fusion is required; it must not replace the existing RRF fusion with a parallel ranking system.

### 2.3 Layer permissions

| Layer | Read canonical graph | Traversable by default | May affect default rank | May affect graph rank | May be promoted |
|---|---:|---:|---:|---:|---:|
| Canonical | yes | yes | yes | yes | n/a |
| Derived index | yes | no | no | explicit Layer 7 policy only | no |
| Discovery record | yes | no | no | no by default | yes, after review |

## 3. Delta invariants

| ID | Domain | Rule |
|---|---|---|
| `DELTA-CORE-001` / `E201` | Ontology | Derived signals and discovery candidates MUST NOT mutate canonical relations or registries. |
| `DELTA-CORE-002` / `E202` | Epistemology | Derived signals MUST NOT alter evidence, verification, authority, consensus, confidence, or status. |
| `DELTA-CORE-003` / `E203` | Taxonomy | Graph analysis MUST NOT change or automatically propose taxonomy/file-placement mutations. |
| `DELTA-CORE-004` / `E204` | Governance | Generated candidates MUST enter Discovery with `pending` status. Promotion requires explicit approval and Layer 1–5 validation. |
| `DELTA-CORE-005` / `E205` | Axiom | Community membership is analytical metadata and MUST NOT be used as taxonomy classification. |
| `DELTA-CORE-006` / `E206` | Lifecycle | Pending candidates MUST have UTC timestamps and an expiry no later than 90 calendar days after creation. Expiry is an auditable state transition, not silent deletion. |
| `DELTA-CORE-007` / `E207` | Security | Cross-scope derived/discovery records are denied by default. Cross-scope access requires an explicit Delta scope policy. |

Delta errors MUST be implemented in a separate Delta validator/pipeline namespace. They MUST NOT be silently mixed into the base linter's error-code contract. Per the error-code allocation register in `VALIDATION.md` §10.3, the base linter owns `E001`–`E050` and the ingestion engine owns `E101`–`E199`; `E201`–`E299` is reserved for the Delta graph pipeline, of which `E201`–`E207` are allocated here.

## 4. Scope firewall and privacy

The default policy is scope isolation:

```yaml
version: "1.0.0"
default_cross_scope: false
community_partition: per_scope
allowed_cross_scope_relations: []
allow_cross_scope_similarity: false
allow_cross_scope_cooccurrence: false
```

The `cross_scope` concept MUST NOT be assumed to exist in the base relation registry. If cross-scope behavior is later needed, it MUST be introduced through this explicit Delta policy or through a separately versioned, backward-compatible registry extension. A future `global` scope is not part of this version; adding one requires an object/taxonomy/governance registry change and must not be inferred by the Delta pipeline.

Derived records MUST carry `scope`. A cross-scope record MUST be rejected unless the policy explicitly permits it. Embeddings, excerpts, cooccurrence data, and community assignments MUST be treated as potentially sensitive derived artifacts and subject to the same scope filtering as source metadata.

## 5. Versioned data contracts

Every derived and discovery artifact MUST include:

```yaml
record_id: "..."
artifact_type: "..."
schema_version: "..."
architecture_version: "3.8.10"
corpus_hash: "sha256:..."
source_node_ids: []
source_node_hashes: {}
algorithm: "..."
algorithm_version: "..."
policy_version: "..."
created_at: "2026-01-01T00:00:00Z"
expires_at: null
scope: "personal"
status: "active"
provenance: {}
```

### 5.1 Derived edge

A `DerivedEdge` MUST contain:

- stable `edge_id` based on canonicalized source/target IDs and algorithm version;
- source and target node IDs;
- optional canonical relation reference;
- component scores and final score;
- evidence references, not unsupported claims;
- scope and policy metadata;
- corpus and source-node hashes.

`source_id` and `target_id` MUST refer to existing canonical node IDs at generation time. A derived edge MUST NOT introduce a new node identity or use a discovery candidate as a traversable endpoint.

The initial logical score schema is:

```yaml
canonical_edge_exists: false
component_scores:
  canonical: 0.0
  similarity: 0.0
  proximity: 0.0
  cooccurrence: 0.0
final_score: 0.0
```

Every component score and `final_score` MUST be a finite number in `[0.0, 1.0]`. `final_score` MUST equal the versioned edge-strength policy calculation after decimal rounding specified by the policy. Phase 1 does not emit derived edges; Phase 2 may emit only topology/manifest metrics, and later phases may add the optional components declared by the policy.

Derived edges are analytical records, not canonical relations.

### 5.1.1 Derivation provenance

Derived records MAY carry a `derivation` object that describes how the record was produced. The `derivation.mode` value is orthogonal to epistemic metadata; derivation metadata MUST NOT alter epistemic fields and MUST NOT be written into canonical `evidence`, `verification`, `authority`, `consensus`, `confidence`, or `status` fields.

```yaml
derivation:
  mode: extracted       # extracted | inferred | ambiguous
  extractor: rule       # rule | parser | ast | llm | human
  extractor_version: "1.0.0"
  source_revision: null
  prompt_version: null
  confidence: 0.0
```

`extracted` means that a deterministic or structured extractor identified an observation in source material; `inferred` means that the observation was derived by a semantic or probabilistic method; `ambiguous` means that the method could not establish a single interpretation. A derivation confidence is a property of the derivation process, not epistemic confidence in the canonical knowledge claim. LLM-derived records MUST additionally record model and prompt versions, source excerpts or spans, and `best-effort` determinism.

### 5.1.2 Evidence references and source spans

Derived relations, community reports, discovery candidates, and evidence bundles SHOULD reference stable source spans rather than only whole documents. A source-span reference is an optional, deterministic, repository-relative projection of a source object; it does not create a new canonical document hierarchy or change the retrieval unit from Knowledge Object to fragment:

```yaml
evidence_unit_id: "PERS-ART-DEMO-0001-C017"
document_id: "PERS-ART-DEMO-0001"
unit_type: "chunk"       # chunk | paragraph | heading | code_block | table
source_span:
  start: 1832
  end: 2241
text_hash: "sha256:..."
```

`source_span` offsets (the source span in the normalized text) MUST use the declared text-normalization policy. The optional `evidence_unit_id` MUST be a stable identifier derived from the source node ID, source-node hash, chunk/segment index, and chunking/segmentation policy version; the hash and policy version need not be rendered literally in the identifier string when they are carried in the surrounding record. Source-span references are derived metadata and MUST NOT be treated as canonical Knowledge Objects or as a replacement retrieval hierarchy.

### 5.1.3 Context-budget observability

An evidence bundle MAY include non-ranking observability metadata:

```yaml
context:
  estimated_tokens: 0
  source_tokens: 0
  reduction_ratio: 0.0
  selection_reasons: []
```

These fields MUST be computed with a declared tokenizer or estimation policy, MUST NOT affect ranking or epistemic fields, and MUST NOT introduce a derived scalar epistemic-support signal. Missing context-budget measurements MUST be represented as absent metadata, not fabricated zero-cost claims.

> **§5.2 Discovery candidate** and **§6 Discovery lifecycle and promotion** are
> specified in `DISCOVERY.md`. Section numbering is preserved across the
> document family so that cross-references remain stable.

## 7. Determinism contract

The implementation MUST distinguish three determinism levels:

- `bitwise`: identical serialized output for identical input, policy, and runtime contract;
- `ranked-equivalent`: identical ordering and selected IDs, while floating-point serialization may differ;
- `best-effort`: useful analytical output without reproducibility guarantees.

The baseline Delta pipeline MUST be `bitwise` or `ranked-equivalent` and MUST define:

- sorted file and node traversal;
- stable tokenization/chunking;
- explicit float precision and rounding;
- explicit missing-signal behavior;
- stable score and node-ID tie-breaks;
- algorithm and policy versions;
- corpus and source-node hashes;
- single-threaded mode where required.

Optional Leiden/PPR/embedding/ANN/LLM stages MUST declare their determinism level and versions. `random_seed: 42` alone is insufficient. Optional stages MUST also specify convergence thresholds, maximum iterations, backend versions, embedding model, prompt version, model parameters, and label canonicalization.

### 7.1 Deterministic chunking policy

The baseline text index MUST use a deterministic character-based chunking policy for cooccurrence. The defaults are:

```yaml
chunking:
  unit: unicode_codepoints
  chunk_size: 500
  overlap: 50
  tokenization: whitespace
  normalize: unicode_nfkc_lowercase_collapse_whitespace
```

Text is normalized with Unicode NFKC, lower-cased, and consecutive whitespace is collapsed before chunking. Chunks are consecutive 500-codepoint windows with a 50-codepoint overlap; the final short window is retained. `overlap` MUST be smaller than `chunk_size`. Canonical node IDs and aliases are normalized with the same policy. An alias match requires the complete normalized alias phrase, with all whitespace-separated tokens present consecutively and in order within the same chunk; substring matches and single-token partial alias matches are not allowed. The chunking policy, including its version, MUST be recorded in the manifest. A policy-version bump requires regeneration of all affected derived artifacts; in particular, it invalidates cooccurrence-derived edges and requires a full cooccurrence re-index. An implementation MAY use a different policy only by changing the policy version and regenerating all affected derived artifacts. Chunking is not required by Phase 1; it becomes a prerequisite for the first implementation of `cooccurrence_count` in Phase 2 or later.

> **§8 Delta graph-feature and edge-strength policy** and **§9 Graph-enhanced
> retrieval** are specified in `GRAPH-RETRIEVAL.md`. **§10 Discovery rules** is
> specified in `DISCOVERY.md`.

## 11. Storage and pipeline lifecycle

Recommended layout:

```text
derived/
├── manifest.jsonl
├── config/
│   ├── edge_strength_policy.yaml
│   └── scope_policy.yaml
└── graph/
    ├── derived_edges.jsonl
    ├── node_metrics.jsonl
    ├── communities.jsonl
    └── relation_evidence.jsonl

discovery/
├── manifest.jsonl
├── duplicates.jsonl
├── knowledge_gaps.jsonl
├── node_proposals.jsonl
└── audit_log.jsonl
```

JSON Lines is the dependency-light baseline format because it is inspectable with standard text tools and requires no database dependency. SQLite MAY be used as an indexed local backend. Parquet MAY be used for large corpora or analytical workloads, but is an optional backend and MUST expose the same versioned logical schema. The choice of backend MUST be recorded in the manifest.

Each run follows:

```text
canonical scan
→ input manifest and hashes
→ parse/index
→ deterministic derived metrics
→ optional communities
→ optional discovery generation
→ TTL reconciliation
→ output schema validation
→ atomic manifest publication
```

Writes MUST use temporary files followed by atomic rename. A failed run MUST NOT replace the last valid manifest. Artifacts MUST contain schema, corpus, algorithm, and policy versions. The repository policy MUST explicitly state whether derived/discovery outputs are committed, ignored, cached, or distributed. Large generated Parquet files SHOULD NOT be treated as canonical Git truth.

## 12. Implementation phases

### Phase 1 — Immutable canonical manifest [REQUIRED]

- scan canonical objects and registries;
- produce sorted node/relation manifests;
- hash all inputs;
- verify no canonical mutation;
- add corpus permutation and hash tests;
- prerequisite: the base conformance matrix MUST be consulted; only implemented and verified base contracts may be treated as prerequisites, while open rows (currently including `W001-W011`) remain explicit non-blocking gaps for the Delta manifest slice.

If `conformance_matrix.yaml` is absent, the minimal matrix created by Phase 1 MUST use this logical schema:

```yaml
# Illustrative manifest shape; the executable artifact is planned, not present
# in this repository. Its policy version MUST reference threshold_policy.yaml.
schema_version: "1.0.0"
production_locked: false
rows:
  - rule_id: "E001"
    domain: "base"
    status: "implemented"   # implemented | planned | gap
    verified_by: "python3 linter.py"
    notes: ""
```

`rule_id` MUST be unique. `status: implemented` requires a successful verification command recorded in `verified_by`; `planned` and `gap` rows MUST remain non-blocking for the Phase 1 manifest but MUST be listed in the manifest header as open rows.

### Phase 2 — Deterministic derived metrics [REQUIRED after Phase 1]

- degree and connected components;
- bounded canonical distance;
- deterministic node metrics;
- versioned logical schema with JSONL as the baseline backend; SQLite or Parquet are optional backends;
- use manifest hashes to skip unchanged inputs during incremental runs;
- invalidate derived contributions for deleted or changed inputs before atomic publication;
- atomic output and stale-output detection.

Phase 2 remains limited to the semantic/canonical graph and its deterministic projections. AST/Tree-sitter/LSP extraction, a structural relation registry, Git-specific structural nodes, and structural-to-semantic bridge relations are out of scope for this Delta and require a separate Structural Knowledge Graph specification.

### 12.1 Backend selection decision

Phase 1 MUST use JSON Lines. SQLite and Parquet MAY be added from Phase 2 onward only when a measured performance or indexing requirement justifies them. The backend choice MUST NOT change the logical record schema or deterministic ordering. A backend adapter MUST be selected explicitly in configuration and recorded in the artifact manifest. Every adapter MUST pass equivalence tests against the JSONL reference output before it is used for a production-like run; equivalence means identical logical records, field values, record count, and ordering after canonical serialization.

### 12.1.1 Optional observability fields

Manifest and evidence-bundle producers MAY report non-normative coverage and context-budget observations, for example:

```yaml
observability:
  nodes_indexed: 0
  canonical_edges_indexed: 0
  derived_edges_indexed: 0
  unresolved_references: 0
  communities_detected: 0
context:
  estimated_tokens: 0
  source_tokens: 0
  reduction_ratio: 0.0
```

These values MUST have an explicitly declared measurement policy and MUST NOT be presented as conformance status, epistemic confidence, or ranking inputs. Structural-specific fields such as AST nodes, symbol resolution, or structural edges belong to a future Structural Knowledge Graph specification and MUST NOT be populated with invented values by the semantic Delta pipeline.

### Phase 3 — Opt-in graph retrieval [OPTIONAL]

- add explicit graph-enhanced mode;
- preserve baseline ranking and evidence bundles;
- add golden ranking and tie-break tests;
- include graph policy and mode in output metadata.

### Phase 4 — Discovery candidates [OPTIONAL]

- duplicate pair candidates;
- knowledge-gap candidates;
- candidate schemas and stable IDs;
- TTL reconciliation;
- scope firewall;
- no promotion yet.

### Phase 5 — Governance promotion [OPTIONAL; requires explicit human workflow]

- lifecycle state machine;
- audit log;
- explicit approval;
- full base validation;
- canonical commit workflow;
- promotion/rejection/expiry tests.

Optional Leiden, PPR, embeddings, ANN, and LLM stages MUST be added only after the deterministic phases pass.

### 12.2 Minimal Phase 1 example

Input:

```text
personal/example/PERS-ART-DEMO-0001.md
```

Output (`derived/manifest.jsonl`):

```json
{"artifact_type":"manifest_header","schema_version":"1.0.0","architecture_version":"3.8.10","delta_spec_version":"1.0.0","pipeline_version":"0.1.0","chunking_policy_version":"1.0.0","corpus_hash":"sha256:<aggregate-hash>","backend":"jsonl","base_conformance_matrix":"conformance_matrix.yaml","base_open_rows":["W001-W011"]}
{"artifact_type":"canonical_input","node_id":"PERS-ART-DEMO-0001","path":"personal/example/PERS-ART-DEMO-0001.md","sha256":"sha256:<file-hash>","scope":"personal"}
{"artifact_type":"canonical_registry","path":"relation_registry.yaml","sha256":"sha256:<registry-hash>"}
```

The placeholders are calculated values, not literal strings. `delta_spec_version` identifies this normative document; `pipeline_version` identifies the implementation release and follows an independent versioning scheme. `canonical_input` records MUST include their repository-relative POSIX `path`; `canonical_registry` records use `path` and have no `node_id`. Node proposal serialization MUST omit absent optional fields (equivalent to Pydantic `exclude_none=True`). An empty canonical corpus is valid: its manifest contains the header and registry entries only. Graph-enhanced retrieval with empty seeds is defined to return an empty result set. Reordering input file creation MUST NOT change the sorted manifest or its aggregate hash.

### 12.3 Corpus-size guidance

JSONL is the default for all corpus sizes in the normative baseline. SQLite MAY be added from Phase 2 onward only for a measured indexing/query requirement, and Parquet MAY be added only for a measured analytical batch requirement. The approximate corpus sizes previously associated with backend choices are heuristics, not correctness boundaries, and do not override the Phase 1 JSONL requirement. The selected backend MUST be recorded in the manifest and MUST preserve the same logical schema and ordering contract.

Graph-enhanced retrieval is not recommended for very small corpora (approximately fewer than 500 nodes) unless the corpus has unusually dense, high-value canonical relations. Below that scale, baseline retrieval is the default and usually provides better simplicity-to-value. The threshold is a decision heuristic, not a correctness boundary; teams SHOULD measure ranking improvement before enabling graph-enhanced mode. Phase 1 and Phase 2 manifest/metric generation remain valid at any corpus size; this guidance applies only to the optional graph-enhanced retrieval mode.

### 12.4 Phi intuition and phase availability

| Signal | Intuition | Availability |
|---|---|---|
| `phi1` | Shorter canonical distance is stronger | Phase 3+ |
| `phi2` | A canonical path exists; stronger weighting can later distinguish path quality | Phase 3+ |
| `phi3` | Shared provenance references are stronger | Optional Phase 3+; requires provenance references |
| `phi4` | Same enabled community is stronger | Phase 4+ |
| `phi5` | Personalized PageRank proximity is stronger | Optional Phase 3+ |
| `phi6` | Better-connected canonical nodes are stronger | Computed Phase 2+; consumable by retrieval only from Phase 3 |

### 12.5 Policy invalidation and unknown keys

Changing `edge_strength_policy.yaml` or `scope_policy.yaml` MUST increment its policy version and invalidate affected derived or discovery artifacts. A scope-policy change MUST invalidate any artifact whose scope decision depends on that policy. Unknown keys in a policy document, including unknown weight keys for a known policy version, MUST fail schema validation; implementations MUST NOT silently ignore them.

## 13. Conformance test suite

The Delta suite MUST include at least:

```text
conformance/delta/
├── test_delta_core_invariants.py
├── test_canonical_immutability.py
├── test_delta_manifest_and_hashes.py
├── test_edge_strength_math.py
├── test_graph_retrieval_opt_in.py
├── test_graph_retrieval_fusion.py
├── test_derived_schema_and_atomicity.py
├── test_discovery_ttl.py
├── test_discovery_state_machine.py
├── test_duplicate_pair_canonicalization.py
├── test_community_independence.py
├── test_scope_firewall.py
├── test_stale_artifact_rejection.py
└── test_promotion_validation_and_audit.py
```

Acceptance criteria:

- canonical Markdown and registries remain unchanged after a derived run;
- default retrieval output remains unchanged;
- graph-enhanced retrieval is explicit and versioned;
- identical inputs and policy produce deterministic output at the declared level;
- stale artifacts are rejected;
- all candidates are schema-valid and auditable;
- TTL boundaries and state transitions are tested;
- cross-scope leakage is rejected by default;
- promotion cannot bypass base Layer 1–5 validation;
- partial failures do not replace the last valid output;
- `production_locked` is not claimed until all required matrix rows are green.

## 14. Deferred items

The following are intentionally deferred until the preceding contracts are implemented:

- graph-health signal reporting and threshold policy;
- structural Knowledge Graph extraction (AST/Tree-sitter/LSP), structural registry, source-revision binding, reconciliation, and impact analysis — now specified separately in `STRUCTURAL-GRAPH.md` (status: Proposed, not implemented);
- temporal claim/query semantics beyond the base `validity` contract;
- community-report summarization and global/adaptive retrieval profiles;
- bitwise guarantees for external ANN/vector/reranker systems;
- LLM-driven concept extraction and promotion;
- legacy HTML graph migration;
- large-scale corpus migration;
- cross-scope analytics;
- **recurrence signals** — temporal-frequency discovery over the ingestion history
  (which themes keep returning, which unresolved question keeps attracting sources,
  stated versus revisited interest). All current Discovery candidate types are
  structural snapshot properties of a single `corpus_hash`; recurrence needs a
  time-series over successive manifests and its own candidate type
  (`research/critiques-and-community-feedback.md` §3).

Graph-health signals are intentionally not assigned `W012`–`W016` codes in this version. The base warning framework is not currently implemented; introducing unregistered warning codes would create a second, ambiguous warning contract. A future version MAY define named Delta health signals with their own schema, severity, suppression, and reporting policy.

---

**End of LLM Wiki Graph Intelligence Specification v1.0.0**

See also: `GRAPH-RETRIEVAL.md` (§8–§9), `DISCOVERY.md` (§5.2, §6, §10),
`STRUCTURAL-GRAPH.md` (SG-001–SG-020), `OKF-INTEROP.md` (OKF-001–OKF-010).