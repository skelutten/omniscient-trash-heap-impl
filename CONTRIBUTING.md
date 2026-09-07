# Contributing to The Omniscient Trash Heap

Welcome! This document outlines how **The Omniscient Trash Heap** (`trashheap`) is structured and how to navigate the specifications, registries, and implementation plans.

---

## 1. Core Architectural Axioms

Before proposing changes, ensure you understand the system's non-negotiable axioms:
1. **Axiom 1 (Canonical Sovereignty):** Markdown files + YAML frontmatter in Git are the absolute, single source of truth. No database holds irreplaceable state.
2. **Axiom 2 (Disposable Projections):** All indexes, vector caches, and graph projections can be deleted and deterministically rebuilt from scratch in seconds.
3. **Axiom 3 (Propose-Then-Promote):** LLMs may propose structured diffs; only deterministic validation gates and human governance review may promote changes into canonical storage.
4. **Axiom 4 (Declarative Registries):** Object types, relation rules, taxonomies, and governance policies are defined in `schemas/registry/*.yaml`, never hardcoded in application logic.

---

## 2. Repository Layout

- **`input-artifacts/`**: Product discovery and vision documents (`initiative.md`, `problem_statement.md`, `END-TO-END-CONTRACT-EXAMPLE.md`).
- **`PRD.md`**: Master Product Requirements Document, aligned with 21 functional requirements and testable acceptance criteria.
- **`specs/`**: Normative technical specifications (`ARCHITECTURE.md`, `DATA_MODEL.md`, `ONTOLOGY.md`, `VALIDATION.md`, `AGENT-SKILLS.md`, etc.).
- **`schemas/registry/`**: Declarative YAML registries defining object types, relations, taxonomies, and governance.
- **`plans/`**: Sequenced execution plans (`00-ROADMAP.md`, `01-REPOSITORY-FOUNDATION.md` through `05-CONNECTORS-OPERATIONS-CI.md`).
- **`plans/DECISION_LOG.md`**: Auditable record of every `Dnn` decision identifier cited in the specs, plus the EPI-SPEC-001 sign-offs authorising post-freeze changes. A new decision MUST be logged in the same commit that first cites its identifier.
- **`prompts/prd-pipeline/`**: Complete cognitive reasoning and review prompt suite.

---

## 3. Development & Verification Flow

1. **Verify Registries & Invariants:**
   - Run the validation gate: `bash tools/check.sh`
2. **Code Style & Toolchain:**
   - Python `>=3.11`, `pydantic v2`, `PyYAML`, `uv`, `pytest`, and `ruff`.
3. **Submitting Changes:**
   - Ensure all changes preserve the invariant rules in `specs/VALIDATION.md` (`E001`–`E031`, `E050`, `W001`–`W015`).
   - Any new relation or object type MUST be added to `schemas/registry/`, not hardcoded in Python.
