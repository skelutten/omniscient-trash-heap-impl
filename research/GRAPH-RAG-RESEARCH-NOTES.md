# Source Material: GraphRAG, Graphify, Codebase-Memory & OKF

> **Type**: Source material / research notes (raw dialogue transcript)
> **Status**: NON-NORMATIVE — this is not a specification
> **Language**: English (dialogue transcript)
> **Date**: 2026-08-17
> **Derived specifications**:
> - `specs/STRUCTURAL-GRAPH.md` (SG-001–SG-020)
> - `specs/OKF-INTEROP.md` (OKF-001–OKF-010)
> - `specs/GRAPH-INTELLIGENCE.md` §9.2 (community memory)
> - `specs/ARCHITECTURE.md` §2.2 (Canonical/Derived Knowledge Principle)
> - `specs/ARCHITECTURE.md` §2.3 (Knowledge Library)

This document was previously located in `specs/` as `GRAPH-ADD.md`. It is a raw transcript of a design discussion regarding Microsoft GraphRAG, Graphify, `code-review-graph`, `codebase-memory-mcp`, `rahulnyk/knowledge_graph`, and Google's Open Knowledge Format (OKF) v0.2. It contains reasoning, recommendations, and rejected alternatives mixed with normative proposals.

It was moved here because, according to the repository's design philosophy, `specs/` only contains normative, section-numbered specifications with `Part of / Source / Status` headers. The normative content has been extracted into the specifications listed above. The text is preserved below as provenance documentation (**source material is never deleted**).

---

## 1. GraphRAG & Graphify Analysis

Yes — and I actually think that GraphRAG and the newer Graphify variants provide even more critical ideas for your LLM Wiki than the Rahulnyk project.

The major difference is that your current architecture already possesses a formal, human-governed knowledge graph. Therefore, you should not copy GraphRAG's model blindly. Instead, you can take their retrieval, community, summarization, and discovery mechanisms and place them in the Delta layer we discussed.

I have examined the current Microsoft GraphRAG architecture and several current Graphify implementations.

### Summary of Lessons Learned

| Idea | Origin (GraphRAG/Graphify) | Fits Your Wiki? | Recommendation |
|---|---|---|---|
| Entity/relation extraction | Both | Yes | ⭐⭐⭐⭐⭐ Yes |
| Provenance per edge | Both | Yes | ⭐⭐⭐⭐⭐ Must have |
| Extracted vs inferred | Graphify | Yes | ⭐⭐⭐⭐⭐ Must have |
| Community detection | Both | Yes | ⭐⭐⭐⭐⭐ Yes |
| Hierarchical communities | GraphRAG | Yes | ⭐⭐⭐⭐⭐ Yes |
| Community summaries | GraphRAG | Yes | ⭐⭐⭐⭐⭐ Yes |
| Local GraphRAG | GraphRAG | Yes | ⭐⭐⭐⭐⭐ Yes |
| Global GraphRAG | GraphRAG | Yes | ⭐⭐⭐⭐⭐ Yes |
| DRIFT-style retrieval | GraphRAG | Yes | ⭐⭐⭐⭐⭐ Highly interesting |
| Semantic deduplication | Graphify | Yes | ⭐⭐⭐⭐⭐ Yes |
| Structural code graph | Graphify | Yes | ⭐⭐⭐⭐⭐ Yes for engineering/software |
| God nodes / hubs | Graphify | Yes | ⭐⭐⭐⭐ Yes |
| Surprising connections | Graphify | Yes | ⭐⭐⭐⭐⭐ Yes |
| Hyperedges | Graphify | Yes | ⭐⭐⭐⭐ Experimental |
| Graph-only retrieval | Graphify | No | ⭐⭐ No |
| Replacing RRF | — | No | ⭐ No |
| Automatically mutating ontology | — | No | ⭐ Absolutely not |

---

### 1.1 GraphRAG's Major Insight: Community ≠ Just Graph Visualization

In my view, this is the single largest missing piece in your previous architecture.

GraphRAG does not merely produce:
`nodes + edges`

