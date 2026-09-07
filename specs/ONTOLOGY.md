# LLM Wiki Ontology Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-ONTOLOGY-001`
> **Version**: `3.8.10`
> **Updated**: `2026-08-17`
> **Source**: Extracted from `spec.md` §4; relation ownership is delegated to `relation_registry.yaml`
> **Status**: `LOCKED`
> **Implementation status**: `UNIMPLEMENTED`
> **Compatibility target**: Baseline ontology and relation semantics
> **Normative owner**: This document owns ontology invariants; `relation_registry.yaml` owns relation definitions
> **Related documents**: `DATA_MODEL.md`, `ARCHITECTURE.md`, `VALIDATION.md`, `relation_registry.yaml`

---

## 4. Ontology & Normative Relation Registry

All ontology relations are governed normatively by `relation_registry.yaml`.

Source and Actor lineage is not a second Knowledge Object ontology. Logical
Source Graph edges and provenance metadata MAY be projected alongside the
Knowledge Graph, but source types MUST NOT be added to `object_registry.yaml`
or used as canonical object types. Every persisted canonical relation is a
claim and, when derived or asserted from a source, SHOULD carry source,
representation, derivation and verification provenance.

### 4.1 Ontology Axioms

- **Axiom REL-001:** `relation_registry.yaml` constitutes the only source of truth for ontology relations.
- **Axiom REL-002:** `RelationTypeEnum` in source code MUST be deterministically generated from `relation_registry.yaml`.
- **Axiom REL-003:** Every canonical non-symmetric relation MUST declare an `inverse_view` name. Its uniqueness and enforcement are specified normatively by **REL-008** / **E025**.
- **Axiom REL-005:** Every relation MUST define allowed `source_types` and `target_types` (**REL-006** / **E022**). The linter validates these in Layer 2 and raises `InvalidRelationSourceTargetTypeError` (**E021**). All referenced types MUST exist in `ObjectTypeEnum` (**REL-007** / **E023**).
- **Axiom REL-004:** Virtual inverse relations MUST NOT be persisted in YAML source files (**E019**).
- **Axiom REL-009 (canonical direction):** Where two canonical relations express the
  same fact in opposite directions, the **documented object** SHALL declare the
  relation, not the documenting object. Concretely: use
  `Product|Feature|Component|Requirement|Interface|Protocol|Sequence --DOCUMENTED_BY--> Article|Document|Specification|Report`,
  and reserve `DESCRIBES` for the case where the documenting object is the only one
  under authorial control (e.g. an imported document referencing an object that is
  not being edited). Recording the same fact in both directions is a duplicate and
  SHOULD be avoided; it is not currently machine-detectable.

### 4.2 Relation Categories

Relations are grouped into 10 categories with explicit priorities for graph traversal:

| Category | Priority | Description |
|---|---|---|
| structural | 1 | Structural relations (part-whole) |
| dependency | 2 | Dependency relations |
| engineering | 3 | Engineering relations |
| evolution | 4 | Evolution relations (supersedes, etc.) |
| derivation | 5 | Derivation relations |
| verification | 6 | Verification relations |
| epistemic | 7 | Epistemic relations |
| procedural | 8 | Process relations |
| documentation | 9 | Documentation relations |
| semantic | 10 | Semantic relations |

### 4.3 Relation Registry Structure

`relation_registry.yaml` is the **only** source of truth (**REL-001**). This section
does not reproduce it: a second copy of the contract would drift and break REL-001.
The table below is a generated navigation aid listing only the fields needed to
reason about traversal. The authoritative `source_types` / `target_types`
constraints live **exclusively** in the registry.

Field contract per relation:

```yaml
# relation_registry.yaml  (shape only — see the file for all 30 relations)
relations:
  PART_OF:
    category: structural        # one of the 10 categories in §4.2
    inverse_view: HAS_PART      # virtual name; MUST be unique (REL-008)
    dag: true                   # cycle detection applies (GRAPH-001 / E010)
    symmetric: false            # if true, inverse_view equals the relation name
    source_types: [Feature, Component, Requirement, WorkPackage]
    target_types: [Product, Feature, Component, WorkPackage]
```

**All 30 canonical relations** (traversal properties only):

