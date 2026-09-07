# Wiki Schema & Knowledge Model

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-SCHEMA-001`
> **Version**: `3.8.10`
> **Updated**: `2026-08-17`
> **Source**: Reader-facing overview; normative owners are named per section
> **Status**: `LOCKED` reader-facing overview
> **Implementation status**: `NOT_APPLICABLE`
> **Compatibility target**: Reader-facing documentation only; normative contracts remain owned by the referenced specifications
> **Scope**: Official schema overview for the LLM Wiki Knowledge Architecture;
> compliant with the modular specification in `specs/` v3.8.10 (see `README.md`)
> **Normative owner**: None for delegated sections; normative owners are named inline and in `README.md`
> **Related documents**: `README.md`, `ARCHITECTURE.md`, `DATA_MODEL.md`, `VALIDATION.md`

---

## 1. The 9 Metadata Categories (META-001)

Every knowledge object frontmatter MUST map fields into exactly one of these nine structural categories:

| Category | Fields |
|---|---|
| **IDENTITY** | `id`, `title`, `schema_version`, `aliases`, `keywords` |
| **ORGANIZATION** | `scope`, `taxonomy_path`, `taxonomy_id` |
| **CLASSIFICATION** | `object_type`, `domain` |
| **FACETS** | `toolchain`, `prog_language`, `language`, `audience`, `architecture`, `lifecycle`, `test_level` |
| **EPISTEMOLOGY** | `evidence`, `verification`, `authority`, `consensus` |
| **PROVENANCE** | `source_type`, `source_refs`, `author`, `last_modified`, `reviewer`, `last_verified`, `next_review`, `confidence` |
| **TEMPORAL** | `validity` (`valid_from`, `valid_until`) |
| **GOVERNANCE** | `status` |
| **ONTOLOGY** | `relations` |

---

## 2. Knowledge Object Model & Object Types

Knowledge is divided into two primary domain layers: **Knowledge World** and **Engineering World**, connected via semantic ontology links.

> **Normative owner:** `specs/DATA_MODEL.md` §3 (object types, allowed scopes,
> mandatory facets, TYPE_CODES, tag strategy) and `schemas/registry/object_registry.yaml`.
> The tables below are a reader-facing summary. On any divergence, `DATA_MODEL.md`
> and the registry win.

### 2.1 Object Types & Allowed Scopes

| `object_type` | Allowed Scopes | Mandatory Classification | Mandatory Facets |
|---|---|---|---|
| **Article** | personal, engineering | `domain` (1..1) | `language` (1..N), `audience` (1..1) |
| **Document** | personal, engineering | `domain` (1..1) | `language` (1..N) |
| **Specification** | engineering | `domain` (1..1) | `toolchain` (1..N), `lifecycle` (1..1), `architecture` (1..N) |
| **Report** | personal, engineering | `domain` (1..1) | — |
| **Concept** | personal, engineering | `domain` (1..1) | `language` (1..N) |
| **Definition** | personal, engineering | `domain` (1..1) | `language` (1..N) |
| **Principle** | personal, engineering | `domain` (1..1) | `language` (1..N) |
| **Claim** | personal, engineering | `domain` (1..1) | — |
| **Product** | engineering | `domain` (1..1) | `lifecycle` (1..1) |
| **Feature** | engineering | `domain` (1..1) | `toolchain` (1..N), `prog_language` (1..N), `lifecycle` (1..1) |
| **Requirement** | engineering | `domain` (1..1) | `lifecycle` (1..1) |
| **Component** | engineering | `domain` (1..1) | `prog_language` (1..N), `toolchain` (1..N), `lifecycle` (1..1) |
| **Sequence** | engineering | `domain` (1..1) | `architecture` (1..N) |
| **WorkPackage** | engineering | `domain` (1..1) | `lifecycle` (1..1) |
| **Interface** | engineering | `domain` (1..1) | `architecture` (1..N) |
| **Protocol** | engineering | `domain` (1..1) | `architecture` (1..N) |
| **Incident** | engineering | `domain` (1..1) | `toolchain` (1..N), `lifecycle` (1..1) |
| **TroubleReport** | engineering | `domain` (1..1) | `toolchain` (1..N), `lifecycle` (1..1) |
| **Experiment** | personal, engineering | `domain` (1..1) | `toolchain` (1..N) |
| **Observation** | personal, engineering | `domain` (1..1) | `toolchain` (1..N) |
| **Lesson** | personal, engineering | `domain` (1..1) | `toolchain` (1..N), `language` (1..N) |
| **Workflow** | personal, engineering | `domain` (1..1) | `toolchain` (1..N), `audience` (1..1) |
| **Procedure** | personal, engineering | `domain` (1..1) | `audience` (1..1) |
| **Checklist** | personal, engineering | `domain` (1..1) | `audience` (1..1) |
| **Skill** | personal, engineering | `domain` (1..1) | `audience` (1..1) |

### 2.2 Facet Cardinality

| Code | Pydantic Type | Rule |
|---|---|---|
| `0..1` | `Optional[Enum] = None` | Optional scalar. At most one value. |
| `1..1` | `Enum` | Mandatory scalar. Exactly one value required. |
| `0..N` | `Optional[List[Enum]] = None` | Optional list. May be omitted. If given, must not be empty. |
| `1..N` | `List[Enum]` | Mandatory list. Must contain at least 1 value. |

### 2.3 Facet Value Sets

Cardinality (which facets are mandatory) is declared per object type in
`object_registry.yaml`. **Legal values** are declared per facet in
`facet_registry.yaml` (**FAC-003** / **E026**).

| Facet | Card. | Value set (see `facet_registry.yaml` for the complete list) |
|---|---|---|
| `toolchain` | `1..N` | `bazel`, `cargo`, `pytest`, `jest`, `docker`, `kubernetes`, `opentelemetry`, `kafka`, … `none` |
| `prog_language` | `1..N` | `c`, `cpp`, `python`, `rust`, `go`, `typescript`, `bash`, `yaml`, … `none` |
| `language` | `1..N` | `en`, `sv` |
| `audience` | `1..1` | `newcomer`, `engineer`, `architect`, `tester`, `integrator`, `operator`, `customer`, `manager`, `agent` |
| `architecture` | `1..N` | `x86_64`, `aarch64`, `baremetal`, `container`, `kubernetes`, `cloud_native`, `serverless`, … `none` |
| `lifecycle` | `1..1` | `planned`, `ongoing`, `delivered`, `maintained`, `legacy`, `withdrawn`, `none` |
| `test_level` | `0..N` | `unit`, `smoke`, `integration`, `e2e`, `performance`, `chaos`, `security`, `none` |

`domain` is **not** a facet — it belongs to CLASSIFICATION and its value set lives
in the `domains` block of `object_registry.yaml` (**CLS-001** / **E027**).

---

## 3. Ontology & Relations

All relations are normatively defined in `relation_registry.yaml`. Every knowledge object may declare `relations` as a list of:

```yaml
relations:
  - type: "REFERENCES"
    target: "PERS-CON-AI-0002"
    soft_link: true
    created_date: "2026-08-01"
