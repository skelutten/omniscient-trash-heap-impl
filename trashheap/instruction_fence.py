"""Delimited instruction-fence helpers (DISC-009).

When autonomous discovery/ingestion tooling updates repository-root instruction
files (``AGENTS.md``, ``CLAUDE.md``, ``.cursorrules``, ...), the update MUST be
confined between explicit delimiter comments:

    <!-- TRASHHEAP:START -->
    ... machine-managed knowledge index, ontology summaries, pointers ...
    <!-- TRASHHEAP:END -->

Everything outside the fence is human-owned and MUST NOT be modified, reordered
or overwritten. When the delimiters are absent, tooling MUST append a new
delimited block at the end of the file instead of replacing existing content.

This module provides the single deterministic implementation of that contract
so no caller can drift from it (DISC-009, VALIDATION.md §10.6).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from trashheap.fsutil import atomic_write_text

FENCE_START = "<!-- TRASHHEAP:START -->"
FENCE_END = "<!-- TRASHHEAP:END -->"


def _find_fence_lines(lines: list[str]) -> Optional[tuple[int, int]]:
    """Return (start_idx, end_idx) 0-indexed line positions of the fence, or None.

    The FIRST start marker wins, paired with the first end marker after it, so
    duplicated or malformed fences degrade predictably instead of silently
    selecting the last start marker.
    """
    start_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if start_idx is None:
            if stripped == FENCE_START:
                start_idx = i
        elif stripped == FENCE_END:
            return start_idx, i
    return None


def _normalise_block(block: str) -> str:
    """Normalise the injected block so repeated writes are idempotent."""
    return block.strip("\n")


def apply_fenced_block(content: str, block: str) -> str:
    """Return ``content`` with ``block`` confined inside the TRASHHEAP fence.

    - If the fence is present, replace only the lines strictly between the
      delimiters; the delimiter lines and all outside content are preserved
      byte-for-byte, including the original trailing-newline state.
    - If the fence is absent, append the delimited block at the end of the
      file (with a single blank-line separator) and never touch existing
      content.
    """
    had_trailing_newline = content.endswith("\n") or content == ""
    lines = content.splitlines()
    block = _normalise_block(block)
    block_lines = block.splitlines() if block else []

    fence = _find_fence_lines(lines)
    if fence is None:
        out = list(lines)
        # Append the delimited block at the end, with a single separator.
        if out and out[-1] != "":
            out.append("")
        out.append(FENCE_START)
        out.extend(block_lines)
        out.append(FENCE_END)
    else:
        start_idx, end_idx = fence
        out = lines[: start_idx + 1]
        out.extend(block_lines)
        out.extend(lines[end_idx:])

    result = "\n".join(out)
    if had_trailing_newline:
        result += "\n"
    return result


def update_instruction_file(path: Path, block: str) -> None:
    """Apply the delimited block to the instruction file at ``path`` in place.

    The file is written atomically and durably (temp file + fsync + os.replace
    + directory fsync via trashheap.fsutil) so a crash never leaves a
    half-written instruction file.
    """
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    updated = apply_fenced_block(original, block)
    atomic_write_text(path, updated)


def extract_fenced_block(content: str) -> Optional[str]:
    """Return the current fenced block contents (or None if no fence)."""
    lines = content.splitlines()
    fence = _find_fence_lines(lines)
    if fence is None:
        return None
    start_idx, end_idx = fence
    inner = lines[start_idx + 1 : end_idx]
    return "\n".join(inner).strip("\n")


def has_fence(content: str) -> bool:
    """Return True if the file already carries a TRASHHEAP fence."""
    return _find_fence_lines(content.splitlines()) is not None
