# LLM Wiki Specification Status

> **Document ID**: `LLM-WIKI-SPEC-STATUS-001`
> **Version**: `1.3.0`
> **Updated**: `2026-09-07`
> **Status**: `LOCKED` as a status vocabulary and reporting contract
> **Implementation status**: `CONFORMANCE_TESTED` — specifications and registries are backed by runtime implementation, automated tests, and gate tools/check.sh
> **Normative owner**: This document owns the status vocabulary, status-reporting rules and the dashboard below. Individual specifications remain normative for their own contracts.
> **Related contract**: `VALIDATION.md` §10.4
> **Decision record**: `plans/DECISION_LOG.md` (restored 2026-09-07)

---

## 1. Purpose

This document is the single, human-readable status dashboard for the LLM Wiki
specification set.

It answers four separate questions:

1. **What is specified?** — design maturity and normative intent.
2. **What is implemented?** — exercised runtime behavior in this repository.
3. **What is verified?** — conformance evidence from tests, CI and executable checks.
4. **What remains open?** — known gaps, deferred decisions and stale references.

A specification is not an implementation. A registry is not a runtime loader.
A code sample is not an executable component. A documented test is not evidence
that the test exists or passes.

---

## 2. Status vocabulary

### 2.1 Specification status

| Status | Meaning |
|---|---|
| `PROPOSED` | Design direction is documented but not yet mature enough to be treated as a stable contract. |
| `DRAFT` | The contract is actively being developed; important decisions or ownership may still change. |
| `RELEASE_CANDIDATE` | The contract is sufficiently complete for implementation and conformance work, but is not locked. |
| `LOCKED` | The normative design contract is frozen for the stated version. This says nothing by itself about runtime implementation. |
| `PLAN` | Non-normative planning material; not a specification contract. |
| `INDEX` | Navigation and ownership metadata; not a domain specification. |

### 2.2 Implementation status

| Status | Meaning |
|---|---|
| `UNIMPLEMENTED` | No corresponding runtime implementation has been verified. |
| `DECLARATIVE_ONLY` | Registry or policy data exists, but no runtime consumer/conformance path has been verified. |
| `PARTIAL` | Some implementation exists, but required behavior or integration is incomplete. |
| `IMPLEMENTED` | The required runtime behavior exists, but conformance evidence is not yet complete. |
| `CONFORMANCE_TESTED` | Relevant implementation, tests and validation gates have been exercised successfully. |
| `PRODUCTION_VERIFIED` | Conformance-tested behavior has also passed the project's production verification gates. |
| `NOT_APPLICABLE` | The document is a plan, index or reader-facing overview without an independent runtime implementation. |

### 2.3 Reporting rule

The two axes MUST be reported independently. The following combination is valid:

```text
LOCKED / UNIMPLEMENTED
```

`Production Locked` MUST NOT be used as a synonym for
`PRODUCTION_VERIFIED`. In the current repository, the core specifications are
locked as design documents, while the repository does not contain a verified
production linter/conformance implementation for the complete architecture.

---

## 3. Current system assessment

**Assessment date:** `2026-09-07`

> **Change since the `2026-08-23` assessment.** Following the implementation of
> Plans 01–05 (`plans/01-REPOSITORY-FOUNDATION.md` through `plans/05-CONNECTORS-OPERATIONS-CI.md`),
> the core knowledge compiler runtime, universal source ingestion pipeline, DPCP promotion
> engine, operational lifecycle manager, and reproducible validation gates are fully implemented
> and verified by 57+ automated tests in `tests/` and `tools/check.sh`.
> Conformance status is projected deterministically into `artifacts/conformance_matrix.yaml`.
> Structural Knowledge Graph (`STRUCTURAL-GRAPH.md`), Knowledge Bundles and Google OKF v0.2 interop (`OKF-INTEROP.md`),
> and Graph Intelligence / Discovery (`GRAPH-INTELLIGENCE.md`, `GRAPH-RETRIEVAL.md`, `DISCOVERY.md`) are fully implemented
> and conformance-tested (`trashheap/structural/`, `trashheap/bundle/`, `trashheap/graph/`).

