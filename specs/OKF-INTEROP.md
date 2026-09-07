# LLM Wiki OKF Interoperability & Bundle Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-OKF-001`
> **Version**: `0.1.0`
> **Updated**: `2026-08-17`
> **Covers**: §16 OKF projection · §17 Knowledge Bundles (distribution units)
> **Source**: Verified against the vendored upstream specification
> `external-specs/okf/SPEC.md` (OKF v0.2, Apache-2.0, sha256 `5a3311d2…`).
> Section references of the form "OKF §N" point into that file
> **Status**: `PROPOSED`
> **Implementation status**: `UNIMPLEMENTED`
> **Compatibility target**: Additive, isolated, opt-in (export/import adapter)
> **Base specification**: v3.8.10 (`ARCHITECTURE.md`, `DATA_MODEL.md`, `ONTOLOGY.md`)
> **Normative owner**: This document owns OKF projection and Knowledge Bundle contracts
> **Related documents**: `ARCHITECTURE.md`, `DATA_MODEL.md`, `ONTOLOGY.md`, `VALIDATION.md`

---

## 16. Open Knowledge Format (OKF) Compatibility & Projection

### 16.1 Purpose

Google Open Knowledge Format (OKF) is a deliberately minimalist
interoperability format: Markdown with YAML frontmatter, Git-compatible and
readable by both humans and agents. LLM Wiki v3.8.10 has a strictly
superordinate model (taxonomy, typed objects, typed relations, epistemology,
governance, provenance, deterministic retrieval).

The relation SHALL be modeled as:

> **OKF is an interoperability substrate. LLM Wiki is a governed
> knowledge architecture on top of that substrate.**

```text
                    LLM Wiki
                       │
             ┌─────────┴─────────┐
             │                   │
       OKF compatibility    Native semantics
       (minimal contract)   (v3.8.10 contract)
             │                   │
       Markdown + YAML       taxonomy / object types
                             typed relations
                             epistemology / governance
                             provenance / retrieval
             │                   │
             └─────────┬─────────┘
                       │
                Derived projections
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        Graph        BM25        Vector
                       │
                       ▼
                   RRF / Rerank
```

This document defines OKF as an **adapter** (cf. `TOOL-INTEGRATION.md`),
not as a competing data model.

### 16.2 What SHALL and SHALL NOT be adopted from OKF

| Idea | Adopted? | Rationale |
|---|---|---|
| Markdown + YAML as canonical source | Yes | Already LLM Wiki's model. |
| Git as distribution mechanism | Yes | Already assumed. |
| Tolerance for unknown fields at the consumer | Yes | Required for forward compatibility (OKF-009). |
| Namespaced extension fields | Yes | Avoids collision with OKF core fields (OKF-004). |
| Progressive disclosure via `index.md` | Yes | See §16.5. |
| Attested Computation | Evaluated | See §16.6, deferred. |
| OKF's untyped link model | **No** | OKF §6.1 links are plain markdown links; LLM Wiki has typed relations (`ONTOLOGY.md` REL-001). |
| Path-as-identity (`Concept ID` = file path) | **No** | OKF §2. Conflicts with `ID-001`; see §16.4.1. |
| Permissive consumer conformance | Yes | OKF §11 forbids rejecting a bundle for unknown types/keys/broken links. Our importer MUST match this. |
| Actor convention for authorship | Yes | Adopted verbatim into `provenance.author`/`reviewer` (**PROV-001**). |
| Deriving trust tiers instead of storing a score | Partly | Adopted as an informative reading; we still store `confidence` (see §16.4.2). |
| OKF as canonical source of truth | **No** | Violates OKF-005. |
| Automatic derivation of ontology on import | **No** | Violates OKF-008. |

### 16.3 Normative Invariants (OKF-001–OKF-012)