| Relation | Category | `inverse_view` | DAG | Symmetric |
|---|---|---|---:|---:|
| `INSTANCE_OF` | structural | `HAS_INSTANCE` | yes | no |
| `PART_OF` | structural | `HAS_PART` | yes | no |
| `TYPE_OF` | structural | `HAS_TYPE` | yes | no |
| `DEPENDS_ON` | dependency | `REQUIRED_BY` | yes | no |
| `AFFECTS` | engineering | `AFFECTED_BY` | no | no |
| `IMPLEMENTS` | engineering | `IMPLEMENTED_BY` | no | no |
| `PROVIDES` | engineering | `PROVIDED_BY` | no | no |
| `REQUIRES` | engineering | `REQUIRED_FOR` | no | no |
| `SATISFIES` | engineering | `SATISFIED_BY` | no | no |
| `USES` | engineering | `USED_BY` | no | no |
| `INTRODUCED_IN` | evolution | `INTRODUCES` | no | no |
| `SUPERSEDES` | evolution | `REPLACED_BY` | yes | no |
| `DERIVED_FROM` | derivation | `GENERATED` | yes | no |
| `TESTED_BY` | verification | `TESTS` | no | no |
| `VERIFIED_BY` | verification | `VERIFIES` | no | no |
| `CONTRADICTS` | epistemic | `CONTRADICTS` | no | yes |
| `DISPUTED_BY` | epistemic | `DISPUTES` | no | no |
| `EVIDENCED_BY` | epistemic | `EVIDENCES` | no | no |
| `INFERRED_FROM` | epistemic | `INFERS` | no | no |
| `SUPPORTED_BY` | epistemic | `SUPPORTS` | no | no |
| `APPLIES_TO` | procedural | `APPLIED_BY` | no | no |
| `IMPLEMENTED_AS` | procedural | `IMPLEMENTS_PROCEDURE` | no | no |
| `CITES` | documentation | `CITED_BY` | no | no |
| `DEFINES` | documentation | `DEFINED_BY` | no | no |
| `DESCRIBES` | documentation | `DESCRIBED_BY` | no | no |
| `DOCUMENTED_BY` | documentation | `DOCUMENTS` | no | no |
| `REFERENCES` | documentation | `REFERENCED_BY` | no | no |
| `CONTRASTS_WITH` | semantic | `CONTRASTS_WITH` | no | yes |
| `RELATED_TO` | semantic | `RELATED_TO` | no | yes |
| `SIMILAR_TO` | semantic | `SIMILAR_TO` | no | yes |

Counts by category: structural (3), dependency (1), engineering (6), evolution (2), derivation (1), verification (2), epistemic (5), procedural (2), documentation (5), semantic (3).

### 4.3.1 Work Breakdown & Delivery State

Programme structure is carried by relations, never by the taxonomy:

```text
Product ◄── PART_OF ── Feature ◄── PART_OF ── Requirement
   ▲                      │
   │                      └── INTRODUCED_IN ──► WorkPackage ◄── PART_OF ── WorkPackage
   └── PART_OF ── Component ── IMPLEMENTS ──► Feature
```

`PART_OF` is `dag: true`, so a work breakdown gets cycle detection for free
(**GRAPH-001** / **E010**). Progress (`planned`/`ongoing`/`delivered`) is
`facets.lifecycle`, not a relation and not a taxonomy node — see
`DATA_MODEL.md` §3.5.

### 4.4 Relation Properties

| Property | Description | Example |
|---|---|---|
| `category` | The relation's category (1-10) | structural, engineering |
| `inverse_view` | Name of the inverse relation | HAS_PART (inverse of PART_OF) |
| `dag` | Whether the relation should form a DAG | true, false |
| `symmetric` | Whether the relation is symmetric | true, false |
| `source_types` | Allowed source object types | [Feature, Component] |
| `target_types` | Allowed target object types | [Product, Feature] |

### 4.5 Graph Properties

#### DAG vs Non-DAG Relations

- **DAG Relations** (dag: true):
  - Require an acyclic graph
  - Cycle detection is performed by the linter (**GRAPH-001** / **E010**)
  - Example: PART_OF, DEPENDS_ON, SUPERSEDES, DERIVED_FROM

