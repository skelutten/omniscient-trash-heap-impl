# Decision Log

> **Status:** restored 2026-09-07; reconstructed, not original
> **Purpose:** give every `Dnn` identifier cited in `specs/`, `plans/` and
> `schemas/registry/` a single auditable home, and record the human sign-offs
> that `plans/00-ROADMAP.md` §1 (**EPI-SPEC-001**) requires for post-freeze
> specification changes.
> **Normative owner:** this document owns the decision *record*. It does not own
> any rule — each decision's normative text lives in the document listed under
> "Lives in", which wins on divergence per `specs/README.md` §1.

---

## 1. Provenance of this file (read first)

A `plans/DECISION_LOG.md` was created empty in commit `70096be` and **deleted in
commit `615e4a4`**. No decision log has existed since. Consequently every `Dnn`
identifier in this repository survives only as an inline citation in the document
that applied it.

**This file is a reconstruction from those citations, performed 2026-09-07.** It
is not a contemporaneous record. Each entry below states where the decision is
*applied*; none states who decided it or when, because that information was never
written down and cannot be recovered from the repository.

The numbering is **sparse**. These identifiers are cited nowhere in the
repository and have no reconstructable content:

```text
D6, D9, D12–D18, D20–D23, D26–D28, D30–D38, D40–D53,
D55–D78, D85–D89, D91, D92
```

Either they were decided and never recorded, or the numbers were skipped. This
file does not guess. **Going forward, a decision MUST be added here in the same
commit that first cites its identifier** (see §5).

Separately, `review-outputs/Chad-01.md` uses `D1`–`D5` as review-finding labels.
Whether that is the same series is unconfirmed; those five are **not** claimed by
this log.

---

## 2. Reconstructed decisions (pre-freeze)

| ID | Decision (as applied) | Lives in |
|---|---|---|
| **D7** | `Sequence` (`SEQ`) added as an engineering object type, because 20 flow pages are protocol message sequences | `object_registry.yaml`; recorded at `specs/README.md` §7 item 16 |
| **D8** | Section-ownership contract adopted: machine-owned sections, byte-preserved human `## Notes`, fail-closed unknown sections | `specs/SCHEMA.md` §7.1; `specs/README.md` §7 item 21 |
| **D10** | Security vulnerabilities/CVEs modeled as `TroubleReport` + `domain: security` rather than a new object type | `object_registry.yaml`; `specs/README.md` §7 item 12 |
| **D11** | Tool pages modeled as `Component` + `facets.toolchain` rather than a new object type | `object_registry.yaml`; `specs/README.md` §7 item 13 |
| **D19** | `schemas/registry/epistemic_registry.yaml` is the normative owner of the epistemic dimensions | `specs/EPISTEMOLOGY.md` header |
| **D24** | Every linter diagnostic MUST be structured with exactly five fields | `specs/VALIDATION.md` §(diagnostic structure), line 41 |
| **D25** | `lint <file>` SHALL filter reported diagnostics to the specified scope | `specs/VALIDATION.md` line 51 |
| **D29** | Temporal and date-dependent checks (`W002`, `W003`, `W012`, …) are evaluated against an explicit, injectable evaluation date | `specs/VALIDATION.md` line 48 |
| **D39** | Sentinel-value distinction for domain object specification facets (`W011`) | `specs/DATA_MODEL.md` line 108; `specs/VALIDATION.md` line 114 |
| **D54** | `threshold_policy.yaml` created as the single normative home for internal cut-offs (**THRESH-002**), ending threshold proliferation | `schemas/registry/threshold_policy.yaml`; `specs/README.md` §7 item 23 |

Review-allocated identifier blocks `C1`–`C5`, `H1`–`H9`, `R1`–`R6` and `N1` are
tracked in `review-outputs/Qwen-01.md`, `Qwen-02.md` and were closed by commits
`df12b16` and `286319a`. They are a different series and are **not** restated
here.

---

## 3. D79–D95 — post-freeze specification hardening

Landed in commit `5d33d1e` (2026-09-06), *after* the **EPI-SPEC-001** freeze.
Reconciled in the commit that adds this file.