| Invariant | Domain | Rule |
|---|---|---|
| **OKF-001** | Export | All LLM Wiki Knowledge Objects SHALL be exportable to a conformant OKF document. |
| **OKF-002** | Identity | OKF export SHALL carry the canonical Knowledge Object ID in `trashheap.id`. The OKF `Concept ID` (the file path, OKF §2) is **positional and unstable** and MUST NOT be treated as the object's identity. |
| **OKF-003** | Provenance | OKF export SHALL preserve provenance, lifecycle, validity and verification information where it is representable. |
| **OKF-004** | Namespace | LLM Wiki extensions SHALL use namespaced frontmatter fields (`trashheap.*`) to avoid collision with OKF fields. |
| **OKF-005** | Authority | The OKF representation MUST NOT become the canonical source of truth. |
| **OKF-006** | Projection | Graph indexes SHALL be rebuildable from canonical Knowledge Objects. |
| **OKF-007** | Loss | Lossy export SHALL be declared explicitly in the export manifest. |
| **OKF-008** | Import | Import of OKF MUST NOT silently invent ontology, epistemology or governance semantics. |
| **OKF-009** | Round-trip | Unknown OKF/extension fields SHALL be preserved where round-trip is supported. |
| **OKF-010** | Determinism | An OKF export SHALL be deterministic for the same object, policy and export version. |
| **OKF-011** | Loss | Every field whose value space is narrower in OKF than in LLM Wiki SHALL be declared in the lossy map of §16.4.2, and the LLM Wiki value SHALL additionally be carried unreduced under `trashheap.*`. |
| **OKF-012** | Import | An importer MUST NOT reject a bundle for unknown `type` values, unknown frontmatter keys, broken cross-links or a missing `index.md` (OKF §11). It SHALL surface them as review findings instead. |

### 16.4 Export form

#### 16.4.1 Identity (OKF-002)

OKF identity is **positional**: OKF §2 defines `Concept ID` as *"the path of the
concept's file within the bundle, with the `.md` suffix removed."* LLM Wiki
identity is a stable opaque ID with the path *derived* from the taxonomy
(**TAX-002**). The two models cannot be unified, so they are kept explicitly apart:

- the stable identity travels in `trashheap.id`;
- the OKF `Concept ID` is a **positional accident** of the taxonomy at export time
  and MUST NOT be persisted anywhere as an identity;
- **retaxonomising a node changes its OKF Concept ID.** Consumers that cached the
  path must re-resolve via `trashheap.id`;
- cross-links SHALL use the bundle-relative absolute form (`/path/to/x.md`), which
  OKF §6.1 recommends precisely because it survives moves within a subdirectory.

#### 16.4.2 Verified field mapping and lossy map

Mapping against the vendored OKF v0.2 spec. "Lossy" means OKF's value space is
narrower, so **OKF-011** requires the unreduced value under `trashheap.*` as well.

| LLM Wiki | OKF v0.2 | Direction | Lossy? |
|---|---|---|---|
| `object_type` | `type` (REQUIRED, non-empty — OKF §11.2) | direct | no — OKF accepts any string |
| `title` | `title` | direct | no |
| `id` | `trashheap.id` (no OKF equivalent) | extension | no |
| `taxonomy_path` / `taxonomy_id` | bundle directory position + `trashheap.taxonomy_id` | derived + extension | **yes** — OKF has no taxonomy contract (§3: "directory structure is independent of the domain") |
| `domain`, `facets.*` | `tags` + `trashheap.*` | flattened + extension | **yes** — `tags` is untyped (OKF §3) |
| `relations[].type` / `.target` | markdown links (OKF §6.1) + `trashheap.relations` | flattened + extension | **yes** — OKF links are untyped |
| `provenance.source_*` | `sources[]` (`resource` REQUIRED, `id`, `title`) | direct | no |
| `provenance.author` | `generated.by` | direct | no — same Actor convention (**PROV-001** ≡ OKF §7) |
| `provenance.last_modified` | `generated.at` | direct | no |
| `provenance.reviewer` + `last_verified` | `verified[].by` + `.at` | direct | no |
| `provenance.confidence` | **no OKF equivalent** → `trashheap.provenance.confidence` | extension | **yes** — see below |
| `epistemology.verification` (5 values) | trust tier derived from `verified` (3 tiers, OKF §5.3) | derived | **yes** — 5 → 3 |
| `epistemology.evidence` / `authority` / `consensus` | **no OKF equivalent** → `trashheap.epistemology.*` | extension | **yes** |
| `status` (4 values) | `status` (`draft \| stable \| deprecated`, OKF §5.4) | mapped | **yes** — 4 → 3 |
| `validity.valid_until` / `next_review` | `stale_after` (OKF §5.5) | mapped | **yes** — two fields → one |
| `schema_version` | `okf_version` in bundle-root `index.md` (OKF §12) | bundle-level | no |

**`status` mapping (4 → 3):**

