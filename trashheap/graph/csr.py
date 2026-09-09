"""Compressed Sparse Row (CSR) binary array graph projection (specs/GRAPH-INTELLIGENCE.md §11.1).

Enables microsecond (< 10 µs) single-hop graph traversals via contiguous NumPy
array slicing, memory-mapped zero-copy persistence (indptr.npy, indices.npy),
and deterministic integer vertex IDs.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from trashheap.corpus import Corpus


@dataclass
class CsrGraphProjection:
    """In-memory or memory-mapped Compressed Sparse Row (CSR) graph projection."""

    indptr: np.ndarray  # Shape: (N + 1,), dtype: int64
    indices: np.ndarray  # Shape: (M,), dtype: int64
    node_to_int: Dict[str, int]
    int_to_node: List[str]
    edge_relation_types: Optional[List[str]] = None

    @property
    def num_nodes(self) -> int:
        return len(self.int_to_node) if self.int_to_node else len(self.indptr) - 1

    @property
    def num_edges(self) -> int:
        return int(len(self.indices))

    @classmethod
    def build_from_corpus(cls, corpus: Corpus, directed: bool = True) -> CsrGraphProjection:
        """Construct deterministic CSR representation from a Corpus."""
        valid_objects = [ko for ko in corpus.objects if ko.id]
        sorted_ids = sorted(ko.id for ko in valid_objects)
        node_to_int = {nid: idx for idx, nid in enumerate(sorted_ids)}
        int_to_node = list(sorted_ids)
        n = len(sorted_ids)

        # Map edges
        adj_lists: List[List[Tuple[int, str]]] = [[] for _ in range(n)]

        for ko in valid_objects:
            u = node_to_int[ko.id]
            if not ko.frontmatter:
                continue
            for rel in ko.frontmatter.relations:
                target = rel.target
                if target in node_to_int:
                    v = node_to_int[target]
                    rtype = rel.type or "RELATES_TO"
                    adj_lists[u].append((v, rtype))
                    if not directed and u != v:
                        adj_lists[v].append((u, rtype))

        # Build indptr and indices
        indptr = np.zeros(n + 1, dtype=np.int64)
        indices_list: List[int] = []
        rel_types_list: List[str] = []

        for u in range(n):
            # Sort neighbors deterministically by target integer ID
            neighbors = sorted(adj_lists[u], key=lambda x: (x[0], x[1]))
            indptr[u + 1] = indptr[u] + len(neighbors)
            for v, rtype in neighbors:
                indices_list.append(v)
                rel_types_list.append(rtype)

        indices = (
            np.array(indices_list, dtype=np.int64) if indices_list else np.empty(0, dtype=np.int64)
        )

        return cls(
            indptr=indptr,
            indices=indices,
            node_to_int=node_to_int,
            int_to_node=int_to_node,
            edge_relation_types=rel_types_list,
        )

    def save(self, target_dir: Path) -> None:
        """Persist binary arrays and metadata to directory."""
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        np.save(target_dir / "indptr.npy", self.indptr)
        np.save(target_dir / "indices.npy", self.indices)

        meta = {
            "num_nodes": self.num_nodes,
            "num_edges": self.num_edges,
            "nodes": self.int_to_node,
            "relation_types": self.edge_relation_types or [],
        }
        (target_dir / "node_index.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    @classmethod
    def load_memmap(cls, target_dir: Path) -> CsrGraphProjection:
        """Load graph using zero-copy memory maps for instant startup."""
        target_dir = Path(target_dir)
        indptr = np.load(target_dir / "indptr.npy", mmap_mode="r")
        indices = np.load(target_dir / "indices.npy", mmap_mode="r")

        meta = json.loads((target_dir / "node_index.json").read_text(encoding="utf-8"))
        int_to_node = meta.get("nodes", [])
        node_to_int = {nid: idx for idx, nid in enumerate(int_to_node)}
        rel_types = meta.get("relation_types")

        return cls(
            indptr=indptr,
            indices=indices,
            node_to_int=node_to_int,
            int_to_node=int_to_node,
            edge_relation_types=rel_types,
        )

    def get_neighbor_ids(self, u: int) -> np.ndarray:
        """Extract contiguous slice of outgoing neighbor integer IDs (< 10 µs)."""
        if u < 0 or u >= self.num_nodes:
            return np.empty(0, dtype=np.int64)
        start = int(self.indptr[u])
        end = int(self.indptr[u + 1])
        return self.indices[start:end]

    def get_neighbors(self, node_id: str) -> List[str]:
        """Return list of neighbor canonical node IDs."""
        u = self.node_to_int.get(node_id)
        if u is None:
            return []
        neighbor_ints = self.get_neighbor_ids(u)
        return [self.int_to_node[int(v)] for v in neighbor_ints]

    def has_path(self, source_id: str, target_id: str, max_depth: int = 3) -> bool:
        """Evaluate if an admissible path connects two concepts within max_depth."""
        u = self.node_to_int.get(source_id)
        v = self.node_to_int.get(target_id)
        if u is None or v is None:
            return False
        if u == v:
            return True

        visited: Set[int] = {u}
        queue = [(u, 0)]

        while queue:
            curr, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            for nbr in self.get_neighbor_ids(curr):
                nbr_int = int(nbr)
                if nbr_int == v:
                    return True
                if nbr_int not in visited:
                    visited.add(nbr_int)
                    queue.append((nbr_int, depth + 1))

        return False

    def bfs_expansion(
        self, seed_ids: List[str], max_depth: int = 2, max_nodes: int = 200
    ) -> Dict[str, int]:
        """Perform fast multi-seed BFS expansion returning node_id -> depth."""
        visited_depth: Dict[str, int] = {}
        queue: List[Tuple[int, int]] = []

        for sid in seed_ids:
            u = self.node_to_int.get(sid)
            if u is not None and sid not in visited_depth:
                visited_depth[sid] = 0
                queue.append((u, 0))

        while queue and len(visited_depth) < max_nodes:
            curr_u, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            nbrs = self.get_neighbor_ids(curr_u)
            for nbr in nbrs:
                nbr_int = int(nbr)
                nbr_id = self.int_to_node[nbr_int]
                if nbr_id not in visited_depth:
                    visited_depth[nbr_id] = depth + 1
                    queue.append((nbr_int, depth + 1))
                    if len(visited_depth) >= max_nodes:
                        break

        return visited_depth

    def benchmark_traversal(self, num_lookups: int = 10000) -> Dict[str, Any]:
        """Benchmark single-hop contiguous slicing latency."""
        if self.num_nodes == 0:
            return {"error": "empty graph"}

        u_indices = np.random.randint(0, self.num_nodes, size=num_lookups)
        start = time.perf_counter()
        total_edges_traversed = 0
        for u in u_indices:
            edges = self.get_neighbor_ids(int(u))
            total_edges_traversed += len(edges)
        elapsed_sec = time.perf_counter() - start

        us_per_lookup = (elapsed_sec / num_lookups) * 1_000_000
        lookups_per_sec = num_lookups / elapsed_sec if elapsed_sec > 0 else 0

        return {
            "num_nodes": self.num_nodes,
            "num_edges": self.num_edges,
            "num_lookups": num_lookups,
            "elapsed_sec": round(elapsed_sec, 4),
            "us_per_lookup": round(us_per_lookup, 3),
            "lookups_per_sec": round(lookups_per_sec, 1),
            "total_edges_traversed": total_edges_traversed,
        }
