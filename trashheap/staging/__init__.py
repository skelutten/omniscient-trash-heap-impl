"""Opt-in Parquet/DuckDB Discovery Staging and Staging Seam (plans/93-OPT-IN-PARQUET-STAGING.md)."""

from trashheap.staging.backend import (
    StagingBackend,
    check_parquet_dependencies,
    get_staging_backend,
)
from trashheap.staging.baseline import BaselineStagingBackend
from trashheap.staging.equivalence import (
    sync_baseline_to_parquet,
    verify_backend_equivalence,
)
from trashheap.staging.models import (
    TARGET_SCHEMAS,
    BackendAvailability,
    BackendType,
    CommitIdentity,
    CommitResult,
    DSCPIntegrityError,
    EquivalenceDiff,
    EquivalenceReport,
    ParquetMigrationError,
    ParquetProposalRecord,
    StagingBackendStatus,
    StagingManifest,
    StagingTableInfo,
)
from trashheap.staging.parquet import (
    ParquetStagingBackend,
    commit_staged_parquet,
    reconcile_parquet_schema,
    recover_pending_dscp_transactions,
    run_schema_migrations,
)

__all__ = [
    "BackendAvailability",
    "BackendType",
    "BaselineStagingBackend",
    "CommitIdentity",
    "CommitResult",
    "DSCPIntegrityError",
    "EquivalenceDiff",
    "EquivalenceReport",
    "ParquetMigrationError",
    "ParquetProposalRecord",
    "ParquetStagingBackend",
    "StagingBackend",
    "StagingBackendStatus",
    "StagingManifest",
    "StagingTableInfo",
    "TARGET_SCHEMAS",
    "check_parquet_dependencies",
    "commit_staged_parquet",
    "get_staging_backend",
    "reconcile_parquet_schema",
    "recover_pending_dscp_transactions",
    "run_schema_migrations",
    "sync_baseline_to_parquet",
    "verify_backend_equivalence",
]
