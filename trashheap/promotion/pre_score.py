"""Moderator Agent Pre-Scoring pass (REVIEW-011).

Before a candidate proposal containing claims or extracted relations is shown to
a human operator, it MUST be pre-scored for factual alignment against its cited
``source_ref`` text spans:

1. **Span Entailment Score** (0.0 <= s <= 1.0): how strongly the cited span
   textually supports the proposed claim/relation.
2. **Hallucination Fence**: if ``s < tau_pre_score`` (default 0.70), the
   candidate is flagged ``PRE_SCORE_FAILED`` for operator rejection or automated
   culling.

The entailment score is a deterministic lexical-overlap proxy — consistent with
VAL-013 (neural models propose; deterministic verifiers validate). No generative
self-evaluation is involved.
"""

from __future__ import annotations

import re
from typing import Dict, List

DEFAULT_TAU_PRE_SCORE = 0.70


def _content_tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def span_entailment_score(claim: str, span_text: str) -> float:
    """Deterministic span-entailment score in [0, 1].

    Fraction of the claim's content tokens that are also present in the cited
    span text. A fully supported claim scores 1.0; an unsupported one scores 0.0.
    """
    claim_tokens = _content_tokens(claim)
    if not claim_tokens:
        return 0.0
    span_tokens = _content_tokens(span_text)
    return len(claim_tokens & span_tokens) / len(claim_tokens)


def pre_score(claim: str, span_text: str, tau_pre_score: float = DEFAULT_TAU_PRE_SCORE) -> Dict[str, object]:
    """Compute the span-entailment score and apply the hallucination fence."""
    score = span_entailment_score(claim, span_text)
    flagged = score < tau_pre_score
    return {
        "span_entailment_score": score,
        "tau_pre_score": tau_pre_score,
        "flag": "PRE_SCORE_FAILED" if flagged else "PRE_SCORE_PASSED",
        "flagged": flagged,
    }


def pre_score_candidate(
    claim: str, source_spans: List[str], tau_pre_score: float = DEFAULT_TAU_PRE_SCORE
) -> Dict[str, object]:
    """Pre-score a claim against all cited source spans (best match wins)."""
    best = 0.0
    for span in source_spans:
        s = span_entailment_score(claim, span)
        if s > best:
            best = s
    flagged = best < tau_pre_score
    return {
        "span_entailment_score": best,
        "tau_pre_score": tau_pre_score,
        "flag": "PRE_SCORE_FAILED" if flagged else "PRE_SCORE_PASSED",
        "flagged": flagged,
        "spans_evaluated": len(source_spans),
    }
