"""Agent Skills generator and drift verification (AGENT-SKILLS.md, E050)."""

from pathlib import Path

SKILL_RELATIVE_PATH = Path(".agents/skills/trashheap/SKILL.md")

SKILL_TEMPLATE = """---
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
- **Flags:** `--corpus-root <path>`, `--include-drafts`, `--include-body`, `--vector`, `--graph-enhanced`, `--scope {personal|engineering}`, `--max-results <int>`, `--min-confidence <float>`, `--min-relevance <float>`, `--json`
- **Behavior:** Executes hybrid RRF retrieval across lexical index, structural graph, and dense vector embeddings, synthesizing answers with verified note citation links (`[[note-slug]]`). Returns bounded `body_excerpt` (<= 250 chars) and file `path`.

### 2.6 `/show <target>` — Full Knowledge Object Display
- **Command:** `trashheap show <node_id|file_path>` (or `python3 -m trashheap.cli show <target>`)
- **Flags:** `--corpus-root <path>`
- **Behavior:** Reads and displays the complete Markdown text and frontmatter of a Knowledge Object without truncation.

### 2.7 `/rebuild` — Disposable Index Reconstruction
- **Command:** `trashheap rebuild` (or `python3 -m trashheap.cli rebuild`)
- **Flags:** `--output-dir <path>`, `--json`
- **Behavior:** Wipes and idempotently reconstructs ephemeral SQLite metadata, inverted full-text index, and graph caches directly from Markdown notes.

## 3. Exit Codes & JSON Schema Contract

All commands support `--json` output producing standardized JSON payloads:
- `lint`: `{"status": "ok"|"error", "findings": [...]}`
- `validate`: `{"file": "...", "status": "ok"|"error", "findings": [...]}`
- `query`: Evidence bundle JSON adhering to `examples/evidence_bundle.json`
- `rebuild`: `{"status": "ok", "rebuilt_objects": <int>, "manifest": "..."}`
"""


def generate_agent_skills_content() -> str:
    """Return deterministic content of .agents/skills/trashheap/SKILL.md."""
    return SKILL_TEMPLATE.strip() + "\n"


def write_agent_skills(repo_root: Path) -> Path:
    """Write generated SKILL.md to repository."""
    target_path = repo_root / SKILL_RELATIVE_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    content = generate_agent_skills_content()
    target_path.write_text(content, encoding="utf-8")
    return target_path


def check_agent_skills(repo_root: Path) -> bool:
    """Check if SKILL.md is identical bit-for-bit (E050)."""
    target_path = repo_root / SKILL_RELATIVE_PATH
    if not target_path.exists():
        return False
    expected = generate_agent_skills_content()
    actual = target_path.read_text(encoding="utf-8")
    return expected == actual
