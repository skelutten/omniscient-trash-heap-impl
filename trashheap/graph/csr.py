"""Compressed Sparse Row (CSR) binary array graph projection (specs/GRAPH-INTELLIGENCE.md §11.1).

Enables microsecond (< 10 µs) single-hop graph traversals via contiguous NumPy
array slicing, memory-mapped zero-copy persistence (indptr.npy, indices.npy),
and deterministic integer vertex IDs.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from trashheap.corpus import Corpus
from trashheap.fsutil import atomic_write_text

_NUMPY_MAGIC = b"\x93NUMPY"


def _load_int64_memmap(path: Path) -> np.ndarray:
    """Memory-map an int64 array stored as .npy (with header) or as headerless raw bytes.

    Full-scale out-of-core compilers historically streamed ``indices.npy`` as a
    headerless raw int64 file; the package writer emits standard ``.npy``. Both
    formats are detected via the ``\\x93NUMPY`` magic and mapped zero-copy.
    """
    with open(path, "rb") as f:
        magic = f.read(6)
    if magic == _NUMPY_MAGIC:
        return np.load(path, mmap_mode="r")
    return np.memmap(path, dtype=np.int64, mode="r")


def _validate_csr_arrays(indptr: np.ndarray, indices: np.ndarray, source_dir: Path) -> None:
    """Fail closed on structurally inconsistent CSR artifacts.

    Raises:
        ValueError: If indptr is not int64, does not start at 0, or its last
            offset does not equal the number of stored indices.
    """
    if len(indptr) == 0:
        raise ValueError(f"CSR indptr is empty in {source_dir}")
    if indptr.dtype != np.int64:
        raise ValueError(
            f"CSR indptr dtype must be int64, got {indptr.dtype} in {source_dir}"
        )
    if int(indptr[0]) != 0:
        raise ValueError(f"CSR indptr[0] must be 0, got {int(indptr[0])} in {source_dir}")
    if int(indptr[-1]) != len(indices):
        raise ValueError(
            f"CSR artifact mismatch in {source_dir}: indptr[-1]={int(indptr[-1])} "
            f"but indices holds {len(indices)} entries (truncated or corrupt artifact)"
        )


def _atomic_npy_save(path: Path, arr: np.ndarray) -> None:
    """np.save to a temporary file in the same directory, fsync, then os.replace."""
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            np.save(f, arr)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    try:
        dir_fd = os.open(str(path.parent), os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(dir_fd)
    except OSError:
        pass
    finally:
        os.close(dir_fd)


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
            if directed:
                neighbors = sorted(adj_lists[u], key=lambda x: (x[0], x[1]))
            else:
                # Undirected: mutual relations would otherwise add the same
                # (target, type) pair twice; dedupe so they are not double-counted.
                neighbors = sorted(set(adj_lists[u]))
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
        """Persist binary arrays and metadata to directory atomically."""
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        _atomic_npy_save(target_dir / "indptr.npy", self.indptr)
        _atomic_npy_save(target_dir / "indices.npy", self.indices)

        meta = {
            "num_nodes": self.num_nodes,
            "num_edges": self.num_edges,
            "nodes": self.int_to_node,
            "relation_types": self.edge_relation_types or [],
        }
        atomic_write_text(target_dir / "node_index.json", json.dumps(meta, indent=2))

    @classmethod
    def load_memmap(cls, target_dir: Path) -> CsrGraphProjection:
        """Load graph using zero-copy memory maps for instant startup.

        Accepts both artifact formats for each array: standard ``.npy`` files
        (``\\x93NUMPY`` magic) and headerless raw int64 streams. Structural
        invariants (int64 indptr, ``indptr[0] == 0``, ``indptr[-1] ==
        len(indices)``) are validated on load.

        Raises:
            ValueError: If the artifacts are truncated, corrupt, or inconsistent.
        """
        target_dir = Path(target_dir)
        indptr = _load_int64_memmap(target_dir / "indptr.npy")
        indices = _load_int64_memmap(target_dir / "indices.npy")
        _validate_csr_arrays(indptr, indices, target_dir)

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

    def _require_node_mapping(self) -> None:
        """Fail with a clear error when the projection lacks the int -> node ID mapping.

        Full-scale artifacts store ``"nodes": []`` in node_index.json (the mapping
        lives in node_mapping.parquet instead), so string-based lookups cannot be
        served and must not degrade into IndexError or silent empty results.
        """
        if not self.int_to_node:
            raise RuntimeError(
                "CSR projection lacks the node ID mapping (node_index.json 'nodes' is "
                "empty; full-scale artifacts store it in node_mapping.parquet instead). "
                "String-based lookups (get_neighbors, bfs_expansion) are unavailable; "
                "use integer-index access (get_neighbor_ids) or rebuild with the mapping."
            )

    def get_neighbor_ids(self, u: int) -> np.ndarray:
        """Extract contiguous slice of outgoing neighbor integer IDs (< 10 µs)."""
        if u < 0 or u >= self.num_nodes:
            return np.empty(0, dtype=np.int64)
        start = int(self.indptr[u])
        end = int(self.indptr[u + 1])
        return self.indices[start:end]

    def get_neighbors(self, node_id: str) -> List[str]:
        """Return list of neighbor canonical node IDs.

        Raises:
            RuntimeError: If the projection lacks the node ID mapping.
        """
        self._require_node_mapping()
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
        queue: deque[Tuple[int, int]] = deque([(u, 0)])

        while queue:
            curr, depth = queue.popleft()
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
        """Perform fast multi-seed BFS expansion returning node_id -> depth.

        Raises:
            RuntimeError: If the projection lacks the node ID mapping.
        """
        self._require_node_mapping()
        visited_depth: Dict[str, int] = {}
        queue: deque[Tuple[int, int]] = deque()

        for sid in seed_ids:
            u = self.node_to_int.get(sid)
            if u is not None and sid not in visited_depth:
                visited_depth[sid] = 0
                queue.append((u, 0))

        while queue and len(visited_depth) < max_nodes:
            curr_u, depth = queue.popleft()
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
        """Benchmark single-hop contiguous slicing latency with a seeded RNG."""
        if self.num_nodes == 0:
            return {"error": "empty graph"}

        rng = np.random.default_rng(42)
        u_indices = rng.integers(0, self.num_nodes, size=num_lookups)
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
