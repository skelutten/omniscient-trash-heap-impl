"""Agent Skills generator and drift verification (AGENT-SKILLS.md, E050)."""

from pathlib import Path

from trashheap.constants import VERSION

SKILL_RELATIVE_PATH = Path(".agents/skills/trashheap/SKILL.md")

SKILL_TEMPLATE = """---
name: trashheap
description: Comprehensive workflow and schema guide for ingesting sources, running lints, and executing query synthesis in The Omniscient Trash Heap.
version: __VERSION__
license: Apache-2.0
compatibility:
  python: ">=3.11"
  pydantic: ">=2.0"
metadata:
  repository: "https://github.com/skelutten/omniscient-trash-heap-spec"
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
4. **Graph Degree Cap (GRAPH-004, W015):** Outbound links per node must not exceed $k = 20$. The cap is promotion-blocking: canonical promotion rejects candidates violating it.
5. **Deterministic Exit Codes:**
   - `0`: SUCCESS
   - `1`: VALIDATION_ERROR
   - `2`: STRICT_WARNING
   - `3`: CONFIG_OR_ARG_ERROR
   - `4`: NOT_FOUND

## 2. Standard Slash Commands

### 2.1 `/lint` — Whole Repository Integrity Check
- **Command:** `trashheap lint` (or `python3 -m trashheap.cli lint`, `tools/check.sh`)
- **Flags:** `--warnings-as-errors`, `--strict`, `--scope {personal|engineering}`, `--now YYYY-MM-DD`, `--registry-dir <path>`, `--no-check-skills`, `--json`
- **Behavior:** Validates all system invariants (`E001`–`E052`, `W001`–`W017`), YAML registry adherence, DAG acyclicity, taxonomy hierarchy, link integrity, link mirroring (VAL-011/W016), and Mermaid block syntax (VAL-012/W017).

### 2.2 `/validate <file>` — Single File Conformance Check
- **Command:** `trashheap validate <file_path>` (or `python3 -m trashheap.cli validate <file_path>`)
- **Flags:** `--json`
- **Behavior:** Validates frontmatter against Pydantic models for `object_type`, `taxonomy`, and `epistemology` within full corpus context (D25).

### 2.3 `/stage-lint` — Ingestion Staging Triage
- **Command:** `trashheap stage-lint` (or `python3 -m trashheap.cli stage-lint`)
- **Flags:** `--json`
- **Behavior:** Scans `staging/`, analyzes raw content, drafts suggested frontmatter, and detects candidate relations.

### 2.4 `/ingest <file>` — Governed Source Intake
- **Command:** `trashheap ingest <file_path> [--source-type <type>]` (or `python3 -m trashheap.cli ingest <file_path>`)
- **Flags:** `--source-type <type>`, `--staging-dir <dir>`, `--workspace-root <path>`, `--json`
- **Behavior:** Calculates SHA-256 content hash, places normalized raw representation into `staging/`, and registers source reference. `--source-type` defaults to `document` and must be a registered type from `source_registry.yaml` (e.g. `document`, `web_resource`).

### 2.5 `/query <prompt>` — Evidence-Based Query Synthesis
- **Command:** `trashheap query "<prompt>"` (or `python3 -m trashheap.cli query "<prompt>"`)
- **Flags:** `--corpus-root <path>`, `--registry-dir <path>`, `--scope {personal|engineering}`, `--seed-top-k <int>`, `--max-depth <int>`, `--max-results <int>`, `--min-confidence <float>`, `--min-relevance <float>`, `--include-drafts`, `--include-deprecated`, `--include-body`, `--vector`, `--graph-enhanced`, `--enforce-structural-gates`, `--claim <text>`, `--json`
- **Behavior:** Executes hybrid RRF retrieval across lexical index, structural graph, and dense vector embeddings, synthesizing answers with verified note citation links (`[[note-slug]]`). Returns bounded `body_excerpt` (<= 250 chars) and file `path`. With `--claim`, the Stage-2 propositional gate (RET-007) runs the RCVA protocol (RET-011): the claim is verified against retrieved passages with a deterministic entailment proxy and the bundle carries an `rcva` block; failed verification refuses with `INSUFFICIENT_EVIDENCE`.

### 2.6 `/show <target>` — Full Knowledge Object Display
- **Command:** `trashheap show <node_id|file_path>` (or `python3 -m trashheap.cli show <target>`)
- **Flags:** `--corpus-root <path>`
- **Behavior:** Reads and displays the complete Markdown text and frontmatter of a Knowledge Object without truncation.

### 2.7 `/rebuild` — Disposable Index Reconstruction
- **Command:** `trashheap rebuild` (or `python3 -m trashheap.cli rebuild`)
- **Flags:** `--output-dir <path>`, `--json`
- **Behavior:** Wipes and idempotently reconstructs disposable projections directly from Markdown notes: the graph projection (`graph.json`), the metadata catalog, and (with `--vector`) the persisted vector index consumed by `query --vector`.

### 2.8 `/init` — Knowledge Library Scaffolding
- **Command:** `trashheap init [path]` (or `trashheap new [path]`)
- **Flags:** `--name <str>`, `--scope {personal|engineering|all}`, `--author <id>`, `--force`, `--json`
- **Behavior:** Scaffolds a complete, self-contained Knowledge Library wiki instance with all 10 YAML registries, taxonomy trees, Agent Skills, .gitignore, and a certified starter note that passes multi-layer linting with 0 errors. Root instruction files (`AGENTS.md`, existing `CLAUDE.md`/`.cursorrules`) receive a machine-managed knowledge-reference block strictly confined to `<!-- TRASHHEAP:START/END -->` fences (DISC-009); human-owned content outside the fence is never touched.

### 2.9 `/discover literature` — Swanson ABC Literature-Based Discovery
- **Command:** `trashheap discover literature --concept-a <MESH_ID> --concept-c <MESH_ID>`
- **Flags:** `--csr-dir <path>` (compiled full-scale CSR artifact directory), `--top-k <int>`, `--max-background-degree <int>`, `--json`
- **Behavior:** Runs Swanson-style A→B→C discovery over the memory-mapped citation/MeSH CSR graph: ranks intermediate bridges B by the degree-normalized co-occurrence score `(co_A·co_C)/√deg_B`, derives the MeSH partition from `node_mapping.parquet` (no hardcoded boundaries), and reports the measured disjointness precondition (`articles_discussing_both`).

## 2A. Agent Harness Obligations (VAL-014 / E052)

Agent execution harnesses driving `trashheap` MUST wrap tool calls in the
runaway-loop circuit breaker exported by this package:

```python
from trashheap.runaway import RunawayLoopGuard, RunawayLoopError

guard = RunawayLoopGuard()  # trips at >= 5 identical signatures in the sliding ring
guard.observe("trashheap query", {"prompt": p}, failed=not ok, tokens_spent=n, budget=b)
```

On `RunawayLoopError` (E052) the harness MUST abort the degenerate loop rather
than continue burning compute (The 40% Rule).

## 3. Exit Codes & JSON Schema Contract

All commands support `--json` output producing standardized JSON payloads:
- `init`: `{"status": "ok", "path": "...", "name": "...", "created_files": [...], "created_directories": [...]}`
- `lint`: `{"status": "ok"|"error", "findings": [...]}`
- `validate`: `{"file": "...", "status": "ok"|"error", "findings": [...]}`
- `query`: Evidence bundle JSON adhering to `examples/evidence_bundle.json`
- `rebuild`: `{"status": "ok", "rebuilt_objects": <int>, "manifest": "..."}`
"""


def generate_agent_skills_content() -> str:
    """Return deterministic content of .agents/skills/trashheap/SKILL.md."""
    return SKILL_TEMPLATE.replace("__VERSION__", VERSION).strip() + "\n"


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
