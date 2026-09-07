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

- **`trashheap/`**: Core executable Python package (CLI, retrieval, linter, graph intelligence, AST analysis, staging).
- **`tests/`**: Pytest test suite covering all 37 invariant families across Layers 1–5.
- **`fixtures/`**: Certified reference Knowledge Objects (`fixtures/canonical/`) and adversarial security payloads (`fixtures/adversarial/`).
- **`schemas/registry/`**: Declarative YAML registries defining object types, relations, taxonomies, and governance.
- **`specs/` & `plans/` & `PRD.md`**: Authoritative normative specifications, requirements, and implementation plans are maintained in the companion specification repository: [`skelutten/omniscient-trash-heap-spec`](https://github.com/skelutten/omniscient-trash-heap-spec).

---

## 3. Development & Verification Flow

1. **Verify Registries & Invariants:**
   - Run the validation gate: `bash tools/check.sh`
2. **Code Style & Toolchain:**
   - Python `>=3.11`, `pydantic v2`, `PyYAML`, `uv`, `pytest`, and `ruff`.
3. **Submitting Changes:**
   - Ensure all changes preserve the invariant rules in `specs/VALIDATION.md` (`E001`–`E031`, `E050`, `W001`–`W015`).
   - Any new relation or object type MUST be added to `schemas/registry/`, not hardcoded in Python.
