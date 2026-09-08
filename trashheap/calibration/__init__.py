"""Constrained Logit Decoding & Posterior Calibration (specs/RETRIEVAL.md §9.7, RET-008, Plan 97)."""

from trashheap.calibration.engine import (
    QA_DECISION_TOKENS,
    TRIAGE_DECISION_TOKENS,
    ClassPriorCalibrator,
    ConstrainedLogitDecoder,
    DecisionResult,
    EpistemicAbstentionGate,
    LengthSortedBatcher,
    PosteriorDistribution,
)

__all__ = [
    "ClassPriorCalibrator",
    "ConstrainedLogitDecoder",
    "DecisionResult",
    "EpistemicAbstentionGate",
    "LengthSortedBatcher",
    "PosteriorDistribution",
    "QA_DECISION_TOKENS",
    "TRIAGE_DECISION_TOKENS",
]
