# The Omniscient Trash Heap Specification: Agent Skills Standard Integration

> **Part of**: The Omniscient Trash Heap Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-AGENT-SKILLS-001`
> **Version**: `1.0.0`
> **Status**: `PROPOSED`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Normative owner**: This document owns the agent skill generation contract, slash command specifications, and compliance rules with the Agent Skills standard (`agentskills.io` / `dot-agents.com`).
> **Related documents**: `ARCHITECTURE.md`, `VALIDATION.md`, `TOOL-INTEGRATION.md`, `specs/README.md`

---

## 1. Scope & Objective

This specification formalizes the **Agent Skills standard** interface for autonomous coding and reasoning agents interacting with The Omniscient Trash Heap knowledge base.

### Primary Directives:
1. **No Hand-Edited Placeholders:** The skill file `.agents/skills/trashheap/SKILL.md` MUST NOT be manually maintained. It is a compiled, generated artifact emitted deterministically by `trashheap generate-skills` (or `tools/generate_skills.py`).
2. **Strict Standard Compliance:** The generated `SKILL.md` MUST strictly adhere to the [Agent Skills Specification](https://agentskills.io/specification) and [dot-agents standard](https://www.dot-agents.com/) format, including YAML frontmatter and structured command documentation.
3. **Execution Invariance:** Agents executing workflows (`/ingest`, `/stage-lint`, `/lint`, `/validate`, `/query`, `/rebuild`) must invoke deterministic underlying CLI entry points with standardized exit codes.

---

## 2. Normative Frontmatter & Metadata Contract

The generated `.agents/skills/trashheap/SKILL.md` MUST begin with YAML frontmatter conforming to this schema:

```yaml
---
name: trashheap
description: Comprehensive workflow and schema guide for ingesting sources, running lints, and executing query synthesis in The Omniscient Trash Heap.
version: 3.8.10
license: Apache-2.0
compatibility:
  python: ">=3.11"
  pydantic: ">=2.0"
metadata:
  repository: "https://github.com/skelutten/omniscient-trash-heap-spec"
  specification: "LLM-WIKI-AGENT-SKILLS-001"
---
```

---

## 3. Standard Slash Commands Contract

The generated skill MUST specify the following 6 core operations:

### 3.1 `/lint` — Whole Repository Integrity Check
- **Command:** `python3 -m trashheap.cli lint` (or `tools/check.sh`)
- **Flags:** `--warnings-as-errors`, `--strict`, `--scope {personal|engineering}`, `--now YYYY-MM-DD`, `--registry-dir <path>`, `--no-check-skills`, `--json`
- **Behavior:** Validates all system invariants (`E001`–`E051`, `W001`–`W015`), YAML registry adherence, DAG acyclicity, and broken `[[wiki-link]]` targets.

### 3.2 `/validate <file>` — Single File Conformance Check
- **Command:** `python3 -m trashheap.cli validate <file_path>`
- **Behavior:** Validates frontmatter against Pydantic models for `object_type`, `taxonomy`, and `epistemology`.

### 3.3 `/stage-lint` — Ingestion Staging Triage
- **Command:** `python3 -m trashheap.cli stage-lint`
- **Behavior:** Scans `staging/`, analyzes raw content, drafts suggested frontmatter, and detects candidate relations.

### 3.4 `/ingest <file>` — Governed Source Intake
- **Command:** `python3 -m trashheap.cli ingest <file_path> [--source-type <type>]`
- **Flags:** `--source-type <type>`, `--staging-dir <dir>`, `--workspace-root <path>`, `--json`
- **Behavior:** Calculates SHA-256 content hash, places normalized raw representation into `staging/`, and registers source reference. `--source-type` defaults to `document` and must be a registered type from `source_registry.yaml` (e.g. `document`, `web_resource`).

### 3.5 `/query <prompt>` — Evidence-Based Query Synthesis
- **Command:** `python3 -m trashheap.cli query "<prompt>"`
- **Flags:** `--corpus-root <path>`, `--registry-dir <path>`, `--scope {personal|engineering}`, `--seed-top-k <int>`, `--max-depth <int>`, `--max-results <int>`, `--min-confidence <float>`, `--min-relevance <float>`, `--include-drafts`, `--include-deprecated`, `--include-body`, `--vector`, `--graph-enhanced`, `--enforce-structural-gates`, `--json`
- **Behavior:** Executes hybrid RRF retrieval across lexical index, structural graph, and dense vector embeddings, synthesizing answers with verified note citation links (`[[note-slug]]`). Returns bounded `body_excerpt` ($\le 250$ chars) and file `path`.

### 3.6 `/show <target>` — Full Knowledge Object Display
- **Command:** `python3 -m trashheap.cli show <node_id|file_path>`
- **Flags:** `--corpus-root <path>`
- **Behavior:** Reads and displays the complete Markdown text and frontmatter of a Knowledge Object without truncation.

### 3.7 `/rebuild` — Disposable Index Reconstruction
- **Command:** `python3 -m trashheap.cli rebuild`
- **Behavior:** Wipes and idempotently reconstructs ephemeral SQLite metadata, inverted full-text index, and graph caches directly from Markdown notes.

### 3.8 `/init [path]` — Knowledge Library Scaffolding
- **Command:** `python3 -m trashheap.cli init [path]` (or `trashheap new [path]`)
- **Flags:** `--name <str>`, `--scope {personal|engineering|all}`, `--author <id>`, `--force`, `--json`
- **Behavior:** Scaffolds a complete, self-contained Knowledge Library wiki instance with all 10 YAML registries, taxonomy trees, Agent Skills, .gitignore, and a certified starter note that passes multi-layer linting with 0 errors.

---

## 4. Code Generation & Conformance Verification

- **Emitter Script:** `scripts/generate_agent_skills.py` (invoked via `python3 scripts/generate_agent_skills.py` or CLI `trashheap generate-skills`).
- **Verification Gate (Linter Rule `E050`):** Running the repository linter checks that `.agents/skills/trashheap/SKILL.md` is bit-for-bit identical to the generated output. If drift is detected, `E050: AgentSkillDriftError` is raised.

### 4.1 Installation Scopes (Repository & Global)
- **Repository Scope:** The skill definition lives in `.agents/skills/trashheap/SKILL.md` within the project root. AI coding assistants (e.g. Antigravity, Claude Code, Cursor) automatically discover it when operating in this workspace.
- **Global User Scope:** To make the skill available across all directories and projects on the machine, install it globally using `trashheap generate-skills --global` (or `python3 scripts/generate_agent_skills.py --global`). This writes `~/.agents/skills/trashheap/SKILL.md`. Alternatively, a symlink can be created:
  ```bash
  ln -sfn $(pwd)/.agents/skills/trashheap ~/.agents/skills/trashheap
  ```