```

See `relation_registry.yaml` for the full list of allowed relation types, categories, and source/target type constraints.

---

## 4. Epistemology & Governance

```yaml
# Category 5: EPISTEMOLOGY (orthogonal dimensions from epistemic_registry.yaml)
evidence: observed          # observed | derived | inferred | postulated
verification: peer_verified # formal_proof | peer_verified | self_verified | unverified | falsified
authority: authoritative    # normative | authoritative | informative | advisory | deprecated
consensus: accepted         # accepted | proposed | contested

# Category 8: GOVERNANCE
status: established         # draft | established | deprecated | archived
```

Status/consensus combinations are validated dynamically against `governance_policy.yaml` (GOV-002).

### 4.1 `status` vs `facets.lifecycle` (GOV-001)

The two most easily confused fields in the model. **GOV-001** forbids conflating
them:

| | `status` (GOVERNANCE) | `facets.lifecycle` (FACETS) |
|---|---|---|
| Describes | the **wiki page** | the **system / feature / work item** the page is about |
| Values | `draft`, `established`, `deprecated`, `archived` | `planned`, `ongoing`, `delivered`, `maintained`, `legacy`, `withdrawn` |
| Registry | `governance_policy.yaml` | `facet_registry.yaml` |

A page can be `status: established` (reviewed and trustworthy) while describing a
feature with `lifecycle: planned` (not yet built). Feature progress is therefore a
**facet**, never a taxonomy node and never `status` — see `DATA_MODEL.md` §3.5.

---

## 5. File Path Determinism

The disk path is deterministically computed from the object's `scope` and its
canonical taxonomy node. `taxonomy_path` is a **flat leaf name** that must equal
the registry node's `name`; the directory chain is resolved through `parent_id`
in `taxonomy_registry.yaml` (TAX-007).

> **Normative owner:** `specs/ARCHITECTURE.md` §1.3 holds the single copy of
> `slugify_text`, `normalize_segment`, `ancestor_chain` and
> `taxonomy_id_to_directory`. It is intentionally not duplicated here — a second
> copy has previously drifted out of sync with the registry model.

```text
<scope>/<normalized-ancestor-chain>/<ID>.md
```

Example for `TX-ENG-02`:

```text
engineering/02_event_streaming_ingestion_pipelines/ENG-FET-STREAM-0007.md
```

Violations are reported as **E002** (path/slug mismatch), **E003** (slug
collision) and **E016** (`taxonomy_path`/`scope` diverges from the registry).

---

## 6. ID Convention

- **Format:** `(PERS|ENG)-[A-Z]{2,5}-[A-Z0-9][A-Z0-9_]*-[0-9]{4}`
- **Namespace:** Uniqueness is computed per `(scope, object_type, tag)` with a ceiling of `9999`.
- **TYPE segment:** Must equal `TYPE_CODES[object_type]` (see `object_registry.yaml`).
- **Filename:** The file is named after the ID, not the title slug.

> **Normative owner:** `specs/DATA_MODEL.md` §6 (ID-001–ID-005).

---

### 6.1 Complete Frontmatter Example

All nine categories populated, showing the axis separation in practice:

```yaml
---
# IDENTITY
id: ENG-FET-STREAM-0007
title: "Distributed Stream Ingestion Backpressure Control"
schema_version: "3.8.10"
aliases: ["Stream Backpressure Handling"]
keywords: [stream-engine, ingestion, backpressure, event-loop]

