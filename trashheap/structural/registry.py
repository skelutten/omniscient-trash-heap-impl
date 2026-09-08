"""Structural registry loader and validator (SG-001–SG-003).

Normative rules:
- SG-001: SKG is a separate graph from the semantic knowledge graph and has its own registry (structural_registry.yaml).
- SG-002: Structural node types (FILE, MODULE, CLASS, FUNCTION, METHOD, SYMBOL, ROUTE, TEST) MUST NOT be mixed with ObjectTypeEnum.
- SG-003: Structural edge types declare source_types, target_types, dag, and symmetric contracts.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import yaml

from trashheap.structural.models import StructuralEdgeType, StructuralNodeType


class StructuralRegistryError(Exception):
    """Raised when structural_registry.yaml fails validation."""

    pass


def load_structural_registry(registry_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load and validate structural_registry.yaml from disk."""
    if registry_path is None:
        candidates = [
            Path("schemas/registry/structural_registry.yaml"),
            Path(__file__).resolve().parent.parent.parent
            / "schemas"
            / "registry"
            / "structural_registry.yaml",
        ]
        chosen = None
        for c in candidates:
            if c.is_file():
                chosen = c
                break
        if chosen is None:
            raise FileNotFoundError("Could not find 'schemas/registry/structural_registry.yaml'")
        registry_file = chosen
    else:
        registry_file = Path(registry_path)
        if not registry_file.is_file():
            raise FileNotFoundError(f"Structural registry not found at: {registry_file}")

    with open(registry_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise StructuralRegistryError("structural_registry.yaml must be a YAML dictionary")

    validate_structural_registry(data)
    return data


def validate_structural_registry(data: Dict[str, Any]) -> None:
    """Validate structural registry schema and relational contracts (SG-001..SG-003)."""
    if "node_types" not in data or not isinstance(data["node_types"], dict):
        raise StructuralRegistryError("Missing or invalid 'node_types' in structural registry")

    if "edge_types" not in data or not isinstance(data["edge_types"], dict):
        raise StructuralRegistryError("Missing or invalid 'edge_types' in structural registry")

    node_types: Set[str] = set(data["node_types"].keys())

    # Verify SG-002: node types match StructuralNodeType enum
    expected_nodes = {t.value for t in StructuralNodeType}
    for nt in node_types:
        if nt not in expected_nodes:
            raise StructuralRegistryError(
                f"Unexpected structural node type '{nt}' (expected one of {expected_nodes})"
            )

    for node_name, node_spec in data["node_types"].items():
        if not isinstance(node_spec, dict) or "identity" not in node_spec:
            raise StructuralRegistryError(
                f"Node type '{node_name}' must declare 'identity' keys list"
            )
        if not isinstance(node_spec["identity"], list) or len(node_spec["identity"]) == 0:
            raise StructuralRegistryError(
                f"Node type '{node_name}' identity keys must be a non-empty list"
            )

    # Verify SG-003: edge types contract
    for edge_name, edge_spec in data["edge_types"].items():
        if not isinstance(edge_spec, dict):
            raise StructuralRegistryError(f"Edge type '{edge_name}' must be a dictionary")

        for req_field in ["source_types", "target_types", "dag", "symmetric"]:
            if req_field not in edge_spec:
                raise StructuralRegistryError(
                    f"Edge type '{edge_name}' missing required contract field '{req_field}'"
                )

        if not isinstance(edge_spec["source_types"], list) or not isinstance(
            edge_spec["target_types"], list
        ):
            raise StructuralRegistryError(
                f"Edge type '{edge_name}' source_types and target_types must be lists"
            )

        for st in edge_spec["source_types"]:
            if st not in node_types:
                raise StructuralRegistryError(
                    f"Edge type '{edge_name}' source type '{st}' not in registered node_types"
                )

        for tt in edge_spec["target_types"]:
            if tt not in node_types:
                raise StructuralRegistryError(
                    f"Edge type '{edge_name}' target type '{tt}' not in registered node_types"
                )

        if not isinstance(edge_spec["dag"], bool):
            raise StructuralRegistryError(f"Edge type '{edge_name}' 'dag' must be a boolean")

        if not isinstance(edge_spec["symmetric"], bool):
            raise StructuralRegistryError(f"Edge type '{edge_name}' 'symmetric' must be a boolean")


class StructuralRegistry:
    """Registry query wrapper for structural graph validation."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self._data = data or load_structural_registry()

    @property
    def node_types(self) -> Dict[str, Any]:
        return self._data.get("node_types", {})

    @property
    def edge_types(self) -> Dict[str, Any]:
        return self._data.get("edge_types", {})

    def is_valid_node_type(self, node_type: Union[str, StructuralNodeType]) -> bool:
        val = node_type.value if isinstance(node_type, StructuralNodeType) else str(node_type)
        return val in self.node_types

    def is_valid_edge_type(self, edge_type: Union[str, StructuralEdgeType]) -> bool:
        val = edge_type.value if isinstance(edge_type, StructuralEdgeType) else str(edge_type)
        return val in self.edge_types

    def get_edge_contract(self, edge_type: Union[str, StructuralEdgeType]) -> Dict[str, Any]:
        val = edge_type.value if isinstance(edge_type, StructuralEdgeType) else str(edge_type)
        if val not in self.edge_types:
            raise KeyError(f"Unknown structural edge type: {val}")
        return self.edge_types[val]
