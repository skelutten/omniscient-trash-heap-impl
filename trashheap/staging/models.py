"""Data models for Staging Backend, DSCP Protocol, and Parquet Tables (INGEST-STAGING.md §7, §9)."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


def current_iso_timestamp() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


class BackendType(str, Enum):
    """Available staging backend implementations."""

    BASELINE = "baseline"  # Filesystem YAML + SQLite journal
    PARQUET = "parquet"  # DuckDB + Parquet discovery tables


class StagingBackendStatus(str, Enum):
    """Status of staging backend."""

    READY = "ready"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class BackendAvailability(BaseModel):
    """Availability inspection result for staging backend."""

    model_config = ConfigDict(extra="forbid")

    available: bool
    backend: BackendType
    status: StagingBackendStatus
    duckdb_version: Optional[str] = None
    pyarrow_version: Optional[str] = None
    error_detail: Optional[str] = None


class DSCPIntegrityError(Exception):
    """Raised when DSCP integrity, collision, or disallowed path is encountered (E114)."""

    pass


class ParquetMigrationError(Exception):
    """Raised when Parquet schema migration fails (E111)."""

    pass


@dataclass(frozen=True)
class CommitIdentity:
    """Identity tuple (P, S, T) for DSCP staged commit (INGEST-CORE-012, E114)."""

    proposal_id: str
    input_sha256: str
    target_table: str


# Canonical column definitions per INGEST-STAGING.md §7.2
TARGET_SCHEMAS: Dict[str, List[tuple[str, str, str]]] = {
    "concept_proposals": [
        ("proposal_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_revision", "INTEGER", "1::INTEGER"),
        ("ingestion_id", "VARCHAR", "''::VARCHAR"),
        ("schema_version", "VARCHAR", "'0.5.2'::VARCHAR"),
        ("inferred_scope", "VARCHAR", "'ambiguous'::VARCHAR"),
        ("scope_confidence", "DOUBLE", "0.0::DOUBLE"),
        ("scope_method", "VARCHAR", "'historical_unknown'::VARCHAR"),
        ("scope_status", "VARCHAR", "'inferred'::VARCHAR"),
        ("cross_scope", "BOOLEAN", "FALSE::BOOLEAN"),
        ("inferred_domain", "VARCHAR", "''::VARCHAR"),
        ("inferred_taxonomy_id", "VARCHAR", "''::VARCHAR"),
        ("inferred_facets", "VARCHAR", "'{}'::VARCHAR"),
        ("epistemic_status", "VARCHAR", "'inferred'::VARCHAR"),
        ("evidence_level", "VARCHAR", "'trajectory_observed'::VARCHAR"),
        ("validation_status", "VARCHAR", "'unverified'::VARCHAR"),
        ("promotion_status", "VARCHAR", "'staged'::VARCHAR"),
        ("provenance", "VARCHAR", "'{}'::VARCHAR"),
        ("evidence_bundle", "VARCHAR", "'{}'::VARCHAR"),
        ("incident", "VARCHAR", "NULL::VARCHAR"),
        ("observation", "VARCHAR", "NULL::VARCHAR"),
        ("lesson", "VARCHAR", "NULL::VARCHAR"),
        ("workflow", "VARCHAR", "NULL::VARCHAR"),
        ("model_confidence", "DOUBLE", "0.0::DOUBLE"),
        ("quality_score", "DOUBLE", "NULL::DOUBLE"),
        ("status", "VARCHAR", "'pending'::VARCHAR"),
        ("created_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP"),
        ("expires_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP + INTERVAL '90 days'"),
        ("input_sha256", "VARCHAR", "''::VARCHAR"),
    ],
    "ambiguous_scope": [
        ("proposal_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_revision", "INTEGER", "1::INTEGER"),
        ("ingestion_id", "VARCHAR", "''::VARCHAR"),
        ("schema_version", "VARCHAR", "'0.5.2'::VARCHAR"),
        ("inferred_scope", "VARCHAR", "'ambiguous'::VARCHAR"),
        ("scope_confidence", "DOUBLE", "0.0::DOUBLE"),
        ("scope_method", "VARCHAR", "'historical_unknown'::VARCHAR"),
        ("scope_status", "VARCHAR", "'inferred'::VARCHAR"),
        ("cross_scope", "BOOLEAN", "FALSE::BOOLEAN"),
        ("inferred_domain", "VARCHAR", "''::VARCHAR"),
        ("inferred_taxonomy_id", "VARCHAR", "''::VARCHAR"),
        ("inferred_facets", "VARCHAR", "'{}'::VARCHAR"),
        ("epistemic_status", "VARCHAR", "'inferred'::VARCHAR"),
        ("evidence_level", "VARCHAR", "'trajectory_observed'::VARCHAR"),
        ("validation_status", "VARCHAR", "'unverified'::VARCHAR"),
        ("promotion_status", "VARCHAR", "'staged'::VARCHAR"),
        ("provenance", "VARCHAR", "'{}'::VARCHAR"),
        ("evidence_bundle", "VARCHAR", "'{}'::VARCHAR"),
        ("incident", "VARCHAR", "NULL::VARCHAR"),
        ("observation", "VARCHAR", "NULL::VARCHAR"),
        ("lesson", "VARCHAR", "NULL::VARCHAR"),
        ("workflow", "VARCHAR", "NULL::VARCHAR"),
        ("model_confidence", "DOUBLE", "0.0::DOUBLE"),
        ("quality_score", "DOUBLE", "NULL::DOUBLE"),
        ("status", "VARCHAR", "'pending'::VARCHAR"),
        ("created_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP"),
        ("expires_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP + INTERVAL '180 days'"),
        ("input_sha256", "VARCHAR", "''::VARCHAR"),
    ],
    "rejected_low_quality": [
        ("proposal_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_revision", "INTEGER", "1::INTEGER"),
        ("ingestion_id", "VARCHAR", "''::VARCHAR"),
        ("schema_version", "VARCHAR", "'0.5.2'::VARCHAR"),
        ("inferred_scope", "VARCHAR", "'ambiguous'::VARCHAR"),
        ("inferred_domain", "VARCHAR", "''::VARCHAR"),
        ("rejection_reason", "VARCHAR", "'LOW_QUALITY'::VARCHAR"),
        ("incident", "VARCHAR", "NULL::VARCHAR"),
        ("observation", "VARCHAR", "NULL::VARCHAR"),
        ("model_confidence", "DOUBLE", "0.0::DOUBLE"),
        ("quality_score", "DOUBLE", "NULL::DOUBLE"),
        ("created_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP"),
        ("expires_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP + INTERVAL '90 days'"),
        ("input_sha256", "VARCHAR", "''::VARCHAR"),
    ],
}


class ParquetProposalRecord(BaseModel):
    """Staged proposal record for Parquet tables."""

    model_config = ConfigDict(extra="ignore")

    proposal_id: str
    trajectory_id: str = "default"
    trajectory_revision: int = 1
    ingestion_id: str = ""
    schema_version: str = "0.5.2"
    inferred_scope: str = "ambiguous"
    scope_confidence: float = 0.0
    scope_method: str = "historical_unknown"
    scope_status: str = "inferred"
    cross_scope: bool = False
    inferred_domain: str = ""
    inferred_taxonomy_id: str = ""
    inferred_facets: str = "{}"
    epistemic_status: str = "inferred"
    evidence_level: str = "trajectory_observed"
    validation_status: str = "unverified"
    promotion_status: str = "staged"
    provenance: str = "{}"
    evidence_bundle: str = "{}"
    incident: Optional[str] = None
    observation: Optional[str] = None
    lesson: Optional[str] = None
    workflow: Optional[str] = None
    model_confidence: float = 0.0
    quality_score: Optional[float] = None
    status: str = "pending"
    created_at: str = Field(default_factory=current_iso_timestamp)
    expires_at: Optional[str] = None
    input_sha256: str = Field(..., description="Canonical E109 content hash")
    rejection_reason: Optional[str] = None


class StagingTableInfo(BaseModel):
    """Metadata summary of a Parquet staging table."""

    model_config = ConfigDict(extra="forbid")

    table_name: str
    relative_path: str
    row_count: int
    file_sha256: Optional[str] = None
    size_bytes: int = 0
    columns: List[str] = Field(default_factory=list)


class StagingManifest(BaseModel):
    """Atomic manifest of staging tables (INGEST-STAGING.md §7.1)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "0.5.2"
    backend: str
    tables: Dict[str, StagingTableInfo] = Field(default_factory=dict)
    total_proposals: int = 0
    counts_by_status: Dict[str, int] = Field(default_factory=dict)
    counts_by_scope: Dict[str, int] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=current_iso_timestamp)


class CommitResult(BaseModel):
    """Result of a staging commit operation."""

    model_config = ConfigDict(extra="forbid")

    proposal_id: str
    input_sha256: str
    target_table: str
    is_noop: bool = False
    committed_at: str = Field(default_factory=current_iso_timestamp)


class EquivalenceDiff(BaseModel):
    """Difference record between baseline and Parquet staging."""

    model_config = ConfigDict(extra="forbid")

    proposal_id: str
    field_name: str
    baseline_value: Any
    parquet_value: Any


class EquivalenceReport(BaseModel):
    """Audit report comparing baseline and Parquet staging states."""

    model_config = ConfigDict(extra="forbid")

    is_equivalent: bool
    baseline_count: int
    parquet_count: int
    matched_ids: List[str] = Field(default_factory=list)
    missing_in_parquet: List[str] = Field(default_factory=list)
    missing_in_baseline: List[str] = Field(default_factory=list)
    diffs: List[EquivalenceDiff] = Field(default_factory=list)
    checked_at: str = Field(default_factory=current_iso_timestamp)
