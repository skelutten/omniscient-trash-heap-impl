# Research Note P16: Failure Modes of LLM Knowledge Graph Extraction & Modular Architectures

> **Type**: Non-normative prior-art provenance & architectural analysis
> **Sources**:
>   1. Fabio Yáñez Romero, *Why LLMs Fail at Knowledge Graph Extraction (And What Works Instead)* (Towards AI / Medium, Jan 15, 2026)
>   2. Fabio Yáñez Romero, *From Text to Knowledge Graph in One Command: Building a Modular LLM-Backed Framework* (Towards AI / Medium, March 30, 2026)
> **Retrieved**: 2026-09-08
> **URLs**:
>   - `https://pub.towardsai.net/why-llms-fail-at-knowledge-graph-extraction-and-what-works-instead-dcb029f35f5b`
>   - `https://pub.towardsai.net/from-text-to-knowledge-graph-in-one-command-building-a-modular-llm-backed-framework-ec98abd3d565`
> **Canonical Source Raws**:
>   - `research/raw/2026-01-15-why-llms-fail-at-knowledge-graph-extraction-and-what-works-instead.md`
>   - `research/raw/2026-03-30-from-text-to-knowledge-graph-in-one-command-building-a-modular-llm-backed-framew.md`
> **Informs**: `specs/RELATION-EXTRACTION.md`, `specs/ONTOLOGY.md` §4, `specs/ARCHITECTURE.md` (`CANON-005`, `CANON-006`), `plans/95-RELATION-EXTRACTION-AND-LINKING.md`

---

## 1. Executive Summary

Across two landmark articles, Fabio Yáñez Romero breaks down the fundamental engineering failures that occur when teams attempt naive, open-ended knowledge graph (KG) construction using generative Large Language Models. Romero identifies the **Pipeline Compounding Error Problem**—where multi-stage generative pipelines suffer catastrophic accuracy collapse ($0.9 \times 0.8 \times 0.7 \approx 50\%$) due to entity synonym fragmentation, hallucinated predicates, and unanchored ontology drift.

To resolve this, Romero introduces a strict architectural dichotomy:
1. **Asserted Knowledge Graphs (The Verifiable Ground Truth):** Extraction must be limited strictly to propositions with direct, verbatim text span evidence. No inferred relations or speculative reasoning may enter the base graph. Discriminative or constrained models with strict schema definitions outperform open-ended generative prompts.
2. **Augmented Knowledge Graphs (Governed Inferences):** Higher-order structures (taxonomic hierarchies, transitive closures, link predictions, topic clustering) must be executed by distinct, auditable augmentation layers rather than mixed into raw extraction.
3. **The Modular CLI Builder Pattern (`kgb`):** Orchestrating graph generation through clean abstractions: Provider registries, Domain bundles (switching ontology, taxonomy, and rules per domain without changing engine code), and deterministic CLI pipelines.

This analysis provides direct theoretical and empirical backing for *The Omniscient Trash Heap*'s Closed-Ontology Relation Extraction pipeline (`specs/RELATION-EXTRACTION.md`), our two-stage epistemic validation (`CANON-005`), and our separation of canonical knowledge objects from derived graph intelligence (`specs/GRAPH-INTELLIGENCE.md`).

---

## 2. Why Generative LLMs Fail at Knowledge Graph Extraction

### 2.1 The Core Failure Modes
1. **Entity Resolution & Alias Proliferation:** Open LLM extraction treats surface textual variations as distinct graph entities (e.g., extracting "Party A", "the plaintiff", and "Acme Corp" as three disconnected nodes from one contract paragraph).
2. **Ontological Hallucination & Predicate Drift:** When prompt instructions say "extract all relationships", LLMs invent hundreds of idiosyncratic edge labels (`is_located_substantially_near`, `seems_to_be_affiliated_with`), destroying graph traversability and preventing algebraic querying.
3. **The Compounding Pipeline Trap:**
   $$\text{Accuracy}_{\text{end-to-end}} = \text{Accuracy}_{\text{NER}} \times \text{Accuracy}_{\text{RE}} \times \text{Accuracy}_{\text{Resolution}}$$
   Even with state-of-the-art per-component accuracies of 90% NER, 80% Relation Extraction, and 70% Entity Resolution, the final graph precision drops to **50.4%**, contaminating the knowledge base with noise.

```text
Unstructured Text
       │
       ▼
[ NER Extraction (90%) ] ──> 10% errors
       │
       ▼
[ Relation Extraction (80%) ] ──> 28% cumulative errors
       │
       ▼
[ Entity Resolution (70%) ] ──> 49.6% cumulative errors!
       │
       ▼
Contaminated Graph (Coin-flip accuracy)
```

---

## 3. The Solution: Asserted vs. Augmented Graphs

Romero defines two completely separate stages of graph construction:

