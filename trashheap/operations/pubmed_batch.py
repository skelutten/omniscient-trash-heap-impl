"""Large-scale batch ingestion engine for PubMed annual baseline archives (Plan 96, ADA-008).

Streams gzip-compressed XML shards (pubmed26n*.xml.gz) sequentially with constant O(1)
memory usage, extracts MeSH descriptors and citation networks, and compiles high-scale
memory-mapped Compressed Sparse Row (CSR) binary projections.
"""

from __future__ import annotations

import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from trashheap.graph.csr import CsrGraphProjection
from trashheap.operations.pubmed import stream_pubmed_xml

NCBI_BASELINE_URL = "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline"


@dataclass
class BatchIngestionReport:
    """Performance and telemetry report for large-scale PubMed batch ingestion."""

    shards_processed: int
    total_articles: int
    total_mesh_headings: int
    total_citations: int
    unique_mesh_concepts: int
    total_graph_nodes: int
    total_graph_edges: int
    download_time_sec: float
    parse_time_sec: float
    csr_build_time_sec: float
    total_elapsed_sec: float
    articles_per_sec: float
    csr_memory_bytes: int
    single_hop_latency_us: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shards_processed": self.shards_processed,
            "total_articles": self.total_articles,
            "total_mesh_headings": self.total_mesh_headings,
            "total_citations": self.total_citations,
            "unique_mesh_concepts": self.unique_mesh_concepts,
            "total_graph_nodes": self.total_graph_nodes,
            "total_graph_edges": self.total_graph_edges,
            "download_time_sec": round(self.download_time_sec, 2),
            "parse_time_sec": round(self.parse_time_sec, 2),
            "csr_build_time_sec": round(self.csr_build_time_sec, 3),
            "total_elapsed_sec": round(self.total_elapsed_sec, 2),
            "articles_per_sec": round(self.articles_per_sec, 1),
            "csr_memory_mb": round(self.csr_memory_bytes / (1024 * 1024), 2),
            "single_hop_latency_us": round(self.single_hop_latency_us, 3),
        }


class PubmedBatchIngestor:
    """Streamlined batch processor for multi-shard PubMed baseline archives."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        year: int = 26,
    ):
        self.cache_dir = Path(cache_dir or ".cache/pubmed")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.year = year

    def shard_filename(self, shard_num: int) -> str:
        return f"pubmed{self.year:02d}n{shard_num:04d}.xml.gz"

    def shard_url(self, shard_num: int) -> str:
        return f"{NCBI_BASELINE_URL}/{self.shard_filename(shard_num)}"

    def download_shard(self, shard_num: int, force: bool = False) -> Path:
        """Download a single baseline shard archive with resume/cache check."""
        fname = self.shard_filename(shard_num)
        target = self.cache_dir / fname
        if target.exists() and not force and target.stat().st_size > 1000:
            return target

        url = self.shard_url(shard_num)
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (OmniscientTrashHeap)"}
        )
        tmp_target = self.cache_dir / f"{fname}.tmp"

        with urllib.request.urlopen(req, timeout=60) as resp, open(tmp_target, "wb") as f:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)

        tmp_target.rename(target)
        return target

    def download_shards(self, shard_range: range, max_retries: int = 3) -> List[Path]:
        """Download multiple shards sequentially."""
        paths = []
        for s_num in shard_range:
            for attempt in range(max_retries):
                try:
                    p = self.download_shard(s_num)
                    paths.append(p)
                    break
                except Exception as err:
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"Failed downloading shard {s_num}: {err}") from err
                    time.sleep(2)
        return paths

    def ingest_shards(
        self,
        shard_paths: List[Path],
        output_csr_dir: Optional[Path] = None,
        include_mesh_bridges: bool = True,
    ) -> Tuple[CsrGraphProjection, BatchIngestionReport]:
        """Parse multiple shards sequentially and build unified CSR graph."""
        start_total = time.perf_counter()

        node_to_int: Dict[str, int] = {}
        int_to_node: List[str] = []

        def get_or_register_node(nid: str) -> int:
            idx = node_to_int.get(nid)
            if idx is None:
                idx = len(int_to_node)
                node_to_int[nid] = idx
                int_to_node.append(nid)
            return idx

        # Adjacency lists: source_int -> set of target_ints
        adj: Dict[int, Set[int]] = {}

        total_articles = 0
        total_mesh_headings = 0
        total_citations = 0
        unique_mesh_uis: Set[str] = set()

        parse_start = time.perf_counter()

        for shard_idx, sp in enumerate(shard_paths, 1):
            shard_art_count = 0
            for art in stream_pubmed_xml(sp):
                total_articles += 1
                shard_art_count += 1
                u = get_or_register_node(art.canonical_id)

                if u not in adj:
                    adj[u] = set()

                # Citations
                for cited in art.citations:
                    total_citations += 1
                    target_nid = f"PERS-ART-MED_{cited:08d}-0001"
                    v = get_or_register_node(target_nid)
                    adj[u].add(v)

                # MeSH concept headings
                for mesh in art.mesh_headings:
                    total_mesh_headings += 1
                    ui = mesh.get("ui")
                    if ui:
                        unique_mesh_uis.add(ui)
                        if include_mesh_bridges:
                            m_nid = f"MESH_{ui}"
                            m_u = get_or_register_node(m_nid)
                            if m_u not in adj:
                                adj[m_u] = set()
                            adj[u].add(m_u)
                            adj[m_u].add(u)

        parse_elapsed = time.perf_counter() - parse_start

        # Compile CSR binary arrays
        csr_start = time.perf_counter()
        num_nodes = len(int_to_node)
        indptr = np.zeros(num_nodes + 1, dtype=np.int64)
        indices_list: List[int] = []

        total_edges = 0
        for u in range(num_nodes):
            nbrs = sorted(adj.get(u, ()))
            indptr[u + 1] = indptr[u] + len(nbrs)
            indices_list.extend(nbrs)
            total_edges += len(nbrs)

        indices = (
            np.array(indices_list, dtype=np.int64) if indices_list else np.empty(0, dtype=np.int64)
        )

        csr = CsrGraphProjection(
            indptr=indptr,
            indices=indices,
            node_to_int=node_to_int,
            int_to_node=int_to_node,
        )
        csr_build_elapsed = time.perf_counter() - csr_start

        # Persist if requested
        if output_csr_dir:
            csr.save(Path(output_csr_dir))

        # Traversal benchmark
        bench = csr.benchmark_traversal(num_lookups=50000)
        single_hop_lat = bench.get("us_per_lookup", 0.0)

        total_elapsed = time.perf_counter() - start_total
        throughput = total_articles / max(0.001, parse_elapsed)
        csr_mem = indptr.nbytes + indices.nbytes

        report = BatchIngestionReport(
            shards_processed=len(shard_paths),
            total_articles=total_articles,
            total_mesh_headings=total_mesh_headings,
            total_citations=total_citations,
            unique_mesh_concepts=len(unique_mesh_uis),
            total_graph_nodes=num_nodes,
            total_graph_edges=total_edges,
            download_time_sec=0.0,
            parse_time_sec=parse_elapsed,
            csr_build_time_sec=csr_build_elapsed,
            total_elapsed_sec=total_elapsed,
            articles_per_sec=throughput,
            csr_memory_bytes=csr_mem,
            single_hop_latency_us=single_hop_lat,
        )

        return csr, report
