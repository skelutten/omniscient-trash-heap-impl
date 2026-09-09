"""Tests for VAL-011 (link mirroring), VAL-012 (mermaid degradation) and
VAL-013 (non-neural verifier)."""

import tempfile
from pathlib import Path

import pytest

from trashheap.link_mirror import check_link_mirroring, extract_link_targets
from trashheap.mermaid import (
    LINT_FAILURE_MARKER,
    degrade_broken_mermaid_blocks,
    degrade_mermaid_block,
    validate_mermaid_block,
)
from trashheap.promotion import ValidationRollbackError
from trashheap.promotion.engine import (
    approve_candidate,
    create_candidate_proposal,
    promote_candidate,
)

# ---------------------------------------------------------------------------
# VAL-011: link mirroring
# ---------------------------------------------------------------------------


def test_extract_link_targets_inline_and_reference():
    body = "See [Alpha](./path/ALPHA-001.md).\n\n[Beta]: ./other/BETA-001.md\n"
    targets = extract_link_targets(body)
    assert "./path/ALPHA-001.md" in targets
    assert "./other/BETA-001.md" in targets


def test_check_link_mirroring_flags_unmirrored_target():
    body = "This body has no links."
    relations = [{"type": "RELATES_TO", "target": "ENG-COMP-0001"}]
    findings = check_link_mirroring(body, relations)
    assert len(findings) == 1
    assert findings[0]["code"] == "W016"
    assert "ENG-COMP-0001" in findings[0]["message"]


def test_check_link_mirroring_passes_mirrored_target():
    body = "See [ENG-COMP-0001](./path/ENG-COMP-0001.md)."
    relations = [{"type": "RELATES_TO", "target": "ENG-COMP-0001"}]
    assert check_link_mirroring(body, relations) == []


# ---------------------------------------------------------------------------
# VAL-012: mermaid degradation
# ---------------------------------------------------------------------------

GOOD_MERMAID = "```mermaid\ngraph TD\n  A --> B\n```"
BAD_MERMAID = "```mermaid\nnot a real directive\n```"


def test_validate_mermaid_block_good_and_bad():
    ok, reason = validate_mermaid_block("graph TD\n A --> B")
    assert ok is True
    ok, reason = validate_mermaid_block("this is not mermaid")
    assert ok is False
    assert "directive" in reason


def test_degrade_broken_mermaid_blocks():
    body = f"Intro\n\n{BAD_MERMAID}\n\nOutro"
    out = degrade_broken_mermaid_blocks(body)
    assert "```mermaid" not in out
    assert "```text" in out
    assert "LINT_FAILURE: mermaid syntax error" in out
    assert "Intro" in out and "Outro" in out


def test_degrade_keeps_good_mermaid_intact():
    out = degrade_broken_mermaid_blocks(GOOD_MERMAID)
    assert "```mermaid" in out
    assert "LINT_FAILURE" not in out


def test_degrade_mermaid_block_emits_marker():
    out = degrade_mermaid_block("bad", "unrecognized directive")
    assert LINT_FAILURE_MARKER.format(reason="unrecognized directive") in out


# ---------------------------------------------------------------------------
# VAL-013: non-neural (deterministic) verifier
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_workspace():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir).resolve()
        (ws / "staging" / "proposals").mkdir(parents=True)
        (ws / "staging" / "transactions" / "locks").mkdir(parents=True)
        (ws / "engineering" / "01_domain_system_architecture").mkdir(parents=True)
        yield ws


def test_promotion_requires_deterministic_linter(temp_workspace):
    """A structurally invalid candidate MUST be rejected by the deterministic
    5-layer linter — never accepted on the basis of a self-evaluation."""
    create_candidate_proposal(
        candidate_id="CAND-VAL013",
        workspace_root=temp_workspace,
        frontmatter_overrides={
            "relations": [{"type": "RELATES_TO", "target": "ENG-MISSING-0000"}]
        },
    )
    approve_candidate("CAND-VAL013", "human:reviewer", "ok", temp_workspace)
    with pytest.raises(ValidationRollbackError):
        promote_candidate("CAND-VAL013", temp_workspace)
