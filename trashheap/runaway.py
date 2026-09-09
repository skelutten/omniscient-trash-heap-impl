"""Runaway-loop circuit breaker (VAL-014, E052).

Agent execution harnesses MUST maintain an in-memory sliding ring of recent
tool-call signatures (tool name + canonicalised arguments). If identical
signatures repeat ``>= 5`` times without state mutation, OR if repeated
identical failures consume ``>= 40%`` of the allocated token/turn budget, the
harness MUST trip the breaker, abort execution, and emit ``E052:
RunawayLoopError`` rather than burn compute in a degenerate loop.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Optional


class RunawayLoopError(RuntimeError):
    """Raised when the runaway-loop circuit breaker trips (E052)."""

    code = "E052"


def _canon(value: Any) -> Any:
    """Deterministically canonicalise an argument value for signature hashing."""
    if value is None or isinstance(value, (str, int, float, bool, bytes)):
        return value
    if isinstance(value, dict):
        return tuple(sorted((str(k), _canon(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_canon(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted(_canon(v) for v in value))
    # Fallback: canonicalise by stable repr.
    return repr(value)


def signature(tool_name: str, args: Any = None) -> tuple:
    """Return a hashable (tool_name, canonical_args) signature."""
    return (tool_name, _canon(args))


class RunawayLoopGuard:
    """Sliding-ring guard that trips on degenerate repetition."""

    def __init__(self, max_identical_signatures: int = 5, budget_fraction: float = 0.40):
        self.max_identical_signatures = max_identical_signatures
        self.budget_fraction = budget_fraction
        self._ring: deque = deque(maxlen=max_identical_signatures)
        self._last_signature: Optional[tuple] = None
        self._streak: int = 0
        self._fail_tokens: int = 0

    @property
    def recent(self) -> list:
        return list(self._ring)

    def observe(
        self,
        tool_name: str,
        args: Any = None,
        *,
        mutated: bool = False,
        failed: bool = False,
        tokens_spent: int = 0,
        budget: Optional[int] = None,
    ) -> None:
        """Record one tool call and trip if the breaker threshold is crossed.

        Raises ``RunawayLoopError`` (E052) when an identical signature repeats
        ``max_identical_signatures`` times without mutation, or when a run of
        identical failures consumes ``budget_fraction`` of ``budget``.
        """
        sig = signature(tool_name, args)
        self._ring.append(sig)

        # A state mutation breaks the repetition streak.
        if mutated:
            self._last_signature = sig
            self._streak = 0
            self._fail_tokens = 0
            return

        if sig == self._last_signature:
            self._streak += 1
        else:
            self._streak = 1
            self._fail_tokens = 0
        self._last_signature = sig

        if failed:
            self._fail_tokens += tokens_spent
            if (
                budget is not None
                and budget > 0
                and self._fail_tokens >= self.budget_fraction * budget
            ):
                raise RunawayLoopError(
                    "E052: repeated identical tool-call failures consumed "
                    f"{self._fail_tokens} tokens, exceeding {self.budget_fraction:.0%} "
                    f"of the {budget}-token budget (The 40% Rule / VAL-014)"
                )

        if self._streak >= self.max_identical_signatures:
            raise RunawayLoopError(
                f"E052: identical tool-call signature repeated {self._streak} times "
                f"without state mutation (VAL-014)"
            )
