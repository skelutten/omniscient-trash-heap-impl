"""Tests for the full-scale CSR compilation pipeline (scripts/ingest_full_pubmed.py).

Pins the C1 regression class: artifacts written by the out-of-core compiler MUST
be loadable by the package's own ``CsrGraphProjection.load_memmap``, and resume
validity MUST require the completion marker rather than file size alone.
"""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")
pytest.importorskip("duckdb")

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "ingest_full_pubmed.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("ingest_full_pubmed", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_edges(tmp_path: Path, edges: list) -> Path:
    edge_dir = tmp_path / "edges"
    edge_dir.mkdir()
    table = pa.table({"u": [e[0] for e in edges], "v": [e[1] for e in edges]})
    pq.write_table(table, edge_dir / "edges_0000.parquet")
    return edge_dir


def test_compile_csr_roundtrip_via_package_loader(tmp_path: Path):
    mod = _load_script()
    edges = [
        ("PERS-ART-MED_00000001", "MESH_D000001"),
        ("PERS-ART-MED_00000001", "MESH_D000002"),
        ("PERS-ART-MED_00000002", "MESH_D000001"),
        ("PERS-ART-MED_00000002", "PERS-ART-MED_00000001"),
    ]
    edge_dir = _write_edges(tmp_path, edges)
    out = tmp_path / "csr"

    csr, num_articles = mod.compile_csr_from_parquet(edge_dir, out, log_func=lambda m: None)

    assert num_articles == 2
    assert csr.num_nodes == 4
    assert csr.num_edges == 4
    assert (out / "csr_manifest.json").exists()
    assert (out / "node_mapping.parquet").exists()

    from trashheap.graph.csr import CsrGraphProjection

    loaded = CsrGraphProjection.load_memmap(out)
    assert loaded.num_nodes == 4
    assert loaded.num_edges == 4
    nbrs = loaded.get_neighbors("PERS-ART-MED_00000001")
    assert set(nbrs) == {"MESH_D000001", "MESH_D000002"}


def test_resume_requires_completion_marker(tmp_path: Path):
    mod = _load_script()
    edges = [("A_1", "B_1"), ("A_1", "B_2")]
    edge_dir = _write_edges(tmp_path, edges)
    out = tmp_path / "csr"
    mod.compile_csr_from_parquet(edge_dir, out, log_func=lambda m: None)

    # Size-consistent arrays WITHOUT the marker must not count as complete.
    (out / "csr_manifest.json").unlink()
    complete, _reason = mod.check_csr_complete(out, 3, 2)
    assert not complete

    # A verified resume returns the loaded projection without recompiling.
    mod.write_csr_manifest(out, 3, 2)
    complete, _reason = mod.check_csr_complete(out, 3, 2)
    assert complete


def test_load_memmap_rejects_truncated_indices(tmp_path: Path):
    from trashheap.graph.csr import CsrGraphProjection

    d = tmp_path / "csr"
    d.mkdir()
    np.save(d / "indptr.npy", np.array([0, 2, 3], dtype=np.int64))
    np.save(d / "indices.npy", np.array([0, 1], dtype=np.int64))
    (d / "node_index.json").write_text(
        json.dumps({"num_nodes": 2, "num_edges": 3, "nodes": ["A", "B"]}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="mismatch"):
        CsrGraphProjection.load_memmap(d)


def test_load_memmap_accepts_headerless_legacy_indices(tmp_path: Path):
    from trashheap.graph.csr import CsrGraphProjection

    d = tmp_path / "csr"
    d.mkdir()
    np.save(d / "indptr.npy", np.array([0, 2, 3], dtype=np.int64))
    (d / "indices.npy").write_bytes(np.array([1, 0, 1], dtype=np.int64).tobytes())
    (d / "node_index.json").write_text(
        json.dumps({"num_nodes": 2, "num_edges": 3, "nodes": ["A", "B"]}), encoding="utf-8"
    )
    loaded = CsrGraphProjection.load_memmap(d)
    assert loaded.num_edges == 3
    assert set(loaded.get_neighbors("A")) == {"B", "A"}
