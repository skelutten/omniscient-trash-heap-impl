"""Tests for large-scale PubMed batch ingestion and multi-shard CSR compilation."""

from pathlib import Path

from trashheap.operations.pubmed_batch import PubmedBatchIngestor


def test_pubmed_batch_ingestor_shard_naming():
    ingestor = PubmedBatchIngestor(year=26)
    assert ingestor.shard_filename(1) == "pubmed26n0001.xml.gz"
    assert ingestor.shard_filename(42) == "pubmed26n0042.xml.gz"
    assert ingestor.shard_filename(1218) == "pubmed26n1218.xml.gz"
    assert (
        "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed26n0001.xml.gz" == ingestor.shard_url(1)
    )


def test_pubmed_batch_ingest_single_shard(tmp_path: Path):
    cached_shard = Path(".cache/pubmed/pubmed26n0001.xml.gz")
    if not cached_shard.exists():
        # Skip if shard not pre-cached locally
        return

    ingestor = PubmedBatchIngestor(download_workers=2, parse_workers=1)
    csr, report = ingestor.ingest_shards([cached_shard], output_csr_dir=tmp_path / "csr_out")

    assert report.shards_processed == 1
    assert report.total_articles == 30000
    assert report.total_mesh_headings > 300000
    assert report.total_graph_nodes > 30000
    assert report.total_graph_edges > 600000
    assert report.articles_per_sec > 250.0
    assert (tmp_path / "csr_out" / "indptr.npy").exists()
    assert (tmp_path / "csr_out" / "indices.npy").exists()


def test_pubmed_batch_parallel_multiprocess(tmp_path: Path):
    s1 = Path(".cache/pubmed/pubmed26n0001.xml.gz")
    s2 = Path(".cache/pubmed/pubmed26n0002.xml.gz")
    if not s1.exists() or not s2.exists():
        return

    ingestor = PubmedBatchIngestor(download_workers=2, parse_workers=2)
    csr, report = ingestor.ingest_shards(
        [s1, s2],
        output_csr_dir=tmp_path / "csr_2shards",
        num_parse_workers=2,
    )

    assert report.shards_processed == 2
    assert report.total_articles == 60000
    assert report.parse_workers == 2
    assert report.total_graph_nodes > 50000
    assert report.total_graph_edges > 1000000
    assert (tmp_path / "csr_2shards" / "indptr.npy").exists()
    assert (tmp_path / "csr_2shards" / "indices.npy").exists()
    assert (tmp_path / "csr_2shards" / "node_index.json").exists()