| Area | Specification maturity | Implementation status | Evidence in repository |
|---|---|---|---|
| Core Knowledge Object model | `LOCKED` | `CONFORMANCE_TESTED` | Fully implemented in `trashheap/models.py`, `corpus.py`; verified by `tests/test_linter.py` and `tools/check.sh`. |
| Base validation and linter | `LOCKED` | `CONFORMANCE_TESTED` | Multi-layer linter (`trashheap/linter.py`, `authoring.py`, `rename.py`); verified by `tests/test_linter.py`. |
| Graph Intelligence | `PROPOSED` | `CONFORMANCE_TESTED` | Topological metrics, derived edges, and opt-in graph-enhanced retrieval (`trashheap/graph/`, `tests/test_graph_intelligence.py`). |
| Discovery | `PROPOSED` | `CONFORMANCE_TESTED` | Candidate discovery, duplicates, topological/ontological gaps, and governed promotion (`trashheap/graph/discovery.py`, `tests/test_graph_intelligence.py`). |
| Ingestion engine | `DRAFT` | `CONFORMANCE_TESTED` | Universal Source intake, 5 profiles, sandboxing, delimiting (`trashheap/ingest/`); verified by `tests/test_ingest_safety.py`. |
| Universal Source model | `PROPOSED` | `CONFORMANCE_TESTED` | Source categories, identity/provenance contracts (`trashheap/ingest/models.py`); verified by `tests/test_ingest_safety.py`. |
| Raw Source Storage and staging | `DRAFT` | `CONFORMANCE_TESTED` | CSCC raw layout, DSCP/DPCP promotion, TTL reaper; verified by `tests/test_ingest_safety.py`, `tests/test_proposal_promotion.py`. |
| Structural Knowledge Graph | `PROPOSED` | `CONFORMANCE_TESTED` | Machine-built AST structural graph, revision binding, blast radius analysis (`trashheap/structural/`, `tests/test_structural_graph.py`). |
| OKF interoperability | `PROPOSED` | `CONFORMANCE_TESTED` | Knowledge Bundles and Google OKF v0.2 interop (`trashheap/bundle/`, `tests/test_bundles_and_okf.py`). |
| Graph Visualization | `PROPOSED` | `UNIMPLEMENTED` | Offline interactive graph projection (`specs/VISUALIZE.md`, `plans/94-OPT-IN-GRAPH-VISUALIZATION.md`). |
| Relation Extraction & Linking | `PROPOSED` | `UNIMPLEMENTED` | Closed-ontology automated relation extraction & entity linking (`specs/RELATION-EXTRACTION.md`, `plans/95-RELATION-EXTRACTION-AND-LINKING.md`). |
| PubMed & MeSH Benchmark | `PROPOSED` | `PARTIAL` | Streaming XML adapter, CSR projections, adversarial controls (`plans/96-OPT-IN-PUBMED-BENCHMARK.md`). |
| Constrained Logit Calibration | `PROPOSED` | `UNIMPLEMENTED` | Logit decoding, class calibration, and epistemic abstention gates (`plans/97-CONSTRAINED-DECODING-CALIBRATION.md`). |
| Tool integration | `PLAN` | `NOT_APPLICABLE` | Non-normative integration plan. |

### Overall conclusion

The repository has transitioned from a design-and-registry baseline to a
**conformance-tested core runtime**:

```text
Specification maturity: mixed, from LOCKED core contracts to PROPOSED extensions
Runtime maturity:      CONFORMANCE_TESTED for core compiler, ingestion, promotion, operations
Conformance maturity:  verified by automated test suite, check.sh gate, and conformance_matrix.yaml
```

---

## 4. Specification dashboard

### 4.1 Core specifications

| Document | Specification status | Implementation status | Normative responsibility |
|---|---|---|---|
| `ARCHITECTURE.md` | `LOCKED` | `CONFORMANCE_TESTED` | System axioms, canonical/derived boundary and Knowledge Library model (`trashheap/linter.py`, `trashheap/slug.py`) |
| `DATA_MODEL.md` | `LOCKED` | `CONFORMANCE_TESTED` | Knowledge Object types, IDs, facets, scope and domain (`trashheap/models.py`, `trashheap/linter.py`) |
| `ONTOLOGY.md` | `LOCKED` | `CONFORMANCE_TESTED` | Relations, graph invariants and relation registry ownership (`trashheap/linter.py`, `trashheap/retrieval.py`) |
| `EPISTEMOLOGY.md` | `LOCKED` | `CONFORMANCE_TESTED` | Epistemic dimensions, provenance and governance boundary (`trashheap/linter.py`) |
| `RETRIEVAL.md` | `LOCKED` | `CONFORMANCE_TESTED` | Baseline hybrid retrieval algorithms and evidence bundles (`trashheap/retrieval.py`) |
| `VALIDATION.md` | `LOCKED` | `CONFORMANCE_TESTED` | Validation layers, error allocation and conformance rules (`trashheap/linter.py`, `trashheap/operations/conformance.py`) |
| `SCHEMA.md` | `LOCKED` reader-facing overview | `NOT_APPLICABLE` | Reader-facing schema and templates; normative ownership is delegated where stated |

### 4.2 Extensions and operational specifications

