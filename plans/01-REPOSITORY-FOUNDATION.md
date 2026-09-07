# Plan 01 — Repository foundation

> **Status:** complete (2026-09-07)
> **Prerequisite:** none
> **Next:** `02-DETERMINISTIC-CORE.md`

## Goal

Create the smallest installable and testable repository boundary before implementing domain behavior.

## Scope

1. Create `pyproject.toml` with Python `>=3.11`, Pydantic v2, PyYAML, pytest and ruff.
2. Create package skeleton under `trashheap/` and scriptable, non-interactive CLI entry point with deterministic exit codes and structured output support (`--json`).
3. Create `tests/__init__.py` and a package-import smoke test.
4. Create `tools/check.sh` and configure ruff to exclude Markdown/specification trees.
5. Implement registry loading for the registries in `schemas/registry/`.
6. Validate `spec_ownership.yaml`, `threshold_policy.yaml`, source taxonomy paths and unique registry keys.
7. Add golden registry fixtures and stable error output.
8. Add `trashheap --version` and `trashheap check-registries` smoke tests.
9. Provide root `README.md` user documentation covering quickstart via `uv`, data layout, storage boundaries (`fixtures/canonical/` vs external production wikis), and CLI command workflows.

The registry slice MUST include the current actor, epistemic, facet, source,
ownership and threshold registries, not only the original object/relation/
taxonomy/governance quartet. `spec_ownership.yaml` and `threshold_policy.yaml`
are declarative policy inputs; loading them MUST NOT be reported as runtime
enforcement or calibration evidence.

## Acceptance

```text
clean install → package import → registry load → registry validation → CLI smoke test
```

Required evidence:

- clean virtual environment install succeeds;
- all current registry YAML files parse;
- ownership families have one owner and existing owner paths;
- threshold IDs are unique and policy references resolve;
- `pytest` and `tools/check.sh` pass;
- runtime status remains conservative.

## Non-goals

No canonical object linter, ingestion, promotion, retrieval backend, migration or optional feature implementation belongs here.

## Source material

- `../input-artifacts/PREFERRED-TECH-STACK.md`
- `../specs/VALIDATION.md`
- `../schemas/registry/spec_ownership.yaml`