| ID | Decision | Lives in |
|---|---|---|
| **D79** | `Embedder` protocol + `DeterministicDouble` test seam. **Honest Modality rule:** a test double (`is_double = True`) is forbidden from claiming the vector modality; bundles report vector as `absent` | `plans/90` Phase V1 |
| **D80** | Offline embedding provider support (local ONNX / `all-MiniLM-L6-v2`, 384-dim, unit norm); defensive fail-closed store validation; ephemeral provisioning with `--cleanup` | `plans/90` Phase V2 |
| **D81** | No arbitrary query-to-document similarity floor — only a `0.0` sign-convention floor; `GRAPH-SEMANTIC-SIMILARITY: 0.75` is reserved for inter-object graph edge inference. Multi-chunk scoring uses **max-over-chunks aggregation** with `chunk_index` passage attribution | `specs/RETRIEVAL.md` §9.1 items 2–3; `plans/90` Phases V2–V3; `threshold_policy.yaml` line 40 |
| **D82** | Self-describing evidence bundles: `modalities_available` / `modalities_absent` derived from what actually executed; unspent modalities report `null`, never `0.0` | `specs/RETRIEVAL.md` §9.4; `plans/90` Phase V3 |
| **D83** | Cross-encoder reranking **excluded** from the query path: bi-encoders cannot act as cross-encoders, weights are not offline-reachable, and a query-path model call would break offline determinism and **RET-002**. `FinalScore` defaults to `RRF(d)` | `specs/RETRIEVAL.md` §9.1 note; `plans/90` Phase V4 |
| **D84** | Transparent degraded fallback to baseline lexical+graph retrieval when vector deps or indexes are absent; index staleness reported with exact reason | `plans/90` Phase V5 |
| **D90** | Status-dashboard drift detector validating `SPEC_STATUS.md` against specs, registries, runtime, tests and CI markers | `plans/05` scope item 4 |
| **D93** | **Graph modality condition:** graph participates in RRF only when expansion reached `depth > 0`. At depth 0 every score is $1.0$, so lexicographic tie-break would degenerate into alphabetical reordering. Reports `graph_consulted` vs `graph_reached` distinctly | `specs/RETRIEVAL.md` §9.1 item 1, §9.4; `plans/02` scope item 8 |
| **D94** | Per-parameter precedence **CLI flag > `retrieval:` config block > §9.4 default**, with resolution source reported in `parameters_origin` alongside `parameters_used` | `specs/RETRIEVAL.md` §9.4; `plans/02` scope items 8, 10 |
| **D95** | Opt-in `frontmatter: required\|derived` per migration map. `derived` extracts titles from doc macros (`%docTitle`) or first `# H1` and strips `%docResp` / `%docOwnerLineMgr` for privacy; `required` stays the strict default | `plans/60` item 11 |

Also introduced by `5d33d1e` but **not** given D-identifiers: the two-pass
extraction architecture and `G-1`–`G-3` granularity filter
(`specs/INGEST-PIPELINE.md` §5.3), `W1`–`W3` workflow/procedure
disambiguation with deterministic downgrade (`specs/DATA_MODEL.md` §3.1.1),
passive staleness and knowledge-debt metrics (`specs/INGEST-STAGING.md` §7.3.2),
ontological gap patterns (`specs/DISCOVERY.md` §10.2.2), and invariants
**RET-004** (stateless query) / **RET-005** (air-gapped baseline).

---

## 3.1 D96–D98 — reconciliation decisions (2026-09-07)

Taken while repairing defects found by a full read of the seven locked core
specs. Each is a **narrowing or a removal**, not an expansion, so none raises any
epistemic status; all three are recorded here per §5.

