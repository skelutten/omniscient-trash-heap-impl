"""Tests for Compressed Sparse Row (CSR) binary array graph projection (specs/GRAPH-INTELLIGENCE.md §11.1)."""

from pathlib import Path

from trashheap.corpus import load_corpus
from trashheap.graph.csr import CsrGraphProjection


def test_csr_graph_build_and_traversal():
    corpus = load_corpus(Path("fixtures/canonical"))
    csr = CsrGraphProjection.build_from_corpus(corpus)

    assert csr.num_nodes == len(corpus)
    assert csr.num_edges > 0
    assert len(csr.indptr) == csr.num_nodes + 1
    assert len(csr.indices) == csr.num_edges

    # Check a known node with relations
    first_with_rels = next(
        ko for ko in corpus.objects if ko.frontmatter and ko.frontmatter.relations
    )
    expected_targets = {
        r.target for r in first_with_rels.frontmatter.relations if r.target in csr.node_to_int
    }

    actual_neighbors = set(csr.get_neighbors(first_with_rels.id))
    assert actual_neighbors == expected_targets


def test_csr_graph_memmap_persistence(tmp_path: Path):
    corpus = load_corpus(Path("fixtures/canonical"))
    csr = CsrGraphProjection.build_from_corpus(corpus)

    out_dir = tmp_path / "csr_cache"
    csr.save(out_dir)

    assert (out_dir / "indptr.npy").exists()
    assert (out_dir / "indices.npy").exists()
    assert (out_dir / "node_index.json").exists()

    # Load via memory map
    mmap_csr = CsrGraphProjection.load_memmap(out_dir)
    assert mmap_csr.num_nodes == csr.num_nodes
    assert mmap_csr.num_edges == csr.num_edges

    # Check neighbors match
    for ko in corpus.objects:
        if ko.id:
            assert mmap_csr.get_neighbors(ko.id) == csr.get_neighbors(ko.id)


def test_csr_graph_path_and_bfs():
    corpus = load_corpus(Path("fixtures/canonical"))
    csr = CsrGraphProjection.build_from_corpus(corpus)

    # Pick connected pair
    connected_pair = None
    for ko in corpus.objects:
        nbrs = csr.get_neighbors(ko.id)
        if nbrs:
            connected_pair = (ko.id, nbrs[0])
            break

    assert connected_pair is not None
    src, dst = connected_pair
    assert csr.has_path(src, dst, max_depth=1) is True
    assert csr.has_path(src, "NON_EXISTENT_NODE_9999", max_depth=3) is False

    # BFS expansion
    depths = csr.bfs_expansion([src], max_depth=2)
    assert src in depths
    assert depths[src] == 0
    assert dst in depths
    assert depths[dst] == 1


def test_csr_graph_benchmark_microsecond_latency():
    corpus = load_corpus(Path("fixtures/canonical"))
    csr = CsrGraphProjection.build_from_corpus(corpus)

    bench = csr.benchmark_traversal(num_lookups=5000)
    assert bench["num_lookups"] == 5000
    assert bench["elapsed_sec"] > 0
    # Slicing numpy array contiguous memory should easily execute in < 25 microseconds per lookup
    assert bench["us_per_lookup"] < 50.0
