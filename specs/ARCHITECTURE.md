# LLM Wiki Architecture Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-ARCHITECTURE-001`
> **Version**: `3.8.10`
> **Updated**: `2026-08-17`
> **Source**: Extracted from `spec.md` §1–2, §7; extended by current modular specs
> **Status**: `LOCKED`
> **Implementation status**: `UNIMPLEMENTED`
> **Compatibility target**: Baseline canonical architecture; additive extensions opt-in
> **Normative owner**: This document owns architecture axioms, canonical/derived boundaries, the Knowledge Library model and architecture-level storage semantics
> **Related documents**: `DATA_MODEL.md`, `ONTOLOGY.md`, `EPISTEMOLOGY.md`, `UNIVERSAL-SOURCE-EXTENSION.md`

---

## 1. Purpose, Core Principles & Metadata Categorization

This document constitutes the architecture specification for an LLM-driven Wiki / Second Brain. The system handles both a broad personal knowledge base (`scope: personal`) and a deep software and platform engineering domain for Duckburg Vibe Inc (`scope: engineering`).

### 1.1 The Five Central Axioms

To prevent taxonomy, object type, domain, facets or relations from becoming overloaded or conflated, five inviolable principles apply:

- **Taxonomy** answers **WHERE IN THE TREE** the knowledge is organized (hierarchical topic structure). A foreign-source taxonomy mapping is only an exact classification when the complete source meaning is preserved; otherwise it is a provisional/lossy migration mapping.
- **Object Type** answers **WHAT KIND** of Knowledge Object it is (information, semantic, domain entity, event, procedure).
- **Domain** answers **WHICH AREA OF EXPERTISE** the knowledge belongs to (orthogonal domain classification at the object level).
- **Facets** answer **WHICH PROPERTIES** the object has (toolchain, programming language, audience, architecture).
- **Relations** answer **HOW** the object relates semantically, structurally, epistemically, procedurally or in an engineering sense to other Knowledge Objects.

### 1.2 The 9 Metadata Categories in Frontmatter

All metadata is sorted into nine strict structural categories. Each frontmatter field belongs to exactly one category (**META-001**):

- **IDENTITY:** `id`, `title`, `schema_version`, `aliases`, `keywords`
- **ORGANIZATION:** `scope`, `taxonomy_path`, `taxonomy_id`
- **CLASSIFICATION:** `object_type`, `domain`
- **FACETS:** `toolchain`, `prog_language`, `language`, `audience`, `architecture`, `lifecycle`, `test_level`
- **EPISTEMOLOGY:** `evidence`, `verification`, `authority`, `consensus`
- **PROVENANCE:** `source_type`, `source_refs`, `author`, `last_modified`, `reviewer`, `last_verified`, `next_review`, `confidence`
- **TEMPORAL:** `validity` (`valid_from`, `valid_until`)
- **GOVERNANCE:** `status`
- **ONTOLOGY:** `relations`

> **Storage Shape Contract (C5 Decision):** Frontmatter fields are flat top-level keys in canonical Markdown files (`evidence: observed`, `verification: peer_verified`). Dotted notation in staging/ingestion specifications (`epistemology.verification`) denotes logical attribute paths or extraction mapping targets, never nested YAML dictionaries in storage.

### 1.3 Formal Slug Algorithm & Path Validation

The disk path is computed deterministically from the canonical registry node's name in
`taxonomy_path` and `scope`. `taxonomy_path` is a single flat leaf-name value and
MUST be identical to the `name` of the corresponding node in `taxonomy_registry.yaml`;
the hierarchy is represented by `parent_id` in the registry, not by slash-separated
breadcrumbs in the frontmatter (**TAX-007**).

The directory chain is therefore built by resolving `parent_id` from the leaf node to
the root and normalizing each node name individually:

