"""Tests for RET-010 (section-targeted retrieval via `show --section/--lines`)."""

import contextlib
import io
from pathlib import Path

from trashheap.cli import main

DOC = """---
id: PERS-CONC-TST-0001
title: Test Object
schema_version: 1.0.0
scope: personal
object_type: Concept
domain: ai
taxonomy_path: Test
taxonomy_id: TEST-001
evidence: none
verification: none
authority: none
consensus: none
source_type: book
source_refs: []
author: Tester
status: established
---

## Summary
A short summary paragraph.

## Core Content
First core line.
Second core line.

## Notes
Human note.
"""


def _run(args):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        rc = main(args)
    return rc, stdout.getvalue(), stderr.getvalue()


def test_show_section(tmp_path: Path):
    p = tmp_path / "obj.md"
    p.write_text(DOC, encoding="utf-8")
    rc, out, err = _run(["show", str(p), "--section", "Core Content"])
    assert rc == 0
    assert out.strip() == "First core line.\nSecond core line."
    assert "Summary" not in out


def test_show_lines(tmp_path: Path):
    p = tmp_path / "obj.md"
    p.write_text(DOC, encoding="utf-8")
    # Body starts after the frontmatter; use --section-independent raw line access
    # via a file with known line numbers: search for the Core Content block.
    rc, out, err = _run(["show", str(p), "--lines", "1-3"])
    assert rc == 0
    assert "---" in out


def test_show_section_missing(tmp_path: Path):
    p = tmp_path / "obj.md"
    p.write_text(DOC, encoding="utf-8")
    rc, out, err = _run(["show", str(p), "--section", "DoesNotExist"])
    assert rc != 0


def test_show_invalid_lines(tmp_path: Path):
    p = tmp_path / "obj.md"
    p.write_text(DOC, encoding="utf-8")
    rc, out, err = _run(["show", str(p), "--lines", "bogus"])
    assert rc != 0
