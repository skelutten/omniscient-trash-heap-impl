"""Constrained Logit Decoding & Posterior Calibration engine (specs/RETRIEVAL.md §9.7, RET-008, Plan 97).

Eliminates brittle regex parsing on hedged prose by extracting discrete token logits
at decision positions, computing softmax posteriors, fitting prior calibrations on DEV,
and executing calibrated epistemic abstention gates.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, TypeVar, Union

QA_DECISION_TOKENS: List[str] = ["yes", "no", "maybe"]
TRIAGE_DECISION_TOKENS: List[str] = ["approve", "reject", "revise"]

T = TypeVar("T")
U = TypeVar("U")


@dataclass
class PosteriorDistribution:
    """Normalized softmax posterior over discrete candidate tokens."""

    probabilities: Dict[str, float]
    top_choice: str
    confidence: float
    entropy: float
    raw_logits: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "probabilities": {k: round(v, 6) for k, v in self.probabilities.items()},
            "top_choice": self.top_choice,
            "confidence": round(self.confidence, 6),
            "entropy": round(self.entropy, 6),
            "raw_logits": {k: round(v, 4) for k, v in self.raw_logits.items()},
        }


class ConstrainedLogitDecoder:
    """Decodes discrete vocabulary tokens into normalized probability distributions."""

    @staticmethod
    def normalize_logits(
        candidate_logits: Dict[str, float], temperature: float = 1.0
    ) -> PosteriorDistribution:
        """Compute numerically stable softmax posterior over candidate vocabulary."""
        if not candidate_logits:
            raise ValueError("candidate_logits dictionary cannot be empty")

        t = max(1e-5, temperature)
        max_z = max(candidate_logits.values())

        # Subtract max for numerical stability: exp(z - max_z)
        exp_vals = {tok: math.exp((z - max_z) / t) for tok, z in candidate_logits.items()}
        total_exp = sum(exp_vals.values())

        probs = {tok: val / total_exp for tok, val in exp_vals.items()}

        # Find top choice deterministically (highest prob, then lexicographical order)
        sorted_candidates = sorted(probs.items(), key=lambda x: (-x[1], x[0]))
        top_choice, confidence = sorted_candidates[0]

        # Shannon entropy: - sum(p * ln(p))
        entropy = -sum(p * math.log(max(p, 1e-12)) for p in probs.values())

        return PosteriorDistribution(
            probabilities=probs,
            top_choice=top_choice,
            confidence=confidence,
            entropy=entropy,
            raw_logits=dict(candidate_logits),
        )


class ClassPriorCalibrator:
    """Fits class-bias adjustments on disjoint DEV splits to correct model prior skew."""

    def __init__(self, class_offsets: Optional[Dict[str, float]] = None):
        self.class_offsets: Dict[str, float] = class_offsets or {}

    def fit(
        self,
        dev_posteriors: Sequence[Dict[str, float]],
        gold_labels: Sequence[str],
        classes: Sequence[str],
        grid_steps: int = 21,
        bound: float = 0.5,
    ) -> Dict[str, float]:
        """Fit additive class offsets beta_c in [-bound, bound] optimizing macro accuracy."""
        if len(dev_posteriors) != len(gold_labels):
            raise ValueError("dev_posteriors and gold_labels must have identical length")
        if not dev_posteriors:
            return {}

        best_offsets: Dict[str, float] = {c: 0.0 for c in classes}
        best_acc = self._score_offsets(dev_posteriors, gold_labels, best_offsets)

        step_values = [-bound + (2 * bound * i / (grid_steps - 1)) for i in range(grid_steps)]

        # Coordinate-wise grid search over classes
        for c in classes:
            current_best = best_offsets[c]
            for val in step_values:
                candidate = dict(best_offsets)
                candidate[c] = val
                score = self._score_offsets(dev_posteriors, gold_labels, candidate)
                if score > best_acc:
                    best_acc = score
                    current_best = val
            best_offsets[c] = current_best

        self.class_offsets = best_offsets
        return dict(self.class_offsets)

    def _score_offsets(
        self,
        posteriors: Sequence[Dict[str, float]],
        gold: Sequence[str],
        offsets: Dict[str, float],
    ) -> float:
        correct = 0
        for p, g in zip(posteriors, gold):
            pred = max(
                offsets.keys(),
                key=lambda c: (p.get(c, 0.0) + offsets.get(c, 0.0), -ord(c[0])),
            )
            if pred == g:
                correct += 1
        return correct / max(1, len(posteriors))

    def calibrate(self, posterior: PosteriorDistribution) -> PosteriorDistribution:
        """Apply learned class prior offsets to adjust decision and confidence."""
        if not self.class_offsets:
            return posterior

        adjusted_scores: Dict[str, float] = {}
        for tok, p in posterior.probabilities.items():
            offset = self.class_offsets.get(tok, 0.0)
            adjusted_scores[tok] = p + offset

        # Find new top choice
        sorted_adj = sorted(adjusted_scores.items(), key=lambda x: (-x[1], x[0]))
        top_choice = sorted_adj[0][0]
        # Confidence is the original posterior probability of the selected choice
        confidence = posterior.probabilities.get(top_choice, 0.0)

        return PosteriorDistribution(
            probabilities=posterior.probabilities,
            top_choice=top_choice,
            confidence=confidence,
            entropy=posterior.entropy,
            raw_logits=posterior.raw_logits,
        )


@dataclass
class DecisionResult:
    """Outcome of calibrated epistemic gate."""

    status: str  # 'accepted' or 'abstained'
    decision: Optional[str]
    confidence: float
    posterior: PosteriorDistribution
    refusal_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "decision": self.decision,
            "confidence": round(self.confidence, 6),
            "refusal_reason": self.refusal_reason,
            "posterior": self.posterior.to_dict(),
        }


class EpistemicAbstentionGate:
    """Halts execution when model posterior mass falls below epistemic safety threshold."""

    def __init__(
        self,
        tau_abstain: float = 0.65,
        calibrator: Optional[ClassPriorCalibrator] = None,
    ):
        self.tau_abstain = tau_abstain
        self.calibrator = calibrator

    def decide(
        self,
        logits_or_posterior: Union[Dict[str, float], PosteriorDistribution],
    ) -> DecisionResult:
        """Evaluate epistemic confidence and return accepted decision or abstention refusal."""
        if isinstance(logits_or_posterior, dict):
            post = ConstrainedLogitDecoder.normalize_logits(logits_or_posterior)
        else:
            post = logits_or_posterior

        if self.calibrator:
            post = self.calibrator.calibrate(post)

        if post.confidence < self.tau_abstain:
            return DecisionResult(
                status="abstained",
                decision=None,
                confidence=post.confidence,
                posterior=post,
                refusal_reason="EPISTEMIC_ABSTENTION",
            )

        return DecisionResult(
            status="accepted",
            decision=post.top_choice,
            confidence=post.confidence,
            posterior=post,
            refusal_reason=None,
        )


class LengthSortedBatcher:
    """Sorts sequences by length before batched tensor evaluation, restoring original index."""

    @staticmethod
    def batch(items: List[T], length_fn: Callable[[T], int] = len) -> Tuple[List[T], List[int]]:
        """Sort items by length. Returns (sorted_items, restore_indices)."""
        indexed = sorted(enumerate(items), key=lambda x: length_fn(x[1]))
        sorted_items = [item for _, item in indexed]
        # restore_indices maps sorted position back to original position
        original_indices = [idx for idx, _ in indexed]
        return sorted_items, original_indices

    @staticmethod
    def unbatch(processed_items: List[U], original_indices: List[int]) -> List[U]:
        """Restore original item order from length-sorted outputs."""
        if len(processed_items) != len(original_indices):
            raise ValueError("processed_items and original_indices must have matching lengths")

        restored: List[Optional[U]] = [None] * len(processed_items)
        for orig_idx, item in zip(original_indices, processed_items):
            restored[orig_idx] = item

        return [item for item in restored if item is not None]
