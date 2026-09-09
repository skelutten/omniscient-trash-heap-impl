"""Tests for VAL-014 / E052 (runaway-loop circuit breaker, trashheap/runaway.py)."""

import pytest

from trashheap.runaway import RunawayLoopError, RunawayLoopGuard, signature


def test_identical_signatures_trip_after_five():
    guard = RunawayLoopGuard(max_identical_signatures=5)
    for i in range(4):
        guard.observe("query", {"prompt": "same", "top_k": 5}, mutated=False)
    with pytest.raises(RunawayLoopError) as exc:
        guard.observe("query", {"prompt": "same", "top_k": 5}, mutated=False)
    assert exc.value.code == "E052"


def test_different_signatures_do_not_trip():
    guard = RunawayLoopGuard(max_identical_signatures=5)
    for i in range(10):
        guard.observe("query", {"prompt": f"q{i}"}, mutated=False)
    # No exception raised.


def test_mutation_resets_streak():
    guard = RunawayLoopGuard(max_identical_signatures=5)
    for i in range(4):
        guard.observe("write", {"id": "X", "content": "same"}, mutated=False)
    guard.observe("write", {"id": "X", "content": "same"}, mutated=True)  # state changed
    # Streak reset: four more identical non-mutating calls must not trip yet.
    for i in range(4):
        guard.observe("write", {"id": "X", "content": "same"}, mutated=False)


def test_budget_fraction_rule_trips():
    guard = RunawayLoopGuard(max_identical_signatures=1000, budget_fraction=0.40)
    budget = 100
    with pytest.raises(RunawayLoopError):
        for i in range(5):
            guard.observe(
                "retry", {"url": "x"}, mutated=False, failed=True, tokens_spent=10, budget=budget
            )


def test_signature_canonicalises_argument_order():
    assert signature("t", {"a": 1, "b": 2}) == signature("t", {"b": 2, "a": 1})
    assert signature("t", [1, 2]) == signature("t", [1, 2])
    assert signature("t", [1, 2]) != signature("t", [2, 1])
