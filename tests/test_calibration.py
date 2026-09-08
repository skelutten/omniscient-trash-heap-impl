"""Tests for Constrained Logit Decoding & Epistemic Calibration (RET-008, specs/RETRIEVAL.md §9.7, Plan 97)."""

import math

import pytest

from trashheap.calibration.engine import (
    QA_DECISION_TOKENS,
    ClassPriorCalibrator,
    ConstrainedLogitDecoder,
    EpistemicAbstentionGate,
    LengthSortedBatcher,
)


def test_constrained_logit_decoder_softmax_normalization():
    """RET-008: Softmax posteriors over discrete tokens sum to 1.0 with numerical stability."""
    logits = {"yes": 2.5, "no": 1.0, "maybe": -0.5}
    post = ConstrainedLogitDecoder.normalize_logits(logits)

    assert post.top_choice == "yes"
    assert math.isclose(sum(post.probabilities.values()), 1.0, rel_tol=1e-5)
    assert post.confidence == post.probabilities["yes"]
    assert post.confidence > post.probabilities["no"] > post.probabilities["maybe"]
    assert post.entropy > 0.0

    # Extreme logits test (numerical stability without overflow)
    extreme_logits = {"yes": 1050.0, "no": 1000.0, "maybe": 950.0}
    extreme_post = ConstrainedLogitDecoder.normalize_logits(extreme_logits)
    assert extreme_post.top_choice == "yes"
    assert math.isclose(sum(extreme_post.probabilities.values()), 1.0, rel_tol=1e-5)
    assert extreme_post.confidence > 0.99


def test_temperature_scaling():
    """Higher temperature increases entropy and smooths posterior distribution."""
    logits = {"yes": 3.0, "no": 1.0, "maybe": 0.0}
    post_cold = ConstrainedLogitDecoder.normalize_logits(logits, temperature=0.5)
    post_hot = ConstrainedLogitDecoder.normalize_logits(logits, temperature=2.0)

    assert post_cold.confidence > post_hot.confidence
    assert post_cold.entropy < post_hot.entropy


def test_class_prior_calibrator():
    """Calibrator fits additive class offsets on DEV set to correct prior skew."""
    # Simulated DEV split where 'maybe' is slightly penalized by model prior
    dev_posteriors = [
        {"yes": 0.45, "no": 0.10, "maybe": 0.45},
        {"yes": 0.48, "no": 0.12, "maybe": 0.40},
        {"yes": 0.20, "no": 0.70, "maybe": 0.10},
    ]
    gold_labels = ["maybe", "maybe", "no"]

    calibrator = ClassPriorCalibrator()
    offsets = calibrator.fit(dev_posteriors, gold_labels, QA_DECISION_TOKENS)

    assert "maybe" in offsets
    # Calibrate a borderline instance where raw top choice is 'yes'
    test_post = ConstrainedLogitDecoder.normalize_logits({"yes": 0.46, "no": 0.10, "maybe": 0.44})
    calibrated_post = calibrator.calibrate(test_post)
    # The learned prior offset should promote 'maybe'
    assert calibrated_post.top_choice == "maybe"


def test_epistemic_abstention_gate():
    """Gate halts execution and emits EPISTEMIC_ABSTENTION when confidence < tau."""
    gate = EpistemicAbstentionGate(tau_abstain=0.70)

    # Case A: Clear confidence (0.85) -> accepted
    clear_logits = {"yes": 5.0, "no": 1.0, "maybe": 0.0}
    res_accept = gate.decide(clear_logits)
    assert res_accept.status == "accepted"
    assert res_accept.decision == "yes"
    assert res_accept.refusal_reason is None
    assert res_accept.confidence >= 0.70

    # Case B: Ambiguous confidence (entropy high, max prob < 0.70) -> abstained
    hedged_logits = {"yes": 1.1, "no": 1.0, "maybe": 0.9}
    res_abstain = gate.decide(hedged_logits)
    assert res_abstain.status == "abstained"
    assert res_abstain.decision is None
    assert res_abstain.refusal_reason == "EPISTEMIC_ABSTENTION"
    assert res_abstain.confidence < 0.70


def test_length_sorted_batcher_order_restoration():
    """LengthSortedBatcher sorts sequences by length and restores original indices."""
    prompts = [
        "Very long prompt with multiple detailed medical instructions and questions",
        "Short query",
        "Medium length question about aspirin",
    ]

    sorted_prompts, orig_indices = LengthSortedBatcher.batch(prompts)
    assert len(sorted_prompts[0]) <= len(sorted_prompts[1]) <= len(sorted_prompts[2])
    assert sorted_prompts[0] == "Short query"

    # Simulate processing (e.g. logit extraction)
    processed = [f"Result: {p[:10]}" for p in sorted_prompts]
    restored = LengthSortedBatcher.unbatch(processed, orig_indices)

    assert len(restored) == len(prompts)
    assert restored[0] == f"Result: {prompts[0][:10]}"
    assert restored[1] == f"Result: {prompts[1][:10]}"
    assert restored[2] == f"Result: {prompts[2][:10]}"


def test_empty_logits_raises_error():
    with pytest.raises(ValueError, match="cannot be empty"):
        ConstrainedLogitDecoder.normalize_logits({})
