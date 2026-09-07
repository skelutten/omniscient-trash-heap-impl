# The Omniscient Trash Heap — Specification Index

> **Project Name**: The Omniscient Trash Heap  
> **Short Name**: Trash Heap  
> **CLI / Package**: `trashheap`  
> **Tagline**: *All the sources. All the wisdom. Some of the trash.*  
> **Part of**: The Omniscient Trash Heap Knowledge Architecture v3.8.10  
> **Document ID**: `LLM-WIKI-SPEC-INDEX-001`  
> **Version**: `3.8.10`  
> **Updated**: `2026-09-07`  
> **Source**: Specification index and ownership map  
> **Status**: `INDEX`  
> **Implementation status**: `NOT_APPLICABLE`  
> **Compatibility target**: Documentation-only; does not alter canonical data or runtime behavior  
> **Normative owner**: This document owns the specification index, ownership map and cross-document status references  
> **Related documents**: `SPEC_STATUS.md`, `VALIDATION.md`

---

## 1. Document Conventions

| Convention | Rule |
|---|---|
| Language | English throughout (specifications, registries and diagrams) |
| File name | Specifications use `UPPERCASE-HYPHEN` + `.md`; registries use `snake_case` + `.yaml` |
| Header | Every specification opens with a blockquote stating `Part of`, unique `Document ID`, optional `Document family ID`, `Source` and `Status` |
| Normative keywords | `MUST` / `MUST NOT` / `SHALL` / `SHOULD` / `MAY` per RFC 2119 usage |
| Single ownership | Where a rule is stated in more than one document, the owning document is named explicitly and wins on divergence |

> **Registry file names are load-bearing.** The specification texts refer
> normatively to `relation_registry.yaml`, `taxonomy_registry.yaml`,
> `object_registry.yaml` and `governance_policy.yaml` under
> `schemas/registry/`. `linter.py`, the `RelationTypeEnum` generation
> (**REL-002**) and the conformance suite read exactly those names. A repository
> MUST NOT contain a second copy or variant of a registry — that would create two
> competing sources of truth and violate **REL-001** / **TAX-001** / **CANON-001**.

## 2. Design Philosophy (summary)

1. **Canonical vs. derived** — Markdown + YAML is the only source of truth; graph,
   indexes, communities and exports are rebuildable projections
   (`ARCHITECTURE.md` §2.2).
2. **Orthogonal axioms** — taxonomy (WHERE), object type (WHAT KIND), domain
   (WHICH AREA OF EXPERTISE), facets (WHICH PROPERTIES) and relations (HOW) are
   never conflated (`ARCHITECTURE.md` §1.1).
3. **Registries as single source of truth** — object types, relations, taxonomy and
   governance are read declaratively from `schemas/registry/`, never hard-coded.
4. **Epistemology is orthogonal** — evidence, verification, authority and consensus
   are never derived from one another and never collapsed into a scalar
   (**EPI-001**).
5. **Determinism before functionality** — every algorithm (slug, RRF, conflict
   ranking, neighbor selection, hashing) is formally specified and machine
   verifiable.
6. **Additive extensions are isolated and opt-in** — an extension may never change
   canonical data, the base linter's error-code contract, or baseline retrieval
   results.
7. **Approval ≠ truth** — governance approval grants *admissibility*, not epistemic
   certainty.

## 3. Core Specification (v3.8.10, Production Locked)

`Production Locked` in this index denotes a locked normative design baseline,
not production-verified runtime implementation. Implementation maturity is
reported separately according to `VALIDATION.md` §10.4; the current repository
contains specification and registry artifacts but no completed runtime
conformance for the Universal Source extension.

| Document | Sections | Ownership |
|---|---|---|
| `ARCHITECTURE.md` | §1–§2, §7 | Axioms, metadata categories, slug algorithm, 7-layer model, canonical/derived, Knowledge Library, taxonomy registry |
| `DATA_MODEL.md` | §3, §6, §8 | Object types, facets & cardinality, ID convention, scope & domain |
| `ONTOLOGY.md` | §4 | Relation registry, categories, DAG/symmetry, graph invariants |
| `EPISTEMOLOGY.md` | §5 | Epistemic dimensions & scales, epistemic ranking, governance policy, provenance (authorship, actor convention), validity |
| `RETRIEVAL.md` | §9 | Hybrid retrieval pipeline, RRF, neighbor selection, conflict clusters, evidence bundle |
| `VALIDATION.md` | §10–§12 | Linter layers, error-code table, **error-code allocation (§10.3)**, system invariants, conformance suite |
| `SCHEMA.md` | — | Reader-facing schema overview and article templates (non-normative where a normative owner is named) |