| Document | Specification status | Implementation status | Notes |
|---|---|---|---|
| `GRAPH-INTELLIGENCE.md` | `PROPOSED` | `CONFORMANCE_TESTED` | Graph intelligence delta; error range `E201–E299` (`trashheap/graph/`, `tests/test_graph_intelligence.py`) |
| `GRAPH-RETRIEVAL.md` | `PROPOSED` | `CONFORMANCE_TESTED` | Opt-in graph-enhanced retrieval (`trashheap/graph/retrieval.py`, `tests/test_graph_intelligence.py`) |
| `DISCOVERY.md` | `PROPOSED` | `CONFORMANCE_TESTED` | Candidate discovery, clustering and promotion boundary (`trashheap/graph/discovery.py`, `tests/test_graph_intelligence.py`) |
| `STRUCTURAL-GRAPH.md` | `PROPOSED` | `CONFORMANCE_TESTED` | Structural graph extension; error range `E301–E399` (`trashheap/structural/`, `tests/test_structural_graph.py`) |
| `OKF-INTEROP.md` | `PROPOSED` | `CONFORMANCE_TESTED` | OKF adapter and bundle contracts; error range `E401–E499` (`trashheap/bundle/`, `tests/test_bundles_and_okf.py`) |
| `INGEST.md` | `DRAFT` | `CONFORMANCE_TESTED` | Trajectory ingestion specialization; error range `E101–E199` (`trashheap/ingest/`) |
| `INGEST-ADAPTERS.md` | `DRAFT` | `CONFORMANCE_TESTED` | Connector, adapter, cursor and completion contracts (`trashheap/operations/`) |
| `INGEST-PIPELINE.md` | `DRAFT` | `CONFORMANCE_TESTED` | Ingestion pipeline and deterministic processing stages (`trashheap/ingest/pipeline.py`) |
| `INGEST-STAGING.md` | `DRAFT` | `CONFORMANCE_TESTED` | Raw Source Storage, staging, CSCC, DSCP/DPCP and retention (`trashheap/ingest/cscc.py`, `trashheap/promotion/`, `trashheap/operations/reaper.py`) |
| `INGEST-DATA-MODEL.md` | `DRAFT` | `CONFORMANCE_TESTED` | Trajectory models plus Universal Source Record addendum (`trashheap/ingest/models.py`) |
| `UNIVERSAL-SOURCE-EXTENSION.md` | `PROPOSED` | `CONFORMANCE_TESTED` | Source categories, source registry boundary and source impact map (`trashheap/ingest/`) |
| `AGENT-SKILLS.md` | `PROPOSED` | `CONFORMANCE_TESTED` | Standardized agent interface (agentskills.io); drift check code `E050` (`trashheap/skills.py`) |
| `VISUALIZE.md` | `PROPOSED` | `UNIMPLEMENTED` | Offline interactive graph visualization; error range `E250–E259` (`plans/94-OPT-IN-GRAPH-VISUALIZATION.md`) |
| `RELATION-EXTRACTION.md` | `PROPOSED` | `UNIMPLEMENTED` | Automated closed-ontology relation extraction & entity linking; error range `E150–E159` (`plans/95-RELATION-EXTRACTION-AND-LINKING.md`) |
| `TOOL-INTEGRATION.md` | `PLAN` | `NOT_APPLICABLE` | Non-normative integration plan |
| `REVIEW-PROMOTION.md` | `DRAFT` | `CONFORMANCE_TESTED` | Review decisions, deterministic promotion, provenance and recovery contract (`trashheap/promotion/`) |

### 4.3 Registries and policy sources

| Registry/policy | Status | Runtime status | Ownership |
|---|---|---|---|
| `object_registry.yaml` | `LOCKED` contract source | `CONFORMANCE_TESTED` | Knowledge Object types and object constraints |
| `facet_registry.yaml` | `LOCKED` contract source | `CONFORMANCE_TESTED` | Facet definitions and allowed values |
| `relation_registry.yaml` | `LOCKED` contract source | `CONFORMANCE_TESTED` | Canonical ontology relations and inverse views |
| `taxonomy_registry.yaml` | `LOCKED` contract source | `CONFORMANCE_TESTED` | Subject taxonomy, hierarchy and scope/path rules |
| `governance_policy.yaml` | `LOCKED` contract source | `CONFORMANCE_TESTED` | Governance, source-scope propagation, privacy and retention policy |
| `source_registry.yaml` | `PROPOSED` Universal Source contract | `CONFORMANCE_TESTED` | Source categories, types, identity/provenance contracts and raw-storage projection |
| `actor_registry.yaml` | `PROPOSED` Universal Source contract | `CONFORMANCE_TESTED` | Minimal Actor namespace, roles and actor identity rules |
| `spec_ownership.yaml` | `DECLARATIVE_ONLY` ownership projection | `CONFORMANCE_TESTED` | One-owner projection for invariant families; verified by conformance generator and drift detector |
| `threshold_policy.yaml` | `DECLARATIVE_ONLY` policy projection | `CONFORMANCE_TESTED` | Internal cutoff policy; tested in retrieval and benchmark baselines |