```python
import re
import unicodedata

SEGMENT_RE = re.compile(r"^(?P<prefix>\d+(?:\.\d+)*\.?)\s*(?P<text>.*)$")

def ascii_fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")

def slugify_text(text: str) -> str:
    text = ascii_fold(text).lower()
    text = re.sub(r"[&/,\-()]+", "_", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")

def normalize_segment(segment: str) -> str:
    segment = segment.strip()
    match = SEGMENT_RE.match(segment)
    if match:
        prefix = match.group("prefix").rstrip(".")
        text = slugify_text(match.group("text"))
        if text:
            return f"{prefix}_{text}"
        return prefix
    return slugify_text(segment)

def ancestor_chain(registry: dict, taxonomy_id: str) -> list[str]:
    """Leaf -> root -> reversed; deterministic and acyclic (TAX-006 / E024)."""
    chain, seen, current = [], set(), taxonomy_id
    while current is not None:
        if current in seen:
            raise TaxonomyCycleError(current)          # E024
        seen.add(current)
        node = registry[current]                       # missing leaf -> E017; missing parent -> E018
        chain.append(node["name"])
        current = node["parent_id"]
    return list(reversed(chain))

def taxonomy_id_to_directory(registry: dict, scope: str, taxonomy_id: str) -> str:
    node = registry[taxonomy_id]
    if node["scope"] != scope:
        raise TaxonomyIdMismatchError(taxonomy_id)     # E016
    normalized = [normalize_segment(name)
                  for name in ancestor_chain(registry, taxonomy_id)]
    return f"{scope}/" + "/".join(normalized) + "/"
```

### 1.4 Universal Source boundary

The canonical architecture recognizes the Universal Source extension as an additive boundary above the baseline Knowledge Object compiler:

```text
SOURCE
 ├── Artifact
 ├── Event
 └── Experience
        ↓
      INGEST → DISCOVERY → STAGING → KNOWLEDGE OBJECTS
```

`AgentTrajectory` is a specialized Event source, not the general ingestion abstraction. The full Artifact/Event/Experience and Source-versus-Representation contract is owned by `UNIVERSAL-SOURCE-EXTENSION.md`; this architecture section only fixes the top-level boundary.

**Validation rules:**
- The linter (`linter.py`) raises `PathScopeMismatchError` (**E002**) if the file's disk path deviates from the computed path
- `TaxonomySlugCollisionError` (**E003**) if two `taxonomy_path` strings within the same scope generate the same disk path (**TAX-003**)
- `TaxonomyIdMismatchError` (**E016**) if `taxonomy_path` or `scope` deviates from the registry node's `name` respectively `scope` (**TAX-004**)

---

## 2. Architecture (7 Layers)

The system's data flow and structure is divided into seven isolated layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           1. INFORMATION MODEL                          │
│     Knowledge Objects (Information, Semantic, Domain, Events, Procedural)│
├─────────────────────────────────────────────────────────────────────────┤
│                        2. INFORMATION ORGANIZATION                      │
│     Taxonomy (Dual-Tree & Registry) • Facets (Multi-Valued Arrays)       │
├─────────────────────────────────────────────────────────────────────────┤
│                          3. KNOWLEDGE SEMANTICS                         │
│     Ontology  •  Canonical Binary Relations  •  Relation Registry       │
├─────────────────────────────────────────────────────────────────────────┤
│                          4. KNOWLEDGE EPISTEMOLOGY                      │
│     Evidence  •  Verification  •  Authority  •  Consensus  • Confidence │
├─────────────────────────────────────────────────────────────────────────┤
│                        5. LIFECYCLE & GOVERNANCE                        │
│     Operative Status  •  Domain Lifecycle  • Validity  • Governance Policy│
├─────────────────────────────────────────────────────────────────────────┤
│                            6. KNOWLEDGE GRAPH                           │
│     Typed Subgraph Traversals  •  Selective Relation-Level DAG Checks   │
├─────────────────────────────────────────────────────────────────────────┤
│                           7. HYBRID RETRIEVAL                           │
│     Seed Retrieval • Graph Expansion • Epistemic Ranking • Reranking     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Layer Descriptions

**Layer 1 - Information Model:**
- Defines the types and structure of Knowledge Objects
- Divides knowledge into Information, Semantic, Domain, Events, Procedural

**Layer 2 - Information Organization:**
- Hierarchical taxonomy (Dual-Tree per scope)
- Multi-valued facets for classification

**Layer 3 - Knowledge Semantics:**
- Ontology with canonical binary relations
- Relation Registry as single source of truth

