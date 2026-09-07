# Plan 92 — Opt-in structural graph

> **Status:** opt-in, deferred
> **Prerequisite:** `02-DETERMINISTIC-CORE.md` green
> **Dependency:** language toolchain decision, Tree-sitter/LSP availability and bounded parsing policy.

## Scope

Add structural code relations as a derived projection with stable IDs, parser-version metadata, invalidation and degraded behavior when a grammar is unavailable.

## Gate

No structural graph data may become canonical source truth. Acceptance requires fixture repositories, parser-versioned rebuilds and explicit unsupported-language reporting.

## Source material

- `../specs/STRUCTURAL-GRAPH.md`