## 4. Extensions (Proposed / Release Candidate)

| Document | Sections | Status | Error-code range |
|---|---|---|---|
| `GRAPH-INTELLIGENCE.md` | §1–§5.1, §7, §11–§14 | Proposed | `E201`–`E299` |
| `GRAPH-RETRIEVAL.md` | §8–§9 | Proposed (Phase 3+) | — |
| `DISCOVERY.md` | §5.2, §6, §10 | Proposed (Phase 4–5) | — |
| `STRUCTURAL-GRAPH.md` | §15 | Proposed (not implemented) | `E301`–`E399` |
| `OKF-INTEROP.md` | §16–§17 | Proposed (not implemented) | `E401`–`E499` |
| `INGEST.md` | §1–§2, §8, §12 | Draft | `E101`–`E199` |
| `INGEST-ADAPTERS.md` | §3 | Draft | — |
| `INGEST-PIPELINE.md` | §4–§6 | Draft | — |
| `INGEST-STAGING.md` | §7, §9–§10 | Draft | — |
| `INGEST-DATA-MODEL.md` | §11, §13 | Draft | — |
| `TOOL-INTEGRATION.md` | — | Plan (non-normative) | — |
| `REVIEW-PROMOTION.md` | §1–§7 | Draft (unimplemented) | `REVIEW-*`, `PROMO-*` |
| `AGENT-SKILLS.md` | §1–§8 | Released (Normative for Agent Skills) | `E050` |
| `UNIVERSAL-SOURCE-EXTENSION.md` | §1–§15 | Proposed (additive; unimplemented; v0.2.0) | `E130`–`E149` reserved |

> **Canonical Promotion Journal (C3 Decision):** `REVIEW-PROMOTION.md` §4 owns the authoritative, canonical promotion journal (`PROMO-*` state machine: `pending` → `in_review` → `approved` → `promoted` / `failed`) for candidate approval, atomic writes (`.tmp` + `os.replace`), and crash-recovery in the primary Knowledge Library. The DPCP/DSCP staging journal in `INGEST-STAGING.md` §9 is restricted to external ingestion buffering.

The complete non-executable contract example in
`../input-artifacts/END-TO-END-CONTRACT-EXAMPLE.md` is an illustrative input
for review and implementation planning. It does not upgrade implementation or
conformance status and is subordinate to the normative owners above.

**Section numbering:** every document preserves the original section numbering of
its source specification. Numbers are therefore not contiguous within a single
document, and they are **namespaced per document family** — there are three
independent §-series:

| Family | §-series | Documents |
|---|---|---|
| Core specification (v3.8.10) | §1–§12 | `ARCHITECTURE`, `DATA_MODEL`, `ONTOLOGY`, `EPISTEMOLOGY`, `RETRIEVAL`, `VALIDATION` |
| Graph Intelligence Delta | §1–§14 | `GRAPH-INTELLIGENCE`, `GRAPH-RETRIEVAL`, `DISCOVERY` |
| Ingestion Engine | §1–§13 | `INGEST*` |
| New extensions | §15–§16 | `STRUCTURAL-GRAPH`, `OKF-INTEROP` |

Within a family, cross-references (`§9.2`, `§5.1.1`) are stable and MAY be written
without a document name. **Across family boundaries the reference SHALL name the
document** (e.g. "§9.2 of `RETRIEVAL.md`"), because `§9` means Hybrid Retrieval
in the core, graph-enhanced retrieval in the Delta, and DPCP in the ingestion
engine.

## 5. Registries (`schemas/registry/`)