**Layer 4 - Knowledge Epistemology:**
- Epistemic dimensions: evidence, verification, authority, consensus (**EPI-001**: orthogonal, never collapsed)
- Epistemic ranking and conflict resolution (**EPI-003**)
- Note: `confidence` belongs to PROVENANCE (§1.2), not to the epistemic dimensions

**Layer 5 - Lifecycle & Governance:**
- Operative status (draft, established, deprecated, archived)
- Domain-specific lifecycle
- Time-based validity

**Layer 6 - Knowledge Graph:**
- Typed subgraph traversals
- Selective DAG checks per relation type

**Layer 7 - Hybrid Retrieval:**
- Seed retrieval (BM25 + Vector + ID lookup)
- Graph expansion via BFS
- Epistemic ranking and reranking

### 2.2 Canonical Knowledge / Derived Knowledge Principle

All external and internally captured information enters through the Universal
Source Model. The canonical/derived distinction has a preceding evidential
boundary:

```text
external world → immutable raw Source Representation → normalized Source Record
               → discovery/evidence → governed canonical Knowledge Object
```

Raw capture is append-only and is not itself canonical knowledge. Source
identity, representation identity and content identity MUST remain distinct.

Markdown and YAML are the system's **only** source of truth. Everything else —
graph database, indexes, communities, retrieval metadata, exports — is a
**rebuildable projection**:

```text
Markdown + YAML
      │  canonical source of truth
      ▼
Knowledge Objects
      │
      ├──► Taxonomy projection (directories)
      ├──► Ontology / graph projection
      ├──► BM25-index
      ├──► Vektorindex
      ├──► Retrieval-metadata
      └──► Agent-facing export (e.g. OKF)
```

- **CANON-001**: Canonical Knowledge Objects in `personal/` and `engineering/` as well as the
  normative registries in `schemas/registry/` constitute the source of truth.
- **CANON-002**: Every derived artifact SHALL be fully rebuildable from
  the canonical objects. A graph database MUST NOT become the real database.
- **CANON-003**: A derived artifact SHALL carry `corpus_hash`, algorithm and
  policy version so that it can be invalidated deterministically
  (`GRAPH-INTELLIGENCE.md` §5).
- **CANON-004**: Derived data MUST NOT be written into a Knowledge Object's
  frontmatter.
- **CANON-006**: **The LLM reasons; deterministic code writes.** All structural
  operations — creating and placing files, computing slugs and IDs, maintaining
  relations and inverse views, merging, indexing, hashing — SHALL be performed by
  deterministic code. An LLM MAY propose content and classifications; it MUST NOT be
  the component that performs the write. This makes behaviour auditable and
  reproducible across runs, and it is what allows the same corpus to compile to the
  same output twice (**RET-002**). It generalises the extraction capability firewall
  (**INGEST-CORE-018** / E120) and the derived-pipeline restriction
  (**DELTA-CORE-001**) into a system-wide rule.
- **CANON-005**: Two distinct senses of "source of truth" MUST NOT be conflated:
  - **evidential** — raw sources are what claims are traced back to
    (`provenance.source_refs`). They are immutable and are never rewritten by the
    system.
  - **architectural** — canonical Knowledge Objects and the registries are what every
    derived artifact is rebuilt from (**CANON-002**).

  A derived index, graph or bundle SHALL be rebuilt from the **canonical objects**,
  never directly from raw sources; doing the latter would bypass review and
  governance. Conversely a canonical object SHALL cite its raw source rather than
  claim to be the origin of the knowledge.

### 2.3 Knowledge Library (Logical Layer)

The folder hierarchy is a **projection** of the knowledge organization, not
the knowledge model. When the corpus grows, the file system would otherwise take on the role of
knowledge graph, which breaks the axioms in §1.1.

```text
                 KNOWLEDGE OBJECT
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Taxonomy       Ontology       Facets
        ▼              ▼              ▼
     directories      graph        filters
```

- **LIB-001**: A Knowledge Library is defined as *typed Knowledge Objects +
  indexes + relations + policies*, not as a folder tree.
