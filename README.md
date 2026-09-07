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
   - Location: `/home/daniel6651/omniscient-trash-heap-impl` (this repository)
   - CLI package: `trashheap/`
   - Local test suites: `tests/`
2. **Canonical Reference Corpus (Test Fixtures):**
   - Location: `fixtures/canonical/`
   - Contains 20 certified reference Knowledge Objects used for conformance testing and CI gates. Standard default for `--corpus-root`.
3. **Converted Real-World Wiki:**
   - Location: `/home/daniel6651/wiki`
   - Contains **572 migrated articles** categorized under `personal/` taxonomy directories (e.g. `02_formella_vetenskaper_matematik/` [formal sciences & mathematics], `04_psykologi_kognition/` [psychology & cognition]).
   - Every note carries full YAML frontmatter and unbroken provenance back to its original source (`source_refs`).
4. **Historical Raw Capture:**
   - Location: `/home/daniel6651/wiki-old/wiki`
   - Preserved as a read-only historical snapshot.

---

## 🔍 Search & Retrieval (`query`)

The `query` command runs a 4-way hybrid Reciprocal Rank Fusion (RRF, $k=60$) search and returns a structured **Evidence Bundle** (JSON).

### Searching Your Real Wiki
Because the default root is `fixtures/canonical/`, specify `--corpus-root`:

```bash
uv run trashheap query "poker" --corpus-root /home/daniel6651/wiki --include-drafts
```

> **Why `--include-drafts`?**  
> Per migration rules ([Plan 60](https://github.com/skelutten/omniscient-trash-heap-spec/blob/master/plans/60-OLD-WIKI-MIGRATION.md) / Contract Rule 10), unreviewed legacy articles carry safety status `status: draft` so unmoderated text is not mistaken for verified truth. Use `--include-drafts` to include them in search queries.

### Advanced Search Flags
```bash
# Enable opt-in offline 384-dimensional dense vector embeddings
uv run trashheap query "game theory decision making" --corpus-root /home/daniel6651/wiki --include-drafts --vector

# Filter by scope
uv run trashheap query "architecture" --scope engineering

# Include full article body in the JSON payload
uv run trashheap query "poker" --corpus-root /home/daniel6651/wiki --include-drafts --include-body
```

---

## 📖 Reading Notes (`show` & Direct Filesystem Access)

In the Evidence Bundle, `body_excerpt` is intentionally capped at $\le 250$ characters to save agent context budget. The complete note text is always available:

### Option 1: `trashheap show` (Recommended)
```bash
uv run trashheap show PERS-DOC-MIG_DOYLE_BRUNSON_SUPER_SYSTEM_1_2CC294-0001 --corpus-root /home/daniel6651/wiki
```

### Option 2: Direct Markdown file access
Open the note directly from the filesystem in any editor (`less`, `cat`, VS Code, Obsidian):
```bash
cat /home/daniel6651/wiki/personal/02_formella_vetenskaper_matematik/PERS-DOC-MIG_DOYLE_BRUNSON_SUPER_SYSTEM_1_2CC294-0001.md
```

---

## ⌨️ Shell Aliases (`~/.bashrc`)

Add these to your `~/.bashrc` for instant terminal access without typing paths:

```bash
alias mywiki='uv run --directory /home/daniel6651/omniscient-trash-heap-impl trashheap query --corpus-root /home/daniel6651/wiki --include-drafts'
alias mywikishow='uv run --directory /home/daniel6651/omniscient-trash-heap-impl trashheap show --corpus-root /home/daniel6651/wiki'
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