- **Non-DAG Relations** (dag: false):
  - May have cycles
  - No automatic cycle detection
  - Example: IMPLEMENTS, SATISFIES, DESCRIBES

#### Symmetric vs Asymmetric Relations

- **Symmetric** (symmetric: true):
  - If A RELATED_TO B, then B RELATED_TO A
  - No need for inverse_view
  - Example: RELATED_TO, SIMILAR_TO, CONTRASTS_WITH

- **Asymmetric** (symmetric: false):
  - If A PART_OF B, then B HAS_PART A (different relation types)
  - Require inverse_view
  - The majority of relations

### 4.6 Ontology Validation Rules

- **REL-001**: relation_registry.yaml is the only source of truth
- **REL-002**: RelationTypeEnum MUST be generated from the registry
- **REL-003**: Non-symmetric relations MUST have an `inverse_view`; the uniqueness requirement is enforced by REL-008/E025
- **REL-004a** (counting): Graph metrics — degree, orphan status, connectivity —
  SHALL be computed over **persisted canonical edges only**. Counting an
  `inverse_view` as an edge double-counts every relation and, for orphan detection,
  **inverts the verdict**: a page reachable only through inverse views is reported as
  linked when it is in fact an orphan. This failure is silent. Prior art: a published
  wiki compiler reported 0 orphans on a corpus containing 13 because its linter
  counted inbound-link listings as outbound edges
  (`research/critiques-and-community-feedback.md` L1).
- **REL-004**: Virtual inverse relations MUST NOT be persisted
- **REL-005**: Relations MUST satisfy source_types and target_types
- **REL-006**: All relations MUST declare source_types and target_types
- **REL-007**: All types in source_types/target_types MUST exist in ObjectTypeEnum
- **REL-008**: Each **non-symmetric** relation's `inverse_view` MUST be unique. A symmetric relation (`symmetric: true`) MUST set `inverse_view` equal to its own relation name and is exempt from the uniqueness check — without that exemption `E025` would fire on every symmetric relation
- **REL-009**: Where two canonical relations express the same fact in opposite directions, the documented object SHALL declare the relation (`DOCUMENTED_BY`), not the documenting object (`DESCRIBES`)

---

## Graph Invariants

| Invariant | Description | Error code |
|---|---|---|
| **GRAPH-001** | Cycle detection SHALL be executed separately per relation type where `dag: true` is specified, as well as across the composite transitive closure of the hierarchical edges (`PART_OF`, `INSTANCE_OF`, `TYPE_OF`) | E010 |
| **GRAPH-002** | Self-references (target == id) and identical duplicate relations (type, target) SHALL be rejected | E011, E012 |
| **GRAPH-003** | Ontology links without soft_link: true MUST point to an existing object ID in the repository | E009 |

> **GRAPH-001 relation set (D96).** The composite-closure clause formerly cited
> `SUBCOMPONENT_OF`, `CONTAINS` and `SPECIALIZES`. **None of the three exists in
> `relation_registry.yaml`**, which defines exactly 30 relations, and none is
> mentioned anywhere else in `specs/`. Per **REL-001** the registry is the only
> source of truth for relation types, so an invariant MUST NOT name relations
> outside it; the closure set is therefore restricted to the hierarchical
> `dag: true` relations that do exist (`PART_OF`, `INSTANCE_OF`, `TYPE_OF`). The
> remaining three `dag: true` relations (`SUPERSEDES`, `DEPENDS_ON`,
> `DERIVED_FROM`) are not hierarchical and stay under per-type detection only.
> If a genuine containment relation is wanted, it MUST first be added to the
> registry with `source_types`, `target_types` and an `inverse_view`
> (**REL-006**, **REL-003**) and only then cited here. This narrowing is a
> design decision, recorded in `plans/DECISION_LOG.md` §3 as **D96**.
>
> This table is the **owning** statement of `GRAPH-001`–`GRAPH-003`.
> `VALIDATION.md` §11 restates them for the error-code mapping and MUST NOT
> diverge; `GRAPH-004` is stated in `VALIDATION.md` and its threshold record in
> `threshold_policy.yaml` names that document as owner.