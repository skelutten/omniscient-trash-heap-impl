"""Legacy corpus migration package (plans/60-OLD-WIKI-MIGRATION.md).

Implements:
- Rule 1: Normative migration manifest with exact source hash, file counts, source_mutated flag.
- Rule 2: Fresh-target-only executor with idempotent reruns and fail-closed checks.
- Rule 3: Exact-byte SHA-256 over sorted POSIX relative paths.
- Rule 4: Read-only link and facet proposals (link_proposals.json, facet_proposals.json).
- Rule 5: Explicit ambiguity and quarantine tracking for malformed metadata.
- Rule 6: Normalization of legacy source_ref to source_refs while preserving paths.
- Rule 7: Source preservation verification.
- Rule 8: Anti-contamination: preserve legacy tags for audit, empty canonical keywords.
- Rule 9: Explicit verified-personal vs ambiguous scope (no silent default).
- Rule 10: Conservative defaults for unverified fields.
- Rule 11 & D95: Opt-in frontmatter: required|derived mode with title extraction and privacy stripping.
"""

from trashheap.migration.engine import (
    ChangedSourceError,
    MigrationEngine,
    MigrationError,
    UnmanagedTargetError,
    compute_corpus_hash,
)
from trashheap.migration.models import (
    FacetProposal,
    FrontmatterMode,
    LinkProposal,
    MigrationManifest,
    MigrationMap,
    MigrationMode,
    QuarantineRecord,
)
from trashheap.migration.parser import LegacyParser

__all__ = [
    "ChangedSourceError",
    "FacetProposal",
    "FrontmatterMode",
    "LegacyParser",
    "LinkProposal",
    "MigrationEngine",
    "MigrationError",
    "MigrationManifest",
    "MigrationMap",
    "MigrationMode",
    "QuarantineRecord",
    "UnmanagedTargetError",
    "compute_corpus_hash",
]
