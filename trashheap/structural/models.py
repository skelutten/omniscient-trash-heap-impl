"""Data models for Structural Knowledge Graph (specs/STRUCTURAL-GRAPH.md).

Normative Invariants:
- SG-001: Separate graph from semantic knowledge graph.
- SG-002: Structural node types MUST NOT be mixed with ObjectTypeEnum.
- SG-003: Structural edge types declare source_types, target_types, dag, and symmetric contracts.
- SG-007: Nodes and edges bound to source_revision and content_hash.
- SG-011: Context budget calculation.
- SG-013: Bridge relations between Knowledge Objects and Structural Nodes.
- SG-014: Derivation metadata with mode: extracted and extractor: ast|parser.
- SG-015: Coverage reporting.
- SG-020: Explicit degradation tracking.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from trashheap.constants import VERSION
from trashheap.timeutil import current_iso_timestamp


class StructuralNodeType(str, Enum):
    """Structural node types (SG-002).

    Normatively defined; MUST NOT be mixed with ObjectTypeEnum (SG-AX-002).
    """

    FILE = "FILE"
    MODULE = "MODULE"
    CLASS = "CLASS"
    FUNCTION = "FUNCTION"
    METHOD = "METHOD"
    SYMBOL = "SYMBOL"
    ROUTE = "ROUTE"
    TEST = "TEST"


class StructuralEdgeType(str, Enum):
    """Structural edge types (SG-003, SG-AX-001).

    Belong to structural_registry.yaml, NOT relation_registry.yaml.
    """

    DEFINES = "DEFINES"
    CALLS = "CALLS"
    IMPORTS = "IMPORTS"
    INHERITS = "INHERITS"
    ROUTES_TO = "ROUTES_TO"
    TESTS_SYMBOL = "TESTS_SYMBOL"


class DerivationMetadata(BaseModel):
    """Derivation provenance metadata (SG-014)."""

    model_config = ConfigDict(extra="forbid")

    mode: str = Field(default="extracted", description="Extraction mode (extracted)")
    extractor: str = Field(default="ast", description="Extractor tool/method (ast | parser)")
    extractor_version: str = Field(..., description="Version of the extraction tool")
    grammar_version: str = Field(..., description="Grammar / language version")
    source_revision: str = Field(..., description="Git SHA or resolved ref")
    source_file: str = Field(..., description="Relative file path")


class LSPMetadata(BaseModel):
    """Optional LSP semantic type resolution metadata (SG-005)."""

    model_config = ConfigDict(extra="forbid")

    server: str = Field(..., description="LSP server name")
    server_version: str = Field(..., description="LSP server version")
    resolution_status: str = Field(
        ..., description="Resolution status, e.g. resolved | partial | failed"
    )


class StructuralNode(BaseModel):
    """Structural node representation (SG-002, SG-007, SG-AX-002).

    Structural nodes are machine-built from code AST and are not Knowledge Objects.
    """

    model_config = ConfigDict(extra="forbid")

    node_id: str = Field(..., description="Deterministic structural identity URI/string")
    node_type: StructuralNodeType = Field(..., description="Structural node type")
    repo: str = Field(default="canonical", description="Repository name/identifier")
    path: str = Field(..., description="Normalized relative path to file")
    qualified_name: Optional[str] = Field(default=None, description="Qualified symbol name")
    line_start: Optional[int] = Field(default=None, description="Starting line in source file")
    line_end: Optional[int] = Field(default=None, description="Ending line in source file")
    source_revision: str = Field(..., description="Source git revision or resolved ref (SG-007)")
    content_hash: str = Field(..., description="SHA-256 hash of file content (SG-007, SG-008)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary structural metadata"
    )


class StructuralEdge(BaseModel):
    """Structural edge representation (SG-003, SG-007, SG-014)."""

    model_config = ConfigDict(extra="forbid")

    edge_id: str = Field(..., description="Deterministic edge identifier")
    edge_type: StructuralEdgeType = Field(..., description="Structural edge type")
    source_id: str = Field(..., description="Source structural node ID")
    target_id: str = Field(..., description="Target structural node ID")
    source_revision: str = Field(..., description="Source revision binding (SG-007)")
    derivation: DerivationMetadata = Field(..., description="Extraction provenance (SG-014)")
    lsp_metadata: Optional[LSPMetadata] = Field(
        default=None, description="Optional LSP resolution info (SG-005)"
    )


class BridgeEdge(BaseModel):
    """Bridge relation connecting a Knowledge Object to a Structural Node (SG-013, §15.5).

    Bridge edges are derived, typed and reviewable; they MUST NOT create canonical relations automatically.
    """

    model_config = ConfigDict(extra="forbid")

    bridge_id: str = Field(..., description="Deterministic bridge identifier")
    knowledge_object_id: str = Field(..., description="Knowledge Object ID (e.g. ENG-CMP-0102)")
    structural_node_id: str = Field(..., description="Target structural node ID")
    bridge_type: str = Field(
        default="represented_by", description="Bridge type: represented_by | documents | tested_by"
    )
    derivation: DerivationMetadata = Field(..., description="Derivation provenance")
    status: str = Field(
        default="pending", description="Status: pending | reviewed | approved | rejected"
    )


class ImpactReport(BaseModel):
    """Blast radius impact analysis result (SG-010, SG-011)."""

    model_config = ConfigDict(extra="forbid")

    target_node_id: str = Field(..., description="Target node analyzed")
    max_depth: int = Field(..., description="Bounded max traversal depth")
    node_ceiling: int = Field(..., description="Bounded node ceiling")
    affected_nodes: List[str] = Field(
        default_factory=list, description="List of affected structural node IDs"
    )
    traversal_paths: List[Dict[str, Any]] = Field(
        default_factory=list, description="Step-by-step traversal edges"
    )
    context_budget_tokens: int = Field(..., description="Estimated token context budget (SG-011)")
    depth_reached: int = Field(..., description="Maximum depth reached in traversal")
    ceiling_hit: bool = Field(default=False, description="Whether node ceiling stopped traversal")


class CoverageReport(BaseModel):
    """Structural coverage and observability report (SG-015, SG-020)."""

    model_config = ConfigDict(extra="forbid")

    total_files_scanned: int = Field(..., description="Total candidate files scanned")
    indexed_files: int = Field(..., description="Files successfully indexed")
    total_nodes: int = Field(..., description="Total structural nodes extracted")
    total_edges: int = Field(..., description="Total structural edges extracted")
    unresolved_references: List[Dict[str, str]] = Field(
        default_factory=list, description="Unresolved symbol references"
    )
    failed_files: List[Dict[str, str]] = Field(
        default_factory=list, description="Failed files with parse errors (SG-020)"
    )
    parser: str = Field(..., description="Parser implementation name")
    parser_version: str = Field(..., description="Parser version string")
    grammar_version: str = Field(..., description="Grammar version string")


class StructuralGraphManifest(BaseModel):
    """Structural Graph Manifest publication record (SG-004, SG-007, SG-009)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="0.1.0", description="Manifest schema version")
    revision: str = Field(..., description="Source code revision (git SHA or ref)")
    aggregate_hash: str = Field(
        ..., description="SHA-256 over all indexed files and content hashes"
    )
    generated_at: str = Field(
        default_factory=current_iso_timestamp, description="Timestamp of indexing"
    )
    node_count: int = Field(..., description="Total nodes in graph")
    edge_count: int = Field(..., description="Total edges in graph")
    tool_version: str = Field(default=VERSION, description="trashheap tool version")