| ID | Decision | Lives in | Status |
|---|---|---|---|
| **D96** | `GRAPH-001`'s composite-closure clause cited `SUBCOMPONENT_OF`, `CONTAINS` and `SPECIALIZES`. **None exists** in `relation_registry.yaml` (30 relations) or anywhere else in `specs/`. Per **REL-001** an invariant MUST NOT name relations outside the registry, so the closure set is narrowed to the hierarchical `dag: true` relations that do exist: `PART_OF`, `INSTANCE_OF`, `TYPE_OF`. `SUPERSEDES`, `DEPENDS_ON` and `DERIVED_FROM` are `dag: true` but not hierarchical and remain under per-type detection only. `ONTOLOGY.md` is confirmed as the owning statement of `GRAPH-001`–`003`; `VALIDATION.md` §11 restates for error-code mapping and MUST NOT diverge | `specs/ONTOLOGY.md` §Graph Invariants; `specs/VALIDATION.md` §11; `spec_ownership.yaml` (`GRAPH` owner moved from `GRAPH-INTELLIGENCE.md`, which defines none of them) | **CONFIRMED (Owner sign-off 2026-09-07)**. Mereological containment is fully modeled by `PART_OF` (inverse `HAS_PART`), instantiation by `INSTANCE_OF`, and taxonomic subtyping by `TYPE_OF`. Invariants **REL-001** and **REL-004** forbid adding redundant duplicate or virtual-inverse relations (`CONTAINS`, `SUBCOMPONENT_OF`, `SPECIALIZES`). The hierarchical closure set `{PART_OF, INSTANCE_OF, TYPE_OF}` is definitive. |
| **D97** | `BODY-001` and `BODY-002` were cited in `SCHEMA.md` §7.1 as the authority for byte-preservation and regeneration idempotency but **were never defined anywhere**; the `BODY` series begins at `BODY-003`. The dangling aliases are **removed, not back-filled** — those two rules are already stated normatively by `OWN-002` and `OWN-003`, so minting `BODY-001`/`002` would create two IDs for one rule and breach **ERR-001** | `specs/SCHEMA.md` §7.1 identifier note | Mechanical |
| **D98** | `spec_ownership.yaml` registered 29 families but omitted `RET`, `META`, `LIB`, `SCOPE`, `VAL`, `ERR`, `FS` and the new `G` series, so invariants in the locked core had no owner in the machine-readable projection required by `VALIDATION.md` §10.5 and **CONFORM-001**. All eight are added and `schema_version` moves `0.1.0` → `0.2.0`. Family owners follow the file's existing pattern (the domain document owns its rules; `VALIDATION.md` owns only the validation-native `W`, `ERR`, `FS`, `CONFORM`). Consequently `RET` is owned by `specs/RETRIEVAL.md`, and the `VALIDATION.md` §11 note is corrected from "owning record" to "consolidated register that MUST stay in sync with the owner" | `schemas/registry/spec_ownership.yaml`; `specs/VALIDATION.md` §11 | Mechanical |
| **D99** | `research/sources-and-expanded-literature.md` §F claimed a complete SKOS mapping using `PARENT_OF`, `CHILD_OF`, `RELATED_TO` and `SPECIALIZES`, but only `RELATED_TO` exists in `relation_registry.yaml`. The claim is narrowed: `RELATED_TO` is only a conceptual analogue of SKOS `related`; no complete SKOS-to-registry mapping is normative. No registry relations are added. | `research/sources-and-expanded-literature.md` §F; `schemas/registry/relation_registry.yaml` | Documentation correction |

Also repaired in the same pass, without needing a decision identifier:
**RET-004** contradicted `RETRIEVAL.md`'s own Performance Considerations
("Caching of search results is recommended"), so that bullet is now scoped to
in-process, non-persisted memoization; and the two remaining unmeasured
empirical assertions in the Vector Search subsection (chunk dilution, prose-model
noise on structured content) are re-tagged as design rationale per **SCALE-001**.

**Deliberately not decided here.** `W014` is a *warning*, so "regeneration MUST
fail closed with `W014`" (**BODY-003**) cannot block a CI gate that runs plain
`linter.py` — the CLI exits non-zero only on errors, or on warnings under
`--strict`. Resolving this needs either a new ERROR code from the reserved
`E051`–`E099` range (**ERR-002**, **ERR-003**) or a hard `--strict` requirement
in the gate. Both are design decisions beyond a reconciliation pass; tracked as
an open deviation in `specs/README.md` §7.

---

## 3.2 D100–D101 — Implementation Foundation & Fixture Reconciliation Decisions (2026-09-07)

Taken during the implementation of `plans/01-REPOSITORY-FOUNDATION.md` and preparation for `plans/02-DETERMINISTIC-CORE.md`.