Instead, it constructs:
```text
Nodes
  ↓
Relationships
  ↓
Communities
  ↓
Community Reports
  ↓
Hierarchical Community Reports
```

Microsoft's pipeline extracts entities, relationships, and claims, builds communities using hierarchical community detection (Leiden/Louvain), and generates multi-level summaries.

This is extremely valuable for your wiki.

#### Example
Your engineering domain might automatically discover:

```text
Community C42
├── Bazel
├── Remote Execution
├── Remote Cache
├── RBE
├── BuildFarm
├── Distributed Compilation
└── CI/CD
```

The system can then generate:
`COMMUNITY_REPORT:C42:L2`

Containing, for example:
```yaml
community_id: C42
level: 2
entity_count: 37
summary: ...
key_entities: ...
key_relationships: ...
key_claims: ...
source_nodes: [...]
```

This is **not** a new Knowledge Object. It is a **derived retrieval artifact**. It fits cleanly into your Delta specification.

---

### 1.2 Hierarchical Communities Are Even More Compelling

GraphRAG does not just build a flat cluster layer, but a full community hierarchy:

```text
L0
└── Engineering

    L1
    ├── Distributed Processing
    ├── Platform Infrastructure
    └── Build Systems

        L2
        ├── Bazel
        ├── Remote Execution
        ├── CI/CD
        └── Toolchains
```

This is crucial because it does **not** compete with your taxonomy.

You will have:
- **Taxonomy (Normative)**: *Where does the object reside administratively?*
- **Community Hierarchy (Emergent)**: *Which objects function together dynamically as an active knowledge cluster?*

These are two entirely distinct structures.

I would formulate this explicitly as an invariant:
```text
COMM-001
Community membership MUST NOT modify taxonomy_path, taxonomy_id, or taxonomy_registry.yaml.
```

---

### 1.3 Community Reports as a "Memory Compression Layer"

This provides massive scalability. Your wiki may grow from 10,000 to 20,000 or 100,000 Knowledge Objects. You cannot pass thousands of objects into an LLM context window.

Community reports function as hierarchically compressed graph memory:

```text
Knowledge Objects
      ↓
Canonical Graph
      ↓
Communities
      ↓
Community Reports
      ↓
Community Summaries
```

Yielding:
```text
Raw Knowledge → Structured Knowledge → Compressed Knowledge → LLM Context
```

This is vastly more powerful than naive vector RAG chunk windows.

---

### 1.4 Global Search — A Crucial Capability

Your previous retrieval was primarily structured around:
```text
Query → Seed Retrieval → Graph Expansion → Fusion → Reranking
```

This works well for localized questions like:
> *"What rules apply to Bazel remote caching?"*

But what happens with macro-questions like:
> *"What are the major structural bottlenecks across our entire build infrastructure?"*

This is a **global question**. GraphRAG solves this using community reports combined with Map/Reduce.

I recommend defining four explicit retrieval modes:

1. **LOCAL (Entity/Node-centric)**:
   ```text
   Entity (e.g. Bazel) → Neighbors → Relations → Direct Documents
   ```
2. **GLOBAL (Corpus/Community-centric)**:
   ```text
   All Communities → Community Reports → Map → Reduce → Global Synthesis
   ```
3. **BASIC**:
   ```text
   Standard Lexical BM25 + Vector Search
   ```
4. **DRIFT**:
   ```text
   Hybrid, adaptive multi-turn exploration.
   ```

---

### 1.5 DRIFT Search for Adaptive Exploration

GraphRAG's DRIFT search begins broadly at the community level and drills down into local retrieval via follow-up questions and adaptive expansion:

```text
User Query
    │
    ▼
Community-Level Understanding
    │
    ▼
Follow-up Questions
    │
    ├────► Local Search
    │
    ├────► Local Search
    │
    └────► Local Search
             │
             ▼
       Evidence Aggregation
             │
             ▼
           Answer
```

This aligns with your workflow: `Plan → Retrieve → Expand → Critique → Retry`. DRIFT acts as a dynamic retrieval-time exploration policy.

