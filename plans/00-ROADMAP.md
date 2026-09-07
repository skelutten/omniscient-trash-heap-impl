# LLM Wiki Implementation Roadmap

> **Status:** core proving slice complete (Plans 01–05 verified)  
> **Start here:** this is the single sequencing document for runtime work.  
> **Normative owners:** `specs/` and `schemas/registry/`  
> **Current phase:** Core proving slice (Plans 01–05) fully implemented and verified; opt-in extension plans deferred.

---

## 1. Architectural Anti-Loop Invariant

> **Rule (EPI-SPEC-001):** *No amount of review or reasoning iteration can increase the epistemic status of an architectural specification without either empirical verification (passing runtime tests on real fixtures) or explicit human sign-off.*
>
> Specification expansion is now frozen. All effort is channeled into executing the sequenced plans below.
>
> Any post-freeze change MUST record its basis — measurement artifact or named human sign-off — in `plans/DECISION_LOG.md` §4, in the same commit.

---

## 2. The Architectural Proving Slice (Execution Order)

The implementation is executed as a minimal, vertical proving slice designed to test and validate 80% of the architecture's core invariants before any advanced opt-in extensions are introduced.

```text
Phase 0 (Foundation):  Repository + Minimal Registry Loader
Phase 1 (Core):        Canonical Parser + Validator (tested on ~20 real Markdown notes)
Phase 2 (Ingestion):   Untrusted Web/Doc Ingestion (Fencing & Sandboxing) → Immutable Staging
Phase 3 (Promotion):   LLM Candidate Proposal → Human Review → Deterministic Atomic Promotion
Phase 4 (Retrieval):   Disposable Index Rebuild → Baseline Lexical/RRF Retrieval → /query
Phase 5 (Resilience):  Rebuild Invariance & Crash/Recovery Verification
```

### Detailed Sequence Table:

| Order | Plan | Status | Prerequisite | Deliverable & Proof Boundary |
|---:|---|---|---|---|
| **01** | `01-REPOSITORY-FOUNDATION.md` | complete | none | Installable package, minimal YAML registry loader, CLI entry point. |
| **02** | `02-DETERMINISTIC-CORE.md` | complete | 01 green | Canonical frontmatter parser, linter (`E001`–`E099`), Agent Skills emitter (`SKILL.md`), atomic rename. |
| **03** | `03-SOURCE-INGESTION-SAFETY.md` | complete | 02 green | Universal source intake, untrusted web/pdf fencing (`<untrusted_source>`), path sandboxing, SHA-256 hash deduplication. |
| **04** | `04-PROPOSAL-PROMOTION-RECOVERY.md` | complete | 03 green | Candidate proposal extraction, human review approval contract, deterministic atomic promotion (`.tmp` + `os.replace`). |
| **05** | `05-CONNECTORS-OPERATIONS-CI.md` | complete | 04 green | Operational lifecycle, connectors, TTL-reaper, conformance projection, drift detector (D90), clean-checkout CI. |

---

## 3. Opt-in Extensions & Separate Tracks (Deferred)

These tracks are strictly additive and opt-in. They MUST NOT block or complicate the execution of the core proving slice (Plans 01–05).

| Plan | Classification | Status | Relation to Core Proving Slice |
|---|---|---|---|
| `60-OLD-WIKI-MIGRATION.md` | Corpus Migration | deferred | Separate corpus track; requires Plan 02, not an ingestion blocker. |
| `61-BUNDLES-OKF-INTEROP.md` | Standards Interop | deferred | Google OKF v0.2 export/import; requires Plan 02, does not block 03. |
| `90-OPT-IN-VECTOR-RETRIEVAL.md` | Opt-in Retrieval | complete (D108) | Dense embeddings; offline provider, multi-chunk max-aggregation, 3-way RRF. |
| `91-OPT-IN-GRAPH-INTELLIGENCE.md` | Opt-in Intelligence | deferred | Multi-hop community graph synthesis; requires Plan 02 + separate gate. |
| `92-OPT-IN-STRUCTURAL-GRAPH.md` | Opt-in Code Graph | deferred | Tree-sitter / AST graph intelligence for code repositories. |
| `93-OPT-IN-PARQUET-STAGING.md` | Opt-in Analytics | deferred | DuckDB / Parquet analytical staging; requires Plan 03. |
| `99-FUTURE-SCOPE.md` | Deferred Ideas | deferred | Unscheduled concepts; not active work. |

---

## 4. Gate Transition Criteria

A plan is complete ONLY when its runtime files, targeted tests, generated artifacts, and observed gate output exist. Plans and dry-run reports do not upgrade implementation status.

```text
01 Gate: clean install → registry load → registry validation → CLI smoke test
02 Gate: parse → validate → link → lint → generate-skills → author/query (tested on 20 notes)
03 Gate: untrusted input → injection fence & path sandbox → immutable staging → normalized record
04 Gate: candidate → review → approval → deterministic promotion → atomic materialization
05 Gate: clean clone → local gate → rebuild verification → CI-equivalent conformance
```

---

## 5. Status Invariant Rule

Keep runtime statuses `UNIMPLEMENTED` / `DECLARATIVE_ONLY` in `specs/SPEC_STATUS.md` until executable tests pass.
