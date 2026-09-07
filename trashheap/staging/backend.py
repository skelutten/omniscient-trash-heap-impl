"""Backend seam and abstraction for Staging layer (plans/93-OPT-IN-PARQUET-STAGING.md)."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from trashheap.staging.models import (
    BackendAvailability,
    BackendType,
    CommitResult,
    ParquetProposalRecord,
    StagingBackendStatus,
    StagingManifest,
)


def check_parquet_dependencies() -> BackendAvailability:
    """Check whether DuckDB and PyArrow are installed and importable."""
    try:
        import duckdb
        import pyarrow

        return BackendAvailability(
            available=True,
            backend=BackendType.PARQUET,
            status=StagingBackendStatus.READY,
            duckdb_version=getattr(duckdb, "__version__", "unknown"),
            pyarrow_version=getattr(pyarrow, "__version__", "unknown"),
            error_detail=None,
        )
    except ImportError as e:
        return BackendAvailability(
            available=False,
            backend=BackendType.PARQUET,
            status=StagingBackendStatus.DEGRADED,
            duckdb_version=None,
            pyarrow_version=None,
            error_detail=f"Optional dependencies DuckDB and/or PyArrow are missing: {e}",
        )


class StagingBackend(ABC):
    """Abstract staging backend seam (Plan 93)."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()

    @property
    @abstractmethod
    def backend_type(self) -> BackendType:
        """Return the concrete backend type."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether backend dependencies and prerequisites are satisfied."""
        pass

    @abstractmethod
    def get_status(self) -> BackendAvailability:
        """Return structured availability and status report."""
        pass

    @abstractmethod
    def commit_proposal(
        self,
        record: ParquetProposalRecord,
        target_table: str = "concept_proposals",
    ) -> CommitResult:
        """Atomically commit a proposal to staging with DSCP idempotency."""
        pass

    @abstractmethod
    def get_proposal(
        self,
        proposal_id: str,
        target_table: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a staged proposal by its identifier."""
        pass

    @abstractmethod
    def list_proposals(
        self,
        target_table: str = "concept_proposals",
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List proposals in deterministic order."""
        pass

    @abstractmethod
    def count_proposals(self, target_table: Optional[str] = None) -> int:
        """Return count of proposals in target table or total across all tables."""
        pass

    @abstractmethod
    def emit_manifest(self) -> StagingManifest:
        """Emit an atomic manifest of staging tables and counts."""
        pass

    @abstractmethod
    def run_migrations(self) -> None:
        """Execute type-safe dual-engine schema migrations without data loss."""
        pass

    @abstractmethod
    def recover_transactions(self) -> Dict[str, int]:
        """Recover pending DSCP transactions and purge orphan temporary files."""
        pass


def get_staging_backend(
    backend_type: Union[BackendType, str] = BackendType.PARQUET,
    workspace_root: Optional[Path] = None,
    require_available: bool = True,
) -> StagingBackend:
    """Factory creating staging backend with explicit degraded reporting.

    Rule: If Parquet dependencies are absent, report blocked/degraded; never
    substitute SQLite while claiming Parquet conformance (Plan 93 Gate).
    """
    if isinstance(backend_type, BackendType):
        b_type = backend_type
    else:
        b_type = BackendType(str(backend_type).lower())

    if b_type == BackendType.PARQUET:
        avail = check_parquet_dependencies()
        if not avail.available and require_available:
            raise RuntimeError(
                f"Parquet/DuckDB staging backend is degraded: {avail.error_detail}. "
                "Per Plan 93 Gate: Never substitute SQLite while claiming Parquet conformance."
            )
        from trashheap.staging.parquet import ParquetStagingBackend

        return ParquetStagingBackend(workspace_root=workspace_root)
    else:
        from trashheap.staging.baseline import BaselineStagingBackend

        return BaselineStagingBackend(workspace_root=workspace_root)