---

### 1.6 Graphify's Distinction: EXTRACTED vs INFERRED

Graphify tags relations explicitly:
- `EXTRACTED` (verbatim from text or AST)
- `INFERRED` (deduced via semantic model)
- `AMBIGUOUS` (uncertain or conflicting)

This separates epistemic validity from graph derivation:

```yaml
derivation:
  mode: extracted | inferred | ambiguous
  extractor: llm | ast | parser | rule
  confidence: 0.91
```

- **Epistemology**: *"How well-established and verified is this knowledge?"*
- **Derivation**: *"How did the indexing engine arrive at this specific graph relation?"*

---

### 1.7 Surprising Connections & Graph Hubs

Graphify identifies cross-community links and reports why they are interesting:
```text
Bazel Remote Cache ──[inferred]──► Knowledge Decay ──► Ephemeral Build Artifacts
```
*Reason: Objects belong to disjoint communities but share strong semantic and evidential signals.*

Graph hubs (nodes with high degree and betweenness centrality) assist with navigation, onboarding, and documentation prioritization. However, graph centrality **must not** automatically inflate epistemic confidence (a popular node is not inherently more true).

---

### 1.8 Deterministic AST Pass for Codebases

Graphify uses Tree-sitter to construct structural relationships without LLMs (`CALLS`, `IMPORTS`, `INHERITS`), allowing semantic models to operate on top of verified syntax:

```text
                    INPUT
                      │
             ┌────────┴────────┐
             │                 │
       DETERMINISTIC       SEMANTIC
         EXTRACTION         EXTRACTION
             │                 │
          AST/Parser          LLM
             │                 │
             └────────┬────────┘
                      ▼
                 GRAPH LAYER
```

This dramatically reduces hallucinations.

---

### 1.9 TextUnits & Grounding

GraphRAG links graph objects back to source text units:
`Document → TextUnit → Entity → Relationship`

In our Evidence Bundle:
```yaml
evidence:
  - document_id: DOC-123
    unit_id: DOC-123-C017
    span:
      start: 1832
      end: 2241
```
Enabling rigorous provenance chains: `Claim → Relation → Evidence → Exact Source Passage`.

---

### 1.10 Invariant Boundaries: What NOT To Do

We must establish hard invariant boundaries:
1. **No direct LLM ontology mutation**: Inferred relations enter the *Derived Graph* or staging candidates (`discovery/`), requiring validation before canonical promotion.
2. **No taxonomy mutation via community clustering**: Community detection is emergent; taxonomy is normative.
3. **Centrality ≠ Confidence**: Centrality in the graph does not equal epistemic certainty.

---

## 2. Structural Code Graphs, Codebase Memory & Ingestion Protocols

Examining `code-review-graph`, `codebase-memory-mcp`, `rahulnyk/knowledge_graph`, and OKF reinforces a clear conclusion:

> **Do not turn LLM Wiki into just another codebase graph. Turn it into a semantic/epistemic knowledge layer sitting above a fast, machine-generated structural graph.**

### Comparison of Related Projects

| Project | Strongest Feature | Relevance to LLM Wiki |
|---|---|---|
| `code-review-graph` | Incremental graph + blast radius + MCP | High for Engineering Domain |
| `codebase-memory-mcp` | Tree-sitter + LSP + persistent graph + structural queries | Very High |
| `rahulnyk/knowledge_graph` | Entity/relation extraction, deduplication, clustering | High for automated enrichment |
| OKF Pipeline | Git-triggered self-updating knowledge bundle | Very High for lifecycle & automation |
| **LLM Wiki v3.8.1** | Taxonomy + ontology + epistemology + governance + hybrid retrieval | Far more general, governed, and robust |

`codebase-memory-mcp` reports **83% answer quality** vs **92%** for file-exploration agents, but uses **10× fewer tokens** and **2.1× fewer tool calls**. This justifies structural retrieval as a first-class primitive.

---

### 2.1 The Two-Graph Architecture

