"""Data models for Legacy Wiki Migration (plans/60-OLD-WIKI-MIGRATION.md).

Normative rules:
- Rule 1: Manifest is a normative artifact with source corpus hash, counts, source_mutated flag.
- Rule 2: Fresh-target-only executor with idempotent reruns and fail-closed behavior.
- Rule 4: Read-only link and facet proposal artifacts; no automatic canonical mutation.
- Rule 5: Explicit ambiguity and quarantine records for malformed metadata.
- Rule 8: Anti-contamination rule: preserve legacy tags for audit, initialize keywords empty.
- Rule 9: Explicit verified-personal vs ambiguous scope (never silent default to personal).
- Rule 11 & D95: Opt-in frontmatter: required|derived mode with title extraction and privacy stripping.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


def current_iso_timestamp() -> str:
    """Generate RFC3339 / ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class FrontmatterMode(str, Enum):
    """Frontmatter processing mode (Rule 11, D95)."""

    REQUIRED = "required"  # Strict default: requires YAML frontmatter
    DERIVED = (
        "derived"  # Opt-in for external docs: extracts title from macro/H1, strips privacy macros
    )


class MigrationMode(str, Enum):
    """Execution mode for migration."""

    DRY_RUN = "dry-run"
    EXECUTE = "execute"


class QuarantineRecord(BaseModel):
    """Record of an excluded or quarantined legacy file (Rule 5)."""

    model_config = ConfigDict(extra="forbid")

    file_path: str = Field(..., description="Repository-relative POSIX path to quarantined file")
    reason: str = Field(
        ..., description="Classification reason (e.g. malformed_metadata, ambiguous_scope)"
    )
    error_detail: Optional[str] = Field(
        default=None, description="Exception message or ambiguity explanation"
    )


class LinkProposal(BaseModel):
    """Enrichment proposal for discovered wiki link (Rule 4).

    Emitted as read-only proposal artifact; never automatically promoted to canonical relations.
    """

    model_config = ConfigDict(extra="forbid")

    source_file: str = Field(..., description="Source legacy file path")
    raw_link: str = Field(..., description="Raw link text or markdown target")
    inferred_target: Optional[str] = Field(
        default=None, description="Inferred canonical object ID or target"
    )
    resolved: bool = Field(default=False, description="Whether target resolved deterministically")


class FacetProposal(BaseModel):
    """Enrichment proposal for legacy keyword/term (Rule 4).

    Emitted as read-only proposal artifact; never automatically promoted to canonical facets.
    """

    model_config = ConfigDict(extra="forbid")

    source_file: str = Field(..., description="Source legacy file path")
    raw_term: str = Field(..., description="Raw term or legacy tag")
    facet_name: str = Field(..., description="Target facet dimension (e.g. toolchain, language)")
    matched_value: Optional[str] = Field(
        default=None, description="Matched canonical registry value"
    )
    accepted: bool = Field(default=False, description="Whether matched in registry vocabulary")


class MigrationManifest(BaseModel):
    """Normative migration manifest record (Rule 1)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="1.0.0", description="Migration manifest schema version")
    source_corpus_hash: str = Field(
        ..., description="Exact-byte SHA-256 over sorted source paths and bytes (Rule 3)"
    )
    target_corpus_hash: Optional[str] = Field(
        default=None, description="SHA-256 over emitted canonical files"
    )
    source_location: str = Field(..., description="Source corpus directory path")
    target_location: str = Field(..., description="Target corpus directory path")
    source_mutated: bool = Field(
        default=False, description="Whether source files were mutated (must be False, Rule 1)"
    )
    mode: str = Field(..., description="Execution mode: dry-run or execute")
    frontmatter_mode: str = Field(
        default="required", description="Frontmatter mode: required or derived (Rule 11)"
    )
    counts: Dict[str, int] = Field(
        default_factory=lambda: {
            "total_source_files": 0,
            "eligible_files": 0,
            "emitted_files": 0,
            "excluded_files": 0,
            "quarantined_files": 0,
            "ambiguity_count": 0,
        },
        description="Detailed file and ambiguity counts",
    )
    quarantined: List[QuarantineRecord] = Field(
        default_factory=list, description="List of quarantined files"
    )
    generated_at: str = Field(
        default_factory=current_iso_timestamp, description="UTC ISO generation timestamp"
    )


class MigrationMap(BaseModel):
    """Migration configuration mapping legacy metadata to canonical registries."""

    model_config = ConfigDict(extra="ignore")

    frontmatter_mode: FrontmatterMode = Field(
        default=FrontmatterMode.REQUIRED,
        description="Frontmatter mode: required (default) or derived (Rule 11, D95)",
    )
    target_scope: Optional[str] = Field(
        default=None,
        description="Explicit verified target scope: 'engineering' or 'personal' (Rule 9)",
    )
    taxonomy_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Map from legacy taxonomy / category string to canonical taxonomy_id",
    )
    type_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Map from legacy type string to canonical object_type",
    )
    privacy_stripping: List[str] = Field(
        default_factory=lambda: ["%docResp", "%docOwnerLineMgr", "%docApprover"],
        description="Doc macros to strip in derived mode for privacy (Rule 11, D95)",
    )
    default_domain: str = Field(
        default="software_engineering", description="Default domain if not inferred"
    )
    default_audience: str = Field(default="engineer", description="Default audience facet")
