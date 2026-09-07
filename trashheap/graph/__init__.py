"""Graph intelligence, topological analysis, and discovery pipeline."""

from trashheap.graph.analysis import (
    GraphAnalyzer,
    chunk_text_deterministic,
    normalize_chunk_text,
)
from trashheap.graph.discovery import (
    DiscoveryEngine,
    DiscoveryLifecycleManager,
)
from trashheap.graph.manifest import (
    build_and_publish_manifest,
    compute_aggregate_corpus_hash,
    scan_canonical_inputs,
)
from trashheap.graph.models import (
    Community,
    DerivationMetadata,
    DerivedEdge,
    DiscoveryAuditEntry,
    DiscoveryCandidate,
    GraphManifest,
    NodeDiscoveryCandidate,
    NodeMetrics,
    RelationDiscoveryCandidate,
)
from trashheap.graph.retrieval import GraphFeatureScorer

__all__ = [
    "Community",
    "DerivationMetadata",
    "DerivedEdge",
    "DiscoveryAuditEntry",
    "DiscoveryCandidate",
    "DiscoveryEngine",
    "DiscoveryLifecycleManager",
    "GraphAnalyzer",
    "GraphFeatureScorer",
    "GraphManifest",
    "NodeDiscoveryCandidate",
    "NodeMetrics",
    "RelationDiscoveryCandidate",
    "build_and_publish_manifest",
    "chunk_text_deterministic",
    "compute_aggregate_corpus_hash",
    "normalize_chunk_text",
    "scan_canonical_inputs",
]