# ORGANIZATION — WHERE in the subject tree
scope: engineering
taxonomy_path: "02. Event Streaming & Ingestion Pipelines"   # flat leaf-name (TAX-007)
taxonomy_id: TX-ENG-02

# CLASSIFICATION — WHAT KIND, WHICH expertise
object_type: Feature
domain: data_pipelines                      # from object_registry.yaml: domains

# FACETS — WHICH properties
toolchain: [bazel, kafka]
prog_language: [cpp, rust]
architecture: [container, kubernetes]
lifecycle: ongoing                          # state of the FEATURE, not of this page
language: [en]

# EPISTEMOLOGY — orthogonal dimensions, never derived from each other
evidence: observed
verification: peer_verified
authority: authoritative
consensus: accepted

# PROVENANCE — who produced it, who confirmed it, how reliable
source_type: internal_document
source_refs: ["DV-ARCH-2026-089", "DV-RFC-2026-0012"]
author: duckburg-agent/vibe-coder   # Actor: who PRODUCED the content
last_modified: "2026-08-15"         # when the content last changed
reviewer: human:donald_duck         # Actor: who CONFIRMED it (nullable for unreviewed drafts per PROV-006)
last_verified: "2026-08-17"         # when it was confirmed (nullable with reviewer per PROV-006)
next_review: "2027-02-17"
confidence: 0.9

