# LLM Wiki Specification Status

> **Document ID**: `LLM-WIKI-SPEC-STATUS-001`
> **Version**: `1.3.0`
> **Updated**: `2026-09-07`
> **Status**: `LOCKED` as a status vocabulary and reporting contract
> **Implementation status**: `PARTIAL` — specifications and registries exist; runtime conformance is not established
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

> **Change since the `2026-08-23` assessment.** Commit `5d33d1e` (2026-09-06)
> hardened `RETRIEVAL.md`, `DATA_MODEL.md`, `INGEST-PIPELINE.md`,
> `INGEST-STAGING.md` and `DISCOVERY.md` with decisions D79–D95, and was
> reconciled on 2026-09-07: `RET-004`/`RET-005` are now registered in
> `VALIDATION.md` §11.6, the dangling `G104`/`G107` identifiers were folded into
> the `G-N` series owned by `INGEST-PIPELINE.md` §5.3, `plans/DECISION_LOG.md`
> was restored, and one uncited calibration figure was withdrawn as evidence per
> **SCALE-001**. **No row in §4 changed status.** These are prose and registry
> edits; per `plans/00-ROADMAP.md` §5 and §6 below, no status upgrade may be
> inferred from them. The repository still contains zero runtime code.

| Area | Specification maturity | Implementation status | Evidence in repository |
|---|---|---|---|
| Core Knowledge Object model | `LOCKED` | `UNIMPLEMENTED` / not independently verified | Core contracts and registries are present; no verified runtime linter was found. |
| Base validation and linter | `LOCKED` | `UNIMPLEMENTED` | `VALIDATION.md` specifies `linter.py`, but no `linter.py` was found in the repository. |
| Graph Intelligence | `PROPOSED` | `UNIMPLEMENTED` | Design documents exist; implementation and conformance matrix are not present. |
| Discovery | `PROPOSED` | `UNIMPLEMENTED` | `DISCOVERY.md` exists; no verified discovery runtime was found. |
| Ingestion engine | `DRAFT` | `UNIMPLEMENTED` / design samples only | Ingestion specifications are broad and executable-looking examples exist; runtime, profile validators and recovery conformance are not verified. |
| Universal Source model | `PROPOSED` | `DECLARATIVE_ONLY` / `UNIMPLEMENTED` | `source_registry.yaml`, actor/governance policy and extension contracts exist; source loader, normalizer and validator are not verified. |
| Raw Source Storage and staging | `PROPOSED` | `UNIMPLEMENTED` | Storage layout, CSCC, DSCP/DPCP boundaries and retention rules are specified in `INGEST-STAGING.md`. |
| Structural Knowledge Graph | `PROPOSED` | `UNIMPLEMENTED` | Specification exists; runtime and conformance tests are not verified. |
| OKF interoperability | `PROPOSED` | `UNIMPLEMENTED` | Specification and vendored external material exist; adapter implementation is not verified. |
| Tool integration | `PLAN` | `NOT_APPLICABLE` | Non-normative integration plan. |

### Overall conclusion

The repository is currently a **design-and-registry baseline**, not a
production-verified implementation. The most accurate aggregate description is:

```text
Specification maturity: mixed, from LOCKED core contracts to PROPOSED extensions
Runtime maturity:      UNIMPLEMENTED to DECLARATIVE_ONLY
Conformance maturity:  not established for the complete system
```

---

## 4. Specification dashboard

### 4.1 Core specifications

| Document | Specification status | Implementation status | Normative responsibility |
|---|---|---|---|
| `ARCHITECTURE.md` | `LOCKED` | `UNIMPLEMENTED` | System axioms, canonical/derived boundary and Knowledge Library model |
| `DATA_MODEL.md` | `LOCKED` | `UNIMPLEMENTED` | Knowledge Object types, IDs, facets, scope and domain |
| `ONTOLOGY.md` | `LOCKED` | `UNIMPLEMENTED` | Relations, graph invariants and relation registry ownership |
| `EPISTEMOLOGY.md` | `LOCKED` | `UNIMPLEMENTED` | Epistemic dimensions, provenance and governance boundary |
| `RETRIEVAL.md` | `LOCKED` | `UNIMPLEMENTED` | Baseline hybrid retrieval algorithms and evidence bundles |
| `VALIDATION.md` | `LOCKED` | `UNIMPLEMENTED` | Validation layers, error allocation and conformance rules |
| `SCHEMA.md` | `LOCKED` reader-facing overview | `NOT_APPLICABLE` | Reader-facing schema and templates; normative ownership is delegated where stated |

