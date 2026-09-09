"""Tests for Graph Intelligence, Topological Analysis, and Discovery.

Complies with specs/GRAPH-INTELLIGENCE.md, specs/GRAPH-RETRIEVAL.md, and specs/DISCOVERY.md.
Verifies invariants DELTA-CORE-001..DELTA-CORE-007 and DISC-001..DISC-005.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from trashheap.cli import main
from trashheap.corpus import load_corpus
from trashheap.graph import (
    DiscoveryEngine,
    DiscoveryLifecycleManager,
    GraphAnalyzer,
    build_and_publish_manifest,
    chunk_text_deterministic,
    compute_aggregate_corpus_hash,
    scan_canonical_inputs,
)
from trashheap.graph.models import (
    RelationDiscoveryCandidate,
    current_iso_timestamp,
)
from trashheap.registry.loader import load_registries
from trashheap.retrieval import HybridRetriever

CANONICAL_DIR = Path("fixtures/canonical")
REGISTRY_DIR = Path("schemas/registry")


def test_manifest_generation_and_immutability(tmp_path: Path):
    """Test canonical input scanning, SHA-256 calculation, and manifest publication (GRAPH-INTELLIGENCE.md §1, §12)."""
    ws_root = Path(".")
    entries = scan_canonical_inputs(ws_root)
    assert len(entries) >= 20  # 20 canonical objects + registries

    # Verify sort order
    paths = [e[0] for e in entries]
    assert paths == sorted(paths)

    corpus_hash = compute_aggregate_corpus_hash(entries)
    assert corpus_hash.startswith("sha256:")

    # Build and publish manifest
    manifest, m_path = build_and_publish_manifest(ws_root, tmp_path / "derived")
    assert m_path.exists()
    assert manifest.corpus_hash == corpus_hash
    assert manifest.schema_version == "1.0.0"
    assert manifest.architecture_version == "3.8.10"

    # Verify content in manifest.jsonl
    lines = m_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == len(entries) + 1  # 1 header + N entries
    header_data = json.loads(lines[0])
    assert "manifest_header" in header_data
    assert header_data["manifest_header"]["corpus_hash"] == corpus_hash


def test_deterministic_chunking():
    """Test deterministic character-based chunking with Unicode NFKC normalization (§7.1)."""
    text = "Hello    World!   This is a test with\nnewlines and   multiple   spaces."
    chunks = chunk_text_deterministic(text, chunk_size=30, overlap=10)
    assert len(chunks) >= 2
    # Consecutive chunks overlap by 10 codepoints
    for c in chunks:
        assert len(c) <= 30
        assert "   " not in c  # Whitespace collapsed

    # Empty text
    assert chunk_text_deterministic("") == []
    # Short text
    assert chunk_text_deterministic("Short text", chunk_size=50) == ["short text"]


def test_graph_topology_and_node_metrics():
    """Test degree calculation, connected components, and per-scope communities (§12 Phase 2)."""
    ws_root = Path(".")
    corpus = load_corpus(CANONICAL_DIR)
    analyzer = GraphAnalyzer(corpus, ws_root)

    metrics = analyzer.compute_node_metrics()
    assert len(metrics) == len(corpus.objects)

    for nid, m in metrics.items():
        assert m.node_id == nid
        assert m.in_degree >= 0
        assert m.out_degree >= 0
        assert m.total_degree == m.in_degree + m.out_degree
        assert m.component_id.startswith("comp_")
        assert m.community_id.startswith(f"comm_{m.scope}_")
        assert nid in m.distances
        assert m.distances[nid] == 0


def test_derived_edges_calculation():
    """Test derived edges with 4-part weights and scope firewall (GRAPH-RETRIEVAL.md §8, DELTA-CORE-007)."""
    ws_root = Path(".")
    corpus = load_corpus(CANONICAL_DIR)
    analyzer = GraphAnalyzer(corpus, ws_root)
    corpus_hash = "sha256:dummyhash"

    edges = analyzer.compute_derived_edges(
        corpus_hash, min_edge_strength=0.10, semantic_cutoff=0.60
    )
    assert len(edges) > 0

    # Verify score components and scope isolation
    objects_by_id = {ko.id: ko for ko in corpus.objects if ko.id}
    for e in edges:
        assert 0.0 <= e.final_score <= 1.0
        assert "canonical" in e.component_scores
        assert "similarity" in e.component_scores
        assert "proximity" in e.component_scores
        assert "cooccurrence" in e.component_scores
        # Scope firewall: endpoints must have the same scope
        u_scope = objects_by_id[e.source_id].scope
        v_scope = objects_by_id[e.target_id].scope
        assert u_scope == v_scope == e.scope

    # Verify deterministic ordering: (-final_score, edge_id)
    scores = [(-e.final_score, e.edge_id) for e in edges]
    assert scores == sorted(scores)


def test_discovery_candidates_disc_001_to_disc_004():
    """Test duplicate detection, topological gaps, and ontological gaps (DISC-001..DISC-004)."""
    ws_root = Path(".")
    corpus = load_corpus(CANONICAL_DIR)
    registries = load_registries(REGISTRY_DIR)
    engine = DiscoveryEngine(corpus, registries, ws_root)
    corpus_hash = "sha256:testhash"

    candidates = engine.scan_all_candidates(corpus_hash)
    assert len(candidates) > 0

    types_found = {c.candidate_type for c in candidates}
    assert "duplicate" in types_found or "knowledge_gap" in types_found

    for c in candidates:
        # DISC-001: mandatory fields & lineage envelope
        assert c.candidate_id
        assert 0.0 <= c.confidence <= 1.0
        assert c.status == "pending"  # DELTA-CORE-004
        assert c.corpus_hash == corpus_hash
        assert isinstance(c.evidence_refs, list)
        assert isinstance(c.source_refs, list)
        assert c.derivation_ref

        # DISC-001: mandatory expires_at no later than 90 calendar days
        exp_dt = datetime.fromisoformat(c.expires_at.replace("Z", "+00:00"))
        create_dt = datetime.fromisoformat(c.created_at.replace("Z", "+00:00"))
        diff = (exp_dt - create_dt).days
        assert diff <= 90

        if isinstance(c, RelationDiscoveryCandidate):
            if c.candidate_type == "duplicate":
                # DISC-002: canonicalized (min, max) pair identity
                assert c.source_id < c.target_id
                assert c.candidate_id == f"DISC-DUP-{c.source_id}-{c.target_id}"
            elif c.candidate_type == "knowledge_gap":
                if c.metadata.get("gap_type") == "topological":
                    # DISC-003: topological gap 2-of-3 predicates
                    preds = c.metadata.get("predicates", {})
                    true_count = sum(1 for v in preds.values() if v)
                    assert true_count >= 2


def test_discovery_lifecycle_and_audit_disc_005(tmp_path: Path):
    """Test candidate review, promotion, audit trail, and expiration sweep (DISC-005, DELTA-CORE-006)."""
    ws_root = Path(".")
    corpus = load_corpus(CANONICAL_DIR)
    registries = load_registries(REGISTRY_DIR)
    disc_dir = tmp_path / "discovery"

    mgr = DiscoveryLifecycleManager(disc_dir, ws_root)

    # Create dummy candidate
    created = current_iso_timestamp()
    exp = (datetime.fromisoformat(created.replace("Z", "+00:00")) + timedelta(days=90)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    cand = RelationDiscoveryCandidate(
        candidate_id="DISC-GAP-TEST-001",
        candidate_type="knowledge_gap",
        confidence=0.85,
        status="pending",
        created_at=created,
        expires_at=exp,
        scope="engineering",
        corpus_hash="sha256:corpus",
        algorithm_version="1.0.0",
        evidence_refs=["ref1"],
        source_refs=["ENG-CMP-0102", "ENG-FET-0105"],
        representation_refs=[],
        evidence_unit_refs=[],
        derivation_ref="test_rule",
        source_id="ENG-CMP-PARSER-0001",
        target_id="ENG-FET-LINTER-0001",
        suggested_relation="PART_OF",
    )

    mgr.add_candidates([cand], actor="tester")
    assert "DISC-GAP-TEST-001" in mgr.candidates
    assert mgr.candidates["DISC-GAP-TEST-001"].status == "pending"

    # Cannot promote before approval
    with pytest.raises(ValueError, match="must be 'approved' before promotion"):
        mgr.validate_and_promote("DISC-GAP-TEST-001", "operator", corpus, registries)

    # Review to approved
    mgr.review_candidate("DISC-GAP-TEST-001", "approved", "curator", "Reviewed and accepted")
    assert mgr.candidates["DISC-GAP-TEST-001"].status == "approved"

    # Promote
    promoted = mgr.validate_and_promote("DISC-GAP-TEST-001", "curator", corpus, registries)
    assert promoted.status == "promoted"

    # Audit log verification
    audit_entries = mgr.audit_log
    assert len(audit_entries) >= 3
    assert audit_entries[-1].new_status == "promoted"
    assert audit_entries[-1].validation_result == "PASSED"

    # Expiry sweep test: candidate with past expiration
    past_date = "2020-01-01T00:00:00Z"
    past_exp = "2020-03-01T00:00:00Z"
    old_cand = RelationDiscoveryCandidate(
        candidate_id="DISC-GAP-OLD-002",
        candidate_type="knowledge_gap",
        confidence=0.5,
        status="pending",
        created_at=past_date,
        expires_at=past_exp,
        scope="engineering",
        corpus_hash="sha256:old",
        algorithm_version="1.0.0",
        evidence_refs=[],
        source_refs=[],
        representation_refs=[],
        evidence_unit_refs=[],
        derivation_ref="test",
    )
    mgr.add_candidates([old_cand])
    assert mgr.candidates["DISC-GAP-OLD-002"].status == "pending"

    # Sweep expires old candidate without deleting
    swept = mgr.sweep_expiry()
    assert swept >= 1
    assert mgr.candidates["DISC-GAP-OLD-002"].status == "expired"
    # Audit log updated with expiry
    assert any(
        a.new_status == "expired" and a.candidate_id == "DISC-GAP-OLD-002" for a in mgr.audit_log
    )


def test_opt_in_graph_retrieval():
    """Test baseline canonical retrieval vs opt-in graph-enhanced retrieval (specs/GRAPH-RETRIEVAL.md §9)."""
    ws_root = Path(".")
    corpus = load_corpus(CANONICAL_DIR)
    registries = load_registries(REGISTRY_DIR)

    retriever = HybridRetriever(
        corpus=corpus,
        registries=registries,
        workspace_root=ws_root,
    )

    # 1. Canonical baseline mode
    bundle_canon = retriever.retrieve(
        query="architecture",
        cli_params={"retrieval_mode": "canonical", "max_depth": 2},
    )
    assert bundle_canon["retrieval_mode"] == "canonical"
    assert len(bundle_canon["evidence_bundle"]) > 0

    # 2. Opt-in graph-enhanced mode
    bundle_graph = retriever.retrieve(
        query="architecture",
        cli_params={"retrieval_mode": "graph_enhanced", "max_depth": 2},
    )
    assert bundle_graph["retrieval_mode"] == "graph_enhanced"
    assert len(bundle_graph["evidence_bundle"]) > 0

    # Check graph signal breakdown in graph-enhanced bundle
    graph_signals = [
        node["retrieval_signals"].get("graph")
        for node in bundle_graph["evidence_bundle"]
        if node["retrieval_signals"].get("graph")
    ]
    assert len(graph_signals) > 0
    for sig in graph_signals:
        if "features" in sig:
            feats = sig["features"]
            assert "phi1_distance" in feats
            assert "phi2_path_score" in feats
            assert "phi3_proximity" in feats
            assert "phi4_community" in feats
            assert "phi6_degree" in feats


def test_graph_and_discover_cli(tmp_path: Path):
    """Test CLI commands for graph manifest, analyze, and discover scan, list, review, promote."""
    derived_dir = tmp_path / "derived"
    disc_dir = tmp_path / "discovery"

    # 1. graph manifest
    rc = main(["graph", "manifest", "--output-dir", str(derived_dir), "--json"])
    assert rc == 0
    assert (derived_dir / "manifest.jsonl").exists()

    # 2. graph analyze
    rc = main(["graph", "analyze", "--output-dir", str(derived_dir / "graph"), "--json"])
    assert rc == 0
    assert (derived_dir / "graph" / "node_metrics.jsonl").exists()
    assert (derived_dir / "graph" / "derived_edges.jsonl").exists()

    # 3. discover scan
    rc = main(["discover", "scan", "--discovery-dir", str(disc_dir), "--json"])
    assert rc == 0
    assert (disc_dir / "candidates.jsonl").exists()
    assert (disc_dir / "audit_log.jsonl").exists()

    # 4. discover list
    rc = main(["discover", "list", "--discovery-dir", str(disc_dir), "--json"])
    assert rc == 0

    # Read candidates to find one to review
    candidates_lines = (
        (disc_dir / "candidates.jsonl").read_text(encoding="utf-8").strip().splitlines()
    )
    assert len(candidates_lines) > 0
    first_cand = json.loads(candidates_lines[0])
    cid = first_cand["candidate_id"]

    # 5. discover review
    rc = main(
        [
            "discover",
            "review",
            cid,
            "--decision",
            "approved",
            "--actor",
            "lead_architect",
            "--discovery-dir",
            str(disc_dir),
            "--json",
        ]
    )
    assert rc == 0

    # 6. discover sweep
    rc = main(["discover", "sweep", "--discovery-dir", str(disc_dir), "--json"])
    assert rc == 0

    # 7. query --graph-enhanced
    rc = main(["query", "architecture", "--graph-enhanced", "--json"])
    assert rc == 0


def test_literature_discovery(tmp_path: Path) -> None:
    """Test literature discovery function and CLI error handling."""
    from trashheap.cli import main
    from trashheap.graph.discovery import discover_literature_bridges

    # Non-existent CSR dir throws FileNotFoundError
    with pytest.raises(FileNotFoundError):
        discover_literature_bridges(
            tmp_path / "nonexistent",
            concept_a_id="MESH_D011928",
            concept_c_id="MESH_D005395",
        )

    # CLI handles missing CSR gracefully
    rc = main(
        [
            "discover",
            "literature",
            "--concept-a",
            "MESH_D011928",
            "--concept-c",
            "MESH_D005395",
            "--csr-dir",
            str(tmp_path / "nonexistent"),
        ]
    )
    assert rc != 0

    # If full CSR cache exists in workspace, verify real discovery execution
    csr_dir = Path(".cache/pubmed/csr_full")
    if csr_dir.exists() and (csr_dir / "node_mapping.parquet").exists():
        res = discover_literature_bridges(
            csr_dir=csr_dir,
            concept_a_id="MESH_D011928",
            concept_c_id="MESH_D005395",
            top_k=3,
        )
        assert res["concept_a"] == "MESH_D011928"
        assert res["concept_c"] == "MESH_D005395"
        assert len(res["top_bridges"]) <= 3
        assert res["total_intermediate_bridges"] > 0

        rc = main(
            [
                "discover",
                "literature",
                "--concept-a",
                "MESH_D011928",
                "--concept-c",
                "MESH_D005395",
                "--top-k",
                "2",
                "--json",
            ]
        )
        assert rc == 0
