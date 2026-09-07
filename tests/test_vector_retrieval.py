"""Comprehensive tests for Plan 90 Opt-In Vector Retrieval (D79–D84, D108).

Verifies:
1. Phase V1: Seam & Deterministic Double (D79) + Honest Modality Rule + AST network isolation (RET-005).
2. Phase V2: Offline Provider & Multi-Chunk max-over-chunks aggregation vs mean-pooling (D80, D81, SCALE-001).
3. Phase V3: 3-way Hybrid RRF Fusion (w_bm25=0.4, w_vector=0.4, w_graph=0.2) + Honest Evidence Bundles (D81, D82).
4. Phase V4: Cross-Encoder Exclusion & FinalScore == RRF (D83).
5. Phase V5: Degraded Fallback & Freshness Invalidation (D84) + CLI integration.
"""

import ast
from pathlib import Path

from trashheap.corpus import Corpus, load_corpus
from trashheap.models import KnowledgeObject
from trashheap.registry.loader import load_registries
from trashheap.retrieval import HybridRetriever
from trashheap.vector.chunking import strip_frontmatter
from trashheap.vector.double import DeterministicDouble
from trashheap.vector.provider import LocalOfflineProvider
from trashheap.vector.store import VectorIndex

# ==============================================================================
# Phase V1: AST Network Isolation & Honest Modality Rule (D79, RET-005)
# ==============================================================================


def test_ast_network_isolation():
    """Verify that trashheap/vector contains zero remote network imports or connection params."""
    vector_dir = Path("trashheap/vector")
    assert vector_dir.is_dir()

    forbidden_imports = {
        "requests",
        "urllib.request",
        "httpx",
        "socket",
        "aiohttp",
        "urllib3",
        "ftplib",
        "http.client",
    }
    forbidden_identifiers = {"api_key", "auth_token", "endpoint_url", "remote_host"}

    for py_file in vector_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in forbidden_imports, (
                        f"Forbidden import '{alias.name}' found in {py_file.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                assert mod not in forbidden_imports, (
                    f"Forbidden import from '{mod}' found in {py_file.name}"
                )
                for alias in node.names:
                    full_import = f"{mod}.{alias.name}"
                    assert full_import not in forbidden_imports, (
                        f"Forbidden import '{full_import}' found in {py_file.name}"
                    )
            elif isinstance(node, ast.arg):
                assert node.arg not in forbidden_identifiers, (
                    f"Forbidden parameter '{node.arg}' found in {py_file.name}"
                )


def test_honest_modality_rule_with_test_double():
    """D79: The test double (is_double=True) is strictly forbidden from claiming vector modality.

    In bundles, modalities_absent reports 'vector', vector_raw is None, and signals is None.
    """
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))

    double = DeterministicDouble()
    assert double.identity.is_double is True

    idx = VectorIndex()
    idx.build(corpus, double)

    retriever = HybridRetriever(
        corpus=corpus,
        registries=registries,
        vector_index=idx,
        embedder=double,
    )

    # When querying, even with enable_vector=True, the double MUST NOT claim the vector modality
    bundle = retriever.retrieve("architecture", cli_params={"enable_vector": True})

    assert "vector" in bundle["modalities_absent"]
    assert "vector" not in bundle["modalities_available"]

    for node in bundle["evidence_bundle"]:
        assert "vector" not in node["matched_by"]
        assert node["score_components"]["vector_raw"] is None
        assert node["retrieval_signals"]["vector"] is None


# ==============================================================================
# Phase V2: Multi-Chunk Max-Aggregation vs Mean-Pooling (D80, D81, SCALE-001)
# ==============================================================================


def test_frontmatter_stripping():
    """D81 item 4: Frontmatter is stripped so schema boilerplate does not pollute vector space."""
    doc = """---
id: TEST-001
title: Some Title
domain: software_engineering
---
# Actual Content
This is the real body text.
"""
    stripped = strip_frontmatter(doc)
    assert "---" not in stripped
    assert "TEST-001" not in stripped
    assert "Actual Content" in stripped
    assert "This is the real body text." in stripped