```text
                    ┌──────────────────────────┐
                    │     SOURCE MATERIAL      │
                    │ Markdown / Code / Docs   │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │      INGESTION LAYER     │
                    │ parsers / extractors     │
                    └────────────┬─────────────┘
                                 │
             ┌───────────────────┴───────────────────┐
             │                                       │
   ┌─────────▼─────────┐                   ┌─────────▼─────────┐
   │ STRUCTURAL GRAPH  │                   │ SEMANTIC KNOWLEDGE│
   │                   │                   │ GRAPH             │
   │ AST               │                   │                   │
   │ imports           │                   │ Concepts          │
   │ calls             │                   │ Claims            │
   │ inheritance       │                   │ Lessons           │
   │ symbols           │                   │ Principles        │
   │ HTTP routes       │                   │ Requirements      │
   │ tests             │                   │ Relations         │
   └─────────┬─────────┘                   └─────────┬─────────┘
             │                                       │
             └──────────────────┬────────────────────┘
                                │
                     ┌──────────▼──────────┐
                     │ UNIFIED KNOWLEDGE   │
                     │ GRAPH / IDENTITY    │
                     │ & CROSS-LINKING     │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │ HYBRID RETRIEVAL    │
                     │ lexical/vector/     │
                     │ structural/graph    │
                     │ epistemic           │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │ EVIDENCE BUNDLE     │
                     └─────────────────────┘
```

#### Separation:
- **Semantic Graph**: Governed by `relation_registry.yaml` (`DEPENDS_ON`, `IMPLEMENTS`, `VERIFIED_BY`).
- **Structural Graph**: Governed by `structural_registry.yaml` (`DEFINES`, `CALLS`, `IMPORTS`, `INHERITS`).

---

### 2.2 Git Revision Binding & Impact Analysis (Blast Radius)

Binding graph edges to Git revisions (`source_revision: "a8f31c..."`) allows incremental change detection and impact analysis:

```text
Component A Changed ──► CALLS ──► Component B ──► IMPLEMENTS ──► Feature C ──► SATISFIES ──► Requirement D ──► VERIFIED_BY ──► Test E
```

Answering *"What is impacted by this change?"* becomes a deterministic graph query rather than an LLM guess.

---

### 2.3 Incremental Reconciliation Layer

When source code changes:
`old graph + new source → reconciliation`

The system detects: `ADDED`, `REMOVED`, `CHANGED`, `MOVED`, `RENAMED`, `INVALIDATED`, `UNRESOLVED`. If a component is renamed, the structural graph detects the rename while preserving the semantic Knowledge Object ID.

---

### 2.4 Structural Graph Extension Specification (SG-001–SG-020)

Extracted into `specs/STRUCTURAL-GRAPH.md`:
- `SG-001`: Structural Graph definition
- `SG-002`: Structural Node Model
- `SG-003`: Structural Edge Registry
- `SG-004`: AST Extraction (Tree-sitter)
- `SG-005`: LSP Resolution
- `SG-006`: Incremental Indexing
- `SG-007`: Git Revision Binding
- `SG-008`: Change Detection
- `SG-009`: Graph Reconciliation
- `SG-010`: Impact Analysis
- `SG-011`: Context Budgeting
- `SG-012`: Graph-Native Retrieval
- `SG-013`: Structural/Semantic Graph Bridge
- `SG-014`: Derived Provenance
- `SG-015`: Graph Coverage Metrics
- `SG-016`: Deterministic Structural Queries
- `SG-017`: MCP Query Interface
- `SG-018`: Evidence Bundle Extension
- `SG-019`: Conformance Tests
- `SG-020`: Failure & Degradation Semantics

---

## 3. Google Open Knowledge Format (OKF v0.2) & Interoperability

David R. Oliver's analysis of Google OKF v0.2 emphasizes keeping Markdown + YAML as the canonical source of truth, treating graphs, indexes, and retrieval structures as derived projections.

