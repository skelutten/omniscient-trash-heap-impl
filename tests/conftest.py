"""Shared pytest configuration: CWD anchoring and repo-root fixtures.

Historically ~11 test files referenced repo-relative paths (``fixtures/``,
``schemas/registry``, ``.cache/``), making the suite runnable only from the
repository root. The autouse fixture below anchors every test's CWD to the
repo root regardless of where pytest was invoked. Tests that need a different
CWD can still use ``monkeypatch.chdir`` / ``tmp_path`` — those run after this
fixture and take precedence.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _anchor_cwd(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(REPO_ROOT)


@pytest.fixture
def repo_root() -> Path:
    """Absolute path to the repository root (CWD-independent)."""
    return REPO_ROOT
