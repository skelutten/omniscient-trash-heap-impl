# The Omniscient Trash Heap (`trashheap`) — Reference Implementation

> *All the sources. All the wisdom. Some of the trash.*

[![Tests](https://img.shields.io/badge/pytest-130%20passed-brightgreen)](tests/)
[![Architecture Conformance](https://img.shields.io/badge/Conformance-37%2F37%20Families%20(100%25)-blue)](artifacts/conformance_matrix.yaml)
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
# Enable opt-in offline 384-dimensional dense vector embeddings
uv run trashheap query "game theory decision making" --corpus-root /home/$USER/wiki --include-drafts --vector

# Filter by scope
uv run trashheap query "architecture" --scope engineering

# Include full article body in the JSON payload
uv run trashheap query "poker" --corpus-root /home/$USER/wiki --include-drafts --include-body
```

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
| `query` | Hybrid RRF search (BM25 + graph + vector) | `uv run trashheap query "architecture"` |
| `show` | Display full content of a Knowledge Object | `uv run trashheap show <node-id> --corpus-root ~/wiki` |
| `lint` | 5-layer validation of Markdown files (`E001`–`E099`) | `uv run trashheap lint fixtures/canonical` |
| `validate` | Validate a single note within corpus context | `uv run trashheap validate <path/to/note.md>` |
| `check-registries` | Validate all 11 YAML schemas and registries | `uv run trashheap check-registries` |
| `staging` | Parquet/DuckDB staging status and equivalence | `uv run trashheap staging status` |
| `structural` | AST code graph indexing and blast radius impact | `uv run trashheap structural impact --symbol HybridRetriever` |
| `graph` | Analyze graph topology, centrality, and gaps | `uv run trashheap graph analyze` |
| `discover` | Discover duplicates, ontological/topological gaps | `uv run trashheap discover scan` |
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
| `conformance` | Generate the 37-family architectural conformance matrix | `uv run trashheap conformance` |

---

## 🧪 Verification & Testing

The entire system's integrity is guaranteed by automated test suites and validation gates:

```bash
# Run the complete validation gate (Ruff, pytest, and check-registries)
bash tools/check.sh

# Run pytest unit and integration tests (130 passing)
uv run pytest -v

# Run Ruff linter
uv run ruff check
```

---

## 📜 License

Licensed under the **Apache License, Version 2.0**. See [`LICENSE`](LICENSE) for details.