- **LIB-002**: The file system is a physical persistence and
  distribution representation; the directory structure MUST NOT carry semantics that are not
  also present in `taxonomy_registry.yaml`.

### 2.4 Measured scale transitions and derived-state safety

The file-based baseline MUST be measured before any scale transition is
approved. A measurement record MUST identify corpus shape, workload, hardware
and filesystem tier, tool/pipeline versions, measurement window, and the
observed values for scan/rebuild duration, derived-view freshness lag, storage
growth, proposal inflow and review latency. No threshold in this section is a
performance claim; thresholds MUST be selected from those measurements and
recorded as versioned deployment policy.

A transition to incremental indexing, another backend, or a different review
operating mode MUST be triggered only by a recorded policy rule whose measured
workload repeatedly breaches an agreed usability/resource budget, or by a
correctness/recovery requirement that the baseline cannot satisfy. The decision
MUST include a rollback path and equivalence evidence against the canonical
file-based representation. Corpus size alone is not a transition criterion.

**SCALE-001**: Scale decisions MUST be evidence-based, reproducible and
reversible; implementations MUST NOT invent capacity numbers or present
unmeasured targets as conformance evidence.

Every derived artifact MUST carry a source snapshot marker consisting of the
canonical corpus hash, relevant registry/policy versions, algorithm version and
generation timestamp. A derived artifact is **current** only when all source
markers match the active inputs; otherwise it is **stale** and MUST be
invalidated before publication. Changes to canonical objects, relevant
registries/policies, algorithm/schema versions, deletions, or detected source
hash drift MUST invalidate affected artifacts. A stale artifact MUST NOT be
presented as current or used as an authoritative input to promotion; it MAY be
served only when explicitly labelled stale for diagnostics.

Invalidation and regeneration MUST be observable with artifact identity,
previous/current markers, reason, state (`current`, `stale`, `rebuilding`, or
`failed`) and timestamp. Correction or deletion of a canonical object MUST
invalidate its derived contributions before a replacement view is published;
publication MUST be atomic, and a failed rebuild MUST leave the prior view
marked stale rather than silently current.

**DERIVED-001**: Derived views require version-bound freshness markers,
deterministic invalidation, stale-result isolation and observable atomic
regeneration.

---

## 7. Taxonomic Structure & Registry Mapping

`taxonomy_registry.yaml` constitutes the canonical source of truth for the taxonomy. Nodes in the registry form a forest structure of directed trees per scope without cycles (**TAX-006** / **E024**).

### 7.1 Taxonomy Principles

- **TAX-001**: Every specified taxonomy_id MUST correspond to a node in taxonomy_registry.yaml
- **TAX-002**: taxonomy_path + scope SHALL deterministically compute the disk path
- **TAX-003**: Two different taxonomy_path strings within the same scope MUST NOT normalize to the same disk path
- **TAX-004**: If taxonomy_id is specified, taxonomy_path and scope MUST exactly match the canonical data in taxonomy_registry.yaml
- **TAX-005**: parent_id in taxonomy_registry.yaml MUST point to an existing node within the same scope
- **TAX-006**: taxonomy_registry.yaml SHALL form an acyclic forest structure per scope
- **TAX-007**: `taxonomy_path` in frontmatter SHALL be a flat leaf-name and SHALL be identical to the registry node's `name`. Slash-separated breadcrumbs MUST NOT be used in frontmatter (**E016**)
- **TAX-008**: A registry node MAY declare an optional `description`. It is documentation and a boundary guard only, and MUST NOT affect path computation or any validation outcome
- **TAX-009**: The taxonomy SHALL classify **subject** only. A node MUST NOT encode what kind of object something is (`object_type`), what state it is in (`facets.lifecycle`), who it is for (`facets.audience`), or how it relates to other objects (`relations`)

### 7.4 Taxonomy evolution

`taxonomy_registry.yaml` is owned by the architecture specification and is the
only authority for taxonomy identity, parentage and names. Registry changes
MUST be reviewed as schema changes, increment the registry `schema_version`,
and preserve globally unique `taxonomy_id` values; an ID MUST NOT be reused for
a different subject. Additions are preferred. A rename, split, merge, move or
deprecation MUST retain the old node as an auditable migration source and
declare an explicit mapping to its replacement node(s), with an effective
version and migration owner.