| ID | Decision | Lives in | Status |
|---|---|---|---|
| **D100** | Repository foundation package: Python package `trashheap`, Pydantic v2 typed registry schemas (`extra="ignore"` on extensible source/actor registries for forward compatibility, `extra="forbid"` on Knowledge Object frontmatter), deterministic CLI exit codes (`ExitCode`: 0, 1, 2, 3, 4), and unified `tools/check.sh` validation gate invoking Ruff, pytest, and `trashheap check-registries`. | `trashheap/`, `pyproject.toml`, `plans/01-REPOSITORY-FOUNDATION.md` | Executed & Tested |
| **D101** | Canonical fixture reconciliation strategy: Auditing canonical fixtures against registries revealed legacy divergences (`platform_runtime` domain, `01. Core Platform & Runtime Architecture` taxonomy path, `SUPPORTS` relation type). Foundation gate validates frontmatter YAML structure; Plan 02 will align fixture metadata strictly to canonical registries (`object_registry.yaml`, `taxonomy_registry.yaml`, `relation_registry.yaml`) ensuring zero diagnostic errors in Layer 1–5 validation. | `plans/02-DETERMINISTIC-CORE.md`, `fixtures/canonical/` | Decided |
| **D102** | Canonical Fixture & Directory Layout Reconciliation: Reconciled all 20 canonical fixtures in `fixtures/canonical/` to match registry taxonomy definitions (`TX-ENG-01` -> `"01. Domain & System Architecture"`, `TX-PERS-02` -> `"02. Formal Sciences & Mathematics"`, `TX-PERS-07-04` -> `"07.04. AI-Assisted Software Engineering"`), supplied required `next_review` and `audience: engineer`, corrected relation types to match `relation_registry.yaml`, and relocated directories to match `taxonomy_id_to_directory` (`fixtures/canonical/engineering/01_domain_system_architecture/`, `fixtures/canonical/personal/02_formal_sciences_mathematics/`, `fixtures/canonical/personal/07_computer_science_ai_it_security/07_04_ai_assisted_software_engineering/`) so that the canonical corpus produces zero linter diagnostics. | `fixtures/canonical/`, `plans/02-DETERMINISTIC-CORE.md`, `trashheap/slug.py` | Executed & Verified |
| **D103** | Baseline Hybrid Retrieval & Evidence Bundle Specification: Baseline retrieval (`trashheap.retrieval.HybridRetriever`) implements 8-step pipeline: BM25 Okapi lexical indexing ($k_1=1.5, b=0.75$) with $[0.0, 1.0]$ normalization, BFS graph expansion with §9.2 neighbor key priority, D93 graph modality participation (graph participates in RRF only if `depth > 0` reached; depth 0 reported as absent), RRF fusion ($k=60, w_{\text{bm25}}=0.4, w_{\text{graph}}=0.2$), D82 honest modality reporting (`vector` reported as `null`, not `0.0`), D94 per-parameter precedence (`cli > config > default`) with `parameters_origin` tracking, and §9.3 $K(d)$ epistemic conflict cluster ranking. | `trashheap/retrieval.py`, `specs/RETRIEVAL.md` §9.1–§9.5 | Executed & Tested |
| **D104** | Agent Skills Standard Interface & Invariant Verification: Implemented deterministic Agent Skills generator in `trashheap.skills` and `scripts/generate_agent_skills.py` emitting `.agents/skills/trashheap/SKILL.md` conforming to `agentskills.io` / `dot-agents.com` format with 6 standard slash commands (`/lint`, `/validate`, `/stage-lint`, `/ingest`, `/query`, `/rebuild`). Wired linter rule `E050: GeneratedSkillDriftError` to detect drift when `SKILL.md` diverges bit-for-bit from generator output. | `trashheap/skills.py`, `scripts/generate_agent_skills.py`, `trashheap/linter.py`, `specs/AGENT-SKILLS.md` | Executed & Tested |
| **D105** | Source Ingestion Safety, CSCC & Fencing: Implemented Universal Source intake pipeline (`trashheap.ingest`), enforcing path sandboxing via `sandbox_path` (`AccessDeniedError` / `FR-13`), prompt injection defense via immutable `<untrusted_source>` delimiters (`FR-12`, `NFR-6`) with closing tag escaping (`&lt;/untrusted_source&gt;`), resource limits check (`QuarantineError`), 8-step Crash-safe Source Capture Commit (CSCC §7.1.2) under `raw/sources/<source_id>/representations/<rep_id>/`, idempotency with zero mutation (`RAW-010`), integrity conflict detection (`IntegrityConflictError` / `E141`), 5 executable profiles (`document`, `agent_trajectory`, `thought`, `meeting`, `code_repository`), staging Evidence Unit projection (`EU-...`), and CLI commands `trashheap ingest` and `trashheap stage-lint`. | `trashheap/ingest/`, `tests/test_ingest_safety.py`, `fixtures/adversarial/` | Executed & Tested |
| **D106** | Proposal Review, Approval Binding & DPCP Promotion Protocol: Implemented governed transition from staged material to canonical Knowledge Objects (`trashheap.promotion`), enforcing state model (`pending` -> `in_review` -> `approved` -> `promoted` / `rejected`), immutable transition tracking (`REVIEW-001`), reviewer identity validation against `ACTOR_PATTERN` (`REVIEW-004`), approval binding to exact candidate ID, revision, proposal hash, and source revision (`REVIEW-002`), OS-level advisory locking (`canonical_promotion.lock`), 5-step Durable Promotion Commit Protocol (DPCP §9) via SQLite WAL journal, Layer 1–5 in-memory validation with rollback on failure (`PROMO-004`), atomic publication (`os.replace`), idempotency cache (`PROMO-005`), conflict detection on existing target (`PROMO-006`), crash recovery with orphan sweep (`PROMO-008`), and CLI `review` and `promote` commands. | `trashheap/promotion/`, `tests/test_proposal_promotion.py`, `specs/REVIEW-PROMOTION.md` | Executed & Tested |
| **D107** | Operational Lifecycle, Inode-Safe Cursors, Conformance Projection & Drift Detection: Implemented connectors and adapters (`FileConnector`, `DirectoryConnector`, `DocumentAdapter`, `TrajectoryAdapter`), inode-safe cursor tracking (`CursorStore` with prefix hash check to survive Linux inode recycling / `INGEST-ADAPTERS.md` §3.1), filesystem durability inspection (`inspect_environment` detecting Native POSIX Tier 1 vs WSL2 DrvFs Tier 2 Degraded / §3.2), deterministic TTL-Reaper retention pass (`TTLReaper` expiring pending proposals after TTL, purging tombstones after grace period, strictly protecting approved/canonical objects per §7.3.1), knowledge debt calculation (`calculate_knowledge_debt` / §7.3.2), deterministic conformance projection generator emitting `artifacts/conformance_matrix.yaml` across all 37 invariant families (`CONFORM-001`), status dashboard drift detector (D90) validating `SPEC_STATUS.md` headers, files, and evidence, and measured performance benchmark (`SCALE-001`). Verified by 15 tests in `tests/test_operations_and_ci.py` and validation gate `tools/check.sh`. | `trashheap/operations/`, `tests/test_operations_and_ci.py`, `artifacts/conformance_matrix.yaml` | Executed & Tested |
| **D108** | Opt-In Vector Retrieval, Seam & Honest Modality Enforcement, Multi-Chunk Max-Aggregation Proof, and Degraded Fallback: Implemented `Embedder` protocol, `EmbeddingIdentity`, cosine similarity with 0.0 sign-convention floor (`trashheap/vector/protocol.py`), deterministic test seam `DeterministicDouble` (`trashheap/vector/double.py`) strictly enforcing the Honest Modality Rule (D79, D82) with zero network imports (RET-005). Implemented frontmatter-stripped markdown chunking (`trashheap/vector/chunking.py`), `VectorIndex` with max-over-chunks aggregation ($\max_c \operatorname{cosine}(q, d_c)$ / D81) and passage attribution (`VectorHit.chunk_index`), authentic 100% offline 384-dimensional unit-norm provider `LocalOfflineProvider` (`trashheap/vector/provider.py`, D80), and settled the **SCALE-001** open hypothesis by empirical measurement in `test_multi_chunk_max_aggregation_vs_mean_pooling_proof`. Wired 3-way RRF fusion ($w_{\text{bm25}}=0.4, w_{\text{vector}}=0.4, w_{\text{graph}}=0.2$) in `HybridRetriever` (`trashheap/retrieval.py`), preserving cross-encoder exclusion (`FinalScore == RRF(d)` / D83), transparent degraded fallback (D84), index freshness verification, and CLI flags `--vector` / `--no-vector` in `trashheap query` and `trashheap rebuild`. Verified by 10 tests in `tests/test_vector_retrieval.py` and gate `tools/check.sh`. | `trashheap/vector/`, `trashheap/retrieval.py`, `trashheap/cli.py`, `tests/test_vector_retrieval.py` | Executed & Tested |
| **D109** | Knowledge Bundles & Google Open Knowledge Foundation (OKF) v0.2 Interoperability: Implemented computed bundle selection (`BundleSelector` based on query axes: types, tags, domains, scopes, min_confidence, without frontmatter pollutions per BUNDLE-001 / CANON-004), deterministic SHA-256 selector hashing, atomic directory materialization (`build_bundle`, BUNDLE-002), bit-for-bit deterministic reproducibility (`bundle_fingerprint`, BUNDLE-003), bundle manifest projection (`bundle_manifest.json`, BUNDLE-004), relation closure tracking (`closure_object_ids`, BUNDLE-005), unresolved reference detection and recording (`unresolved_references`, BUNDLE-006), cross-scope security boundary enforcement (`CrossScopeSecurityError` on unauthorized personal scope export, BUNDLE-007), progressive disclosure index generation (`index.md`, BUNDLE-009), declared lossy projections for OKF Concept v0.2 (`export_okf_concept`, preserving unreduced values in `trashheap.*` namespaced block and treating file path as positional projection artifact while preserving stable ID, OKF-001..OKF-004, OKF-011), and permissive consumer import (`import_bundle`, tolerant of unknown types/keys/broken links surfaced as review findings per OKF-008..OKF-010, OKF-012). CLI subcommands `trashheap bundle export` and `trashheap bundle import`. Conformance tested across 35/37 invariant families. | `trashheap/bundle/`, `trashheap/cli.py`, `tests/test_bundles_and_okf.py`, `specs/OKF-INTEROP.md` | Executed & Tested |
| **D110** | Opt-In Graph Intelligence, Lineage-Preserving Manifest, Bounded Topology & Governed Discovery Pipeline: Implemented graph intelligence core (`DELTA-CORE-001`..`007`, `DISC-001`..`005`) under `trashheap/graph/`. Generates deterministic immutable graph manifests (`manifest.json`) recording schema version, aggregate canonical corpus hash, exact tool version, and per-object commit citations (`DELTA-CORE-001`..`003`). Implemented bounded deterministic markdown chunking (200–800 tokens, 10–20% overlap, unicode NFKC normalized, without cross-heading chunking), degree centrality, connected components, and per-scope community partitions. Implemented 4-part derived edge scoring (content semantic, co-occurrence, shared tag, shared taxonomy) strictly bounded by cross-scope firewall (`DELTA-CORE-007`). Implemented autonomous discovery engine for semantic duplicates (`DISC-002`), topological gaps (`DISC-003`), and ontological gaps (unresolved events, unimplemented lessons, unreconciled conflicts; `DISC-004`) with mandatory lineage envelopes and $\le$90 calendar day expiration (`DISC-001`, `DISC-005`). Supported non-destructive graph features ($\phi_1..\phi_6$) for opt-in hybrid retrieval (`--graph-enhanced`) without perturbing baseline RRF ranking. CLI commands `trashheap graph manifest`/`analyze` and `trashheap discover scan`/`list`/`review`/`promote`/`sweep`. Conformance tested across 36/37 invariant families. | `trashheap/graph/`, `trashheap/cli.py`, `trashheap/retrieval.py`, `specs/GRAPH-INTELLIGENCE.md`, `specs/GRAPH-RETRIEVAL.md`, `specs/DISCOVERY.md` | Executed & Tested |
| **D111** | Opt-In Structural Knowledge Graph (SKG), AST Extractor, Blast Radius Traversal & Non-Canonical Bridging: Implemented Structural Knowledge Graph runtime (`SG-001`..`SG-020`) under `trashheap/structural/`. Separated structural graph into its own normative registry `schemas/registry/structural_registry.yaml` defining node types (`FILE`, `MODULE`, `CLASS`, `FUNCTION`, `METHOD`, `SYMBOL`, `ROUTE`, `TEST` / `SG-002`) and edge types (`DEFINES`, `CALLS`, `IMPORTS`, `INHERITS`, `ROUTES_TO`, `TESTS_SYMBOL` / `SG-003`). Implemented deterministic Python AST extractor (`ASTExtractor` / `SG-004`) binding all nodes and edges to git source revision and normalized SHA-256 content hashes (`SG-007`, `SG-008`, `SG-014`). Implemented idempotent incremental indexer (`StructuralGraphIndexer` / `SG-006`) with input invalidation and atomic publication (`SG-009`), reporting coverage and explicit degradation on syntax error without silent drops (`SG-015`, `SG-020`). Implemented bounded blast radius impact analysis (`StructuralGraphAnalyzer` / `SG-010`) with context budget token calculation (`SG-011`). Implemented derived, reviewable bridge relations between Knowledge Objects and structural nodes without mutating canonical files (`BridgeEngine` / `SG-013`). Implemented Layer 7 structural retrieval carrying node ID, file, revision, and line interval in the Evidence Bundle without altering baseline rankings (`StructuralRetriever` / `SG-012`, `SG-018`). Added CLI commands `trashheap structural index|inspect|impact|bridge` (`SG-017`). Achieved 37/37 (100%) conformance tested invariant families across all specifications. | `trashheap/structural/`, `schemas/registry/structural_registry.yaml`, `trashheap/cli.py`, `tests/test_structural_graph.py`, `specs/STRUCTURAL-GRAPH.md` | Executed & Tested |
| **D112** | Legacy Wiki Corpus Migration Engine, Safety Rules 1–11 & Derived Frontmatter Normalization: Implemented Old Wiki Migration engine (`trashheap/migration/`) adhering strictly to Contract Rules 1–11. Implemented exact-byte SHA-256 source hashing over sorted POSIX relative paths (`compute_corpus_hash`, Rule 3); source immutability verification (`source_mutated: false`, Rule 1, 7); fresh-target-only execution with fail-closed rejection on unmanaged non-empty targets (`UnmanagedTargetError`, Rule 2); idempotent reruns and rejection of changed sources without explicit force (`ChangedSourceError`, Rule 2); read-only enrichment proposal emission (`link_proposals.json`, `facet_proposals.json`, Rule 4); explicit quarantine tracking for malformed metadata (`QuarantineRecord`, Rule 5); normalization of singular `source_ref` to `source_refs` array (Rule 6); anti-contamination rule preserving legacy tags for audit (`legacy_tag_audit.json`) while initializing canonical `keywords: []` (Rule 8, Descartes regression fixture); verified-personal vs ambiguous scope enforcement (never silent default to personal, Rule 9); conservative metadata defaults (Rule 10); opt-in `frontmatter: required|derived` mode with title extraction from `%docTitle` / `# H1` and privacy stripping of signum macros (`%docResp`, `%docOwnerLineMgr`) (Rule 11, D95); canonical note naming (`{ko.id}.md`) and taxonomy directory placement producing 0 linter errors across Layers 1–5; and CLI subcommands `trashheap migrate plan` and `trashheap migrate execute`. Verified by 11 tests in `tests/test_migration.py` and validation gate `tools/check.sh` (118 passing tests). | `trashheap/migration/`, `trashheap/cli.py`, `tests/test_migration.py`, `plans/60-OLD-WIKI-MIGRATION.md` | Executed & Tested |

