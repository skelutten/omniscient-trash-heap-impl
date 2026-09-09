#!/usr/bin/env python3
"""High-scale batch ingestion & CSR compilation for Full PubMed 2026 baseline (1,334 shards).

Invariants & Features:
- O(1) memory invariance via per-shard Parquet edge streaming (.cache/pubmed/edge_shards/).
- Multi-threaded concurrent shard downloading (ThreadPoolExecutor).
- Multi-process CPU parallelization (multiprocessing spawn Pool).
- Crash-resilient resumption (skips already-downloaded archives and parsed parquet shards).
- Out-of-core DuckDB CSR binary compilation (indptr.npy, indices.npy).
- Detailed progress telemetry, ETA, and logging to .cache/pubmed/full_job.log.
"""

from __future__ import annotations

import argparse
import datetime
import json
import multiprocessing
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import duckdb
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from trashheap.graph.csr import CsrGraphProjection
from trashheap.operations.pubmed import stream_pubmed_xml
from trashheap.operations.pubmed_batch import PubmedBatchIngestor


def get_current_rss_mb() -> float:
    """Read resident set size from /proc/self/status on Linux."""
    try:
        with open("/proc/self/status", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    parts = line.split()
                    return float(parts[1]) / 1024.0  # kB to MB
    except Exception:
        pass
    return 0.0


def _parse_shard_to_parquet_worker(args: Tuple[str, str, bool]) -> Dict[str, Any]:
    """Worker process streaming one XML shard and writing its edges to Parquet."""
    shard_path_str, out_parquet_str, include_mesh_bridges = args
    shard_path = Path(shard_path_str)
    out_parquet = Path(out_parquet_str)

    if out_parquet.exists() and out_parquet.stat().st_size > 1000:
        return {
            "shard_path": shard_path_str,
            "parquet_path": out_parquet_str,
            "status": "cached",
            "articles": 0,
            "citations": 0,
            "mesh_headings": 0,
            "edges": 0,
            "elapsed_sec": 0.0,
        }

    t0 = time.perf_counter()
    u_list: List[str] = []
    v_list: List[str] = []
    num_arts = 0
    num_citations = 0
    num_mesh = 0
    unique_mesh: Set[str] = set()

    for art in stream_pubmed_xml(shard_path):
        num_arts += 1
        u_nid = f"PERS-ART-MED_{art.pmid:08d}-0001"

        for cited in art.citations:
            num_citations += 1
            v_nid = f"PERS-ART-MED_{cited:08d}-0001"
            u_list.append(u_nid)
            v_list.append(v_nid)

        for m in art.mesh_headings:
            num_mesh += 1
            ui = m.get("ui")
            if ui:
                unique_mesh.add(ui)
                if include_mesh_bridges:
                    m_nid = f"MESH_{ui}"
                    u_list.append(u_nid)
                    v_list.append(m_nid)
                    u_list.append(m_nid)
                    v_list.append(u_nid)

    table = pa.Table.from_arrays(
        [pa.array(u_list, type=pa.string()), pa.array(v_list, type=pa.string())],
        names=["u", "v"],
    )
    tmp_parquet = out_parquet.with_suffix(".tmp.parquet")
    pq.write_table(table, tmp_parquet, compression="snappy")
    tmp_parquet.rename(out_parquet)
    elapsed = time.perf_counter() - t0

    return {
        "shard_path": shard_path_str,
        "parquet_path": out_parquet_str,
        "status": "parsed",
        "articles": num_arts,
        "citations": num_citations,
        "mesh_headings": num_mesh,
        "unique_mesh": len(unique_mesh),
        "edges": len(u_list),
        "elapsed_sec": elapsed,
    }


def compile_csr_from_parquet(
    edge_dir: Path,
    out_csr_dir: Path,
    max_memory: str = "5GB",
    threads: int = 2,
    log_func=print,
) -> Tuple[CsrGraphProjection, int]:
    """Compile Compressed Sparse Row binary projection from Parquet edge shards via DuckDB."""
    import shutil

    t0 = time.perf_counter()
    out_csr_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = out_csr_dir / "duckdb_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = edge_dir.parent
    distinct_nodes_pq = cache_dir / "distinct_nodes.parquet"
    node_mapping_pq = out_csr_dir / "node_mapping.parquet"
    indptr_npy = out_csr_dir / "indptr.npy"
    indices_npy = out_csr_dir / "indices.npy"

    con = duckdb.connect()
    con.execute(f"PRAGMA max_memory = '{max_memory}';")
    con.execute(f"PRAGMA threads = {threads};")
    con.execute("PRAGMA preserve_insertion_order = false;")
    con.execute(f"PRAGMA temp_directory = '{temp_dir}';")

    # Step 1: Distinct nodes
    if not distinct_nodes_pq.exists() or distinct_nodes_pq.stat().st_size < 1000:
        log_func("DuckDB: Extracting distinct source nodes (u)...")
        con.execute(
            f"COPY (SELECT DISTINCT u AS id FROM read_parquet('{edge_dir}/*.parquet')) TO '{cache_dir}/u_nodes.parquet' (FORMAT PARQUET);"
        )
        log_func("DuckDB: Extracting distinct target nodes (v)...")
        con.execute(
            f"COPY (SELECT DISTINCT v AS id FROM read_parquet('{edge_dir}/*.parquet')) TO '{cache_dir}/v_nodes.parquet' (FORMAT PARQUET);"
        )
        log_func("DuckDB: Merging and ordering distinct nodes...")
        con.execute(f"""
            COPY (
                SELECT DISTINCT id FROM (
                    SELECT id FROM read_parquet('{cache_dir}/u_nodes.parquet')
                    UNION ALL
                    SELECT id FROM read_parquet('{cache_dir}/v_nodes.parquet')
                ) ORDER BY id
            ) TO '{distinct_nodes_pq}' (FORMAT PARQUET);
        """)
        (cache_dir / "u_nodes.parquet").unlink(missing_ok=True)
        (cache_dir / "v_nodes.parquet").unlink(missing_ok=True)

    # Step 2: Node mapping
    if not node_mapping_pq.exists() or node_mapping_pq.stat().st_size < 1000:
        log_func("DuckDB: Generating 0-based integer node mapping...")
        con.execute(f"""
            COPY (
                SELECT (row_number() OVER () - 1)::BIGINT AS node_idx, id AS node_id
                FROM read_parquet('{distinct_nodes_pq}')
            ) TO '{node_mapping_pq}' (FORMAT PARQUET);
        """)

    num_nodes = con.execute(
        f"SELECT count(*) FROM read_parquet('{distinct_nodes_pq}');"
    ).fetchone()[0]
    total_edges = con.execute(
        f"SELECT count(*) FROM read_parquet('{edge_dir}/*.parquet');"
    ).fetchone()[0]
    num_articles = con.execute(
        f"SELECT count(*) FROM read_parquet('{distinct_nodes_pq}') WHERE id LIKE 'PERS-ART-MED_%';"
    ).fetchone()[0]
    log_func(
        f"DuckDB: Verified {num_nodes:,} unique nodes ({num_articles:,} articles) and {total_edges:,} directed edges."
    )

    # Step 3: Degrees & indptr.npy
    if not indptr_npy.exists() or indptr_npy.stat().st_size < 1000:
        log_func("DuckDB: Calculating degree sequences and indptr offsets...")
        con.execute(f"""
            CREATE VIEW deg_counts AS
            SELECT u, count(*)::BIGINT AS deg
            FROM read_parquet('{edge_dir}/*.parquet')
            GROUP BY u;
        """)
        con.execute(f"""
            CREATE TABLE node_degrees AS
            SELECT m.node_idx, coalesce(d.deg, 0)::BIGINT AS deg
            FROM read_parquet('{node_mapping_pq}') m
            LEFT JOIN deg_counts d ON m.node_id = d.u
            ORDER BY m.node_idx;
        """)
        deg_arr = (
            con.execute("SELECT deg FROM node_degrees ORDER BY node_idx;")
            .to_arrow_table()
            .column(0)
            .to_numpy()
        )
        indptr = np.zeros(num_nodes + 1, dtype=np.int64)
        indptr[1:] = np.cumsum(deg_arr)
        np.save(indptr_npy, indptr)
        log_func(f"DuckDB: Saved indptr.npy ({indptr.nbytes / (1024 * 1024):.1f} MB).")
    else:
        log_func("DuckDB: Loading existing verified indptr.npy from disk...")
        indptr = np.load(indptr_npy)

    # Step 4: Indices.npy memmap streaming
    if not indices_npy.exists() or indices_npy.stat().st_size != total_edges * 8:
        log_func(
            "DuckDB: Streaming indices binary array directly to disk via memory mapping..."
        )
        indices = np.memmap(
            indices_npy,
            dtype=np.int64,
            mode="w+",
            shape=(total_edges,),
        )
        con.execute(f"""
            CREATE VIEW mapped_edges AS
            SELECT m1.node_idx AS u_idx, m2.node_idx AS v_idx
            FROM read_parquet('{edge_dir}/*.parquet') e
            JOIN read_parquet('{node_mapping_pq}') m1 ON e.u = m1.node_id
            JOIN read_parquet('{node_mapping_pq}') m2 ON e.v = m2.node_id;
        """)
        cursor = 0
        batch_size = 20_000_000
        res = con.execute("SELECT v_idx FROM mapped_edges ORDER BY u_idx, v_idx")
        reader = res.to_arrow_reader(batch_size=batch_size)
        for batch in reader:
            arr = batch.column(0).to_numpy()
            sz = len(arr)
            indices[cursor : cursor + sz] = arr
            cursor += sz
            log_func(
                f"DuckDB: Streamed {cursor:,} / {total_edges:,} edges ({cursor / total_edges * 100:.1f}%)..."
            )
        indices.flush()
        log_func("DuckDB: Flushed full indices.npy binary array to disk.")
    else:
        log_func("DuckDB: Mapping existing indices.npy from disk...")
        indices = np.memmap(indices_npy, dtype=np.int64, mode="r", shape=(total_edges,))

    # Node index metadata
    if num_nodes <= 1_000_000:
        node_rows = con.execute(
            f"SELECT node_id FROM read_parquet('{node_mapping_pq}') ORDER BY node_idx;"
        ).fetchall()
        int_to_node = [r[0] for r in node_rows]
        node_to_int = {nid: idx for idx, nid in enumerate(int_to_node)}
    else:
        int_to_node = []
        node_to_int = {}

    meta = {
        "num_nodes": num_nodes,
        "num_edges": total_edges,
        "num_articles": num_articles,
        "nodes": int_to_node,
        "node_mapping_parquet": "node_mapping.parquet",
        "relation_types": ["CITES", "HAS_MESH"],
    }
    (out_csr_dir / "node_index.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    con.close()
    shutil.rmtree(temp_dir, ignore_errors=True)

    csr = CsrGraphProjection(
        indptr=indptr,
        indices=indices,
        node_to_int=node_to_int,
        int_to_node=int_to_node,
        edge_relation_types=["CITES", "HAS_MESH"],
    )
    elapsed = time.perf_counter() - t0
    log_func(f"DuckDB: Full CSR matrix compilation completed in {elapsed:.2f}s!")
    return csr, num_articles


def main() -> None:
    parser = argparse.ArgumentParser(description="Full PubMed 2026 Baseline Batch Ingestion Engine")
    parser.add_argument(
        "--total-shards", type=int, default=1334, help="Total shards to process (default: 1334)"
    )
    parser.add_argument(
        "--shard-start", type=int, default=1, help="Starting shard number (default: 1)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=25, help="Shards per batch checkpoint (default: 25)"
    )
    parser.add_argument(
        "--download-workers", type=int, default=4, help="Download threads (default: 4)"
    )
    parser.add_argument(
        "--parse-workers",
        type=int,
        default=None,
        help="Parse worker processes (default: CPU count)",
    )
    parser.add_argument(
        "--cache-dir", type=Path, default=Path(".cache/pubmed"), help="Cache directory"
    )
    parser.add_argument(
        "--output-csr",
        type=Path,
        default=Path(".cache/pubmed/csr_full"),
        help="Output CSR directory",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path(".cache/pubmed/full_job.log"),
        help="Telemetry log file",
    )
    args = parser.parse_args()

    cache_dir = args.cache_dir.resolve()
    edge_dir = cache_dir / "edge_shards"
    edge_dir.mkdir(parents=True, exist_ok=True)
    args.output_csr.mkdir(parents=True, exist_ok=True)
    args.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(msg: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {msg}"
        print(formatted, flush=True)
        with open(args.log_file, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
            f.flush()

    num_parse_workers = args.parse_workers or min(os.cpu_count() or 1, 4)
    ingestor = PubmedBatchIngestor(
        cache_dir=cache_dir,
        download_workers=args.download_workers,
        parse_workers=num_parse_workers,
    )

    all_shards = list(range(args.shard_start, args.shard_start + args.total_shards))
    log("================================================================================")
    log(
        f"Starting Full PubMed Baseline Batch Pipeline ({len(all_shards)} shards: {all_shards[0]}..{all_shards[-1]})"
    )
    log(
        f"Config: {args.download_workers} download threads | {num_parse_workers} CPU parse workers | Batch size: {args.batch_size}"
    )
    log(f"Cache Dir: {cache_dir}")
    log(f"Edge Shards Dir: {edge_dir}")
    log(f"Target CSR Dir: {args.output_csr}")
    log("================================================================================")

    job_start_time = time.perf_counter()
    total_articles = 0
    total_citations = 0
    total_mesh = 0
    total_edges = 0

    ctx = multiprocessing.get_context("spawn")

    # Process in batches to pipeline download, parse, and checkpoint progress
    for batch_idx in range(0, len(all_shards), args.batch_size):
        batch_slice = all_shards[batch_idx : batch_idx + args.batch_size]
        batch_t0 = time.perf_counter()

        log(
            f"--- [Batch {batch_idx + 1}..{batch_idx + len(batch_slice)} / {len(all_shards)}] Verifying / Downloading {len(batch_slice)} shards ---"
        )
        shard_paths = ingestor.download_shards(batch_slice)

        # Prepare parse tasks
        tasks = []
        for sp in shard_paths:
            s_name = sp.stem.replace(".xml", "")  # e.g. pubmed26n0001
            out_pq = edge_dir / f"{s_name}.parquet"
            tasks.append((str(sp), str(out_pq), True))

        # Parse tasks in parallel worker pool
        with ctx.Pool(processes=min(num_parse_workers, len(tasks))) as pool:
            for res in pool.imap_unordered(_parse_shard_to_parquet_worker, tasks):
                total_articles += res.get("articles", 0)
                total_citations += res.get("citations", 0)
                total_mesh += res.get("mesh_headings", 0)
                total_edges += res.get("edges", 0)

        batch_elapsed = time.perf_counter() - batch_t0
        total_elapsed = time.perf_counter() - job_start_time
        shards_done = batch_idx + len(batch_slice)
        fraction_done = shards_done / len(all_shards)
        eta_sec = (total_elapsed / max(0.001, fraction_done)) - total_elapsed
        eta_hours = eta_sec / 3600.0
        overall_rate = total_articles / max(0.001, total_elapsed)
        rss_mb = get_current_rss_mb()

        log(
            f"✓ Progress: {shards_done}/{len(all_shards)} shards ({fraction_done * 100:.1f}%) | "
            f"Batch Time: {batch_elapsed:.1f}s | "
            f"Articles: {total_articles:,} | "
            f"Edges: {total_edges:,} | "
            f"Rate: {overall_rate:,.1f} arts/s | "
            f"Elapsed: {total_elapsed / 60.0:.1f}m | "
            f"ETA: {eta_hours:.2f}h | "
            f"RSS: {rss_mb:.1f} MB"
        )

    log("================================================================================")
    log(
        f"All {len(all_shards)} XML shards parsed into Parquet edges! Commencing DuckDB CSR matrix compilation..."
    )
    log("================================================================================")

    csr_start = time.perf_counter()
    csr, num_articles = compile_csr_from_parquet(
        edge_dir=edge_dir,
        out_csr_dir=args.output_csr,
        max_memory="5GB",
        threads=2,
        log_func=log,
    )
    csr_elapsed = time.perf_counter() - csr_start
    log(f"DuckDB CSR build finished in {csr_elapsed:.2f}s.")

    log("Benchmarking single-hop CSR neighbor lookup latency...")
    bench = csr.benchmark_traversal(num_lookups=100000)
    single_hop_lat = bench.get("us_per_lookup", 0.0)

    total_job_time = time.perf_counter() - job_start_time
    log("================================================================================")
    log(f"FULL PUBMED BASELINE INGESTION COMPLETE in {total_job_time / 3600.0:.2f} hours!")
    log(f"Total Vertices: {csr.num_nodes:,}")
    log(f"Total Edges: {csr.num_edges:,}")
    log(f"Single-Hop Latency: {single_hop_lat:.3f} µs")
    log(f"CSR Binary Projection stored at: {args.output_csr}")
    log("================================================================================")

    report_data = {
        "status": "completed",
        "total_shards": len(all_shards),
        "total_articles": num_articles if num_articles > 0 else total_articles,
        "total_citations": total_citations,
        "total_mesh_headings": total_mesh,
        "graph_nodes": csr.num_nodes,
        "graph_edges": csr.num_edges,
        "total_elapsed_sec": round(total_job_time, 2),
        "total_elapsed_hours": round(total_job_time / 3600.0, 2),
        "single_hop_latency_us": round(single_hop_lat, 3),
        "csr_dir": str(args.output_csr),
    }
    (cache_dir / "full_pubmed_report.json").write_text(
        json.dumps(report_data, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