# TEMPORAL
validity:
  valid_from: "2026-06-01"
  valid_until: null

# GOVERNANCE — state of THIS PAGE
status: established

# ONTOLOGY — HOW it connects
relations:
  - {type: INTRODUCED_IN, target: ENG-WPK-BUILD-0031}   # which work package delivers it
  - {type: SATISFIES,     target: ENG-REQ-BUILD-0004}
  - {type: AFFECTS,       target: ENG-CMP-BRIDGE-0002}
  - {type: DOCUMENTED_BY, target: ENG-DOC-BUILD-0012}   # its CPI page
---
```

Note what is **not** in the taxonomy: the feature's progress (`lifecycle`), its
programme membership (`INTRODUCED_IN`), its reader, and the fact that it is a
Feature rather than a Lesson. Those are the other three axes.

---

## 7. Article Templates

### Type A: Deep Summary (`object_type: Article` / `Document`)
1. **Source Introduction** — Context, author, purpose.
2. **Core Thesis** — Main argument and paradigm shift.
3. **Central Ideas & Models** — Concepts, frameworks, key quotes.
4. **Application & Methodology** — Practical tools and steps.
5. **Critical Nuance & Limitations** — Counterarguments and boundaries.
6. **Reflection & Contemporary Context** — Relation to other works.
7. **Summary** — Core in 3–5 sentences.

### Type B: Concept Article (`object_type: Concept` / `Definition` / `Principle`)
1. **Introduction & Definition** — Concept description and relevance.
2. **Core Theory & Underlying Models** — Main principles and theoretical frameworks.
3. **Contradictions & Perspectives** — Comparison of different viewpoints.
4. **Practical Application** — Methods and common exercises.
5. **Limitations & Pitfalls** — When the theory does not work.
6. **Cross-References & Synthesis** — How the concept links to other wiki articles.
7. **Summary** — Core in 3–5 sentences.

### Type C: Method Handbook (`object_type: Workflow` / `Procedure` / `Skill` / `Checklist`)
1. **Purpose & Goal** — Objective and expected outcome.
2. **Prerequisites** — Preparation and tool requirements.
3. **Step-by-Step Methodology** — Chronological execution steps.
4. **Best Practices & Tips** — Success factors.
5. **Common Mistakes & Troubleshooting** — Problems and remedies.
6. **Measurability & Evaluation** — KPIs and assessment.
7. **Summary** — Guide in a nutshell.

### Type D: Architectural Sequence (`object_type: Sequence`)
1. **Trigger & Context** — Initiating event, preconditions, protocol context.
2. **Participants** — Components, services, interfaces involved.
3. **Chronological Message Flow** — Numbered sequence of interactions and payload exchanges.
4. **Failure Modes & Fallbacks** — Timeouts, retries, error responses.
5. **Observability & Tracing** — Trace span propagation, metrics to monitor.
6. **Summary** — Sequence flow in 3–5 sentences.

---

## 7.1 Section Ownership Contract (OWN-001–OWN-003, W014)

To prevent automated compilers and daemons from clobbering human knowledge during page updates, Markdown body content is governed by strict section ownership:

```text
┌─────────────────────────────────────────────────────────────┐
│ YAML Frontmatter (Machine Governed & Validated)            │
├─────────────────────────────────────────────────────────────┤
│ ## Summary (Machine / LLM-Owned — Regenerated on Update)    │
│ ...                                                         │
├─────────────────────────────────────────────────────────────┤
│ ## Core Content / Methodology (Human & LLM Co-Authored)     │
│ ...                                                         │
├─────────────────────────────────────────────────────────────┤
│ ## Notes (Human-Owned — Append-Only, Preserved Byte-Verbatim)│
│ ... (Human insights, edge cases, manual observations)       │
├─────────────────────────────────────────────────────────────┤
│ ## Derived Graph References (Machine-Owned — Regenerated)   │
│ ... (Virtual backlinks, community tags, breadcrumbs)        │
└─────────────────────────────────────────────────────────────┘
```

* **OWN-001 (Template Section Ownership):** Headings matching normative Type A–D templates (e.g. `## Summary`, `## Step-by-Step Methodology`, `## Derived Graph References`) are **machine-owned** and regenerated from canonical data on update.
* **OWN-002 (Human Section Preservation):** At most ONE `## Notes` section is permitted per page. It is **human-owned**, append-only, and MUST be preserved byte-for-byte during regeneration. Subheadings or text inside `## Notes` are never parsed as machine templates.
* **OWN-003 (Regeneration Idempotency):** Regenerating an unmodified page with an existing `## Notes` section MUST produce byte-identical file contents.
* **BODY-003 (Section-owned regeneration):** Machine-owned template sections MAY be regenerated, but the compiler MUST preserve the human-owned `## Notes` section byte-for-byte. If a page contains an unrecognized non-Notes section, regeneration MUST fail closed with `E051` (`SectionOwnershipError`) rather than silently overwrite it.
* **BODY-004 (Conflict handling):** If a machine-owned section has been manually edited since the last recorded canonical render, the compiler MUST emit a reviewable conflict and MUST NOT overwrite the section automatically. Promotion of the regenerated version requires an explicit deterministic write decision.
* **W014 (SectionOwnershipViolationWarning):** Static linter warning emitted during read-only inspection if unrecognized template headings appear or if multiple human notes sections are detected.
* **E051 (SectionOwnershipError):** Hard compiler/linter error halting regeneration or promotion if unknown non-Notes sections or duplicate `## Notes` sections are detected, preventing silent data loss.

