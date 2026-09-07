---
name: trashheap
description: Comprehensive workflow and schema guide for ingesting sources, running lints, and executing query synthesis in The Omniscient Trash Heap.
version: 3.8.10
license: Apache-2.0
compatibility:
  python: ">=3.11"
  pydantic: ">=2.0"
metadata:
  repository: "https://github.com/daniel6651/llm-wiki-oe"
  specification: "LLM-WIKI-AGENT-SKILLS-001"
---

# The Omniscient Trash Heap — Agent Skills Interface

The Omniscient Trash Heap is an offline, deterministic, plain-text knowledge compilation system. Autonomous agents interacting with the knowledge base MUST follow the strict operational semantics defined herein.

## 1. System Invariants & Operational Model

1. **Deterministic Single-Pass Execution:** All operations load the corpus in a single pass (`read_count == len(corpus)`).
2. **Nine Metadata Categories (META-001):** Frontmatter contains only allowed categories: IDENTITY, ORGANIZATION, CLASSIFICATION, FACETS, EPISTEMOLOGY, PROVENANCE, TEMPORAL, GOVERNANCE, and ONTOLOGY. Extra fields are forbidden (`extra="forbid"`).
3. **Section Ownership Contract (OWN-001..003, BODY-003..004):**
   - Machine sections are updated deterministically.
   - At most one `## Notes` section is permitted per page, preserved byte-verbatim.
   - Unrecognized non-Notes sections fail closed (`E051`).
4. **Graph Degree Cap (GRAPH-004, W015):** Outbound links per node must not exceed $k = 20$.
5. **Deterministic Exit Codes:**
   - `0`: SUCCESS
   - `1`: VALIDATION_ERROR
   - `2`: STRICT_WARNING
   - `3`: CONFIG_OR_ARG_ERROR
   - `4`: NOT_FOUND

## 2. Standard Slash Commands

### 2.1 `/lint` — Whole Repository Integrity Check
- **Command:** `trashheap lint` (or `python3 -m trashheap.cli lint`, `tools/check.sh`)
- **Flags:** `--warnings-as-errors`, `--scope {personal|engineering}`, `--strict`, `--now YYYY-MM-DD`, `--json`
- **Behavior:** Validates all system invariants (`E001`–`E051`, `W001`–`W015`), YAML registry adherence, DAG acyclicity, taxonomy hierarchy, and link integrity.

### 2.2 `/validate <file>` — Single File Conformance Check
- **Command:** `trashheap validate <file_path>` (or `python3 -m trashheap.cli validate <file_path>`)
- **Flags:** `--json`
- **Behavior:** Validates frontmatter against Pydantic models for `object_type`, `taxonomy`, and `epistemology` within full corpus context (D25).

### 2.3 `/stage-lint` — Ingestion Staging Triage
- **Command:** `trashheap stage-lint` (or `python3 -m trashheap.cli stage-lint`)
- **Flags:** `--json`
- **Behavior:** Scans `staging/`, analyzes raw content, drafts suggested frontmatter, and detects candidate relations.

### 2.4 `/ingest <file>` — Governed Source Intake
- **Command:** `trashheap ingest <file_path> [--source-type {web|pdf|note|transcript}]` (or `python3 -m trashheap.cli ingest <file_path>`)
- **Flags:** `--source-type`, `--json`
- **Behavior:** Calculates SHA-256 content hash, places normalized raw representation into `staging/`, and registers source reference.

### 2.5 `/query <prompt>` — Evidence-Based Query Synthesis
- **Command:** `trashheap query "<prompt>"` (or `python3 -m trashheap.cli query "<prompt>"`)
- **Flags:** `--scope {personal|engineering}`, `--max-results <int>`, `--min-confidence <float>`, `--min-relevance <float>`, `--json`
- **Behavior:** Executes hybrid RRF retrieval across lexical index and structural graph, synthesizing answers with verified note citation links (`[[note-slug]]`).

### 2.6 `/rebuild` — Disposable Index Reconstruction
- **Command:** `trashheap rebuild` (or `python3 -m trashheap.cli rebuild`)
- **Flags:** `--output-dir <path>`, `--json`
- **Behavior:** Wipes and idempotently reconstructs ephemeral SQLite metadata, inverted full-text index, and graph caches directly from Markdown notes.

## 3. Exit Codes & JSON Schema Contract

All commands support `--json` output producing standardized JSON payloads:
- `lint`: `{"status": "ok"|"error", "findings": [...]}`
- `validate`: `{"file": "...", "status": "ok"|"error", "findings": [...]}`
- `query`: Evidence bundle JSON adhering to `examples/evidence_bundle.json`
- `rebuild`: `{"status": "ok", "rebuilt_objects": <int>, "manifest": "..."}`
