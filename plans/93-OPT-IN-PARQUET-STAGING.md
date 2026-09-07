# Plan 93 — Opt-in Parquet/DuckDB staging

> **Status:** complete, verified (D113)
> **Prerequisite:** `03-SOURCE-INGESTION-SAFETY.md` green
> **Dependency:** DuckDB and PyArrow installed in `.venv` under `[project.optional-dependencies.parquet]`.

## Scope

Implement the backend seam, schema/version parity, deterministic writes, atomic manifests and equivalence checks against the baseline staging backend.

## Gate

If dependencies are absent, report `blocked`/`degraded`; never substitute SQLite while claiming Parquet conformance. Acceptance requires dual-backend fixtures and recovery tests.

## Deliverables & Implementation (D113)

- **Pluggable Backend Seam (`trashheap/staging/`):** `StagingBackend` ABC, `check_parquet_dependencies()`, `get_staging_backend()`, `BaselineStagingBackend` (YAML/SQLite), and `ParquetStagingBackend` (DuckDB/PyArrow).
- **Dependency Detection & Degradation:** Enforces the Plan 93 gate. When dependencies are missing, `check_parquet_dependencies()` returns `is_available: False` with degraded status and never fakes Parquet conformance.
- **Type-Safe Dual-Engine Schema Evolution:** Managed SQLite migrations (PRAGMA `user_version` 1 -> 2 -> 3) and `TARGET_SCHEMAS` parity for `concept_proposals`, `ambiguous_scope`, `rejected_low_quality` per `specs/INGEST-STAGING.md` §7.2; emits `state/schema_version.json`.
- **SQL Path Sanitization:** `_validated_sql_path` prevents SQL injection and path traversal (`E114`).
- **Durable Staged Commit Protocol (DSCP §3.3):** Atomic merge, `os.fsync` durability, idempotency (same hash = no-op, divergent hash = `DSCPIntegrityError` `E114`).
- **Deterministic Crash Recovery:** `recover_pending_dscp_transactions` covers CP-1, CP-2/CP-3, CP-4/CP-5, and CP-6.
- **Atomic Manifest Emission:** `staging/discovery/state/manifest.json` with per-table exact row counts, column lists, and exact-byte SHA-256 hashes.
- **Dual-Backend Equivalence & Sync:** `verify_backend_equivalence` and `sync_baseline_to_parquet`.
- **CLI Commands:** `trashheap staging status|sync|verify-equivalence|manifest|recover`.
- **Verification:** 12 tests in `tests/test_parquet_staging.py` passing; verified via `tools/check.sh`.

## Source material

- `../specs/INGEST-STAGING.md`, `VALIDATION.md`, `specs/INGEST-ADAPTERS.md` §3.3