| LLM Wiki | OKF | Note |
|---|---|---|
| `draft` | `draft` | direct |
| `established` | `stable` | direct |
| `deprecated` | `deprecated` | direct |
| `archived` | `deprecated` | **collision** — `archived` and `deprecated` both become `deprecated`; the distinction survives only in `trashheap.status` |

**On `confidence` (a deliberate divergence).** OKF §5.1 explicitly refuses to store
a credibility score: *"a score is subjective, unportable across consumers, and goes
stale. Credibility is inferred from the signals, not stored."* LLM Wiki mandates
`provenance.confidence` because its retrieval pipeline needs a deterministic
pre-filter threshold (`RETRIEVAL.md` §9.4 `min_confidence`). Both positions are
coherent for their purpose. The resolution: `confidence` is exported **only** under
`trashheap.*`, never as an OKF core field, and an importer MUST NOT synthesise a
`confidence` value from OKF credibility signals — that would violate **OKF-008**.

#### 16.4.3 Worked example

Internal canonical object (extract):

```yaml
id: ENG-FET-BAZEL-0102
object_type: Feature
domain: build_systems
taxonomy_id: TX-ENG-10-01
status: established
author: duckburg-agent/vibe-coder
last_modified: "2026-08-15"
reviewer: human:donald_duck
last_verified: "2026-08-17"
confidence: 0.9
relations:
  - {type: DEPENDS_ON, target: ENG-CMP-BAZEL-0001}
```

OKF projection (`engineering/10_software_construction_build_systems/10.01_build_tooling_target_layout/ENG-FET-BAZEL-0102.md`):

```yaml
---
type: Feature
title: Bazel Remote Cache
tags: [build_systems, bazel, engineering]
status: stable
generated: { by: duckburg-agent/vibe-coder, at: 2026-08-15 }
verified: { by: human:donald_duck, at: 2026-08-17T00:00:00Z }
sources:
  - id: dv-arch-2026-089
    resource: "internal:DV-ARCH-2026-089"
    title: "Duckburg Vibe Build Systems Architecture"

trashheap:
  id: ENG-FET-BAZEL-0102          # stable identity (OKF-002)
  schema_version: "3.8.10"
  taxonomy_id: TX-ENG-10-01
  domain: build_systems
  status: established             # unreduced (OKF-011)
  facets: { toolchain: [bazel], prog_language: [starlark], lifecycle: delivered }
  epistemology: { evidence: observed, verification: peer_verified, authority: authoritative, consensus: accepted }
  provenance: { confidence: 0.9, next_review: "2027-02-17" }
  relations:
    - { type: DEPENDS_ON, target: ENG-CMP-BAZEL-0001 }
---

See the [Bazel toolchain component](/engineering/10_software_construction_build_systems/10.02_dependency_management_toolchains/ENG-CMP-BAZEL-0001.md).
```

The principle: **internal representation ≠ interoperability representation**, and
the difference is declared rather than implied.

### 16.5 Progressive Disclosure

OKF uses `index.md` so that an agent SHALL first be able to understand *what
exists* before it reads the documents. This is a cheap navigation layer before
expensive retrieval:

```text
QUERY
  ▼
INDEX / TAXONOMY DISCOVERY      (billigt: taxonomiregister + objektindex)
  ▼
TARGETED RETRIEVAL              (Layer 7 seed retrieval)
  ▼
GRAPH EXPANSION
  ▼
EVIDENCE BUNDLE
```

- **REC-OKF-01 (recommendation — deliberately outside the normative OKF-001–OKF-010 series)**: A generated
  taxonomy/object index MAY be used as a navigation step before seed retrieval.
  The index is a derived projection and MUST NOT affect the
  `retrieval_mode: canonical` result (`RETRIEVAL.md` RET-002).

### 16.6 Attested Computation (deferred)

OKF v0.2 introduces that a knowledge object can describe *how* a value is to be
computed and *how* the result can be verified (executor + receipt + attester).
It harmonizes with LLM Wiki's ambition of machine verifiability:

```text
Claim
   ├── EVIDENCED_BY ──► Observation
   └── VERIFIED_BY  ──► Experiment
                            ▼
                     Attested Computation
                     ┌──────┴──────┐
                     ▼             ▼
                  Executor      Attester
                     ▼             ▼
                  Receipt       Verdict
```

This is **deferred** in version `0.1.0`. An introduction requires its own
invariants, schema and conformance tests and MUST NOT be approximated with
LLM-generated verification claims.

### 16.7 Comparison matrix (informative)

