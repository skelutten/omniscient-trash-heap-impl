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

from typing import Any, Dict, List, Optional

from trashheap.rcva import entailment_score

DEFAULT_TAU_PRE_SCORE = 0.70


def span_entailment_score(claim: str, span_text: str) -> float:
    """Deterministic span-entailment score in [0, 1].

    Single implementation shared with the RCVA verifier (trashheap.rcva):
    fraction of the claim's stopword-filtered content tokens present in the
    cited span text. A fully supported claim scores 1.0; an unsupported one 0.0.
    """
    return entailment_score(claim, span_text)


def pre_score(
    claim: str, span_text: str, tau_pre_score: float = DEFAULT_TAU_PRE_SCORE
) -> Dict[str, object]:
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


def _resolve_source_spans(proposal: Any, workspace_root: Any, max_files: int = 5) -> List[str]:
    """Best-effort resolution of the cited source text spans for a proposal.

    Walks ``evidence_unit_ref``, ``representation_refs`` and ``source_refs``;
    reads every existing file under the workspace (raw captures, evidence-unit
    YAML — for the latter, also any nested ``location`` payload pointer).
    Deterministic order, bounded count. Fail-visible: returns [] when nothing
    resolves, which callers MUST surface as PRE_SCORE_UNAVAILABLE.
    """
    from pathlib import Path

    import yaml

    ws = Path(workspace_root)
    refs: List[str] = []
    for ref in (
        [proposal.evidence_unit_ref]
        + list(proposal.representation_refs)
        + list(proposal.source_refs)
    ):
        if ref:
            refs.append(str(ref))

    spans: List[str] = []
    seen: set = set()
    queue = list(refs)
    while queue and len(spans) < max_files:
        ref = queue.pop(0)
        candidate = (ws / ref).resolve()
        try:
            inside = candidate == ws or ws in candidate.parents or candidate.is_relative_to(ws)
        except AttributeError:
            inside = False
        if not inside or str(candidate) in seen or not candidate.is_file():
            continue
        seen.add(str(candidate))
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if candidate.suffix in {".yaml", ".yml"}:
            try:
                data = yaml.safe_load(text)
            except yaml.YAMLError:
                data = None
            if isinstance(data, dict):
                for key in ("location", "raw_location", "capture_path"):
                    nested = _dig_location(data, key)
                    if nested:
                        queue.append(nested)
        spans.append(text[:200_000])
    return spans


def _dig_location(data: Any, key: str) -> Optional[str]:
    """Find the first string value for ``key`` anywhere in a nested dict/list."""
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key and isinstance(v, str):
                return v
            found = _dig_location(v, key)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = _dig_location(item, key)
            if found:
                return found
    return None


def pre_score_proposal(proposal: Any, workspace_root: Any) -> Dict[str, object]:
    """REVIEW-011 Moderator Pre-Pass for a staged CandidateProposal.

    The claim side is the proposed knowledge (title, declared relations and
    body); the support side is the resolved cited source spans. Returns the
    standard pre-score dict, or flag ``PRE_SCORE_UNAVAILABLE`` when no cited
    source text can be resolved (fail-visible, never silently passing).
    """
    fm = proposal.proposed_frontmatter or {}
    claim_parts = [str(fm.get("title", ""))]
    for rel in fm.get("relations") or []:
        if isinstance(rel, dict):
            claim_parts.append(f"{rel.get('type', '')} {rel.get('target', '')}")
    claim_parts.append(str(proposal.proposed_body or ""))
    claim = "\n".join(p for p in claim_parts if p.strip())

    spans = _resolve_source_spans(proposal, workspace_root)
    if not spans:
        return {
            "span_entailment_score": None,
            "tau_pre_score": DEFAULT_TAU_PRE_SCORE,
            "flag": "PRE_SCORE_UNAVAILABLE",
            "flagged": True,
            "spans_evaluated": 0,
        }
    return pre_score_candidate(claim, spans)
