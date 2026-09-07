"""Graph intelligence and discovery data models.

Complies with specs/GRAPH-INTELLIGENCE.md, specs/GRAPH-RETRIEVAL.md, and specs/DISCOVERY.md.
Implements invariants DELTA-CORE-001..DELTA-CORE-007 and DISC-001..DISC-005.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional


def current_iso_timestamp() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class DerivationMetadata:
    """Provenance describing how a derived artifact was generated (GRAPH-INTELLIGENCE.md §5.1.1)."""

    mode: Literal["extracted", "inferred", "ambiguous"] = "inferred"
    extractor: str = "graph_delta"
    extractor_version: str = "1.0.0"
    source_revision: Optional[str] = None
    prompt_version: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "extractor": self.extractor,
            "extractor_version": self.extractor_version,
            "source_revision": self.source_revision,
            "prompt_version": self.prompt_version,
            "confidence": self.confidence,
        }


@dataclass
class DerivedEdge:
    """Derived graph edge between canonical nodes (GRAPH-INTELLIGENCE.md §5.1)."""

    edge_id: str
    source_id: str
    target_id: str
    canonical_edge_exists: bool
    component_scores: Dict[str, float]  # canonical, similarity, proximity, cooccurrence
    final_score: float
    scope: str
    corpus_hash: str
    algorithm_version: str = "1.0.0"
    policy_version: str = "1.0.0"
    created_at: str = field(default_factory=current_iso_timestamp)
    expires_at: Optional[str] = None
    derivation: DerivationMetadata = field(default_factory=DerivationMetadata)
    evidence_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "canonical_edge_exists": self.canonical_edge_exists,
            "component_scores": self.component_scores,
            "final_score": round(self.final_score, 6),
            "scope": self.scope,
            "corpus_hash": self.corpus_hash,
            "algorithm_version": self.algorithm_version,
            "policy_version": self.policy_version,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "derivation": self.derivation.to_dict(),
            "evidence_refs": self.evidence_refs,
        }


@dataclass
class NodeMetrics:
    """Topological metrics for a canonical knowledge node (GRAPH-INTELLIGENCE.md §12 Phase 2)."""

    node_id: str
    scope: str
    in_degree: int
    out_degree: int
    total_degree: int
    component_id: str
    community_id: str
    distances: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "scope": self.scope,
            "in_degree": self.in_degree,
            "out_degree": self.out_degree,
            "total_degree": self.total_degree,
            "component_id": self.component_id,
            "community_id": self.community_id,
            "distances": self.distances,
        }


@dataclass
class Community:
    """Scope-partitioned community of canonical nodes (GRAPH-INTELLIGENCE.md §4, §12)."""

    community_id: str
    scope: str
    level: int
    member_node_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "community_id": self.community_id,
            "scope": self.scope,
            "level": self.level,
            "member_node_ids": sorted(self.member_node_ids),
        }


@dataclass
class DiscoveryCandidate:
    """Base discovery candidate matching DISCOVERY.md §5.2 (DISC-001)."""

    candidate_id: str
    candidate_type: Literal[
        "relation_proposal", "duplicate", "knowledge_gap", "node_proposal"
    ]
    confidence: float
    status: Literal[
        "pending", "reviewed", "approved", "promoted", "rejected", "expired", "superseded"
    ]
    created_at: str
    expires_at: str
    scope: str
    corpus_hash: str
    algorithm_version: str
    evidence_refs: List[str]
    source_refs: List[str]
    representation_refs: List[str]
    evidence_unit_refs: List[str]
    derivation_ref: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_type": self.candidate_type,
            "confidence": round(self.confidence, 4),
            "status": self.status,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "scope": self.scope,
            "corpus_hash": self.corpus_hash,
            "algorithm_version": self.algorithm_version,
            "evidence_refs": self.evidence_refs,
            "source_refs": self.source_refs,
            "representation_refs": self.representation_refs,
            "evidence_unit_refs": self.evidence_unit_refs,
            "derivation_ref": self.derivation_ref,
        }


@dataclass
class RelationDiscoveryCandidate(DiscoveryCandidate):
    """Relation candidate referring to existing canonical nodes (DISCOVERY.md §5.2)."""

    source_id: str = ""
    target_id: str = ""
    suggested_relation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["source_id"] = self.source_id
        d["target_id"] = self.target_id
        d["suggested_relation"] = self.suggested_relation
        d["metadata"] = self.metadata
        return d


@dataclass
class NodeDiscoveryCandidate(DiscoveryCandidate):
    """Node proposal candidate (DISCOVERY.md §5.2)."""

    trigger_source_ids: List[str] = field(default_factory=list)
    suggested_title: str = ""
    suggested_domain: Optional[str] = None
    suggested_taxonomy_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["trigger_source_ids"] = self.trigger_source_ids
        d["suggested_title"] = self.suggested_title
        d["suggested_domain"] = self.suggested_domain
        d["suggested_taxonomy_id"] = self.suggested_taxonomy_id
        d["metadata"] = self.metadata
        return d


@dataclass
class DiscoveryAuditEntry:
    """Auditable lifecycle transition record for a discovery candidate (DISCOVERY.md §6)."""

    candidate_id: str
    previous_status: str
    new_status: str
    actor: str
    timestamp: str
    reason: str
    validation_result: Optional[str] = None
    canonical_commit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "validation_result": self.validation_result,
            "canonical_commit": self.canonical_commit,
        }


@dataclass
class GraphManifest:
    """Manifest for generated derived graph artifacts (GRAPH-INTELLIGENCE.md §1, §5, §11)."""

    schema_version: str
    architecture_version: str
    pipeline_version: str
    corpus_hash: str
    generated_at: str
    backend: str
    determinism: str
    records_count: Dict[str, int]
    observability: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "architecture_version": self.architecture_version,
            "pipeline_version": self.pipeline_version,
            "corpus_hash": self.corpus_hash,
            "generated_at": self.generated_at,
            "backend": self.backend,
            "determinism": self.determinism,
            "records_count": self.records_count,
            "observability": self.observability,
        }