| File | Owning invariants | Read by |
|---|---|---|
| `object_registry.yaml` | **ID-002**, **ID-005**, **FAC-001**, **CLS-001** | Linter Layer 1–3, `DATA_MODEL.md` §3, §8 |
| `facet_registry.yaml` | **FAC-003**, **FAC-004** | Linter Layer 1–3, `DATA_MODEL.md` §3.3 |
| `relation_registry.yaml` | **REL-001**–**REL-008** | Linter Layer 3–4, `ONTOLOGY.md` §4 |
| `taxonomy_registry.yaml` | **TAX-001**–**TAX-009** | Linter Layer 2, `ARCHITECTURE.md` §1.3, §7 |
| `governance_policy.yaml` | **GOV-002**, **SOURCE-012** | Linter Layer 1, `EPISTEMOLOGY.md` §5.4 and source-scope propagation |
| `source_registry.yaml` | **SOURCE-001**–**SOURCE-020**; storage projection **RAW-001**–**RAW-010 | Universal Source Extension, source adapters and future source linter |
| `actor_registry.yaml` | **ACTOR-001**–**ACTOR-006** | Universal Source Extension and future actor validation |
| `threshold_policy.yaml` | **THRESH-002** internal defaults | Retrieval, graph retrieval, discovery and ingestion policy consumers |
| `spec_ownership.yaml` | Ownership projection for invariant families | Future specification/conformance gate |

`source_registry.yaml`, `object_registry.yaml` and `actor_registry.yaml`
are separate namespaces: what entered the system, what canonical knowledge it is,
and who is involved. Source policy metadata never replaces governance/security policy.

The taxonomy classifies **subject only** (**TAX-009**). Object kind, state,
audience and connections live on the other three axes — see `ARCHITECTURE.md` §7.2
for the table of nodes that must *not* be created.

## 6. Source Material (non-normative)

| Path | Kind | Contents |
|---|---|---|
| `research/README.md` | Contract | What belongs in `research/` vs `external-specs/` vs `specs/`; the "do we conform to it?" test |
| `research/GRAPH-RAG-RESEARCH-NOTES.md` | Design notes | Raw discussion of GraphRAG, Graphify, codebase-memory and OKF (Swedish). Derived specifications: `STRUCTURAL-GRAPH.md`, `OKF-INTEROP.md`, `ARCHITECTURE.md` §2.2–§2.3 |
| `research/llm-wiki-pattern-karpathy.md` | Prior art | Provenance record for the underlying wiki pattern: direct derivations, convergent design, deliberate divergences, and the `CANON-005` reconciliation |
| `research/related-implementations.md` | Prior art | graybox, GraphRAG, G-Memory: convergences, divergences, and the source of **CANON-006** |
| `research/critiques-and-community-feedback.md` | Critique | The "compiler not agent" critique and PKM community feedback; source of the measured implementation requirements in `VALIDATION.md` §10.1 and `ONTOLOGY.md` REL-004a |
| `external-specs/okf/` | Vendored external spec | Open Knowledge Format v0.2, pinned and read-only (Apache-2.0). Consumed by `OKF-INTEROP.md`. See `external-specs/README.md` for the vendoring contract |

An **external spec** is a third-party document this project implements against. It is
distinct from an OpenAPI spec, RFC or technical standard that is *wiki content* — that becomes a Knowledge
Object with `object_type: Specification` and an appropriate `source_type`.

## 7. Known Deviations & Open Items

Resolved items are kept with a strikethrough so the history is auditable.

