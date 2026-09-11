# The Omniscient Trash Heap — Practical Examples & Discovery Guide

> **Document ID:** `DOC-EXP-001`  
> **Updated:** September 9, 2026  
> **Status:** Reference Documentation

This document provides concrete, end-to-end command-line and Python examples for using **The Omniscient Trash Heap (`trashheap`)**, covering canonical note validation, hybrid retrieval, graph intelligence, governed discovery candidate lifecycles, structural AST code intelligence, and large-scale literature-based discovery.

---

## Table of Contents
1. [Core Knowledge Base Operations](#1-core-knowledge-base-operations)
   - [Scaffolding a New Wiki (`trashheap init`)](#scaffolding-a-new-wiki-trashheap-init)
   - [Multi-Layer Validation Gate (`trashheap lint` & `validate`)](#multi-layer-validation-gate-trashheap-lint--validate)
   - [Reading & Section Extraction (`trashheap show`)](#reading--section-extraction-trashheap-show)
2. [Hybrid & Graph-Enhanced Retrieval](#2-hybrid--graph-enhanced-retrieval)
   - [Standard 4-Way Reciprocal Rank Fusion Search](#standard-4-way-reciprocal-rank-fusion-search)
   - [Graph-Enhanced Topological Ranking (`--graph-enhanced`)](#graph-enhanced-topological-ranking---graph-enhanced)
   - [Max-Over-Chunks Dense Vector Retrieval (`--vector`)](#max-over-chunks-dense-vector-retrieval---vector)
3. [Graph Intelligence & Community Analysis](#3-graph-intelligence--community-analysis)
   - [Generating the Canonical Input Manifest](#generating-the-canonical-input-manifest)
   - [Graph Topology, Centrality & Derived Edges](#graph-topology-centrality--derived-edges)
4. [Governed Knowledge Discovery (`trashheap discover`)](#4-governed-knowledge-discovery-trashheap-discover)
   - [Automated Multi-Predicate Gap Scanning](#automated-multi-predicate-gap-scanning)
   - [Listing & Filtering Discovery Candidates](#listing--filtering-discovery-candidates)
   - [Reviewing Candidates (Pending → Approved / Rejected)](#reviewing-candidates-pending--approved--rejected)
   - [Validated Candidate Promotion](#validated-candidate-promotion)
   - [Sweeping Expired Proposals (90-day TTL)](#sweeping-expired-proposals-90-day-ttl)
5. [Structural Knowledge Graph: Code-to-Knowledge Bridging](#5-structural-knowledge-graph-code-to-knowledge-bridging)
   - [Indexing Codebase AST into Knowledge Graph](#indexing-codebase-ast-into-knowledge-graph)
   - [Automated Symbol-to-Document Bridge Discovery](#automated-symbol-to-document-bridge-discovery)
   - [Blast Radius & Impact Analysis](#blast-radius--impact-analysis)
6. [Large-Scale Literature-Based Discovery (Swanson ABC Model)](#6-large-scale-literature-based-discovery-swanson-abc-model)
   - [The Swanson Discovery Paradigm ($A \to B \to C$)](#the-swanson-discovery-paradigm-a-to-b-to-c)
   - [CLI Example: Raynaud's Disease $\leftrightarrow$ Fish Oils](#cli-example-raynauds-disease--fish-oils)
   - [CLI Example: Computational Drug Repurposing (Metformin $\leftrightarrow$ Alzheimer's)](#cli-example-computational-drug-repurposing-metformin--alzheimers)
   - [Python API Usage](#python-api-usage)

---

## 1. Core Knowledge Base Operations

### Scaffolding a New Wiki (`trashheap init`)
To create a fully compliant, self-contained knowledge vault anywhere on disk:

```bash
# Initialize inside a new directory
uv run trashheap init /home/$USER/my-vault --name "Engineering Intelligence"

# Inspect the scaffolded structure
tree -L 2 /home/$USER/my-vault
```
*Creates all 10 canonical YAML registries, taxonomic directories (`personal/`, `engineering/`), staging quarantine (`raw/`, `discovery/`), and a passing seed note.*

### Multi-Layer Validation Gate (`trashheap lint` & `validate`)
Linting verifies schema compliance, YAML frontmatter restrictions (`extra: forbid`), relational invariants, and epistemic policies across all files:

```bash
# Lint an entire corpus (e.g. fixtures or personal vault)
uv run trashheap lint fixtures/canonical

# Validate a single specific note within corpus context
uv run trashheap validate fixtures/canonical/engineering/01_domain_system_architecture/ENG-CMP-PARSER-0001.md
```

### Reading & Section Extraction (`trashheap show`)
To view note contents without opening full files in an editor:

```bash
# Display full Knowledge Object by ID
uv run trashheap show ENG-CMP-PARSER-0001 --corpus-root fixtures/canonical

# Extract only a specific H2 section (RET-010 section-targeted retrieval)
uv run trashheap show ENG-CMP-PARSER-0001 --corpus-root fixtures/canonical --section "Summary"

# Extract a bounded 1-indexed line range
uv run trashheap show ENG-CMP-PARSER-0001 --lines 1-25
```

---

## 2. Hybrid & Graph-Enhanced Retrieval

The `query` command runs an 8-stage hybrid retrieval pipeline combining lexical BM25 Okapi, BFS graph expansion, dense vectors, and AST symbols through Reciprocal Rank Fusion ($k=60$):

### Standard 4-Way Reciprocal Rank Fusion Search
```bash
# Query notes with JSON output
uv run trashheap query "deterministic parsing" --corpus-root fixtures/canonical --json
```

### Graph-Enhanced Topological Ranking (`--graph-enhanced`)
Replaces simple depth decay with a 6-dimensional topological feature vector ($\vec{\phi}$):
- $\phi_1$: Structural ontology weight (`PART_OF`, `DEPENDS_ON`, `IMPLEMENTS`)
- $\phi_2$: Semantic embedding similarity
- $\phi_3$: Text chunk co-occurrence
- $\phi_4$: Source reference overlap
- $\phi_5$: Hubness & degree centrality
- $\phi_6$: Scope/community alignment

```bash
uv run trashheap query "compiler pipeline" \
  --corpus-root fixtures/canonical \
  --graph-enhanced \
  --json
```

### Max-Over-Chunks Dense Vector Retrieval (`--vector`)
Enables 384-dimensional dense semantic vector retrieval:

```bash
uv run trashheap query "quarantine transaction commit" \
  --corpus-root fixtures/canonical \
  --vector \
  --graph-enhanced
```

---

## 3. Graph Intelligence & Community Analysis

Graph Intelligence operates in read-only mode over canonical projections ([`specs/GRAPH-INTELLIGENCE.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/GRAPH-INTELLIGENCE.md)):

### Generating the Canonical Input Manifest
Builds an immutable manifest recording bitwise SHA-256 hashes of all canonical files:
```bash
uv run trashheap graph manifest --corpus-root fixtures/canonical --output-dir derived
```

### Graph Topology, Centrality & Derived Edges
Calculates degree distributions, betweenness centrality, Louvain community partitions, and semantic proximity edges:
```bash
uv run trashheap graph analyze --corpus-root fixtures/canonical --output-dir derived/graph
```
*Generated artifacts:*
- `derived/graph/node_metrics.jsonl`: In-degree, out-degree, component ID, community ID, and geodesic distances.
- `derived/graph/derived_edges.jsonl`: Inferred semantic and co-occurrence edges with cryptographic provenance.

---

## 4. Governed Knowledge Discovery (`trashheap discover`)

Discovery identifies duplicate notes, topological gaps, and ontological gaps under [`specs/DISCOVERY.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/DISCOVERY.md):

### Automated Multi-Predicate Gap Scanning
Evaluates the corpus for:
1. **Potential Duplicates (`DISC-002`):** Cosine similarity $\ge 0.80$ within the same scope.
2. **Topological Gaps (`DISC-003`):** Evaluates the 2-of-3 predicate rule ($A$: same community, $B$: $\ge 3$ co-occurrences, $C$: similarity $\ge 0.80$).
3. **Ontological Gaps (`DISC-004`):** Unresolved incidents (`unresolved_event`) or unimplemented principles (`unimplemented_lesson`).

```bash
uv run trashheap discover scan --corpus-root fixtures/canonical --discovery-dir discovery
# Output: ✓ Discovery scan complete: found 3 candidates (3 new pending)
```

### Listing & Filtering Discovery Candidates
```bash
# List all candidates
uv run trashheap discover list

# Filter by lifecycle status
uv run trashheap discover list --status pending --json
```

### Reviewing Candidates (Pending → Approved / Rejected)
Every state change is recorded in an append-only audit journal (`discovery/audit_log.jsonl`):
```bash
uv run trashheap discover review DISC-GAP-ONTO-UNRESOLVED-ENG-INC-2026-0001 \
  --decision approved \
  --actor "lead-architect" \
  --reason "Incident requires a formal resolution lesson"
```

### Validated Candidate Promotion
Promotes an approved candidate into the canonical graph, validating relations against `relation_registry.yaml` and verifying endpoint integrity:
```bash
uv run trashheap discover promote DISC-GAP-ONTO-UNRESOLVED-ENG-INC-2026-0001 \
  --actor "lead-architect"
```

### Sweeping Expired Proposals (90-day TTL)
Purges pending candidates that exceed their 90-day expiration window without human action:
```bash
uv run trashheap discover sweep
```

---

## 5. Structural Knowledge Graph: Code-to-Knowledge Bridging

Bridges source code AST symbols to architectural knowledge objects ([`specs/STRUCTURAL-GRAPH.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/STRUCTURAL-GRAPH.md)):

### Indexing Codebase AST into Knowledge Graph
Parses the repository AST into typed nodes (`FILE`, `CLASS`, `FUNCTION`, `MODULE`) and edges (`IMPORTS`, `CONTAINS`, `CALLS`):
```bash
uv run trashheap structural index
# Output: ✓ Indexed 119 files (1,129 nodes, 3,726 edges)
```

### Automated Symbol-to-Document Bridge Discovery
Discovers candidate links between code symbols and documentation notes:
```bash
uv run trashheap structural bridge scan
# Output: ✓ Discovered 2 candidate bridge relations

# Inspect discovered bridges
uv run trashheap structural bridge list --json
```

### Blast Radius & Impact Analysis
Calculates the downstream transitive impact of modifying a specific code symbol or file:
```bash
uv run trashheap structural impact "repo=canonical;path=trashheap/models.py"
```
**Sample Output:**
```text
Blast radius for 'repo=canonical;path=trashheap/models.py':
  Affected nodes (49): ['repo=canonical;path=trashheap/cli.py', 'repo=canonical;path=trashheap/linter.py', ...]
  Depth reached: 1 (max: 3)
  Context budget: 1765 tokens
```

---

## 6. Large-Scale Literature-Based Discovery (Swanson ABC Model)

The Swanson ABC discovery engine operates directly over the **38.16 million node, 1.083 billion edge** biomedical graph compiled from PubMed.

### The Swanson Discovery Paradigm ($A \to B \to C$)
If Concept $A$ (e.g. a disease) is connected in the literature to intermediate mechanisms $B$, and an unrelated Concept $C$ (e.g. a dietary compound or drug) is also connected to $B$, but no papers discuss $A$ and $C$ together, the graph surfaces $B$ as a candidate functional bridge:

```text
Concept A (Raynaud's Disease) ────► Intermediate B (Blood Viscosity) ◄──── Concept C (Fish Oils)
                                  Intermediate B (Platelet Aggregation)
```

### CLI Example: Raynaud's Disease $\leftrightarrow$ Fish Oils
Replicating Don Swanson's landmark 1986 discovery:

```bash
uv run trashheap discover literature \
  --concept-a MESH_D011928 \
  --concept-c MESH_D005395 \
  --top-k 5
```

**Output in ~3.5 seconds (verbatim, reproduced by `tests/test_csr_compile.py` contract):**
```text
=== Swanson ABC Discovery (MESH_D011928 <-> MESH_D005395) ===
  Articles tagged with MESH_D011928: 6,903
  Articles tagged with MESH_D005395: 8,940
  Total intermediate bridges found: 2,515
  Top 5 intermediate functional bridges:
    # 1 | Score:   256.25 | MESH_D004311     (co-A:  186, co-C:  597, bg: 187,775)
    # 2 | Score:    88.12 | MESH_D001161     (co-A:  142, co-C:  148, bg:  56,881)
    # 3 | Score:    86.69 | MESH_D001794     (co-A:  211, co-C:  226, bg: 302,577)
    # 4 | Score:    84.41 | MESH_D016896     (co-A:  287, co-C:  334, bg: 1,289,731)
    # 5 | Score:    83.78 | MESH_D013997     (co-A:  288, co-C:  327, bg: 1,263,705)
```

> **Prerequisite:** `discover literature` reads a compiled full-scale CSR artifact
> directory (`--csr-dir`, default `.cache/pubmed/csr_full`) produced by
> `scripts/ingest_full_pubmed.py` over the 1,334-shard PubMed baseline. These
> artifacts (~9 GB) are machine-local and are **not** part of a fresh clone.
> "Total intermediate bridges found" counts bridges **after** the
> `--max-background-degree` filter (DISC-010).

### CLI Example: Computational Drug Repurposing (Metformin $\leftrightarrow$ Alzheimer's)
Uncovering the biological pathways connecting diabetes therapies to neurodegenerative amyloid clearance:

```bash
uv run trashheap discover literature \
  --concept-a MESH_D008687 \
  --concept-c MESH_D000544 \
  --top-k 5 \
  --json
```

**JSON Output (verbatim, ~23 s on the 8.6 GB artifact):**
```json
{
  "concept_a": "MESH_D008687",
  "concept_c": "MESH_D000544",
  "articles_a": 20612,
  "articles_c": 138869,
  "articles_discussing_both": 104,
  "disjointness_holds": false,
  "total_intermediate_bridges": 7590,
  "top_bridges": [
    {
      "rank": 1,
      "bridge_id": "MESH_D051379",
      "node_idx": 26739,
      "score": 33096.7,
      "cooccurrences_with_a": 2402,
      "cooccurrences_with_c": 19027,
      "background_degree": 1906853
    },
    {
      "rank": 2,
      "bridge_id": "MESH_D003924",
      "node_idx": 7331,
      "score": 22822.15,
      "cooccurrences_with_a": 8307,
      "cooccurrences_with_c": 1217,
      "background_degree": 196226
    },
    {
      "rank": 3,
      "bridge_id": "MESH_D000369",
      "node_idx": 3941,
      "score": 22240.46,
      "cooccurrences_with_a": 818,
      "cooccurrences_with_c": 28678,
      "background_degree": 1112543
    },
    {
      "rank": 4,
      "bridge_id": "MESH_D004195",
      "node_idx": 7587,
      "score": 18113.05,
      "cooccurrences_with_a": 865,
      "cooccurrences_with_c": 13986,
      "background_degree": 446104
    },
    {
      "rank": 5,
      "bridge_id": "MESH_D007004",
      "node_idx": 10256,
      "score": 14138.27,
      "cooccurrences_with_a": 12617,
      "cooccurrences_with_c": 332,
      "background_degree": 87780
    }
  ]
}
```
*Honest reading of this result: `disjointness_holds: false` — 104 articles already
discuss Metformin and Alzheimer's together, so this is bridge **ranking**, not a
pure Swanson disjoint discovery (DISC-010 requires this precondition to be
measured and reported, never assumed). The top-ranked bridge `MESH_D051379`
scores highest via massive co-occurrence with the Alzheimer's literature;
`MESH_D003924` (rank 2) is the diabetes-side bridge. Descriptor names are not
printed by the CLI; resolve UIs via the NLM MeSH browser.*

### Python API Usage
You can embed Swanson Discovery directly in Python programs:

```python
from pathlib import Path
from trashheap.graph.discovery import discover_literature_bridges

results = discover_literature_bridges(
    csr_dir=Path(".cache/pubmed/csr_full"),
    concept_a_id="MESH_D011928",  # Raynaud Disease
    concept_c_id="MESH_D005395",  # Fish Oils
    top_k=10,
)

print(f"Total bridges: {results['total_intermediate_bridges']:,}")
for bridge in results["top_bridges"]:
    print(f"#{bridge['rank']}: {bridge['bridge_id']} (Score: {bridge['score']})")
```
