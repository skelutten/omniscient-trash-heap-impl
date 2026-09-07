"""Layer 7 Structural Retrieval profile and Evidence Bundle formatting (SG-012, SG-016, SG-018).

Normative rules:
- SG-012: Structural retrieval is an explicit, versioned Layer 7 profile and MUST NOT change baseline retrieval results.
- SG-018: Structural hits carry node ID, file, revision, and line interval.
- SG-016: Deterministic query ranking.
"""

from typing import Any, Dict, List, Optional, Tuple

from trashheap.structural.models import StructuralNode, StructuralNodeType


class StructuralHit:
    """A structural match carried in an Evidence Bundle (SG-018)."""

    def __init__(
        self,
        node_id: str,
        file: str,
        revision: str,
        line_interval: Optional[List[int]],
        node_type: str,
        qualified_name: Optional[str],
        score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.node_id = node_id
        self.file = file
        self.revision = revision
        self.line_interval = line_interval
        self.node_type = node_type
        self.qualified_name = qualified_name
        self.score = score
        self.metadata = metadata or {}

    def to_evidence_dict(self) -> Dict[str, Any]:
        """Format structural hit for the Evidence Bundle (SG-018)."""
        return {
            "node_id": self.node_id,
            "file": self.file,
            "revision": self.revision,
            "line_interval": self.line_interval,
            "node_type": self.node_type,
            "qualified_name": self.qualified_name,
            "score": round(self.score, 4),
            "metadata": self.metadata,
        }


class StructuralRetriever:
    """Explicit Layer 7 structural code retrieval engine (SG-012)."""

    def __init__(self, nodes: Dict[str, StructuralNode]):
        self.nodes = nodes

    def query(
        self,
        query_text: str,
        node_type: Optional[StructuralNodeType] = None,
        top_k: int = 10,
    ) -> List[StructuralHit]:
        """Search structural nodes deterministically (SG-016)."""
        q_norm = query_text.strip().lower()
        if not q_norm:
            return []

        scored_hits: List[Tuple[float, StructuralNode]] = []

        for node in self.nodes.values():
            if node_type and node.node_type != node_type:
                continue

            score = 0.0
            qname = (node.qualified_name or "").lower()
            path = node.path.lower()
            nid = node.node_id.lower()

            # Deterministic scoring
            if qname == q_norm:
                score = 1.0
            elif qname.endswith(f".{q_norm}") or qname.startswith(f"{q_norm}."):
                score = 0.8
            elif q_norm in qname:
                score = 0.6
            elif q_norm in path:
                score = 0.4
            elif q_norm in nid:
                score = 0.2

            if score > 0.0:
                scored_hits.append((score, node))

        # Deterministic sorting (SG-016): score desc, then node_id asc
        scored_hits.sort(key=lambda item: (-item[0], item[1].node_id))

        results: List[StructuralHit] = []
        for score, node in scored_hits[:top_k]:
            line_interval = None
            if node.line_start is not None and node.line_end is not None:
                line_interval = [node.line_start, node.line_end]

            results.append(
                StructuralHit(
                    node_id=node.node_id,
                    file=node.path,
                    revision=node.source_revision,
                    line_interval=line_interval,
                    node_type=node.node_type.value,
                    qualified_name=node.qualified_name,
                    score=score,
                    metadata=node.metadata,
                )
            )

        return results
