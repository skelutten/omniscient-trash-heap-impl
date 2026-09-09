"""Tests for REVIEW-011 (Moderator Agent Pre-Scoring, trashheap/promotion/pre_score.py)."""

from trashheap.promotion.pre_score import (
    DEFAULT_TAU_PRE_SCORE,
    pre_score,
    pre_score_candidate,
    span_entailment_score,
)

SPAN = "The transformer architecture relies on multi-head self-attention for sequence modeling."


def test_span_entailment_full_support():
    claim = "Transformer relies on multi-head self-attention for sequence modeling."
    assert span_entailment_score(claim, SPAN) == 1.0


def test_span_entailment_no_support():
    claim = "Transformer uses quantum annealing for sequence modeling."
    assert span_entailment_score(claim, SPAN) < 1.0


def test_pre_score_flagged_below_threshold():
    claim = "Transformer uses quantum annealing exclusively."
    res = pre_score(claim, SPAN, tau_pre_score=DEFAULT_TAU_PRE_SCORE)
    assert res["flagged"] is True
    assert res["flag"] == "PRE_SCORE_FAILED"


def test_pre_score_passes_above_threshold():
    claim = "Transformer uses multi-head self-attention."
    res = pre_score(claim, SPAN, tau_pre_score=0.5)
    assert res["flag"] == "PRE_SCORE_PASSED"
    assert res["flagged"] is False


def test_pre_score_candidate_best_span_wins():
    spans = ["unrelated span about weather", SPAN]
    claim = "Transformer relies on self-attention."
    res = pre_score_candidate(claim, spans)
    assert res["flag"] == "PRE_SCORE_PASSED"
    assert res["spans_evaluated"] == 2
