"""Structural Knowledge Graph package (specs/STRUCTURAL-GRAPH.md).

Implements invariants SG-001 through SG-020:
- Separate structural graph & registry (structural_registry.yaml)
- Deterministic AST extraction and revision/hash binding
- Idempotent incremental indexing and atomic invalidation
- Bounded blast radius impact analysis and context budget calculation
- Bridge relations to Knowledge Objects (reviewable, non-canonical)
- Layer 7 structural retrieval and Evidence Bundle integration
"""

from trashheap.structural.analysis import StructuralGraphAnalyzer
from trashheap.structural.bridge import BridgeEngine
from trashheap.structural.extractor import ASTExtractor
from trashheap.structural.indexer import StructuralGraphIndexer
from trashheap.structural.models import (
    BridgeEdge,
    CoverageReport,
    DerivationMetadata,
    ImpactReport,
    StructuralEdge,
    StructuralEdgeType,
    StructuralGraphManifest,
    StructuralNode,
    StructuralNodeType,
)
from trashheap.structural.registry import (
    StructuralRegistry,
    StructuralRegistryError,
    load_structural_registry,
    validate_structural_registry,
)
from trashheap.structural.retrieval import StructuralHit, StructuralRetriever

__all__ = [
    "ASTExtractor",
    "BridgeEngine",
    "BridgeEdge",
    "CoverageReport",
    "DerivationMetadata",
    "ImpactReport",
    "StructuralEdge",
    "StructuralEdgeType",
    "StructuralGraphAnalyzer",
    "StructuralGraphIndexer",
    "StructuralGraphManifest",
    "StructuralHit",
    "StructuralNode",
    "StructuralNodeType",
    "StructuralRegistry",
    "StructuralRegistryError",
    "StructuralRetriever",
    "load_structural_registry",
    "validate_structural_registry",
]