> **Identifier note (D97 / Deviation 37 resolved).** `BODY-001` and `BODY-002` were formerly cited here
> as the authority for byte-preservation and regeneration idempotency, but **were
> never defined** in this or any other document — the `BODY` series begins at
> `BODY-003`. Those two rules are owned by **OWN-002** and **OWN-003** above.
> Furthermore, "fail closed with `W014`" has been resolved by allocating **`E051`**
> (`VALIDATION.md` §10.3), guaranteeing that unrecognized non-Notes sections
> abort compilation and fail CI with exit code 1.

---

## 8. Build & Validation Pipeline

```bash
# Validate a single file
python3 linter.py path/to/file.md

# Validate entire repository
python3 linter.py .

# Run conformance test suite
python3 -m pytest conformance/
```

---

## 9. Specification Reference

For the production-locked modular specification, see **`specs/README.md`**, which
indexes every specification document, its owning section range and its status.

Core (Production Locked): `ARCHITECTURE.md`, `DATA_MODEL.md`, `ONTOLOGY.md`,
`EPISTEMOLOGY.md`, `RETRIEVAL.md`, `VALIDATION.md`.

Extensions (Proposed / RC): `GRAPH-INTELLIGENCE.md`, `GRAPH-RETRIEVAL.md`,
`DISCOVERY.md`, `STRUCTURAL-GRAPH.md`, `OKF-INTEROP.md`, `INGEST*.md`,
`TOOL-INTEGRATION.md`.

### Registries (`schemas/registry/`)

| Registry | Owns | Invariants |
|---|---|---|
| `object_registry.yaml` | `ObjectTypeEnum`, TYPE_CODES, required facets, `DomainEnum` | ID-002, ID-005, FAC-001, CLS-001 |
| `facet_registry.yaml` | facet **value sets** | FAC-003, FAC-004 |
| `relation_registry.yaml` | `RelationTypeEnum`, source/target constraints | REL-001–REL-008 |
| `taxonomy_registry.yaml` | the subject tree | TAX-001–TAX-009 |
| `governance_policy.yaml` | status/consensus rules | GOV-002 |