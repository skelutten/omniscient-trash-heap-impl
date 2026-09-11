"""RCVA protocol (RET-011): Retrieve, Constrain, Verify, Abstain.

Grounded question answering, multi-hop reasoning and automated synthesis MUST
follow the four-phase RCVA protocol (specs/RETRIEVAL.md §9.8):

1. RETRIEVE  — hybrid dense + BM25 + graph BFS (RRF fusion)
2. CONSTRAIN — domain/temporal filtering + line/token budgeting
3. VERIFY    — deterministic claim entailment against cited passages
4. ABSTAIN   — posterior-mass check; refuse with EPISTEMIC_ABSTENTION

This module implements the deterministic CONSTRAIN/VERIFY/ABSTAIN half of the
protocol; RETRIEVE is delegated to ``HybridRetriever.retrieve``. Verification is
a deterministic lexical-entailment proxy (no generative self-evaluation), per
VAL-013: neural models propose, deterministic verifiers validate.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from trashheap.textutil import content_tokens

EPISTEMIC_ABSTENTION = "EPISTEMIC_ABSTENTION"

#: Default abstention threshold, aligned with the Stage-2 propositional gate
#: (retrieval.evaluate_stage_2_refusal min_confidence) and the calibration
#: engine's tau (0.65). One conceptual threshold, one default value.
DEFAULT_TAU_ABSTAIN = 0.65


def _content_tokens(text: str) -> set:
    """Lowercase alphanumeric content tokens, stopwords removed (deterministic)."""
    return content_tokens(text)


def entailment_score(claim: str, passage: str) -> float:
    """Deterministic lexical-entailment proxy in [0, 1].

    Fraction of the claim's content tokens that appear in the passage. A claim
    whose every content token is supported by the passage scores 1.0; a claim
    with no textual support scores 0.0.
    """
    claim_tokens = _content_tokens(claim)
    if not claim_tokens:
        return 0.0
    passage_tokens = _content_tokens(passage)
    covered = len(claim_tokens & passage_tokens)
    return covered / len(claim_tokens)


def constrain_passages(
    passages: List[Dict[str, Any]],
    token_budget: int = 512,
    chars_per_token: int = 4,
) -> List[Dict[str, Any]]:
    """Bound each passage to the token budget (Phase 2, RET-010/RET-011)."""
    max_chars = token_budget * chars_per_token
    out: List[Dict[str, Any]] = []
    for p in passages:
        text = p.get("text", "")
        bounded = dict(p)
        if len(text) > max_chars:
            bounded["text"] = text[:max_chars].rstrip() + "\n\n[...]"
        out.append(bounded)
    return out


def verify_claim(
    claim: str, passages: List[Dict[str, Any]], min_entailment: float = 0.5
) -> Dict[str, Any]:
    """Verify an atomic claim against every cited passage (Phase 3)."""
    best = 0.0
    best_ref: Optional[str] = None
    for p in passages:
        score = entailment_score(claim, p.get("text", ""))
        if score > best:
            best = score
            best_ref = p.get("source_ref")
    passed = best >= min_entailment
    return {
        "passed": passed,
        "score": best,
        "threshold": min_entailment,
        "source_ref": best_ref,
    }


def rcva_answer(
    claim: str,
    passages: List[Dict[str, Any]],
    calibrated_confidence: Optional[float] = None,
    *,
    tau_abstain: float = DEFAULT_TAU_ABSTAIN,
    min_entailment: float = 0.5,
    token_budget: int = 512,
) -> Dict[str, Any]:
    """Run the RCVA protocol and return a grounded answer or an abstention.

    Returns a dict with ``decision`` of either ``EPISTEMIC_ABSTENTION`` or
    ``GROUNDED``, plus per-phase evidence. Abstains when verification fails or
    the calibrated posterior clears below ``tau_abstain``.
    """
    bounded = constrain_passages(passages, token_budget=token_budget)
    verification = verify_claim(claim, bounded, min_entailment=min_entailment)

    confidence_passed = calibrated_confidence is None or calibrated_confidence >= tau_abstain

    if not verification["passed"] or not confidence_passed:
        return {
            "decision": EPISTEMIC_ABSTENTION,
            "reason": (
                "verification failed"
                if not verification["passed"]
                else "confidence below abstain threshold"
            ),
            "phases": {
                "retrieve": {"candidate_count": len(passages)},
                "constrain": {"token_budget": token_budget, "passages_kept": len(bounded)},
                "verify": verification,
                "abstain": {
                    "confidence": calibrated_confidence,
                    "tau_abstain": tau_abstain,
                    "confidence_passed": confidence_passed,
                },
            },
        }

    return {
        "decision": "GROUNDED",
        "answer": claim,
        "phases": {
            "retrieve": {"candidate_count": len(passages)},
            "constrain": {"token_budget": token_budget, "passages_kept": len(bounded)},
            "verify": verification,
            "abstain": {
                "confidence": calibrated_confidence,
                "tau_abstain": tau_abstain,
                "confidence_passed": True,
            },
        },
    }
