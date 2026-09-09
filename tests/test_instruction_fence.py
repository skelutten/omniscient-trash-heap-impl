"""Tests for DISC-009 (delimited instruction fence, trashheap/instruction_fence.py)."""

from pathlib import Path

from trashheap.instruction_fence import (
    FENCE_END,
    FENCE_START,
    apply_fenced_block,
    extract_fenced_block,
    has_fence,
    update_instruction_file,
)

HUMAN_OWNED = "# Project instructions\n\nThese lines are human-authored and MUST survive.\n"
BLOCK = "- [[KNOWLEDGE-INDEX]]\n- Ontology summary pointer\n"


def test_apply_fenced_block_preserves_outside_content():
    content = HUMAN_OWNED + f"\n{FENCE_START}\nold managed content\n{FENCE_END}\n"
    out = apply_fenced_block(content, BLOCK)
    assert HUMAN_OWNED in out
    assert "old managed content" not in out
    assert BLOCK in out
    # Outside content is byte-preserved and unchanged in position.
    assert out.startswith(HUMAN_OWNED)


def test_apply_fenced_block_appends_when_no_fence():
    content = HUMAN_OWNED.rstrip("\n")
    out = apply_fenced_block(content, BLOCK)
    assert out.startswith(content)
    assert FENCE_START in out
    assert FENCE_END in out
    assert BLOCK in out
    # The block must appear after the human content, at the end.
    assert out.index(FENCE_START) > out.index("human-authored")


def test_apply_fenced_block_idempotent():
    once = apply_fenced_block(HUMAN_OWNED, BLOCK)
    twice = apply_fenced_block(once, BLOCK)
    assert once == twice
    # A single fence pair remains.
    assert once.count(FENCE_START) == 1
    assert once.count(FENCE_END) == 1


def test_extract_and_has_fence():
    content = apply_fenced_block(HUMAN_OWNED, BLOCK)
    assert has_fence(content)
    assert extract_fenced_block(content) == BLOCK.strip("\n")
    assert not has_fence(HUMAN_OWNED)
    assert extract_fenced_block(HUMAN_OWNED) is None


def test_update_instruction_file_writes_atomically(tmp_path: Path):
    p = tmp_path / "AGENTS.md"
    p.write_text(HUMAN_OWNED, encoding="utf-8")
    update_instruction_file(p, BLOCK)
    updated = p.read_text(encoding="utf-8")
    assert HUMAN_OWNED in updated
    assert BLOCK in updated
    assert has_fence(updated)
