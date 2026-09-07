# Plan 02 — Deterministic core & Agent Skills Generation

> **Status:** complete
> **Prerequisite:** `01-REPOSITORY-FOUNDATION.md` green
> **Next:** `03-SOURCE-INGESTION-SAFETY.md`

## Goal

Implement the canonical Knowledge Object path: parse one object, validate it deterministically, maintain relations, enforce link degree caps, propagate renames atomically, generate compliant Agent Skills definitions, and provide baseline retrieval.

## Work packages

1. Pydantic frontmatter model with nine metadata categories and `extra=forbid`.
2. One-read corpus loader with read-count assertion.
3. Layer 1–5 validation and stable findings (`code`, `field`, `message`, `suggestion`).
4. Registry-driven enums, taxonomy slug/path resolution and relation graph checks.
5. Dynamic link degree cap enforcement ($k \le 20$) with `W015: HighDegreeWarning` (`FR-9`).
6. Atomic rename and backlink propagation tool across Markdown files and `graph.json` (`FR-8`).
7. Canonical authoring and body regeneration with `OWN-001..003`, `BODY-003..004` and `W014`.
8. Baseline lexical/RRF retrieval and evidence bundle shape (incorporating D93 graph fusion condition: graph contributes to RRF only when depth > 0 reached, with depth 0 reported as absent; and D94 per-parameter config precedence: CLI flag > `retrieval:` config block > defaults with `parameters_origin` reporting).
9. Agent Skills generation (`scripts/generate_agent_skills.py`) emitting `.agents/skills/trashheap/SKILL.md` compliant with `agentskills.io` / `dot-agents.com` (`specs/AGENT-SKILLS.md`).
10. Non-interactive, scriptable CLI commands for lint, validate, stage-lint, ingest, query (stateless execution with zero disk context accumulation), rebuild, generate-skills, and generated-artifact drift checks (`E050`), with machine-readable `--json` output, deterministic exit codes, and documented schema for rebuildable projections.
11. Conformance fixtures for positive objects, Agent Skill compliance, and important error codes.

## Stop point

```text
parse → validate → link → enforce degree cap → lint → generate-skills → author/query
```

## Acceptance

- a clean fixture corpus validates;
- `.agents/skills/trashheap/SKILL.md` is emitted deterministically and validates against `agentskills.io` schema;
- renaming an entity updates all backlinks atomically with zero broken references (`AC-3`);
- high-degree nodes (>20 outbound links) trigger linter warnings;
- maximally broken objects return the complete expected finding set;
- corpus files are read exactly once;
- unknown sections fail closed and `## Notes` is preserved byte-for-byte;
- repeated deterministic runs produce identical output;
- targeted tests and the local gate pass.

## Non-goals

No Universal Source capture, connector, promotion workflow, migration or opt-in graph/vector backend.

## Source material

- `../specs/ARCHITECTURE.md`, `DATA_MODEL.md`, `ONTOLOGY.md`, `VALIDATION.md`, `SCHEMA.md`, `RETRIEVAL.md`, `AGENT-SKILLS.md`