### 3.1 Stage 1: The Asserted Knowledge Graph (Verifiable Foundation)
- **Zero Inferred Edges:** The asserted graph represents only what the text explicitly states. Every node and edge carries mandatory text span offsets.
- **Closed Ontological Schema:** Candidate relations are restricted to predefined predicates with explicit source/target type constraints.
- **Discriminative & Structured Precedence:** Enforces strict Pydantic/JSON schemas or discrete token logit extraction (`logits_to_keep=1`) to eliminate unconstrained generative hallucinations.

### 3.2 Stage 2: Augmentation Layers (Derived Intelligence)
Once the asserted graph is locked and validated, secondary deterministic or probabilistic algorithms enrich the graph:
1. **Taxonomic Augmentation:** Linking specific entities to broader parent concepts via explicit taxonomy registries.
2. **Rule-Based Inference:** Applying formal logic (e.g. symmetry, transitivity, inverse view materialization per `REL-008`).
3. **Link Prediction with Knowledge Base Alignment:** Computing topological and semantic edge scores to suggest candidates for human review.
4. **Source Context Preservation:** Retaining original document boundaries and provenance envelopes for all derived connections.

---

## 4. The Modular Framework Architecture (`kgb`)

In *From Text to Knowledge Graph in One Command*, Romero presents a clean software architecture separating graph logic from model providers:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ CLI Layer (kgb run-pipeline --domain legal --input raw/ --output graph/)│
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ The Orchestrator / Pipeline Runner                                     │
│  1. Extract Asserted Graph  ──>  2. Apply Augmentations (Taxonomy/Rules)│
└────────────────────────────────────────────────────────────────────────┘
            │                                           │
            ▼                                           ▼
┌───────────────────────────────┐           ┌────────────────────────────┐
│ Extraction Builder            │           │ Augmentation Builder       │
│ • Closed Ontology Enforcement │           │ • Taxonomic Hierarchy      │
│ • Text Span Offsets Binding   │           │ • Symmetrical Edges        │
│ • Provider-Agnostic Interface │           │ • Deduplication / Alias    │
└───────────────────────────────┘           └────────────────────────────┘
            │                                           │
            └─────────────────────┬─────────────────────┘
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Domain Registry Configuration (schemas/registry/)                      │
│ • Allowed Entities, Predicates, Source/Target Constraints, Rules       │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Tenets:
1. **The Builder Pattern as Graph Orchestrator:** Isolates extraction logic from data store persistence.
2. **One Interface, Every Provider:** Pluggable LLM clients (OpenAI, Anthropic, local vLLM/Ollama) implementing a unified extraction interface.
3. **Domain Bundles:** Switching from `medical` to `legal` is achieved purely by changing configuration files (entity registries, relation constraints), without altering pipeline code.
4. **Clean CLI Entry Point:** High-level operators run single reproducible commands (`kgb run-pipeline`) rather than managing sprawling ad-hoc scripts.

---

## 5. Direct Convergence with *The Omniscient Trash Heap*

| Romero's KG Principles | *The Omniscient Trash Heap* Architecture | Formal Specification |
|---|---|---|
| **Asserted Knowledge Graph** | Canonical Knowledge Objects and explicit frontmatter `links:` | `CANON-001`, `CANON-005` in `ARCHITECTURE.md` |
| **Closed Ontological Schema** | Declarative registry defining source/target type constraints | `relation_registry.yaml`, `REL-005`, `REL-006` in `ONTOLOGY.md` |
| **Augmentation Layer** | Graph Intelligence Delta & Discovery (`staging/discovery/`) | `specs/GRAPH-INTELLIGENCE.md`, `specs/DISCOVERY.md` |
| **Lineage & Span Offsets** | Mandatory lineage envelopes (`source_refs`, line intervals) | `DISC-001`, `SG-007` in `STRUCTURAL-GRAPH.md` |
| **Domain Switch via Registries** | Centralized declarative YAML registries | `schemas/registry/*.yaml` |
| **CLI-First Orchestration** | `trashheap` unified CLI entry point | `trashheap lint`, `trashheap graph`, `trashheap discover` |

---

## 6. Actionable Takeaways for Trash Heap

1. **Reinforcement of Closed-Ontology Extraction (`specs/RELATION-EXTRACTION.md`):** Confirms that open LLM extraction without strict schema constraints produces unusable graphs. `REX-001` and `REX-002` must strictly reject any predicate not registered in `relation_registry.yaml`.
2. **Extraction vs. Augmentation Boundary (`CANON-006`):** LLM extraction creates candidate *asserted* facts; deterministic graph algorithms perform *augmentation* (transitive closures, cycles checks, degree centrality).
3. **Lineage Offset Mandate:** Every extracted candidate relation in `staging/discovery/` must preserve the exact text excerpt and line coordinates of its source document to ensure human reviewers can verify claims in $< 5$ seconds.
