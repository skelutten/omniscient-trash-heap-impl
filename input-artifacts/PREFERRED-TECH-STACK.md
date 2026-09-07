# Preferred technology stack

> **Status:** implementation input artifact
> **Scope:** repository foundation and subsequent runtime plans
> **Normative boundary:** this document records implementation preferences and constraints; it does not replace `specs/` or `schemas/registry/`.

## Runtime baseline — required

- Python `>=3.11`.
- Pydantic v2 for typed runtime models.
- PyYAML for registry loading.
- pytest for automated tests.
- Python standard library by default; additional dependencies require explicit justification.

## Dependency and environment management — preferred

- `uv` for virtual environments, dependency resolution and reproducible installs.
- `pyproject.toml` as the single Python project configuration.
- Commit the lockfile once the runtime package and dependency set exist.

## Formatting and static checks — required for Python code

- Ruff for linting and formatting.
- Ruff applies to Python source and test files, not Markdown or specification examples.
- Exclude `specs/`, `schemas/`, `research/`, `plans/`, `external-specs/` and generated files from automatic formatting unless a specific check explicitly targets them.
- Automatic formatting must never rewrite normative specifications or vendored files.

## Git hooks — preferred

- `pre-commit` for fast local checks.
- Hooks mirror, but do not replace, the repository gate.
- Hooks must not mutate normative specifications automatically.

## Repository and CI platform — preferred

- Git for version control.
- GitHub for repository hosting and pull requests.
- GitHub Actions for clean-checkout CI.
- Local `tools/check.sh` remains the developer-facing verification entry point; CI should invoke the same gate rather than duplicate its logic.

## Optional and deferred technologies

- DuckDB/PyArrow: optional Parquet staging (`93-OPT-IN-PARQUET-STAGING.md`).
- Embedding model/vector index/cross-encoder: optional vector retrieval (`90-OPT-IN-VECTOR-RETRIEVAL.md`).
- NetworkX, igraph or equivalent: optional graph intelligence (`91-OPT-IN-GRAPH-INTELLIGENCE.md`).
- Tree-sitter/LSP and language grammars: optional structural graph (`92-OPT-IN-STRUCTURAL-GRAPH.md`).

## Selection rules

1. Required dependencies belong in the core installation.
2. Optional features must not make the core installation fail.
3. CI must reproduce the local gate from a clean checkout.
4. A new dependency requires a stated problem, normative/implementation owner, tests and fallback or degraded behavior where applicable.
5. Technology choices are implementation constraints, not replacements for normative contracts.
6. Version floors and externally significant tool versions must be pinned or recorded in project metadata when implementation begins.

## Initial foundation mapping

| Choice | Classification | First plan |
|---|---|---|
| Python `>=3.11` | Required runtime baseline | `01-REPOSITORY-FOUNDATION.md` |
| Pydantic v2 | Required core dependency | `01-REPOSITORY-FOUNDATION.md` |
| PyYAML | Required core dependency | `01-REPOSITORY-FOUNDATION.md` |
| pytest | Required development dependency | `01-REPOSITORY-FOUNDATION.md` |
| Ruff | Required quality tool | `01-REPOSITORY-FOUNDATION.md` |
| uv | Preferred package/environment manager | `01-REPOSITORY-FOUNDATION.md` |
| pre-commit | Preferred local hook runner | `01-REPOSITORY-FOUNDATION.md` |
| GitHub/GitHub Actions | Preferred hosting and CI platform | `05-CONNECTORS-OPERATIONS-CI.md` |
| DuckDB/PyArrow | Optional | `93-OPT-IN-PARQUET-STAGING.md` |
| Vector/graph/Tree-sitter tooling | Deferred opt-in | `90–92-*` |
