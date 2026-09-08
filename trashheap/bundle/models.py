"""Data models for Knowledge Bundles and OKF concepts (specs/OKF-INTEROP.md §16–§17, D109)."""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


class CrossScopeSecurityError(Exception):
    """Raised when personal scope objects are included in a bundle without an explicit redaction policy (BUNDLE-007)."""

    pass


@dataclass
class BundleSelector:
    """Canonical query specification defining bundle membership (BUNDLE-001).

    Membership is computed, never declared in object frontmatter (CANON-004).
    """

    bundle_id: str
    title: str
    schema_version: str = "1.0.0"
    scopes: List[str] = field(default_factory=lambda: ["engineering"])
    taxonomy_ids: Optional[List[str]] = None
    include_descendants: bool = True
    object_types: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    facets: Optional[Dict[str, List[str]]] = None
    statuses: Optional[List[str]] = None
    min_confidence: float = 0.0
    valid_at: Optional[str] = None
    closure_relations: Optional[List[str]] = None
    closure_max_depth: int = 0
    allow_personal_scope: bool = False
    redact_scopes: Optional[List[str]] = None
    emit_index: bool = True

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 fingerprint of the selector specification."""
        normalized = {
            "bundle_id": self.bundle_id,
            "title": self.title,
            "scopes": sorted(self.scopes),
            "taxonomy_ids": sorted(self.taxonomy_ids) if self.taxonomy_ids else None,
            "include_descendants": self.include_descendants,
            "object_types": sorted(self.object_types) if self.object_types else None,
            "domains": sorted(self.domains) if self.domains else None,
            "facets": {k: sorted(v) for k, v in sorted(self.facets.items())}
            if self.facets
            else None,
            "statuses": sorted(self.statuses) if self.statuses else None,
            "min_confidence": self.min_confidence,
            "valid_at": self.valid_at,
            "closure_relations": sorted(self.closure_relations) if self.closure_relations else None,
            "closure_max_depth": self.closure_max_depth,
            "allow_personal_scope": self.allow_personal_scope,
            "redact_scopes": sorted(self.redact_scopes) if self.redact_scopes else None,
            "emit_index": self.emit_index,
        }
        raw = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"sha256:{h}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert selector to serializable dictionary."""
        return {
            "bundle_id": self.bundle_id,
            "title": self.title,
            "schema_version": self.schema_version,
            "scopes": self.scopes,
            "taxonomy_ids": self.taxonomy_ids,
            "include_descendants": self.include_descendants,
            "object_types": self.object_types,
            "domains": self.domains,
            "facets": self.facets,
            "statuses": self.statuses,
            "min_confidence": self.min_confidence,
            "valid_at": self.valid_at,
            "closure_relations": self.closure_relations,
            "closure_max_depth": self.closure_max_depth,
            "allow_personal_scope": self.allow_personal_scope,
            "redact_scopes": self.redact_scopes,
            "emit_index": self.emit_index,
        }


@dataclass
class UnresolvedReference:
    """An external or uncontained relation target listed in the manifest (BUNDLE-006)."""

    source_id: str
    relation_type: str
    target_id: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "from": self.source_id,
            "relation": self.relation_type,
            "target": self.target_id,
        }


@dataclass
class BundleManifest:
    """Manifest describing a materialized bundle projection (BUNDLE-004, BUNDLE-008)."""

    bundle_id: str
    title: str
    selector_hash: str
    corpus_hash: str
    generated_at: str
    generator: str
    exporter_version: str
    architecture_version: str
    target_directory: str
    object_ids: List[str]
    closure_object_ids: List[str]
    total_objects: int
    unresolved_references: List[Dict[str, str]]
    lossy: Dict[str, bool]
    schema_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "bundle_id": self.bundle_id,
            "title": self.title,
            "selector_hash": self.selector_hash,
            "corpus_hash": self.corpus_hash,
            "generated_at": self.generated_at,
            "generator": self.generator,
            "exporter_version": self.exporter_version,
            "architecture_version": self.architecture_version,
            "target_directory": self.target_directory,
            "object_ids": sorted(self.object_ids),
            "closure_object_ids": sorted(self.closure_object_ids),
            "total_objects": self.total_objects,
            "unresolved_references": self.unresolved_references,
            "lossy": self.lossy,
        }


@dataclass
class OKFConcept:
    """Representation of an exported or imported OKF concept document."""

    concept_id: str  # e.g. "engineering/10_build_systems/ENG-FET-0001"
    file_path: Path
    frontmatter: Dict[str, Any]
    body: str