Before an evolved registry is used for promotion or path generation, all
affected objects MUST be deterministically revalidated or migrated. Existing
canonical objects MUST NOT be silently refiled: path changes require an
atomic, reviewable migration that preserves object IDs and provenance. Until
that migration completes, the old taxonomy remains resolvable and affected
objects MUST be surfaced as migration work rather than treated as conformant
under the new tree.

**TAX-010**: Taxonomy evolution MUST be versioned, owned, non-reusing and
explicitly migrated; registry edits MUST NOT silently change canonical meaning
or placement.

An import from a foreign taxonomy is not taxonomy verification. A mapping that
retains only a target top-level node while discarding source descendants or
topics MUST be labelled provisional/lossy, preserve the original source path
and mapping rationale, and remain review-gated. It MUST NOT silently change the
canonical object's taxonomy or disk placement. This migration rule complements
TAX-010; it does not add a second taxonomy namespace.

### 7.2 Axis Discipline (TAX-009)

The taxonomy answers exactly one question: **what subject is this about.** The
recurring failure mode is importing another axis into the tree, which produces
nodes that attract either everything or nothing. Consequences of TAX-009:

| Tempting node | Why it is wrong | Correct axis |
|---|---|---|
| `Troubleshooting` | describes the kind of document | `object_type: Lesson`, filed under the affected subject |
| `Standards` | describes the kind of document | `object_type: Specification` + `source_type: api_spec`, filed under what it specifies |
| `Tools` | describes a property | `facets.toolchain` |
| `Features` / `Roadmap` | describes a state | `facets.lifecycle` plus `PART_OF` / `INTRODUCED_IN` relations |
| `Customer Documentation` | describes a reader | `facets.audience: customer` |
| `Legacy` / `Current` | describes a state | `facets.lifecycle` |
| `UT` / `IT` / `E2E` | describes a property | `facets.test_level` |

A node MAY carry a `description` stating its boundary explicitly ("NOT for X —
that is node Y"). An empty node without such a guard tends to attract misfiled
objects from a neighbouring subject.

### 7.3 Registry Structure

The registry is a **flat list** of nodes; the hierarchy is expressed exclusively by
`parent_id`. This is the actual structure in
`schemas/registry/taxonomy_registry.yaml`:

```yaml
# taxonomy_registry.yaml
taxonomy:
  # ---- scope: personal ----
  - taxonomy_id: "TX-PERS-07"
    name: "07. Computer Science, AI & IT Security"
    scope: "personal"
    parent_id: null
    description: >
      Portable computing knowledge. Org- and system-bound engineering practice at
      Duckburg Vibe Inc belongs in scope: engineering, not here.

  - taxonomy_id: "TX-PERS-07-04"
    name: "07.04. AI-Assisted Software Engineering"
    scope: "personal"
    parent_id: "TX-PERS-07"

  # ---- scope: engineering ----
  - taxonomy_id: "TX-ENG-10"
    name: "10. Software Construction & Build Systems"
    scope: "engineering"
    parent_id: null

  - taxonomy_id: "TX-ENG-10-01"
    name: "10.01. Build Tooling & Target Layout"
    scope: "engineering"
    parent_id: "TX-ENG-10"
    description: >
      Monorepo module graph, build rules, target layout, include and linkage models.
```

**Field contract:**

| Field | Type | Requirement |
|---|---|---|
| `taxonomy_id` | str | Mandatory, globally unique (**W010** on duplicate) |
| `name` | str | Mandatory, flat leaf-name. Corresponds to the frontmatter field `taxonomy_path` (**TAX-007**) |
| `scope` | ScopeEnum | Mandatory, `personal` or `engineering` |
| `parent_id` | str \| null | `null` for root node; otherwise an existing node in the **same** scope (**TAX-005** / **E018**) |
| `description` | str | Optional. Documentation and boundary guard only (**TAX-008**) |

Example of computed disk path for `TX-ENG-10-01` according to §1.3:

```text
engineering/10_software_construction_build_systems/10.01_build_tooling_target_layout/
```