| Area | LLM Wiki v3.8.10 | OKF v0.2 |
|---|---|---|
| Markdown / YAML / Git | Yes | Yes |
| Taxonomy | Strongly formalized | Minimal |
| Object types | Strict enum | Free |
| Relations | Typed, registry-governed | Mostly untyped |
| Provenance | Strict | Yes |
| Epistemology | Four-dimensional, orthogonal | Trust-oriented |
| Governance | Declarative policy | Lighter |
| Validity | Explicit | Yes |
| Graph | First-class model | Implicit |
| Retrieval / RRF / conflict resolution | Formal | Outside the format |
| Conformance tests | Extensive | Lighter |
| Interoperability | Area for improvement | Core idea |

### 16.8 Error codes

OKF adapter errors are allocated in the reserved range **E401–E499** according to
the error code registry in `VALIDATION.md` §10.3. No codes are allocated in version
`0.1.0`.

---

---

## 17. Knowledge Bundles (Distribution Units)

### 17.1 What a bundle is

OKF §2 defines a Knowledge Bundle as *"a self-contained, hierarchical collection of
knowledge documents. The unit of distribution."* OKF §3 makes it concrete: a bundle
is simply a directory tree of Markdown files, optionally carrying `index.md` and
`log.md`, distributable as a git repository, an archive, or a subdirectory.

A bundle is therefore a **packaging concern**, orthogonal to all four classification
axes. It is not a fifth axis:

| Tempting encoding | Breaks | Why |
|---|---|---|
| a `bundle:` frontmatter field | **CANON-004** | Membership would be hand-maintained, and one object could not belong to two bundles without duplication |
| a `Bundle` object type | axis discipline (`DATA_MODEL.md` §3) | A bundle is not a kind of knowledge; it is a container of knowledge |
| a taxonomy node per bundle | **TAX-009** | Bundles cut across subjects by design — that is their purpose |

The consequence is the central design decision: **bundle membership is computed,
not declared.** A bundle is a saved query over the axes that already exist.

### 17.2 The three parts

| Part | Status | Reuses |
|---|---|---|
| **Selector** — which objects belong | canonical input (an editorial decision) | the Layer 7 pre-filter vocabulary, `RETRIEVAL.md` §9 step 2 |
| **Manifest** — what was produced, from what | derived | `corpus_hash` and policy versioning, `GRAPH-INTELLIGENCE.md` §5 |
| **Materialisation** — the emitted tree | derived | the OKF projection of §16.4 |

Only the selector is canonical. Everything produced from it is a rebuildable
projection (**CANON-002**).

```yaml
# Illustrative bundle shape; the executable artifact is planned, not present.
# bundles/engineering-build-systems.bundle.yaml — canonical recipe example
bundle_id: BND-ENG-BUILD-0001
title: "Duckburg Vibe Build Systems & Toolchain"
schema_version: "1.0.0"

selector:                                  # vocabulary per RETRIEVAL.md §9 step 2
  scope: [engineering]
  taxonomy_id: [TX-ENG-10, TX-ENG-11, TX-ENG-12]
  include_descendants: true                # resolved via parent_id
  object_type: [Article, Document, Principle, Lesson, Component]
  facets:
    toolchain: [bazel, cargo]
  status: [established, deprecated]
  min_confidence: 0.7
  closure:
    relations: [DEPENDS_ON, DOCUMENTED_BY, DEFINES]
    max_depth: 1

projection:
  format: okf                              # okf | native | mkdocs
  audience: [engineer]
  redact_scopes: [personal]
  emit_index: true
```

### 17.3 Where the manifest lives

**OKF has no manifest concept.** A bundle is only a directory tree, so the manifest
is an LLM Wiki extension and MUST NOT be presented as an OKF feature. Two sanctioned
placements:

1. **Inside the bundle** — `trashheap.*` keys in the bundle-root `index.md`
   frontmatter. OKF §12 permits frontmatter there and *only* there among index
   files, and OKF §11 requires consumers to tolerate unknown keys.
2. **Outside the bundle** — a sibling `bundle_manifest.json`, when the bundle must
   remain byte-clean for a strict consumer.

