"""Large-scale batch ingestion engine for PubMed annual baseline archives (Plan 96, ADA-008).

Streams gzip-compressed XML shards (pubmed26n*.xml.gz) concurrently across CPU cores,
extracts MeSH descriptors and citation networks, and compiles high-scale memory-mapped
Compressed Sparse Row (CSR) binary projections.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import logging
import multiprocessing
import os
import time
import urllib.request
import uuid
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from trashheap.graph.csr import CsrGraphProjection
from trashheap.operations.pubmed import stream_pubmed_xml

logger = logging.getLogger(__name__)

NCBI_BASELINE_URL = "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline"
MIN_TRUSTED_SHARD_BYTES = 1000


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
    download_workers: int = 1
    parse_workers: int = 1

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
            "download_workers": self.download_workers,
            "parse_workers": self.parse_workers,
        }


@dataclass
class ShardExtraction:
    """Compact extraction payload from a single parsed shard for IPC transfer."""

    shard_path: str
    num_articles: int
    num_mesh_headings: int
    num_citations: int
    unique_mesh_uis: Set[str]
    # list of (pmid, citations_list, mesh_uis_list)
    records: List[Tuple[int, List[int], List[str]]]


def _parse_shard_worker(args: Tuple[str, bool]) -> ShardExtraction:
    """Worker function executed in separate worker process for CPU-parallel XML streaming."""
    shard_path_str, include_mesh_bridges = args
    shard_path = Path(shard_path_str)
    num_articles = 0
    num_mesh_headings = 0
    num_citations = 0
    unique_mesh_uis: Set[str] = set()
    records: List[Tuple[int, List[int], List[str]]] = []

    for art in stream_pubmed_xml(shard_path):
        num_articles += 1
        cites = art.citations
        num_citations += len(cites)

        mesh_uis: List[str] = []
        for mesh in art.mesh_headings:
            num_mesh_headings += 1
            ui = mesh.get("ui")
            if ui:
                unique_mesh_uis.add(ui)
                if include_mesh_bridges:
                    mesh_uis.append(ui)

        records.append((art.pmid, cites, mesh_uis))

    return ShardExtraction(
        shard_path=shard_path_str,
        num_articles=num_articles,
        num_mesh_headings=num_mesh_headings,
        num_citations=num_citations,
        unique_mesh_uis=unique_mesh_uis,
        records=records,
    )


class PubmedBatchIngestor:
    """Streamlined batch processor for multi-shard PubMed baseline archives."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        year: int = 26,
        download_workers: int = 4,
        parse_workers: Optional[int] = None,
    ):
        self.cache_dir = Path(cache_dir or ".cache/pubmed")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.year = year
        self.download_workers = max(1, download_workers)
        self.parse_workers = (
            parse_workers if parse_workers is not None else min(os.cpu_count() or 1, 4)
        )

    def shard_filename(self, shard_num: int) -> str:
        return f"pubmed{self.year:02d}n{shard_num:04d}.xml.gz"

    def shard_url(self, shard_num: int) -> str:
        return f"{NCBI_BASELINE_URL}/{self.shard_filename(shard_num)}"

    def shard_md5_url(self, shard_num: int) -> str:
        return f"{NCBI_BASELINE_URL}/{self.shard_filename(shard_num)}.md5"

    def _fetch_expected_md5(self, shard_num: int) -> Optional[str]:
        """Best-effort fetch of the sibling ``{fname}.md5`` checksum.

        Returns the lowercase hex digest, or ``None`` when the checksum file is
        unavailable (404/network/empty), in which case the caller falls back to
        the size heuristic.
        """
        url = self.shard_md5_url(shard_num)
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (OmniscientTrashHeap)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read().decode("utf-8", "replace").strip()
        except Exception as err:
            logger.info("md5 checksum unavailable for %s (%s); using size heuristic", url, err)
            return None
        if not content:
            return None
        return content.split()[0].lower()

    def download_shard(self, shard_num: int, force: bool = False) -> Path:
        """Download a single baseline shard archive with integrity verification.

        Cache hits are trusted only when the shard exceeds the minimum size and,
        ideally, carries a sibling ``{fname}.verified`` marker written after a
        previously verified download. Pre-existing caches without the marker are
        accepted on the size heuristic alone (with a warning) so offline runs keep
        working. Fresh downloads compute an MD5 while streaming; when the upstream
        ``{fname}.md5`` is available the digest is verified exactly (a mismatch
        deletes the temp file and raises), otherwise the size heuristic is used.
        The temp file is fsynced and atomically ``os.replace``d into place.
        """
        fname = self.shard_filename(shard_num)
        target = self.cache_dir / fname
        marker = self.cache_dir / f"{fname}.verified"

        if target.exists() and not force and target.stat().st_size > MIN_TRUSTED_SHARD_BYTES:
            if not marker.exists():
                logger.warning(
                    "cached shard %s has no .verified marker; accepting on size heuristic", fname
                )
            return target

        url = self.shard_url(shard_num)
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (OmniscientTrashHeap)"}
        )
        tmp_target = self.cache_dir / f"{fname}.{os.getpid()}.{uuid.uuid4().hex[:8]}.tmp"

        try:
            md5 = hashlib.md5()
            size = 0
            with urllib.request.urlopen(req, timeout=60) as resp, open(tmp_target, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    md5.update(chunk)
                    size += len(chunk)
                f.flush()
                os.fsync(f.fileno())

            local_hex = md5.hexdigest()
            expected_hex = self._fetch_expected_md5(shard_num)

            checksum_tag: Optional[str]
            if expected_hex is not None:
                if local_hex != expected_hex:
                    raise RuntimeError(
                        f"MD5 mismatch for {fname}: expected {expected_hex}, got {local_hex}"
                    )
                checksum_tag = f"md5:{local_hex}"
            else:
                if size <= MIN_TRUSTED_SHARD_BYTES:
                    raise RuntimeError(
                        f"Downloaded shard {fname} is suspiciously small ({size} bytes) and no "
                        "MD5 checksum was available to verify it"
                    )
                checksum_tag = None

            os.replace(tmp_target, target)
            marker.write_text((checksum_tag or "size_heuristic") + "\n", encoding="utf-8")
            logger.info(
                "pubmed_shard_download %s", json.dumps({"shard": fname, "checksum": checksum_tag})
            )
            return target
        except BaseException:
            tmp_target.unlink(missing_ok=True)
            raise

    def _download_shard_with_retry(
        self, shard_num: int, max_retries: int = 3, force: bool = False
    ) -> Path:
        for attempt in range(max_retries):
            try:
                return self.download_shard(shard_num, force=force)
            except Exception as err:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed downloading shard {shard_num}: {err}") from err
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"Failed downloading shard {shard_num} after {max_retries} attempts")

    def download_shards(
        self,
        shard_range: range,
        max_retries: int = 3,
        num_workers: Optional[int] = None,
        force: bool = False,
    ) -> List[Path]:
        """Download multiple shards concurrently using thread pool."""
        workers = num_workers if num_workers is not None else self.download_workers
        shard_list = list(shard_range)
        if not shard_list:
            return []

        if workers <= 1 or len(shard_list) <= 1:
            return [self._download_shard_with_retry(s, max_retries, force) for s in shard_list]

        paths: Dict[int, Path] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_num = {
                executor.submit(self._download_shard_with_retry, s_num, max_retries, force): s_num
                for s_num in shard_list
            }
            for future in concurrent.futures.as_completed(future_to_num):
                s_num = future_to_num[future]
                paths[s_num] = future.result()

        return [paths[s] for s in shard_list]

    def ingest_shards(
        self,
        shard_paths: List[Path],
        output_csr_dir: Optional[Path] = None,
        include_mesh_bridges: bool = True,
        num_parse_workers: Optional[int] = None,
    ) -> Tuple[CsrGraphProjection, BatchIngestionReport]:
        """Parse multiple shards concurrently and build unified CSR graph."""
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
        adj: Dict[int, Set[int]] = defaultdict(set)

        total_articles = 0
        total_mesh_headings = 0
        total_citations = 0
        unique_mesh_uis: Set[str] = set()

        parse_start = time.perf_counter()
        workers = num_parse_workers if num_parse_workers is not None else self.parse_workers

        def merge_extraction(extraction: ShardExtraction) -> None:
            nonlocal total_articles, total_mesh_headings, total_citations
            total_articles += extraction.num_articles
            total_mesh_headings += extraction.num_mesh_headings
            total_citations += extraction.num_citations
            unique_mesh_uis.update(extraction.unique_mesh_uis)

            for pmid, cites, mesh_uis in extraction.records:
                u_nid = f"PERS-ART-MED_{pmid:08d}-0001"
                u = get_or_register_node(u_nid)

                for cited in cites:
                    target_nid = f"PERS-ART-MED_{cited:08d}-0001"
                    v = get_or_register_node(target_nid)
                    adj[u].add(v)

                if include_mesh_bridges:
                    for ui in mesh_uis:
                        m_nid = f"MESH_{ui}"
                        m_u = get_or_register_node(m_nid)
                        adj[u].add(m_u)
                        adj[m_u].add(u)

        if workers > 1 and len(shard_paths) > 1:
            tasks = [(str(sp), include_mesh_bridges) for sp in shard_paths]
            pool_size = min(workers, len(shard_paths))
            ctx = multiprocessing.get_context("spawn")
            with ctx.Pool(processes=pool_size) as pool:
                for ext in pool.imap_unordered(_parse_shard_worker, tasks, chunksize=1):
                    merge_extraction(ext)
        else:
            for sp in shard_paths:
                ext = _parse_shard_worker((str(sp), include_mesh_bridges))
                merge_extraction(ext)

        parse_elapsed = time.perf_counter() - parse_start

        # Compile CSR binary arrays with direct contiguous memory allocation
        csr_start = time.perf_counter()
        num_nodes = len(int_to_node)
        indptr = np.zeros(num_nodes + 1, dtype=np.int64)

        total_edges = sum(len(adj[u]) for u in range(num_nodes) if u in adj)
        indices = np.empty(total_edges, dtype=np.int64)

        cursor = 0
        for u in range(num_nodes):
            nbrs = adj.get(u)
            if nbrs:
                nbrs_sorted = sorted(nbrs)
                deg = len(nbrs_sorted)
                indices[cursor : cursor + deg] = nbrs_sorted
                cursor += deg
                indptr[u + 1] = cursor
            else:
                indptr[u + 1] = cursor

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
            download_workers=self.download_workers,
            parse_workers=workers,
        )

        return csr, report
