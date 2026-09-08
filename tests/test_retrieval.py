"""Tests for hybrid BM25 + Graph RRF retrieval, D82/D93/D94 invariants, and §9.3 conflict ranking."""

from pathlib import Path

from trashheap.corpus import load_corpus
from trashheap.registry.loader import load_registries
from trashheap.retrieval import BM25Index, HybridRetriever, normalize_scores


def test_bm25_index_and_normalization():
    load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))
    idx = BM25Index()
    idx.index(corpus.objects)

    scores = idx.score("deterministic specification architecture")
    assert len(scores) > 0
    norm_scores = normalize_scores(scores)
    assert max(norm_scores.values()) == 1.0
    for v in norm_scores.values():
        assert 0.0 <= v <= 1.0


def test_d93_graph_modality_condition():
    """D93: Graph participates in RRF only when depth > 0 reached; at depth 0, reported absent."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))
    retriever = HybridRetriever(corpus=corpus, registries=registries)

    # When max_depth == 0, graph is absent
    bundle_d0 = retriever.retrieve("deterministic", cli_params={"max_depth": 0})
    assert "graph" in bundle_d0["modalities_absent"]
    assert "graph" not in bundle_d0["modalities_available"]

    # When max_depth > 0, graph is available
    bundle_d2 = retriever.retrieve("deterministic", cli_params={"max_depth": 2})
    assert "graph" in bundle_d2["modalities_available"]
    assert "graph" not in bundle_d2["modalities_absent"]


def test_d82_modality_nullability():
    """D82: Absent search modalities must report null, never 0.0."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))
    retriever = HybridRetriever(corpus=corpus, registries=registries)

    bundle = retriever.retrieve("architecture")
    assert "vector" in bundle["modalities_absent"]
    for node in bundle["evidence_bundle"]:
        assert node["score_components"]["vector_raw"] is None
        assert node["retrieval_signals"]["vector"] is None


def test_d94_parameter_precedence():
    """D94: Parameter precedence CLI > config > default with origin reporting."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))
    retriever = HybridRetriever(corpus=corpus, registries=registries)

    cli_params = {"max_depth": 3, "min_confidence": 0.8}
    config_params = {"max_depth": 1, "seed_top_k": 5}

    bundle = retriever.retrieve("architecture", cli_params=cli_params, config_params=config_params)
    origins = bundle["parameters_origin"]
    params = bundle["parameters_used"]

    assert params["max_depth"] == 3
    assert origins["max_depth"] == "cli"

    assert params["seed_top_k"] == 5
    assert origins["seed_top_k"] == "config"

    assert origins["max_results"] == "default"


def test_conflict_resolution_epistemic_ranking(tmp_path: Path):
    """RETRIEVAL.md §9.3: CONTRADICTS cluster evaluated with K(d) tie-breaker."""
    registries = load_registries(Path("schemas/registry"))

    # Node 1: higher authority (normative) and verification (formal_proof)
    f1 = tmp_path / "ENG-CLM-2026-0001.md"
    f1.write_text(
        """---
id: ENG-CLM-2026-0001
title: Claim Alpha
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Claim
domain: runtime_frameworks
evidence: observed
verification: formal_proof
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 0.95
status: established
relations:
  - {type: CONTRADICTS, target: ENG-CLM-2026-0002}
---
## Summary
Content Alpha.
""",
        encoding="utf-8",
    )

    # Node 2: lower authority (advisory) and verification (unverified)
    f2 = tmp_path / "ENG-CLM-2026-0002.md"
    f2.write_text(
        """---
id: ENG-CLM-2026-0002
title: Claim Beta
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Claim
domain: runtime_frameworks
evidence: postulated
verification: unverified
authority: advisory
consensus: contested
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 0.50
status: established
relations:
  - {type: CONTRADICTS, target: ENG-CLM-2026-0001}
---
## Summary
Content Beta.
""",
        encoding="utf-8",
    )

    corpus = load_corpus(tmp_path)
    retriever = HybridRetriever(corpus=corpus, registries=registries)
    bundle = retriever.retrieve("Claim")

    assert bundle["returned_count"] == 1
    assert bundle["suppressed_count"] == 1

    winner = bundle["evidence_bundle"][0]
    assert winner["node_id"] == "ENG-CLM-2026-0001"
    assert winner["conflict_detected"] is True
    assert winner["conflicting_node_id"] == "ENG-CLM-2026-0002"

    suppressed = bundle["suppressed_nodes"][0]
    assert suppressed["node_id"] == "ENG-CLM-2026-0002"
    assert suppressed["reason"] == "conflict_lower_epistemic_rank"
    assert suppressed["conflicting_node_id"] == "ENG-CLM-2026-0001"

    # Invariant: Evidence Bundle path MUST be relative, never leaking absolute host directories
    assert winner["path"] == "ENG-CLM-2026-0001.md"
    assert not Path(winner["path"]).is_absolute()