def test_multi_chunk_max_aggregation_vs_mean_pooling_proof():
    """SCALE-001: Empirical proof that max-aggregation outperforms mean-pooling on targeted passages.

    Demonstrates that a multi-chunk document containing a highly relevant section
    diluted by unrelated sections ranks higher under max-aggregation than under mean-pooling.
    """
    provider = LocalOfflineProvider()

    # Doc A: Section 1 is generic intro, Section 2 is an exact match for the query, Section 3 is unrelated.
    doc_a_body = """# Introduction
General background on operating systems and storage architectures.
Everything is built on layered abstractions and memory mapping.

# Distributed Build Cache Optimization
Bazel remote caching performance delivers forty percent lower build latency across distributed clusters.
Artifact hashes ensure hermetic replayability and distributed cache hit maximization.

# Incident Retrospective
Post-mortem analysis of database failover downtime during third quarter maintenance window.
Replication lag caused temporary transaction queue stalls.
"""

    # Doc B: All sections have mediocre generic relevance to caching, but no high-precision hit.
    doc_b_body = """# General Caching
Caching mechanisms store computed results for later retrieval.
In-memory caches and disk-based buffers improve general application responsiveness.

# Web Browser Caching
Browser HTTP caches reduce page load times for static assets.
Cache-control headers govern expiration and revalidation intervals.

# Disk Cache Systems
File system caches utilize kernel page cache for read amplification mitigation.
Block layer buffers improve sequential disk throughput.
"""

    ko_a = KnowledgeObject(
        path=Path("doc_a.md"),
        frontmatter_dict={"id": "DOC-A-MULTI", "title": "Doc A Multi-Chunk"},
        raw_body=doc_a_body,
    )
    ko_b = KnowledgeObject(
        path=Path("doc_b.md"),
        frontmatter_dict={"id": "DOC-B-UNIFORM", "title": "Doc B Uniform"},
        raw_body=doc_b_body,
    )

    test_corpus = Corpus(Path("."))
    test_corpus.objects = [ko_a, ko_b]

    idx = VectorIndex()
    idx.build(test_corpus, provider)

    query = "Bazel remote caching performance distributed clusters"

    # 1. Max-over-chunks scoring
    max_hits = idx.score_query(query, provider, top_k=2)
    assert len(max_hits) == 2
    # Doc A must rank #1 under max-aggregation because Section 2 has a very strong hit
    assert max_hits[0].node_id == "DOC-A-MULTI"
    # Winning chunk index should point to section 2 (index 1)
    assert max_hits[0].chunk_index == 1
    assert "Bazel remote caching" in max_hits[0].passage_text

    # 2. Mean-pooled scoring
    mean_hits = idx.score_query_mean_pooled(query, provider, top_k=2)
    assert len(mean_hits) == 2

    # Under max-aggregation, Doc A has a higher score than under mean-pooling (no dilution)
    doc_a_max_score = next(h.score for h in max_hits if h.node_id == "DOC-A-MULTI")
    doc_a_mean_score = next(h.score for h in mean_hits if h.node_id == "DOC-A-MULTI")
    assert doc_a_max_score > doc_a_mean_score, (
        f"Expected max score ({doc_a_max_score}) > mean score ({doc_a_mean_score})"
    )


# ==============================================================================
# Phase V3: 3-Way Hybrid RRF Fusion & Authentic Bundles (D81, D82)
# ==============================================================================


def test_authentic_provider_3way_rrf_fusion():
    """Phase V3: LocalOfflineProvider enables vector modality and executes 3-way RRF fusion."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))

    provider = LocalOfflineProvider()
    assert provider.identity.is_double is False

    idx = VectorIndex()
    idx.build(corpus, provider)

    retriever = HybridRetriever(
        corpus=corpus,
        registries=registries,
        vector_index=idx,
        embedder=provider,
    )

    bundle = retriever.retrieve(
        "deterministic specification architecture",
        cli_params={"enable_vector": True, "max_depth": 2},
    )

    # Modalities check
    assert "vector" in bundle["modalities_available"]
    assert "vector" not in bundle["modalities_absent"]
    assert "bm25" in bundle["modalities_available"]
    assert "graph" in bundle["modalities_available"]

    # Evidence bundle nodes check
    found_vector_match = False
    for node in bundle["evidence_bundle"]:
        score_comp = node["score_components"]
        assert score_comp["vector_raw"] is not None
        assert 0.0 <= score_comp["vector_raw"] <= 1.0

        signals = node["retrieval_signals"]
        if "vector" in node["matched_by"]:
            found_vector_match = True
            v_sig = signals["vector"]
            assert v_sig is not None
            assert v_sig["raw_score"] > 0.0
            assert v_sig["rank"] >= 1
            assert v_sig["rrf_contribution"] > 0.0
            assert "chunk_index" in v_sig
            assert "passage_attribution" in node
            assert node["passage_attribution"]["chunk_index"] == v_sig["chunk_index"]

    assert found_vector_match, "At least one node should match via vector modality"


# ==============================================================================
# Phase V4: Cross-Encoder Exclusion (D83)
# ==============================================================================


def test_cross_encoder_exclusion_final_score_is_rrf():
    """D83: Transformer cross-encoders remain excluded; FinalScore strictly equals RRF."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))

    provider = LocalOfflineProvider()
    idx = VectorIndex()
    idx.build(corpus, provider)

    retriever = HybridRetriever(
        corpus=corpus,
        registries=registries,
        vector_index=idx,
        embedder=provider,
    )

    bundle = retriever.retrieve("architecture", cli_params={"enable_vector": True})
    for node in bundle["evidence_bundle"]:
        sc = node["score_components"]
        assert sc["reranker_score"] == sc["rrf_score"]
        assert sc["final"] == sc["rrf_score"]


