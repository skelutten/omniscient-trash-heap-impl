"""Tests for SCHEMA-005 / RET-010 (Document Card / Section Map, trashheap/section_map.py)."""

from trashheap.section_map import (
    LINE_THRESHOLD,
    WORD_THRESHOLD,
    build_section_map,
    extract_lines,
    extract_section,
    parse_line_range,
    requires_section_map,
)

BODY = """## Summary
Short summary here.

## Core Content
Line one of core.
Line two of core.

## Notes
Some notes.
"""


def test_build_section_map_line_numbers():
    entries = build_section_map(BODY)
    titles = [e.title for e in entries]
    assert titles == ["Summary", "Core Content", "Notes"]
    assert entries[0].start_line == 1
    assert entries[1].start_line == 4
    assert entries[2].start_line == 8


def test_extract_section_returns_heading_content():
    assert extract_section(BODY, "Core Content") == "Line one of core.\nLine two of core."
    assert extract_section(BODY, "Missing") is None


def test_extract_lines_slice():
    assert extract_lines(BODY, 4, 5) == "## Core Content\nLine one of core."
    assert extract_lines(BODY, 5, 6) == "Line one of core.\nLine two of core."


def test_requires_section_map_thresholds():
    long_words = "word " * (WORD_THRESHOLD + 1)
    assert requires_section_map(long_words)
    assert not requires_section_map("short body")
    long_lines = "\n".join(str(i) for i in range(LINE_THRESHOLD + 1))
    assert requires_section_map(long_lines)


def test_parse_line_range():
    assert parse_line_range("10") == (10, 10)
    assert parse_line_range("4-8") == (4, 8)
    assert parse_line_range("abc") is None
