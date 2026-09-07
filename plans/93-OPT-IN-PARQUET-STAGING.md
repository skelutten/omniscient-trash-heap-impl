# Plan 93 — Opt-in Parquet/DuckDB staging

> **Status:** opt-in/blocked until dependencies are available
> **Prerequisite:** `03-SOURCE-INGESTION-SAFETY.md` green
> **Dependency:** DuckDB and PyArrow availability; SQLite remains the baseline backend.

## Scope

Implement the backend seam, schema/version parity, deterministic writes, atomic manifests and equivalence checks against the baseline staging backend.

## Gate

If dependencies are absent, report `blocked`/`degraded`; never substitute SQLite while claiming Parquet conformance. Acceptance requires dual-backend fixtures and recovery tests.

## Source material

- `../specs/INGEST-STAGING.md`, `VALIDATION.md`