```text
                    LLM Wiki
                       │
             ┌─────────┴─────────┐
             │                   │
       OKF Compatibility    Native Semantics
             │                   │
       Minimal Contract     v3.8.1 Contract
             │                   │
       Markdown + YAML      Taxonomy
                            Object Types
                            Typed Relations
                            Epistemology
                            Governance
                            Provenance
                            Retrieval
             │                   │
             └─────────┬─────────┘
                       │
                Derived Projections
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        Graph        BM25        Vector
          │            │            │
          └────────────┼────────────┘
                       ▼
                    RRF / Rerank
```

### 3.1 OKF Comparison & Interoperability Invariants

| Dimension | LLM Wiki Native | Google OKF v0.2 |
|---|---|---|
| Storage Format | Markdown + YAML | Markdown + YAML |
| Git Integration | Native | Native |
| Taxonomy | Strongly Formalized | Minimal |
| Object Types | Strict Registry | Open / Freeform |
| Relations | 30 Typed Edge Types | Untyped Links |
| Provenance | Strict (PROV-O aligned) | Present |
| Epistemology | 4-Axis Quadrant | Trust-Oriented |
| Governance | Review Gates & Lifecycles | Lightweight |
| Validity | Explicit Temporal Ranges | Present |
| Graph Index | First-Class Rebuildable Layer | Implicit |
| Retrieval / RRF | Formally Specified (Layers 4–7) | Outside Format |
| Conformance Tests | 5-Layer Deterministic Linter | Lightweight |
| Interoperability | Projections via Adapters | Core Philosophy |

---

### 3.2 OKF Interoperability Invariants (OKF-001–OKF-010)

Extracted into `specs/OKF-INTEROP.md`:
- `OKF-001`: All Knowledge Objects SHALL be exportable to conformant OKF documents.
- `OKF-002`: OKF exports SHALL preserve canonical Knowledge Object IDs.
- `OKF-003`: OKF exports SHALL preserve provenance, lifecycle, validity, and verification metadata.
- `OKF-004`: LLM Wiki extensions SHALL use namespaced frontmatter fields (`llm_wiki:`).
- `OKF-005`: The OKF representation SHALL NOT become the canonical source of truth.
- `OKF-006`: Graph indexes SHALL be rebuildable from canonical Knowledge Objects.
- `OKF-007`: Lossy exports SHALL be explicitly declared.
- `OKF-008`: Importing OKF SHALL NOT silently invent ontology, epistemology, or governance semantics.
- `OKF-009`: Unknown OKF/extension fields SHALL be preserved during round-tripping.
- `OKF-010`: OKF export transformations SHALL be deterministic.

---

## 4. The Knowledge Library Paradigm: Filesystem as Projection

When a knowledge base scales, the physical directory hierarchy becomes a bottleneck if treated as the knowledge model.

### 4.1 Core Principle: Physical Storage vs Knowledge Model

```text
                 KNOWLEDGE OBJECT
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Taxonomy       Ontology       Facets
        │              │              │
        ▼              ▼              ▼
     Folders         Graph        Filters
```

A rigid folder hierarchy cannot represent multi-dimensional knowledge (e.g. a feature simultaneously classified under a domain, using a specific toolchain, written in C++, and participating in dependencies, requirements, and test suites).

### 4.2 Invariant Realization

```text
ORG-001 — Knowledge Object Independence from Physical Storage
A Knowledge Object SHALL be semantically identifiable and retrievable independently of its physical filesystem location.

ORG-002 — Filesystem as Projection
Filesystem paths SHALL constitute a deterministic physical projection of taxonomy and scope and SHALL NOT constitute the authoritative representation of ontology, identity, or semantic relationships.
```

### 4.3 Three-Layer Architecture Definition

```text
1. Storage Layer
   └── Markdown, YAML, Git, Directory Trees

2. Knowledge Library Layer
   └── Knowledge Objects, Taxonomy, Ontology, Epistemology, Governance, Provenance

3. Intelligence & Retrieval Layer
   └── BM25, Vector, Graph Walk, RRF, Reranking, Evidence Bundles, LLM Synthesis
```

**Definition**:
> **LLM Wiki is a governed, graph-backed Knowledge Library whose canonical persistence format is Markdown + YAML.**