```json
{"bundle_id":"BND-ENG-BUILD-0001","selector_hash":"sha256:…","corpus_hash":"sha256:…",
 "generated_at":"2026-08-17T18:31:22Z","generator":"wiki-okf/0.1.0",
 "root_taxonomy_id":"TX-ENG-10","target_directory":"exports/okf/build_systems/",
 "object_ids":["ENG-CMP-BAZEL-0101","…"],
 "unresolved_references":[{"from":"ENG-CMP-BAZEL-0101","relation":"DEPENDS_ON","target":"ENG-IFC-SDK-0007"}],
 "lossy":{"taxonomy":true,"relations":true,"epistemology":true,"status":true,"confidence":true},
 "generated_at":"2026-08-17T13:00:00Z"}
```

### 17.4 Normative Invariants (BUNDLE-001–BUNDLE-009)

| Invariant | Domain | Rule |
|---|---|---|
| **BUNDLE-001** | Selection | A bundle SHALL be defined by a selector over `scope`, `taxonomy_id`, `object_type`, `domain`, facets, `status`, `confidence` and `validity`. Membership SHALL be computed; it MUST NOT be declared in object frontmatter (**CANON-004**). |
| **BUNDLE-002** | Authority | A bundle SHALL be a derived, rebuildable projection and MUST NOT become a source of truth (**CANON-002**, **OKF-005**). |
| **BUNDLE-003** | Determinism | Identical corpus, selector and exporter version SHALL produce byte-identical output, including file and key ordering (**OKF-010**). |
| **BUNDLE-004** | Manifest | A bundle SHALL carry a manifest recording `bundle_id`, `selector_hash`, `corpus_hash`, resolved `object_ids`, exporter version and `architecture_version` (**CANON-003**). This supersedes the `ExportManifest` sketch in `TOOL-INTEGRATION.md`. |
| **BUNDLE-005** | Closure | Relation closure SHALL be bounded by explicit relation types and `max_depth`. Objects pulled in by closure SHALL be counted separately from selector matches. |
| **BUNDLE-006** | Integrity | A relation whose target falls outside the bundle SHALL be emitted as an unresolved reference and listed in the manifest. It MUST NOT be silently dropped. |
| **BUNDLE-007** | Security | Cross-scope inclusion SHALL be denied by default. Publishing a bundle containing `scope: personal` requires an explicit redaction policy (mirrors **DELTA-CORE-007** / **E207**). |
| **BUNDLE-008** | Loss | Lossy field groups SHALL be declared per bundle in the manifest, consistent with the lossy map in §16.4.2 (**OKF-007**, **OKF-011**). |
| **BUNDLE-009** | Disclosure | A bundle SHOULD emit an `index.md` for progressive disclosure (OKF §8). The index is derived and MUST NOT affect `retrieval_mode: canonical` results (**RET-002**). |

**BUNDLE-006 is the load-bearing one.** Any subset of a graph has dangling edges;
silently dropping them makes a bundle misrepresent the corpus it came from, which is
exactly the failure a self-contained distribution unit must not have. OKF §11 requires
*consumers* to tolerate broken links — it does not license *producers* to create them
without accounting.

### 17.5 Incremental regeneration

A bundle is invalidated by a change to its `corpus_hash`, its `selector_hash`, or the
exporter version. Regeneration reuses the Delta pipeline's existing incremental
machinery (`GRAPH-INTELLIGENCE.md` §12 Phase 2, §12.5): compare input hashes, rebuild
only affected members, publish with temporary-file-then-atomic-rename. This is what
makes a bundle self-updating rather than a stale snapshot.

### 17.6 Scope of this section

Bundles are format-independent: the same selector and manifest serve an MkDocs,
Obsidian or Hugo export (`TOOL-INTEGRATION.md`). They live here because OKF is
currently their only consumer.

**Promotion criterion:** when a second projection format consumes `BUNDLE-*`, this
section SHALL be promoted to a document of its own (working name BUNDLES.md — it does
not exist yet) with its own error-code range, and
`OKF-INTEROP.md` SHALL retain only the OKF-specific projection rules.

## OKF Invariants (summary)

| Invariant | Domain | Error code |
|---|---|---|
| **OKF-001**–**OKF-004** | Export & namespace | E401–E499 (not allocated) |
| **OKF-011**–**OKF-012** | Loss & import tolerance | E401–E499 (not allocated) |
| **OKF-005**–**OKF-007** | Authority & loss | E401–E499 (not allocated) |
| **OKF-008**–**OKF-010** | Import & determinism | E401–E499 (not allocated) |
| **BUNDLE-001**–**BUNDLE-009** | Distribution units (§17) | E401–E499 (not allocated) |

---

**End of LLM Wiki OKF Interoperability Specification v0.1.0**