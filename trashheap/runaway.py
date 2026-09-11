"""Runaway-loop circuit breaker (VAL-014, E052).

Agent execution harnesses MUST maintain an in-memory sliding hash ring of recent
tool-call signatures (tool name + canonicalised arguments). If identical
signatures repeat ``>= 5`` times within the ring without state mutation, OR if
repeated identical failures consume ``>= 40%`` of the allocated token/turn
budget, the harness MUST trip the breaker, abort execution, and emit ``E052:
RunawayLoopError`` rather than burn compute in a degenerate loop.

The ring-window count (not merely a consecutive streak) is the trip criterion,
so alternating degenerate patterns (A-B-A-B-...) are also detected, exactly as
VAL-014 requires. Once tripped, the guard stays tripped until the caller
observes a state mutation (``mutated=True``) — circuit-breaker semantics.
"""

from __future__ import annotations

import re
from collections import deque
from typing import Any, Optional

_DEFAULT_WINDOW_SIZE = 20

_ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]+")


class RunawayLoopError(RuntimeError):
    """Raised when the runaway-loop circuit breaker trips (E052)."""

    code = "E052"


def _canon(value: Any) -> Any:
    """Deterministically canonicalise an argument value for signature hashing."""
    if value is None or isinstance(value, (str, int, float, bool, bytes)):
        return value
    if isinstance(value, dict):
        return tuple(sorted(((str(k), _canon(v)) for k, v in value.items()), key=str))
    if isinstance(value, (list, tuple)):
        return tuple(_canon(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((_canon(v) for v in value), key=str))
    # Fallback: stable repr with memory addresses neutralised, so logically
    # identical objects with default reprs produce identical signatures.
    return _ADDRESS_RE.sub("0x?", repr(value))


def signature(tool_name: str, args: Any = None) -> tuple:
    """Return a hashable (tool_name, canonical_args) signature."""
    return (tool_name, _canon(args))


class RunawayLoopGuard:
    """Sliding-ring guard that trips on degenerate repetition (VAL-014)."""

    def __init__(
        self,
        max_identical_signatures: int = 5,
        budget_fraction: float = 0.40,
        window_size: Optional[int] = None,
    ):
        self.max_identical_signatures = max_identical_signatures
        self.budget_fraction = budget_fraction
        self.window_size = window_size or max(_DEFAULT_WINDOW_SIZE, max_identical_signatures * 2)
        self._ring: deque = deque(maxlen=self.window_size)
        self._fail_tokens: int = 0
        self._last_fail_sig: Optional[tuple] = None
        self._last_budget: Optional[int] = None

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

        Raises ``RunawayLoopError`` (E052) when the identical signature occurs
        ``max_identical_signatures`` times within the sliding ring without an
        intervening state mutation, or when a run of identical failures consumes
        ``budget_fraction`` of ``budget`` (the most recently supplied budget is
        remembered across calls).
        """
        sig = signature(tool_name, args)
        self._ring.append(sig)

        # A state mutation breaks the repetition window.
        if mutated:
            self._ring.clear()
            self._fail_tokens = 0
            self._last_fail_sig = None
            return

        if budget is not None:
            self._last_budget = budget
        effective_budget = budget if budget is not None else self._last_budget

        if failed:
            if sig != self._last_fail_sig:
                self._fail_tokens = 0
            self._last_fail_sig = sig
            self._fail_tokens += tokens_spent
            if (
                effective_budget is not None
                and effective_budget > 0
                and self._fail_tokens >= self.budget_fraction * effective_budget
            ):
                raise RunawayLoopError(
                    "E052: repeated identical tool-call failures consumed "
                    f"{self._fail_tokens} tokens, exceeding {self.budget_fraction:.0%} "
                    f"of the {effective_budget}-token budget (The 40% Rule / VAL-014)"
                )

        occurrences = sum(1 for s in self._ring if s == sig)
        if occurrences >= self.max_identical_signatures:
            raise RunawayLoopError(
                f"E052: identical tool-call signature repeated {occurrences} times "
                f"within the sliding ring of {len(self._ring)} recent calls "
                "without state mutation (VAL-014)"
            )
