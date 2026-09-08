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

    ingestor = PubmedBatchIngestor()
    csr, report = ingestor.ingest_shards([cached_shard], output_csr_dir=tmp_path / "csr_out")

    assert report.shards_processed == 1
    assert report.total_articles == 30000
    assert report.total_mesh_headings > 300000
    assert report.total_graph_nodes > 30000
    assert report.total_graph_edges > 600000
    assert report.articles_per_sec > 500.0
    assert (tmp_path / "csr_out" / "indptr.npy").exists()
    assert (tmp_path / "csr_out" / "indices.npy").exists()
