"""Structural graph analysis, blast radius impact traversal, and context budget calculation (SG-010, SG-011, SG-016)."""

from collections import deque
from typing import Any, Dict, List, Optional, Set, Tuple

from trashheap.structural.models import (
    ImpactReport,
    StructuralEdge,
    StructuralEdgeType,
    StructuralNode,
)


class StructuralGraphAnalyzer:
    """Graph analyzer for structural code relationships and impact propagation."""

    def __init__(self, nodes: Dict[str, StructuralNode], edges: Dict[str, StructuralEdge]):
        self.nodes = nodes
        self.edges = edges

        # Adjacency indexes
        self.out_edges: Dict[str, List[StructuralEdge]] = {nid: [] for nid in nodes}
        self.in_edges: Dict[str, List[StructuralEdge]] = {nid: [] for nid in nodes}

        for edge in edges.values():
            if edge.source_id in self.out_edges:
                self.out_edges[edge.source_id].append(edge)
            else:
                self.out_edges[edge.source_id] = [edge]

            if edge.target_id in self.in_edges:
                self.in_edges[edge.target_id].append(edge)
            else:
                self.in_edges[edge.target_id] = [edge]

        # Deterministic sort
        for nid in self.out_edges:
            self.out_edges[nid].sort(key=lambda e: (e.edge_type.value, e.target_id))
        for nid in self.in_edges:
            self.in_edges[nid].sort(key=lambda e: (e.edge_type.value, e.source_id))

    def compute_blast_radius(
        self,
        target_node_id: str,
        max_depth: int = 3,
        node_ceiling: int = 50,
        direction: str = "both",
    ) -> ImpactReport:
        """Bounded blast radius traversal from target symbol/node (SG-010, SG-011).

        Args:
            target_node_id: Starting node identifier
            max_depth: Maximum edge hops from target
            node_ceiling: Absolute ceiling on number of visited nodes
            direction: 'downstream' (out_edges), 'upstream' (in_edges), or 'both'
        """
        if max_depth <= 0 or node_ceiling <= 0:
            return ImpactReport(
                target_node_id=target_node_id,
                max_depth=max_depth,
                node_ceiling=node_ceiling,
                affected_nodes=[],
                traversal_paths=[],
                context_budget_tokens=50,
                depth_reached=0,
                ceiling_hit=False,
            )

        visited: Set[str] = {target_node_id}
        traversal_paths: List[Dict[str, Any]] = []
        max_depth_reached = 0
        ceiling_hit = False

        # Queue items: (current_node_id, current_depth)
        queue: deque[Tuple[str, int]] = deque([(target_node_id, 0)])

        while queue:
            curr_id, curr_depth = queue.popleft()
            max_depth_reached = max(max_depth_reached, curr_depth)

            if curr_depth >= max_depth:
                continue

            candidates: List[Tuple[str, str, str]] = []  # (source, edge_type, target)

            if direction in ("downstream", "both"):
                for edge in self.out_edges.get(curr_id, []):
                    candidates.append((edge.source_id, edge.edge_type.value, edge.target_id))

            if direction in ("upstream", "both"):
                for edge in self.in_edges.get(curr_id, []):
                    candidates.append((edge.source_id, edge.edge_type.value, edge.target_id))

            # Deterministic exploration order (SG-016)
            candidates.sort(key=lambda c: (c[1], c[2]))

            for src, etype, tgt in candidates:
                neighbor = tgt if src == curr_id else src

                if neighbor not in visited:
                    if len(visited) >= node_ceiling:
                        ceiling_hit = True
                        break

                    visited.add(neighbor)
                    traversal_paths.append(
                        {
                            "source": src,
                            "edge_type": etype,
                            "target": tgt,
                            "depth": curr_depth + 1,
                        }
                    )
                    queue.append((neighbor, curr_depth + 1))

            if ceiling_hit:
                break

        affected = sorted(visited - {target_node_id})

        # SG-011: Context budget calculation (GRAPH-INTELLIGENCE.md §5.1.3)
        # 50 base envelope tokens + ~15 tokens per node ID + ~20 tokens per path edge
        estimated_tokens = 50 + (len(affected) * 15) + (len(traversal_paths) * 20)

        return ImpactReport(
            target_node_id=target_node_id,
            max_depth=max_depth,
            node_ceiling=node_ceiling,
            affected_nodes=affected,
            traversal_paths=traversal_paths,
            context_budget_tokens=estimated_tokens,
            depth_reached=max_depth_reached,
            ceiling_hit=ceiling_hit,
        )

    def detect_cycles(
        self, edge_types: Optional[List[StructuralEdgeType]] = None
    ) -> List[List[str]]:
        """Detect cycles in the structural graph for DAG edge types."""
        if edge_types is None:
            edge_types = [StructuralEdgeType.DEFINES, StructuralEdgeType.INHERITS]

        allowed_types = {e.value for e in edge_types}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}

        for edge in self.edges.values():
            if edge.edge_type.value in allowed_types:
                adj[edge.source_id].append(edge.target_id)

        visited: Dict[str, int] = {}  # 0: unvisited, 1: visiting, 2: visited
        cycles: List[List[str]] = []

        def dfs(node: str, path: List[str]):
            visited[node] = 1
            for neighbor in sorted(adj.get(node, [])):
                if visited.get(neighbor, 0) == 1:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                elif visited.get(neighbor, 0) == 0:
                    dfs(neighbor, path + [neighbor])
            visited[node] = 2

        for nid in sorted(self.nodes.keys()):
            if visited.get(nid, 0) == 0:
                dfs(nid, [nid])

        return cycles