| # | Item | Where |
|---|---|---|
| 1 | ~~`W001`–`W013` are specified but **not implemented**~~ — **resolved**: `W001`–`W015` allocated in `VALIDATION.md` and deferred to Plan 02 | `VALIDATION.md` §10.2 |
| 2 | ~~`conformance_matrix.yaml` is referenced by Delta Phase 1 but does not exist in the repository~~ — **resolved 2026-09-07**: restored baseline matrix from template tracking base vs Delta rows | `conformance_matrix.yaml`; `GRAPH-INTELLIGENCE.md` §12 |
| 3 | ~~`examples/evidence_bundle.json` is referenced but does not exist in the repository~~ — **resolved 2026-09-07**: restored canonical fixture from template matching hybrid RRF shape | `examples/evidence_bundle.json`; `RETRIEVAL.md` §9.5 |
| 4 | `linter.py`, `conformance/` and `scripts/` are referenced as planned implementation targets in Plan 01–02 | several |
| 5 | ~~`TX-PERS-07`/`TX-PERS-11` overlap~~ — **resolved**: merged into `TX-PERS-07` with children `07.01`–`07.04` | `taxonomy_registry.yaml` |
| 6 | ~~`E026`/`E027` (FAC-003, CLS-001) are specified but **not implemented**~~ — **resolved**: `E001`–`E031`, `E050` allocated; implementation targets Plan 02 | `VALIDATION.md` §10.3 |
| 7 | Exception message strings in code samples are normative only through their bracketed error code; the message text itself is not a contract | `INGEST-DATA-MODEL.md` §11 |
| 8 | ~~`INGEST-CORE-015`/`INGEST-CORE-022` shared `E117`~~ — **resolved**: `E125` allocated to `INGEST-CORE-022` | `INGEST.md` §2 |
| 9 | ~~`ONTOLOGY.md` §4.3 duplicated `relation_registry.yaml` inline (253 lines)~~ — **resolved**: replaced with a traversal-properties summary; `source_types`/`target_types` now live only in the registry | `ONTOLOGY.md` §4.3 |
| 10 | ~~`DESCRIBES`/`DOCUMENTED_BY` allowed the same fact four ways~~ — **resolved**: **REL-009** fixes the canonical direction and `E031` provides structural detection | `ONTOLOGY.md` §4.1; `VALIDATION.md` |
| 11 | `TX-ENG-17` (Edge Computing & Network Ingress) and `TX-ENG-18` (Cloud Infrastructure & Multi-Cloud) are intentionally empty growth nodes with boundary guards per **TAX-008** | `taxonomy_registry.yaml` |
| 12 | ~~No object type for a security vulnerability/CVE~~ — **resolved**: modeled via `TroubleReport` + `domain: security` (D10) | `object_registry.yaml` |
| 13 | ~~19 tool pages in the corpus have no natural object_type~~ — **resolved**: modeled via `Component` + `facets.toolchain` (D11) | `object_registry.yaml` |
| 14 | ~~`ExportManifest` was prose-only and non-normative~~ — **resolved**: superseded by **BUNDLE-004**, which defines the manifest contract normatively | `OKF-INTEROP.md` §17.3–§17.4 |
| 15 | Within the `INGEST*` and graph families, bare `§N` references resolve via the system-documents header rather than inline file names | `INGEST*.md` |
| 16 | ~~20 flow pages are protocol message sequences~~ — **resolved**: `Sequence` (`SEQ`) added as an engineering object type in `object_registry.yaml` (D7) | `object_registry.yaml` |
| 17 | ~~`external-specs/okf/PIN.yaml` records `commit: unknown`~~ — **resolved 2026-09-07**: pinned to verified upstream commit `3fcbb9f828c2f23d109c855ee403c3a4c81f3a96` matching vendored `SPEC.md` and `LICENSE.md` hashes | `external-specs/okf/PIN.yaml` |
| 18 | `status` maps 4→3 on OKF export: `archived` and `deprecated` both become `deprecated`. The distinction survives only in `trashheap.status` | `OKF-INTEROP.md` §16.4.2 |
| 19 | OKF deliberately stores no credibility score while Trash Heap mandates `provenance.confidence`; `confidence` is exported only under `trashheap.*` and MUST NOT be synthesised on import | `OKF-INTEROP.md` §16.4.2 |
| 20 | §17 (bundles) is format-independent but lives in the OKF document because OKF is its only consumer. Promote to a separate document (working name BUNDLES.md, not yet created) when a second format consumes `BUNDLE-*` | `OKF-INTEROP.md` §17.6 |
| 21 | ~~**No section-ownership contract.**~~ **Resolved**: `SCHEMA.md` now defines machine-owned sections, byte-preserved human `## Notes`, fail-closed unknown sections and machine-section conflict handling (`OWN-001`–`OWN-003`, `BODY-003`–`BODY-004`, D8) | `SCHEMA.md` §7.1 |
| 22 | ~9,300 lines of specification and registry (7,339 spec + 2,006 registry, measured 2026-09-07), zero lines of implementation. The deterministic core (extract → validate → link → lint) should be built before further specification | deviation 4; `research/critiques-and-community-feedback.md` §2.3 |
| 23 | ~~**Threshold proliferation.**~~ **Resolved**: `threshold_policy.yaml` created as the single normative home for internal cut-offs (`THRESH-002`, D54) | `schemas/registry/threshold_policy.yaml` |
| 24 | Universal Source & Knowledge Compilation Extension v0.2.0 is deferred to post-proving-slice | `UNIVERSAL-SOURCE-EXTENSION.md` |
| 25 | Source taxonomy is a routing/classification projection, not the Knowledge taxonomy; it must not be used for canonical object placement | `UNIVERSAL-SOURCE-EXTENSION.md` §3; `source_registry.yaml` |
| 26 | Specification status and implementation status are separate; core specs may be normatively designed while runtime conformance remains unimplemented | `VALIDATION.md` §10.4 |
| 27 | Storage contract is split between immutable Source Storage/Capture Layer, mutable staging and canonical Knowledge Storage; `raw/` is not a Knowledge Object workspace | `INGEST-STAGING.md` §7.1 |
| 28 | Raw capture has its own crash-safe commit/recovery protocol (CSCC), separate from DSCP/DPCP normalization and promotion commits | `INGEST-STAGING.md` §7.1.2 |
| 29 | The D81 preference for max-over-chunks aggregation over mean-pooling is an **unmeasured hypothesis**. A calibration figure formerly cited in its support (129 articles / 16,512 pairs; 58% vs 42% paraphrase recall) has no benchmark artifact, dataset or reproduction script in this repository and was withdrawn as evidence per **SCALE-001**. To be settled by the `plans/90` "paraphrase ranking proof" gate | `plans/90-OPT-IN-VECTOR-RETRIEVAL.md` Phase V2; `RETRIEVAL.md` §9.1 item 3 |
| 30 | Vector-modality requirements (chunking, frontmatter stripping, modality reporting) live inside the `LOCKED` core `RETRIEVAL.md` although the vector track is excluded from the core sequence by `plans/99-FUTURE-SCOPE.md`. They are now explicitly scope-marked as opt-in-only, but no formal reversal proposal satisfying the §99 six-part reversal condition (fixtures and tests do not exist) has been made | `RETRIEVAL.md` §9.1 items 2–4 and §9.3; `plans/99-FUTURE-SCOPE.md` |
| 31 | ~~**No decision log.**~~ **Partly resolved 2026-09-07**: `plans/DECISION_LOG.md` restored. It is a *reconstruction* from inline citations — the original was deleted in `615e4a4`. Numbering is sparse and D6, D9, D12–D18, D20–D23, D26–D28, D30–D38, D40–D53, D55–D78, D85–D89, D91, D92 are unrecoverable | `plans/DECISION_LOG.md` §1 |
| 32 | `tools/check.sh` is the only executable gate and validates YAML parsing, external-spec pin hashes, cross-registry type consistency and fixture frontmatter. It does **not** validate invariant registration, identifier resolution, ownership parity or any normative prose. A green gate therefore says nothing about deviations 2, 3, 29–31 | `tools/check.sh`; `SPEC_STATUS.md` §7 item 1 |
| 33 | ~~**`GRAPH-001` cited three relations that do not exist**~~ (`SUBCOMPONENT_OF`, `CONTAINS`, `SPECIALIZES`) **and was defined twice with different semantics** — **resolved 2026-09-07 (D96)**: closure set narrowed to the hierarchical `dag: true` relations present in the registry (`PART_OF`, `INSTANCE_OF`, `TYPE_OF`); confirmed by owner; `ONTOLOGY.md` confirmed as owner and `VALIDATION.md` §11 marked as a restatement. Reported as **H4** in `review-outputs/Qwen-02.md:55` | `ONTOLOGY.md` §Graph Invariants; `VALIDATION.md` §11 |
| 34 | ~~**`BODY-001`/`BODY-002` were cited but never defined**~~ — **resolved 2026-09-07 (D97)**: dangling aliases removed; the two rules are owned by `OWN-002`/`OWN-003` and the `BODY` series begins at `BODY-003` | `SCHEMA.md` §7.1 |
| 35 | ~~**`spec_ownership.yaml` omitted eight invariant families**~~ (`RET`, `META`, `LIB`, `SCOPE`, `VAL`, `ERR`, `FS`, `G`), leaving locked-core invariants with no owner in the projection `VALIDATION.md` §10.5 and **CONFORM-001** require — **resolved 2026-09-07 (D98)**, `schema_version` 0.1.0 → 0.2.0. `GRAPH`'s owner also moved from `GRAPH-INTELLIGENCE.md`, which defines none of `GRAPH-001`–`004` | `schemas/registry/spec_ownership.yaml` |
| 36 | ~~**`RET-004` contradicted the same file's Performance Considerations**~~ ("Caching of search results is recommended for frequent queries") — **resolved 2026-09-07**: scoped to in-process, non-persisted memoization; cross-run reuse must go through a rebuildable index carrying **CANON-003** markers | `RETRIEVAL.md` §Performance Considerations |
| 37 | ~~**"Fail closed with `W014`" cannot fail closed**~~ — **resolved 2026-09-07**: allocated `E051: SectionOwnershipError` to `BODY-003` (`VALIDATION.md` §10.3, `SCHEMA.md` §7.1); compilation/regeneration aborts with exit code 1 on unknown non-Notes sections while `W014` remains a read-only linter warning | `SCHEMA.md` §7.1; `VALIDATION.md` §10.2, §10.3, §11.7 |
| 38 | ~~**One rule, two identifiers:** `validity.valid_until` MUST NOT precede `valid_from` is `VALID-001` in `EPISTEMOLOGY.md` and `VAL-001` in `VALIDATION.md`~~ — **resolved 2026-09-07**: standardized on `VAL-001` in `EPISTEMOLOGY.md` and `spec_ownership.yaml`, preserving single ownership (**ERR-001**) | `EPISTEMOLOGY.md` §Provenance Validation Rules; `VALIDATION.md` §10.2; `spec_ownership.yaml` |
| 39 | ~~**`FAC-003`/`E026` is undecidable for `test_level: [unknown]`**~~ — **resolved 2026-09-07**: added `unknown` to `test_level.values` in `facet_registry.yaml` and clarified `FAC-003` in `DATA_MODEL.md`: all values must exist in `values`, `none` requires `allows_none: true`, and `unknown` triggers `W011` | `DATA_MODEL.md` §3.4; `facet_registry.yaml`; `VALIDATION.md` §10.2 |
| 40 | ~~**`CLS-002` is neither decidable nor tested**~~ — **resolved 2026-09-07**: clarified in `DATA_MODEL.md` as architectural schema constraint (`len(domains) < len(taxonomy nodes)`); domains are independent expertises defined in `object_registry.yaml` rather than derived projections of taxonomy root nodes | `DATA_MODEL.md` §8.2; `VALIDATION.md` §11 |
| 41 | ~~The `trashheap` rebrand (`c974513`) is **incomplete**~~ — **resolved 2026-09-07**: updated all remaining `llm_wiki` / `llm-wiki` identifiers across `OKF-INTEROP.md` (`trashheap.*`), `INGEST-STAGING.md`, `INGEST-DATA-MODEL.md`, `INGEST-ADAPTERS.md` (`~/.trashheap/`), and fixtures | `specs/OKF-INTEROP.md`; `specs/INGEST-*.md`; fixtures |

## 8. Open contracts and reference classification

An explicit path or artifact reference MUST be classified as one of:
`required-now`, `planned`, `illustrative`, `external`, or `historical`.
References in normative prose are `required-now` only when the owning
specification says that the artifact is available in the current implementation.
Code samples and example payloads are `illustrative` unless they are explicitly
marked as executable fixtures. Deferred files such as
`conformance_matrix.yaml`, `linter.py`, `structural_registry.yaml` and
`edge_strength_policy.yaml` are `planned` until generated or implemented.

The specification gate MUST distinguish these classes when checking references;
an absent `planned` or `illustrative` artifact is not a broken current dependency.