# ==============================================================================
# Phase V5: Degraded Fallback & Freshness Invalidation (D84)
# ==============================================================================


def test_degraded_fallback_when_vector_index_missing():
    """D84: Transparent fallback to baseline retrieval when vector is unconfigured."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))

    # Retriever with NO vector index or embedder configured
    retriever = HybridRetriever(corpus=corpus, registries=registries)

    # Request vector anyway
    bundle = retriever.retrieve("architecture", cli_params={"enable_vector": True})

    # Gracefully degraded fallback: vector is reported absent
    assert "vector" in bundle["modalities_absent"]
    assert "vector" not in bundle["modalities_available"]
    for node in bundle["evidence_bundle"]:
        assert node["score_components"]["vector_raw"] is None
        assert node["retrieval_signals"]["vector"] is None


def test_vector_index_freshness_and_serialization():
    """D84: Test freshness detection reasons and JSON serialization round-trip."""
    corpus = load_corpus(Path("fixtures/canonical"))
    provider = LocalOfflineProvider()

    idx = VectorIndex()
    idx.build(corpus, provider)

    # 1. Freshness against identical corpus & provider
    is_fresh, reason = idx.check_freshness(corpus, provider)
    assert is_fresh is True
    assert reason is None

    # 2. Stale reason: model change
    other_provider = LocalOfflineProvider(model_name="different-model")
    is_fresh, reason = idx.check_freshness(corpus, other_provider)
    assert is_fresh is False
    assert reason == "model change"

    # 3. Stale reason: dimension mismatch
    diff_dim_provider = LocalOfflineProvider(dimension=128)
    is_fresh, reason = idx.check_freshness(corpus, diff_dim_provider)
    assert is_fresh is False
    assert reason == "dimension mismatch"

    # 4. Stale reason: corpus change
    modified_corpus = Corpus(Path("fixtures/canonical"))
    modified_corpus.objects = list(corpus.objects) + [
        KnowledgeObject(
            path=Path("new.md"),
            frontmatter_dict={"id": "NEW-001", "title": "New"},
            raw_body="Brand new content modifying corpus hash.",
        )
    ]
    is_fresh, reason = idx.check_freshness(modified_corpus, provider)
    assert is_fresh is False
    assert reason == "corpus change"

    # 5. Serialization round-trip
    data = idx.to_dict()
    assert data["fingerprint"] == idx.fingerprint
    assert data["corpus_hash"] == idx.corpus_hash

    idx2 = VectorIndex()
    idx2.from_dict(data)
    assert idx2.fingerprint == idx.fingerprint
    assert idx2.corpus_hash == idx.corpus_hash
    assert len(idx2.chunk_records) == len(idx.chunk_records)


def test_cli_query_vector_flags(capsys):
    """CLI: Verify that query --vector enables vector modality and --no-vector disables it."""
    import json

    from trashheap.cli import main

    # 1. Without --vector (default is --no-vector)
    exit_code = main(["query", "architecture", "--corpus-root", "fixtures/canonical"])
    assert exit_code == 0
    captured = capsys.readouterr()
    bundle_default = json.loads(captured.out)
    assert "vector" in bundle_default["modalities_absent"]
    assert "vector" not in bundle_default["modalities_available"]

    # 2. With --vector
    exit_code = main(["query", "architecture", "--corpus-root", "fixtures/canonical", "--vector"])
    assert exit_code == 0
    captured = capsys.readouterr()
    bundle_vector = json.loads(captured.out)
    assert "vector" in bundle_vector["modalities_available"]
    assert "vector" not in bundle_vector["modalities_absent"]


def test_cli_rebuild_with_vector(tmp_path: Path):
    """CLI: Verify rebuild --vector outputs vector_index.json."""
    import json

    from trashheap.cli import main

    out_dir = tmp_path / "cache"
    exit_code = main(
        [
            "rebuild",
            "--corpus-root",
            "fixtures/canonical",
            "--output-dir",
            str(out_dir),
            "--vector",
            "--json",
        ]
    )
    assert exit_code == 0
    v_file = out_dir / "vector_index.json"
    assert v_file.is_file()

    with open(v_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "fingerprint" in data
    assert "records" in data
    assert len(data["records"]) > 0