### 4.2 Extensions and operational specifications

| Document | Specification status | Implementation status | Notes |
|---|---|---|---|
| `GRAPH-INTELLIGENCE.md` | `PROPOSED` | `UNIMPLEMENTED` | Graph intelligence delta; error range `E201–E299` |
| `GRAPH-RETRIEVAL.md` | `PROPOSED` | `UNIMPLEMENTED` | Opt-in graph-enhanced retrieval |
| `DISCOVERY.md` | `PROPOSED` | `UNIMPLEMENTED` | Candidate discovery, clustering and promotion boundary |
| `STRUCTURAL-GRAPH.md` | `PROPOSED` | `UNIMPLEMENTED` | Structural graph extension; error range `E301–E399` |
| `OKF-INTEROP.md` | `PROPOSED` | `UNIMPLEMENTED` | OKF adapter and bundle contracts; error range `E401–E499` |
| `INGEST.md` | `DRAFT` | `UNIMPLEMENTED` | Trajectory ingestion specialization; error range `E101–E199` |
| `INGEST-ADAPTERS.md` | `DRAFT` | `UNIMPLEMENTED` | Connector, adapter, cursor and completion contracts |
| `INGEST-PIPELINE.md` | `DRAFT` | `UNIMPLEMENTED` | Ingestion pipeline and deterministic processing stages |
| `INGEST-STAGING.md` | `DRAFT` | `UNIMPLEMENTED` | Raw Source Storage, staging, CSCC, DSCP/DPCP and retention |
| `INGEST-DATA-MODEL.md` | `DRAFT` | `UNIMPLEMENTED` | Trajectory models plus Universal Source Record addendum |
| `UNIVERSAL-SOURCE-EXTENSION.md` | `PROPOSED` | `DECLARATIVE_ONLY` / `UNIMPLEMENTED` | Source categories, source registry boundary and source impact map |
| `AGENT-SKILLS.md` | `RELEASED` | `UNIMPLEMENTED` | Standardized agent interface (agentskills.io); drift check code `E050` |
| `TOOL-INTEGRATION.md` | `PLAN` | `NOT_APPLICABLE` | Non-normative integration plan |
| `REVIEW-PROMOTION.md` | `DRAFT` | `UNIMPLEMENTED` | Review decisions, deterministic promotion, provenance and recovery contract |

### 4.3 Registries and policy sources

| Registry/policy | Status | Runtime status | Ownership |
|---|---|---|---|
| `object_registry.yaml` | `LOCKED` contract source | `DECLARATIVE_ONLY` | Knowledge Object types and object constraints |
| `facet_registry.yaml` | `LOCKED` contract source | `DECLARATIVE_ONLY` | Facet definitions and allowed values |
| `relation_registry.yaml` | `LOCKED` contract source | `DECLARATIVE_ONLY` | Canonical ontology relations and inverse views |
| `taxonomy_registry.yaml` | `LOCKED` contract source | `DECLARATIVE_ONLY` | Subject taxonomy, hierarchy and scope/path rules |
| `governance_policy.yaml` | `LOCKED` contract source | `DECLARATIVE_ONLY` | Governance, source-scope propagation, privacy and retention policy |
| `source_registry.yaml` | `PROPOSED` Universal Source contract | `DECLARATIVE_ONLY` | Source categories, types, identity/provenance contracts and raw-storage projection |
| `actor_registry.yaml` | `PROPOSED` Universal Source contract | `DECLARATIVE_ONLY` | Minimal Actor namespace, roles and actor identity rules |
| `spec_ownership.yaml` | `DECLARATIVE_ONLY` ownership projection | `DECLARATIVE_ONLY` | One-owner projection for invariant families; runtime parity is not verified |
| `threshold_policy.yaml` | `DECLARATIVE_ONLY` policy projection | `DECLARATIVE_ONLY` | Internal cutoff policy; values are uncalibrated and not performance evidence |

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
  implementation_status: PARTIAL
  assessment_date: 2026-09-07
  conformance_verified: false
  production_verified: false
```

This block describes the dashboard itself. It does not upgrade the status of any
individual specification or runtime component.

**End of LLM Wiki Specification Status v1.3.0**