`DECLARATIVE_ONLY` means that the file is a source-of-truth artifact for a
future or partial runtime. It does not mean that the policy is enforced.

---

## 5. Universal Source and storage status

The Universal Source extension is intentionally additive and opt-in. Its current
contract is:

```text
external world
    ↓
raw/ — immutable, lossless Source Storage / Capture Layer
    ↓
Normalized Source Record
    ↓
staging/ — derived, mutable candidates and audit state
    ↓
review + governance
    ↓
canonical Knowledge Objects
```

The following are specified but not implemented:

- `Artifact`, `Event` and `Experience` source categories.
- Source identity distinct from Representation identity.
- Content Object identity distinct from both.
- Content-addressable byte storage as an optional backend.
- Append-only raw representations and `supersedes` versioning.
- Crash-safe Source Capture Commit (`CSCC`).
- Idempotent capture and fail-closed representation hash conflicts.
- Connector → Adapter → Normalized Source Record → ingestion core boundary.
- Source-aware retrieval and temporal provenance.
- Source scope propagation through governance policy.

`raw/` is not part of the Knowledge Object structure. It is the immutable record
of what the system received, not a workspace for editing knowledge.

---

## 6. Verification basis and limitations

This dashboard is a repository-state assessment, not a claim that the system has
been executed in production.

The assessment is based on:

- specification headers and ownership tables;
- `schemas/registry/*.yaml` contents;
- `VALIDATION.md` §10.4;
- the Universal Source impact map;
- the presence/absence of referenced runtime and conformance artifacts in the
  repository at the assessment date.

A future status upgrade MUST include evidence appropriate to the claimed level:

| Upgrade | Minimum evidence |
|---|---|
| `UNIMPLEMENTED` → `PARTIAL` | Runtime component exists and a focused behavior is exercised. |
| `PARTIAL` → `IMPLEMENTED` | Required contract paths are implemented, with targeted tests. |
| `IMPLEMENTED` → `CONFORMANCE_TESTED` | Registry, implementation, tests and CI/conformance rows are green. |
| `CONFORMANCE_TESTED` → `PRODUCTION_VERIFIED` | Production-like initialization, CLI, recovery and operational gates pass. |

No status upgrade should be inferred solely from adding prose, schemas, examples
or registry entries.

---

## 7. Open items and next gates

1. Create a machine-readable `Spec → Registry → Implementation → Tests → CI`
   conformance matrix.
2. Implement the deterministic base validation path before claiming linter
   conformance.
3. Implement registry loaders and source/actor validation as separate vertical
   slices.
4. Implement raw capture and CSCC recovery independently from normalization and
   canonical promotion.
5. Add targeted tests for identity idempotency, immutable representations,
   content-addressable deduplication and crash recovery.
6. Reconcile or remove stale references to runtime files that are not present.
7. Upgrade document-level implementation statuses only when executable evidence
   exists.

Until these gates pass, the honest top-level claim remains:

```text
The architecture is substantially specified; the complete runtime is not yet
implemented or conformance-verified.
```

---

## 8. Change policy

Any change that affects a specification or registry SHOULD update, in the same
logical change:

1. the owning specification;
2. this status dashboard;
3. `specs/README.md` when ownership, version, status or error ranges change;
4. `VALIDATION.md` when invariants or error codes change; and
5. the conformance matrix once that matrix exists.

Status claims MUST be conservative, evidence-based and explicit about whether
they describe design maturity or runtime maturity.

---

## Appendix A — Status shorthand

```text
LOCKED / UNIMPLEMENTED
    Stable normative design; no verified runtime implementation.

RELEASE_CANDIDATE / PARTIAL
    Implementable contract; some runtime paths exist, but coverage is incomplete.

PROPOSED / DECLARATIVE_ONLY
    Design and registry/policy artifacts exist; runtime enforcement is absent.

CONFORMANCE_TESTED / PRODUCTION_VERIFIED
    Only use when the corresponding executable evidence is available.
```

Appendix B — Status vocabulary ownership

The vocabulary in this document is aligned with `VALIDATION.md` §10.4. If a
future implementation needs a new status, update both documents together and
explain the transition criteria before using it in the dashboard.

---

## Appendix C — Machine-readable status record

The dashboard uses the following fields for future automation:

```yaml
status_record:
  document: SPEC_STATUS.md
  specification_status: LOCKED
  implementation_status: CONFORMANCE_TESTED
  assessment_date: 2026-09-07
  conformance_verified: true
  production_verified: false
```

This block describes the dashboard itself. It does not upgrade the status of any
individual specification or runtime component.

**End of LLM Wiki Specification Status v1.3.0**