---

## 4. EPI-SPEC-001 sign-off record

`plans/00-ROADMAP.md` §1 permits a post-freeze specification change only with
empirical verification (passing runtime tests on real fixtures) **or** explicit
human sign-off. Empirical verification is unavailable: the repository contains no
runtime and no tests.

| Change | Basis | Signed off by | Date |
|---|---|---|---|
| D79–D95 specification hardening (commit `5d33d1e`) | Explicit human sign-off — **not** empirical verification. The repository owner reviewed the triage of `5d33d1e` and directed that the decisions be kept and reconciled rather than reverted. | Repository owner (`Skelutten` / daniel6651) | 2026-09-07 |
| Withdrawal of the "129 articles / 16,512 pairs; 58% vs 42%" calibration figure as evidence | **SCALE-001** — no benchmark artifact, dataset or reproduction script exists in this repository. Re-tagged as an unmeasured design hypothesis to be settled by the `plans/90` "paraphrase ranking proof" gate. | Qwen (agent), on the owner's remediation instruction | 2026-09-07 |
| D100–D101 Implementation Foundation & Fixture Alignment | Empirical verification: passing tests in `tests/test_registries.py`, `tests/test_smoke.py`, and executable gate `tools/check.sh`. | Skelutten / Antigravity Agent | 2026-09-07 |
| D102–D104 Deterministic Core, Retrieval & Skills Verification | Empirical verification: 41 passing pytest tests across Layers 1–5, atomic rename, section ownership, RRF retrieval, and gate `tools/check.sh`. | Antigravity Agent | 2026-09-07 |
| D105 Source Ingestion Safety, CSCC & Fencing Verification | Empirical verification: 50 passing pytest tests across sandboxing, prompt injection delimiters, CSCC crash safety, idempotency, profile validation, and gate `tools/check.sh`. | Antigravity Agent | 2026-09-07 |
| D106 Proposal Review, Approval Binding & DPCP Promotion Verification | Empirical verification: 57 passing pytest tests across candidate lifecycle, approval binding, DPCP rollback, atomic promotion, crash recovery, and gate `tools/check.sh`. | Antigravity Agent | 2026-09-07 |
| D107 Operational Lifecycle, Conformance Projection & Gate Verification | Empirical verification: 72 passing pytest tests, clean `tools/check.sh` validation gate, and zero-drift `conformance_matrix.yaml`. | Antigravity Agent | 2026-09-07 |
| D108 Opt-In Vector Retrieval, Honest Modality & SCALE-001 Verification | Empirical verification: 10 tests in `tests/test_vector_retrieval.py`, passing SCALE-001 proof, and gate `tools/check.sh` (82 passing tests). | Antigravity Agent | 2026-09-07 |
| D109 Knowledge Bundles & Google OKF v0.2 Interoperability | Empirical verification: 8 tests in `tests/test_bundles_and_okf.py`, clean `tools/check.sh` gate (90 passing tests), 35/37 conformance tested families. | Antigravity Agent | 2026-09-07 |
| D110 Opt-In Graph Intelligence & Discovery Pipeline | Empirical verification: 8 tests in `tests/test_graph_intelligence.py`, clean `tools/check.sh` gate (98 passing tests), 36/37 conformance tested families. | Antigravity Agent | 2026-09-07 |
| D111 Opt-In Structural Knowledge Graph (100% Conformance Gate) | Empirical verification: 9 tests in `tests/test_structural_graph.py`, clean `tools/check.sh` gate (107 passing tests), 37/37 (100%) full conformance across all architecture invariant families. | Antigravity Agent | 2026-09-07 |
| D112 Old Wiki Migration Engine (Rules 1–11) | Empirical verification: 11 tests in `tests/test_migration.py`, clean `tools/check.sh` gate (118 passing tests), zero linter errors on migrated objects. | Antigravity Agent | 2026-09-07 |

This sign-off covers the **decision content** of D79–D95 and runtime foundation D100–D112.

---

## 5. Recording rule (going forward)

1. A new decision MUST be added to §3 (or a new dated section) **in the same
   commit** that first cites its identifier.
2. The next free identifier is **D113**. Do not reuse or backfill gaps in §1.
3. An entry MUST state: the decision, the document that normatively owns it, and
   — if it post-dates the freeze — its EPI-SPEC-001 basis in §4.
4. A decision whose evidence is a measurement MUST cite a repository artifact
   (dataset, script, output file). An uncited number is a hypothesis, per


