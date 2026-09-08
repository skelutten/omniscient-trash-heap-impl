"""Tests for Two-Stage Refusal Architecture (specs/RETRIEVAL.md §9.6, RET-006, RET-007)
and Truncation Trap defense (RET-009).
"""

from pathlib import Path

from trashheap.corpus import load_corpus
from trashheap.registry.loader import load_registries
from trashheap.retrieval import (
    INSUFFICIENT_EVIDENCE,
    UNGROUNDED_DESCRIPTOR,
    HybridRetriever,
    evaluate_stage_2_refusal,
    prepare_scoring_window,
)


def test_prepare_scoring_window_truncation_trap_defense():
    """RET-009: Document scoring window preserves trailing conclusions and findings."""
    short_text = "Overview of the architecture.\n\nKey components described here."
    assert prepare_scoring_window(short_text, max_tokens=100) == short_text

    # Build long document with conclusion at the end
    opening_paras = "\n\n".join(
        f"Section {i}: Long technical background paragraph {i}." for i in range(1, 30)
    )
    conclusion = "## Conclusions\n\nCrucial finding: Model X outperforms baseline Y under strict condition Z."
    long_doc = f"{opening_paras}\n\n{conclusion}"

    scoring_window = prepare_scoring_window(long_doc, max_tokens=64)  # 256 chars budget
    assert "Crucial finding" in scoring_window
    assert "Model X outperforms baseline Y" in scoring_window
    assert "[...]" in scoring_window


def test_stage_1_structural_gates_admissible_query():
    """RET-006: Admissible query passes Stage 1 structural graph gates."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))
    retriever = HybridRetriever(corpus=corpus, registries=registries)

    bundle = retriever.retrieve(
        "architecture specification", cli_params={"enforce_structural_gates": True}
    )
    assert bundle["retrieval_status"] == "ADMISSIBLE"
    assert bundle["refusal"] is None
    gates = bundle["stage_1_structural_gates"]
    assert gates["status"] == "PASSED"
    assert gates["gates"]["ontology_grounding"]["passed"] is True
    assert gates["gates"]["terminal_validity"]["passed"] is True
    assert len(bundle["evidence_bundle"]) > 0


def test_stage_1_refusal_ungrounded_descriptor():
    """RET-006: Adversarial ungrounded query fails ontology grounding gate."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))
    retriever = HybridRetriever(corpus=corpus, registries=registries)

    ungrounded_query = "Xylophonic Quidditch vibranium antimatter"

    # Permissive mode: reports failure in gates without zeroing results
    permissive_bundle = retriever.retrieve(
        ungrounded_query, cli_params={"enforce_structural_gates": False}
    )
    assert permissive_bundle["stage_1_structural_gates"]["status"] == "FAILED"
    assert permissive_bundle["stage_1_structural_gates"]["reason"] == UNGROUNDED_DESCRIPTOR

    # Enforce mode: returns strict REFUSED and empty evidence bundle
    enforced_bundle = retriever.retrieve(
        ungrounded_query, cli_params={"enforce_structural_gates": True}
    )
    assert enforced_bundle["retrieval_status"] == "REFUSED"
    assert enforced_bundle["evidence_bundle"] == []
    assert enforced_bundle["refusal"]["reason"] == UNGROUNDED_DESCRIPTOR
    assert enforced_bundle["refusal"]["stage"] == 1


def test_stage_2_propositional_refusal_epistemic_separation():
    """RET-007: Graph path does not imply propositional truth; Stage 2 evaluates entailment/confidence."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))
    retriever = HybridRetriever(corpus=corpus, registries=registries)

    bundle = retriever.retrieve("architecture", cli_params={"enforce_structural_gates": True})
    assert bundle["retrieval_status"] == "ADMISSIBLE"

    # Case A: High entailment and calibrated confidence -> Stage 2 ADMISSIBLE
    res_pass = evaluate_stage_2_refusal(
        evidence_bundle=bundle,
        claim_entailment_score=0.92,
        calibrated_confidence=0.88,
        min_entailment=0.5,
        min_confidence=0.65,
    )
    assert res_pass["status"] == "ADMISSIBLE"

    # Case B: Low model confidence -> Stage 2 REFUSED (INSUFFICIENT_EVIDENCE)
    res_low_conf = evaluate_stage_2_refusal(
        evidence_bundle=bundle,
        claim_entailment_score=0.85,
        calibrated_confidence=0.42,
        min_confidence=0.65,
    )
    assert res_low_conf["status"] == "REFUSED"
    assert res_low_conf["reason"] == INSUFFICIENT_EVIDENCE
    assert res_low_conf["stage"] == 2

    # Case C: Low claim entailment -> Stage 2 REFUSED
    res_low_entail = evaluate_stage_2_refusal(
        evidence_bundle=bundle,
        claim_entailment_score=0.21,
        calibrated_confidence=0.90,
        min_entailment=0.5,
    )
    assert res_low_entail["status"] == "REFUSED"
    assert res_low_entail["reason"] == INSUFFICIENT_EVIDENCE
