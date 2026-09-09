# The Omniscient Trash Heap (`trashheap`) — Reference Implementation

> *All the sources. All the wisdom. Some of the trash.*

[![Tests](https://img.shields.io/badge/pytest-208%20passing-brightgreen)](tests/)
[![Architecture Conformance](https://img.shields.io/badge/Conformance-43%2F45%20Families%20(95.6%25)-blue)](artifacts/conformance_matrix.yaml)
[![Python](https://img.shields.io/badge/Python->=3.11-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/License-Apache--2.0-yellow.svg)](LICENSE)

---

## 🗑️ Why Does This Exist?

Like many developers, I was inspired by Andrej Karpathy's vision of an LLM-powered personal wiki: dump your messy notes into Markdown, let an LLM index and synthesize connections, and enjoy an effortless, organic, evolving knowledge base.

Naturally, I tried various implementations. And that is when the central problem became painfully obvious:

**They were entirely too easy to use.**

Where was the friction? Where was the crushing administrative burden? Why was there no formal epistemology? How could anyone sleep at night without an 8-step distributed transaction protocol just to save a Markdown file?

Simplicity, I realized, was a trap. What the world truly needed was an **aggressively over-engineered version that is vastly more complex — without providing any measurable added value.**

Hence, **The Omniscient Trash Heap**.

Named after Madame Trash Heap (*Marjory*) from *Fraggle Rock* — the sentient compost oracle who dispenses cryptic wisdom to anyone willing to dig through rotting cabbage — this project replaces "quick and easy note-taking" with a Byzantine fortress of deterministic compilation, multi-layer validation gates, and filesystem paranoia.

---

## 🏛️ Core Philosophy: "A Compiler, Not An Agent"

Most AI knowledge tools give an LLM direct write access to your files and pray it doesn't hallucinate your life's work into oblivion. 

The Omniscient Trash Heap rejects this. The LLM is treated as an untrusted, stochastic component quarantined inside a deterministic compilation pipeline:

```text
External Raw Source
       │
       ▼  (CSCC: Crash-Safe Source Capture Commit)
Immutable Staging (`raw/`)
       │
       ▼  (Sanitization, Delimiter Escaping & Fencing)
Extraction & Synthesis (Zero-Tool Capability Firewall)
       │
       ▼  (3-Point Granularity Filter: G1, G2, G3)
Candidate Proposal (`staging/discovery/`)
       │
       ▼  (Human Review & HMAC Approval Binding)
Promotion Engine (DPCP: SQLite WAL Journal)
       │
       ▼  (Atomic os.replace)
Canonical Knowledge Object (`personal/` or `engineering/`)
```

### The Unforgiving Axioms:
1. **Markdown is the Single Source of Truth:** All canonical notes are plain Markdown with strict YAML frontmatter (`extra: forbid`).
2. **All Databases are Disposable:** SQLite, DuckDB, Parquet, graph caches, and vector indexes are strictly derived artifacts. You can delete every `.db` and `.parquet` file in the repository, run `trashheap rebuild`, and everything regenerates bit-for-bit.
3. **Fail-Closed Everything:** If a file has an unknown YAML field, an unapproved wikilink, or a missing provenance hash, the entire operation halts with a deterministic error code (`E001`–`E499`).
4. **Zero Silent Fallbacks:** If DuckDB isn't installed, the system will not pretend it used Parquet; it will honestly declare itself degraded.

---

## 🧭 Epistemic Anatomy: How Taxonomy, Ontology, Facets & Types Fit Together

A fatal flaw of casual digital gardens and personal wikis is **metadata collapse**: flattening topics, file paths, properties, and relationships into a disorganized soup of unstructured `#tags` or arbitrary folders.

The Omniscient Trash Heap strictly enforces **orthogonality across distinct conceptual questions** ([`ARCHITECTURE.md §1.1`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/ARCHITECTURE.md) & [`DATA_MODEL.md §3`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/DATA_MODEL.md)):

| Dimension | Core Question | What It Governs | Canonical Registry | Concrete Example |
|---|---|---|---|---|
| **Taxonomy** | *Where in the tree does it live?* | Strict hierarchical directory structure on disk (`taxonomy_path`) | [`taxonomy_registry.yaml`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/schemas/registry/taxonomy_registry.yaml) | `02_formella_vetenskaper_matematik/` |
| **Object Type** | *What kind of knowledge is it?* | Structural archetype (19 types: Article, Concept, Specification, Incident, Workflow...) | [`object_registry.yaml`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/schemas/registry/object_registry.yaml) | `object_type: Concept` (`CON`) |
| **Domain** | *Which field of expertise?* | High-level knowledge domain | [`object_registry.yaml`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/schemas/registry/object_registry.yaml) | `domain: mathematics` |
| **Facets** | *Which orthogonal properties does it have?* | Cross-cutting dimensions (toolchain, language, audience, lifecycle, architecture) | [`facet_registry.yaml`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/schemas/registry/facet_registry.yaml) | `toolchain: [pytest]`, `audience: expert` |
| **Ontology** | *How does it connect to others?* | Directed, typed semantic graph edges with strict source/target constraints | [`relation_registry.yaml`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/schemas/registry/relation_registry.yaml) | `PART_OF`, `DEPENDS_ON`, `EXTENDS` |
| **Epistemology** | *How much can we trust it?* | Evidential foundation, verification status, and authority level | [`epistemic_registry.yaml`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/schemas/registry/epistemic_registry.yaml) | `evidence: empirical`, `verification: peer_verified` |

### How It Renders in a Canonical Knowledge Object

Every Markdown document isolates these dimensions within its strict YAML frontmatter:

```yaml
---
# 1. IDENTITY & TAXONOMY (Where does it live?)
id: PERS-CON-BAYESIAN_INFERENCE-0001
title: "Bayesian Inference"
scope: personal
taxonomy_path: "02_formella_vetenskaper_matematik"  # Resolves disk directory chain deterministically

# 2. CLASSIFICATION & DOMAIN (What is it?)
object_type: Concept                               # Registered in object_registry.yaml
domain: mathematics                                # Registered domain

# 3. FACETS (Orthogonal properties across domains)
language: [en, sv]
audience: advanced
lifecycle: stable

# 4. EPISTEMOLOGY & PROVENANCE (How do we know it's true?)
evidence: theoretical
verification: peer_verified
confidence: 0.95
source_type: book
source_refs: [SRC-BOOK-JAYNES_PROBABILITY_THEORY_2003]

# 5. ONTOLOGY (The directed semantic graph)
relations:
  PART_OF:
    - PERS-CON-PROBABILITY_THEORY-0001
  APPLIES_TO:
    - PERS-CON-DECISION_THEORY-0001
  EXTENDS:
    - PERS-CON-CONDITIONAL_PROBABILITY-0001
---

# Bayesian Inference

Bayesian inference is a method of statistical inference in which Bayes' theorem is used to update the probability for a hypothesis as more evidence or information becomes available...
```

### Why This Separation Prevents Chaos
1. **Taxonomy is a Tree, Not a Graph:** A file can only reside in one folder on disk. Taxonomy solves deterministic file placement and human filesystem browsability (`TAX-007`).
2. **Ontology is a Graph, Not a Folder:** A concept can relate to, implement, or contradict 15 other notes across engineering and personal domains without duplicating files or creating symlink jungles (`REL-001`–`REL-009`).
3. **Facets Slice Orthogonally:** You can query all objects where `toolchain: bazel` and `lifecycle: deprecated` across every directory in the repository without polluting your taxonomy with folders like `bazel_deprecated_things/`.
4. **Epistemology Protects Truth:** A speculative thought experiment (`evidence: anecdotal`) cannot masquerade as an audited production architecture standard (`evidence: formal_proof`), regardless of where it lives.

---

## ⚙️ Architectural Engines & Capabilities

Below is an overview of how the core subsystems interact to turn chaotic inputs into audited, queryable, interconnected knowledge:

| Engine | Primary Specifications | Role & Core Mechanism | Output Artifact |
|---|---|---|---|
| **Ingest & Promotion Pipeline** | [`INGEST-PIPELINE.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/INGEST-PIPELINE.md), [`INGEST.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/INGEST.md), [`REVIEW-PROMOTION.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/REVIEW-PROMOTION.md) | Captures untrusted raw sources, sanitizes prompts, routes scopes, stages candidate proposals, and executes atomic DPCP promotion. | Immutable `raw/` captures & canonical notes in `personal/` or `engineering/` |
| **Hybrid & Graph Retrieval** | [`RETRIEVAL.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/RETRIEVAL.md), [`GRAPH-RETRIEVAL.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/GRAPH-RETRIEVAL.md) | 8-stage search pipeline combining BM25, BFS graph traversal, offline dense vectors, and AST symbols via Reciprocal Rank Fusion ($k=60$). | Grounded, bounded Evidence Bundles with full cryptographic provenance |
| **Graph Intelligence** | [`GRAPH-INTELLIGENCE.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/GRAPH-INTELLIGENCE.md) | Read-only graph analysis: centrality, community detection, dialectic tension/contradiction discovery, cycle detection, and orphan audits. | Derived analytical indexes, graph metrics, and discovery proposals |
| **Discovery & Literature Engine** | [`DISCOVERY.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/DISCOVERY.md) | Governed candidate lifecycle management (`pending` $\to$ `promoted`), multi-predicate gap detection, and high-scale Swanson ABC literature discovery. | Candidate proposals (`discovery/candidates.jsonl`), audit logs, and literature bridge rankings |
| **Structural Knowledge Graph (SKG)** | [`STRUCTURAL-GRAPH.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/STRUCTURAL-GRAPH.md) | Deterministic AST code intelligence linking source code symbols (`FILE`, `CLASS`, `FUNCTION`) directly to knowledge specifications. | Code-to-spec traceability graph ([`structural_registry.yaml`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/schemas/registry/structural_registry.yaml)) |
| **Multi-Layer Validation Gate** | [`VALIDATION.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/VALIDATION.md) | 3-layer deterministic compilation gate checking schema syntax, relational invariants, and epistemic policies with 50+ fail-closed error codes. | Bit-for-bit conformance gate ([`conformance_matrix.yaml`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/conformance_matrix.yaml)) |

---

### 1. 📥 Ingest & Promotion Pipeline: The Quarantine Firewall

Most LLM tools give the model direct write permissions to your notes. The Omniscient Trash Heap treats the LLM as an unprivileged, stochastic worker quarantined behind strict transaction barriers:

```text
External Source (URL, Chat, PDF, Code)
       │
       ▼  (CSCC: Crash-Safe Source Capture Commit — dual fsync + parent directory barriers)
Immutable Capture (`raw/`)
       │
       ▼  (Sanitization & Prompt Injection Fencing — tag escaping + <untrusted_source> wrappers)
Extraction & Synthesis (Zero-Tool Capability Firewall)
       │
       ▼  (Scope Router: Cache ➔ Git Anchor ➔ Keyword Rules ➔ Fallback)
       │
       ▼  (3-Point Granularity Filter: Macro G1, Meso G2, Micro G3)
Candidate Proposal (`staging/discovery/` — pending status, 90-day TTL)
       │
       ▼  (Human-in-the-Loop Review & HMAC Signature Binding)
Promotion Engine (DPCP: SQLite WAL Journal with rollback)
       │
       ▼  (Atomic os.replace)
Canonical Knowledge Object (`personal/` or `engineering/`)
```

- **CSCC (Crash-Safe Source Capture Commit):** An 8-step protocol for capturing raw documents with cryptographic SHA-256 verification and dual `fsync` barriers across parent directory boundaries to survive power loss.
- **Prompt Injection Fencing:** Untrusted input is strictly enclosed in `<untrusted_source>` tags. Any occurrences of closing tags inside the raw source are sanitized to `&lt;/untrusted_source&gt;` prior to LLM inspection (`D105`).
- **Scope Router:** Deterministically assigns objects to `personal` or `engineering` scopes via a 4-tier decision cascade: cached decisions $\rightarrow$ repository anchor heuristics $\rightarrow$ keyword/toolchain rules $\rightarrow$ probabilistic fallback.
- **Granularity Gate (G1–G3):** Enforces proper document splitting so notes remain atomic rather than monolithic kitchen-sink files.
- **DPCP (Durable Promotion Commit Protocol):** A transactional journal with rollback to move approved candidate proposals into canonical storage using atomic `os.replace`.
- **Filesystem Paranoia:** The engine actively verifies filesystem capabilities. On native Linux/macOS filesystems (Tier 1: ext4, XFS, Btrfs, APFS), true POSIX atomic replacement is guaranteed; on WSL2 DrvFs mounts (`/mnt/c/`, Tier 2), it detects translation degradation and issues diagnostic warnings.

---

### 2. 🔍 Hybrid & Graph Retrieval: 4-Way Reciprocal Rank Fusion (RRF)

Searching your second brain shouldn't rely on fuzzy vector similarity alone. The system executes an 8-stage hybrid retrieval pipeline combining lexical precision with graph topology:

```text
User Query
    │
    ▼
1. Query Understanding (Intent, entities, explicit node IDs)
    │
    ▼
2. Scope & Facet Pre-filter (Scope isolation, domain, status, validity period)
    │
    ▼
3. Seed Retrieval (BM25 Okapi lexical search + 384-dim dense vectors) ──► Top-K Seeds
    │
    ▼
4. BFS Graph Expansion (Traverse typed ontology relations by category priority)
    │
    ▼
5. Post-Filter (Epistemic authority, confidence threshold, scope firewall)
    │
    ▼
6. 4-Way Hybrid Fusion (RRF k=60 combining Lexical + Vector + Subgraph + AST)
    │
    ▼
7. Hybrid Reranking (Cross-encoder scoring with deterministic RRF fallback)
    │
    ▼
8. Evidence Bundle (Bounded excerpts ≤ 250 chars with strict provenance hashes)
```

- **Lexical BM25 Okapi:** Exact terminology and code token matching ($k_1=1.5, b=0.75$) with $[0.0, 1.0]$ normalization.
- **BFS Graph Topology Expansion:** Explores neighborhood subgraphs starting from seed nodes. Graph traversal prioritizes structural (`PART_OF`), dependency (`DEPENDS_ON`), and engineering (`IMPLEMENTS`) links over generic associations.
- **Graph-Enhanced Scoring (`--graph-enhanced`):** Opt-in Layer 7 profile replacing simple depth decay with a versioned 6-dimensional graph feature vector ($\phi_1..\phi_6$: structural edge weight, semantic similarity, chunk co-occurrence, provenance proximity, hubness centrality, and community alignment) for superior subgraph ranking.
- **Offline Dense Vectors:** Opt-in 384-dimensional dense vectors scored via *max-over-chunks aggregation* (empirically settling the *SCALE-001* hypothesis by ensuring focused paragraphs inside longer notes are properly scored).
- **Evidence Bundles:** Queries generate self-contained, auditable JSON payloads (`evidence_bundle.json`) with character-bounded excerpts ($\le 250$ chars), node hashes, and relation lineages for verified grounding.

---

### 3. 🧠 Graph Intelligence: The Analytic Microscope

The Graph Intelligence engine operates strictly on read-only projections of the canonical graph ([`GRAPH-INTELLIGENCE.md`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/specs/GRAPH-INTELLIGENCE.md)), ensuring analytical passes never mutate human notes without explicit review:

- **Centrality & Bottleneck Detection:** Computes PageRank, betweenness, and degree centrality to surface high-leverage architectural nodes and identify single-point-of-failure concepts.
- **Community Clustering:** Runs graph partition algorithms (e.g. Leiden-style modularity) to discover emergent thematic clusters without breaking or polluting the directory taxonomy.
- **Dialectical Tension & Contradiction Discovery:** Surfaces conflicting assertions across documents (e.g. conflicting specifications or divergent definitions) by analyzing `CONTRADICTS`, `EXTENDS`, and `SUPERSEDES` relation edges.
- **Integrity & Cycle Auditing:** Enforces Directed Acyclic Graph (DAG) invariants on hierarchical relations (`PART_OF`, `INSTANCE_OF`) to eliminate circular logic (**GRAPH-001** / **E010**), while flagging orphaned notes that lack inbound or outbound connections.
- **Knowledge Gap Analysis:** Surfaces missing documentation links, unverified empirical claims (`evidence: unverified`), or dead ends in dependency chains.

```bash
# Generate canonical input manifest with bitwise immutability verification
uv run trashheap graph manifest --corpus-root /home/$USER/wiki/personal --output-dir derived

# Analyze topology, node metrics, and derive semantic edges
uv run trashheap graph analyze --corpus-root /home/$USER/wiki/personal --output-dir derived/graph
```

---

### 4. 🔭 Governed Discovery & Swanson Literature-Based Discovery

The Discovery engine ([`specs/DISCOVERY.md`](specs/DISCOVERY.md)) operates across both the curated local wiki and external high-scale knowledge graphs:

- **Governed Local Discovery (`trashheap discover`):**
  - **Automated Gap Scanning:** Evaluates 2-of-3 predicates ($A$: community partition, $B$: $\ge 3$ chunk co-occurrences, $C$: cosine similarity $\ge 0.80$) to surface hidden knowledge gaps without hallucination (`DISC-003`).
  - **Ontological Gap Auditing:** Automatically identifies unresolved incidents (`unresolved_event`) and unexecuted recommendations (`unimplemented_lesson`) (`DISC-004`).
  - **Formal Candidate Lifecycle:** Tracks candidate proposals through an immutable audit journal (`pending → reviewed → approved → promoted → expired` under 90-day TTL rules, `DISC-001`–`DISC-005`).
- **Large-Scale Literature-Based Discovery (Swanson ABC Model):**
  - Implements Don Swanson's classic literature discovery paradigm ($A \to B \to C$) directly over the **38.16 million node, 1.083 billion edge** biomedical graph.
  - Computes degree-normalized mutual information across intermediate concepts to uncover latent hypotheses, drug repurposing pathways, and cross-disciplinary bridges in $< 4$ seconds.

```bash
# Scan local corpus for topological and ontological gaps
uv run trashheap discover scan --corpus-root fixtures/canonical

# List pending discovery candidates
uv run trashheap discover list --status pending

# Review and approve a candidate proposal
uv run trashheap discover review DISC-GAP-ONTO-UNRESOLVED-ENG-INC-2026-0001 \
  --decision approved --actor "lead-architect" --reason "Formal resolution required"

# Promote approved candidate with cryptographic provenance
uv run trashheap discover promote DISC-GAP-ONTO-UNRESOLVED-ENG-INC-2026-0001 --actor "lead-architect"

# Run Swanson ABC literature discovery over 1.083B edges (Raynaud <-> Fish Oil)
uv run trashheap discover literature --concept-a MESH_D011928 --concept-c MESH_D005395 --top-k 5
```

---

### 5. 🧬 Structural Knowledge Graph (SKG): Code-to-Knowledge Traceability

Most software documentation drifts away from the implementation within weeks. The Structural Knowledge Graph constructs a deterministic bridge between source code and knowledge objects:

```text
Source Code (AST / Treesitter)          Canonical Knowledge Base
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│ File: trashheap/retrieval.py    │    │ Spec: RETRIEVAL.md              │
│   Class: HybridRetriever        │───►│   Feature: FET-HYBRID_RRF       │
│     Function: reciprocal_rank() │    │   Requirement: REQ-RRF-K60      │
└─────────────────────────────────┘    └─────────────────────────────────┘
          ▲                                       ▲
          └────────── IMPLEMENTS / VERIFIES ──────┘
```

- **Separated Registry:** Governed independently by [`structural_registry.yaml`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/schemas/registry/structural_registry.yaml) to ensure AST relations (`CALLS`, `IMPORTS`, `CONTAINS`, `TESTS_SYMBOL`) never contaminate the human semantic [`relation_registry.yaml`](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/schemas/registry/relation_registry.yaml).
- **Deterministic AST Extraction:** Machine-builds language syntax graphs from Python/TypeScript codebases.
- **Bidirectional Traceability:** Enables answering questions like *"Which architectural requirements are affected if we alter `HybridRetriever.fuse()`?"* or *"Which unit tests verify `REQ-RRF-K60`?"*.

```bash
# Index codebase AST into structural graph (1,129 nodes, 3,726 edges)
uv run trashheap structural index

# Discover candidate bridges between code symbols and architectural notes
uv run trashheap structural bridge scan

# Calculate transitive blast radius impact of modifying a symbol/file
uv run trashheap structural impact "repo=canonical;path=trashheap/models.py"
```

---

### 6. 🛡️ Multi-Layer Validation Gate: The Zero-Tolerance Compiler

Knowledge is continuously compiled and verified through a 3-layer deterministic validation gate:

- **Layer 1: Syntax & Schema Validation:** Validates Pydantic schemas, guarantees frontmatter keys use `extra: forbid`, verifies slug path determinism, and checks mandatory facet compliance per object type.
- **Layer 2: Relational & Graph Invariants:** Verifies allowed `source_types` and `target_types` per relation, guarantees inverse view uniqueness (**REL-008**), prevents duplicate edges, and detects DAG cycles.
- **Layer 3: Epistemic & Policy Drift:** Enforces that procedural objects (`Workflow`, `Procedure`) meet strict executability axioms (W1–W3), validates confidence scores, and prevents Agent Skills drift (`E050`).
- **Fail-Closed Error Hierarchy:** More than 50 deterministic error codes across partitioned namespaces (`E001`–`E050` base linter, `E101`–`E199` ingestion, `E201`–`E299` graph intelligence, `E301`–`E399` structural graph).

---

## 📜 Specifications & Contracts

This repository is the **executable reference implementation** (`trashheap`). The authoritative, normative specifications, 11 declarative YAML registries, and full architectural decision records live in:

👉 **[skelutten/omniscient-trash-heap-spec](https://github.com/skelutten/omniscient-trash-heap-spec)**
- [Normative Architectural Specifications (`specs/`)](https://github.com/skelutten/omniscient-trash-heap-spec/tree/master/specs)
- [Declarative YAML Registries (`schemas/registry/`)](https://github.com/skelutten/omniscient-trash-heap-spec/tree/master/schemas/registry)
- [Architectural Decision Log (`plans/DECISION_LOG.md`)](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/plans/DECISION_LOG.md)

---

## ⚡ Quickstart with `uv`

The project runs effortlessly with [`uv`](https://github.com/astral-sh/uv). No manual virtualenv management required:

```bash
# Sync dependencies (including opt-in Parquet/DuckDB staging backend)
uv sync --extra parquet

# Verify all 11 YAML schemas and registries load cleanly
uv run trashheap check-registries

# Run the full validation gate (130 tests across all 37 invariant families)
bash tools/check.sh
```

To install `trashheap` as a globally available tool on your machine:
```bash
uv tool install .
```

---

## 🏗️ Initialize a New Wiki (`trashheap init`)

To scaffold a brand-new, self-contained Knowledge Library instance anywhere on your system:

```bash
# Initialize in a new directory
trashheap init /home/$USER/my-wiki --name "My Personal Vault"

# Or initialize inside the current directory
cd /home/$USER/my-wiki
trashheap init
```

This creates:
- `schemas/registry/`: Full copies of all 10 canonical declarative YAML registries.
- `personal/` & `engineering/`: Structured taxonomic folder hierarchies.
- `staging/`: Intake (`raw/`) and candidate proposal (`discovery/`) staging buffers.
- `.agents/skills/trashheap/`: Open Agent Skills definition for autonomous coding agents.
- `PERS-DOC-WELCOME-0001.md`: A certified seed note that passes `trashheap lint` with 0 errors.
- `.gitignore` & `README.md`.

---

## 🤖 Agent Skills Integration (`.agents/skills/trashheap`)

The project implements the open **Agent Skills** specification (`agentskills.io` / `dot-agents.com`). AI coding agents (Antigravity, Claude Code, Cursor, Copilot) automatically discover and execute slash-commands (`/lint`, `/validate`, `/query`, `/show`, `/stage-lint`, `/ingest`, `/rebuild`).

### 1. Project-Level (Automatic)
The skill is generated directly inside the repository at:
```text
.agents/skills/trashheap/SKILL.md
```
To regenerate and verify it against current schemas and code:
```bash
uv run trashheap generate-skills
```

### 2. Global Installation (Available in any project folder)
To make the `trashheap` skills available across all your projects:
```bash
# Automatically install to ~/.agents/skills/trashheap/SKILL.md
uv run trashheap generate-skills --global

# Or create a symlink:
mkdir -p ~/.agents/skills
ln -sfn $(pwd)/.agents/skills/trashheap ~/.agents/skills/trashheap
```

---

## 📂 Data Layout & Workspace Boundaries

The system strictly enforces physical separation between code, test fixtures, and real wiki corpora:

1. **Engine & Implementation:**
   - Location: `/home/$USER/omniscient-trash-heap-impl` (this repository)
   - CLI package: `trashheap/`
   - Local test suites: `tests/`
2. **Canonical Reference Corpus (Test Fixtures):**
   - Location: `fixtures/canonical/`
   - Contains 20 certified reference Knowledge Objects used for conformance testing and CI gates. Standard default for `--corpus-root`.
3. **Converted Real-World Wiki:**
   - Location: `/home/$USER/wiki`
   - Contains **572 migrated articles** categorized under `personal/` taxonomy directories (e.g. `02_formella_vetenskaper_matematik/` [formal sciences & mathematics], `04_psykologi_kognition/` [psychology & cognition]).
   - Every note carries full YAML frontmatter and unbroken provenance back to its original source (`source_refs`).
4. **Historical Raw Capture:**
   - Location: `/home/$USER/wiki-old/wiki`
   - Preserved as a read-only historical snapshot.

---

## 🔍 Search & Retrieval (`query`)

The `query` command runs a 4-way hybrid Reciprocal Rank Fusion (RRF, $k=60$) search and returns a structured **Evidence Bundle** (JSON).

### Searching Your Real Wiki
Because the default root is `fixtures/canonical/`, specify `--corpus-root`:

```bash
uv run trashheap query "poker" --corpus-root /home/$USER/wiki --include-drafts
```

> **Why `--include-drafts`?**  
> Per migration rules ([Plan 60](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/plans/60-OLD-WIKI-MIGRATION.md) / Contract Rule 10), unreviewed legacy articles carry safety status `status: draft` so unmoderated text is not mistaken for verified truth. Use `--include-drafts` to include them in search queries.

### Advanced Search Flags
```bash
# Enable opt-in graph-enhanced hybrid retrieval (Plan 91 / GRAPH-RETRIEVAL.md)
# Replaces simple depth decay with versioned 6-dimensional graph feature scoring (φ1..φ6)
uv run trashheap query "game theory decision making" --corpus-root /home/$USER/wiki/personal --include-drafts --graph-enhanced

# Enable opt-in offline 384-dimensional dense vector embeddings
uv run trashheap query "game theory decision making" --corpus-root /home/$USER/wiki/personal --include-drafts --vector

# Combine both graph-enhanced scoring and dense vector retrieval
uv run trashheap query "poker strategy" --corpus-root /home/$USER/wiki/personal --include-drafts --graph-enhanced --vector

# Filter by scope
uv run trashheap query "architecture" --scope engineering

# Include full article body in the JSON payload
uv run trashheap query "poker" --corpus-root /home/$USER/wiki/personal --include-drafts --include-body
```

#### How `--graph-enhanced` Works
When `--graph-enhanced` is passed, the retrieval engine calculates a versioned 6-dimensional feature vector $\vec{\phi} = (\phi_1, \phi_2, \phi_3, \phi_4, \phi_5, \phi_6)$ for every node discovered during graph expansion:
- $\phi_1$ **Structural Ontology Weight:** Prioritizes typed relations (`PART_OF`, `DEPENDS_ON`, `IMPLEMENTS`) over loose associations.
- $\phi_2$ **Semantic Proximity:** Cosine similarity of dense embeddings between candidate and seed nodes.
- $\phi_3$ **Chunk Co-Occurrence:** Frequency of shared co-occurrence across 500-char text windows.
- $\phi_4$ **Provenance Proximity:** Overlap in source references (`source_refs`).
- $\phi_5$ **Hubness / In-Degree Centrality:** Subgraph-normalized structural importance.
- $\phi_6$ **Community Alignment:** Scored boost for notes sharing the same epistemic scope/community.

The resulting score is normalized into $[0.0, 1.0]$ and fused alongside lexical BM25 and dense vector rankings via Reciprocal Rank Fusion ($k=60$).

---

## 📖 Reading Notes (`show` & Direct Filesystem Access)

In the Evidence Bundle, `body_excerpt` is intentionally capped at $\le 250$ characters to save agent context budget. The complete note text is always available:

### Option 1: `trashheap show` (Recommended)
```bash
uv run trashheap show PERS-DOC-MIG_DOYLE_BRUNSON_SUPER_SYSTEM_1_2CC294-0001 --corpus-root /home/$USER/wiki
```

### Option 2: Direct Markdown file access
Open the note directly from the filesystem in any editor (`less`, `cat`, VS Code, Obsidian):
```bash
cat /home/$USER/wiki/personal/02_formella_vetenskaper_matematik/PERS-DOC-MIG_DOYLE_BRUNSON_SUPER_SYSTEM_1_2CC294-0001.md
```

---

## ⌨️ Shell Aliases (`~/.bashrc`)

Add these to your `~/.bashrc` for instant terminal access without typing paths:

```bash
alias mywiki='uv run --directory /home/$USER/omniscient-trash-heap-impl trashheap query --corpus-root /home/$USER/wiki --include-drafts'
alias mywikishow='uv run --directory /home/$USER/omniscient-trash-heap-impl trashheap show --corpus-root /home/$USER/wiki'
```

Then simply use:
```bash
mywiki "game theory"
mywikishow PERS-DOC-MIG_DOYLE_BRUNSON_SUPER_SYSTEM_1_2CC294-0001
```

---

## 🛠️ CLI Cheat Sheet (`trashheap`)

| Command | Description | Example |
|---|---|---|
| `init` | Scaffold a new self-contained wiki instance | `uv run trashheap init /home/$USER/my-wiki --name "My Vault"` |
| `query` | Hybrid RRF search (BM25 + graph + vector) | `uv run trashheap query "poker" --corpus-root ~/wiki/personal --include-drafts --graph-enhanced` |
| `show` | Display full content of a Knowledge Object | `uv run trashheap show <node-id> --corpus-root ~/wiki` |
| `lint` | 5-layer validation of Markdown files (`E001`–`E099`) | `uv run trashheap lint fixtures/canonical` |
| `validate` | Validate a single note within corpus context | `uv run trashheap validate <path/to/note.md>` |
| `check-registries` | Validate all 11 YAML schemas and registries | `uv run trashheap check-registries` |
| `staging` | Parquet/DuckDB staging status and equivalence | `uv run trashheap staging status` |
| `structural` | AST code graph indexing, bridging, and blast radius | `uv run trashheap structural impact "repo=canonical;path=trashheap/models.py"` |
| `graph` | Analyze graph topology, metrics, and derived edges | `uv run trashheap graph analyze --corpus-root ~/wiki/personal` |
| `discover` | Governed discovery, gap detection, and literature search | `uv run trashheap discover literature --concept-a MESH_D011928 --concept-c MESH_D005395` |
| `ingest` | Safe source ingestion with path-sandboxing | `uv run trashheap ingest <source-path> --profile document` |
| `stage-lint` | Inspect and validate staging candidate proposals | `uv run trashheap stage-lint` |
| `review` | Review candidate proposals before promotion | `uv run trashheap review list` |
| `promote` | Atomic transactional promotion via DPCP | `uv run trashheap promote <proposal-id> --actor user@example.com` |
| `bundle` | Export/import Knowledge Bundles / OKF v0.2 | `uv run trashheap bundle export --scope engineering --format okf` |
| `migrate` | Migrate legacy wikis under Rules 1–11 | `uv run trashheap migrate plan --source-dir ... --target-dir ...` |
| `rename` | Atomic rename with full graph/link propagation | `uv run trashheap rename --old-id ... --new-id ...` |
| `rebuild` | Throw away derived indexes and rebuild from Markdown | `uv run trashheap rebuild` |
| `status` | Display system status, durability, and knowledge debt | `uv run trashheap status` |
| `reap` | Purge expired proposals according to TTL rules | `uv run trashheap reap` |
| `conformance` | Generate the 45-family architectural conformance matrix | `uv run trashheap conformance` |

---

## 🧪 Verification, Testing & Reports

The entire system's integrity is guaranteed by automated test suites, validation gates, and empirical scale benchmarks:

```bash
# Run the complete validation gate (Ruff, pytest, and check-registries)
bash tools/check.sh

# Run pytest unit and integration tests (208 passing)
uv run pytest -v

# Run Ruff linter
uv run ruff check
```

### Comprehensive Technical & Test Reports:
- **[Comprehensive Test & Conformance Report (`docs/TEST_REPORT.md`)](docs/TEST_REPORT.md):** Detailed pass rates across all 208 tests, 45 conformance families, and PubMedQA retrieval evaluations.
- **[Examples & Discovery User Guide (`docs/DISCOVERY_AND_EXAMPLES.md`)](docs/DISCOVERY_AND_EXAMPLES.md):** Step-by-step practical recipes for note lifecycle, structural graphs, and Swanson literature discovery.
- **[Full PubMed 40M Scale Ingestion Report (`docs/FULL_PUBMED_40M_SCALE_REPORT.md`)](docs/FULL_PUBMED_40M_SCALE_REPORT.md):** Ingestion of 1,334 XML shards, 38.16M vertices, 1.083B edges, and out-of-core CSR binary compilation.
- **[Advanced Graph Topology & Discovery Report (`docs/PUBMED_ADVANCED_TOPOLOGY_EXPERIMENTS.md`)](docs/PUBMED_ADVANCED_TOPOLOGY_EXPERIMENTS.md):** Global top-20 citation hits, scale-free power law MLE ($\gamma=2.569$), and 4-hop CRISPR lineage tracing.

---

## 📜 License

Licensed under the **Apache License, Version 2.0**. See [`LICENSE`](LICENSE) for details.
