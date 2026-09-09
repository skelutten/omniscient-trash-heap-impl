"""Tests for RET-011 (RCVA protocol, trashheap/rcva.py)."""

from trashheap.rcva import (
    EPISTEMIC_ABSTENTION,
    constrain_passages,
    entailment_score,
    rcva_answer,
    verify_claim,
)

PASSAGES = [
    {"source_ref": "SRC-1#L1-L3", "text": "The transformer uses multi-head self-attention for sequence modeling."},
    {"source_ref": "SRC-2#L4-L6", "text": "Retrieval augmented generation grounds answers in cited evidence."},
]


def test_entailment_score_full_support():
    claim = "The transformer uses self-attention for sequence modeling."
    assert entailment_score(claim, PASSAGES[0]["text"]) == 1.0


def test_entailment_score_no_support():
    claim = "The transformer runs on quantum annealing hardware."
    assert entailment_score(claim, PASSAGES[0]["text"]) < 1.0


def test_verify_claim_passes_with_support():
    res = verify_claim("Transformer uses self-attention.", PASSAGES)
    assert res["passed"] is True
    assert res["source_ref"] == "SRC-1#L1-L3"


def test_rcva_grounds_supported_claim():
    res = rcva_answer(
        "The transformer uses multi-head self-attention.",
        PASSAGES,
        calibrated_confidence=0.9,
    )
    assert res["decision"] == "GROUNDED"
    assert res["answer"].startswith("The transformer")


def test_rcva_abstains_on_unsupported_claim():
    res = rcva_answer(
        "The transformer is trained on nothing but poetry.",
        PASSAGES,
        calibrated_confidence=0.9,
    )
    assert res["decision"] == EPISTEMIC_ABSTENTION
    assert res["phases"]["verify"]["passed"] is False


def test_rcva_abstains_on_low_confidence():
    res = rcva_answer(
        "The transformer uses multi-head self-attention.",
        PASSAGES,
        calibrated_confidence=0.3,
        tau_abstain=0.5,
    )
    assert res["decision"] == EPISTEMIC_ABSTENTION
    assert res["phases"]["abstain"]["confidence_passed"] is False


def test_constrain_passages_truncates():
    long = [{"source_ref": "X", "text": "word " * 5000}]
    out = constrain_passages(long, token_budget=100)
    assert "[...]" in out[0]["text"]
