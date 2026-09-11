"""Document Card / Section Map helpers (SCHEMA-005, RET-010).

For any Knowledge Object exceeding 1,000 words or 100 lines of body content,
the document structure MUST maintain or generate an explicit Section Map (the
"Document Card" pattern) mapping section titles to 1-indexed line numbers and
approximate token counts. Retrieval tools then support line-bounded and
section-bounded extraction using that map.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

WORD_THRESHOLD = 1000
LINE_THRESHOLD = 100


@dataclass
class SectionMapEntry:
    title: str
    start_line: int  # 1-indexed
    end_line: int  # 1-indexed, inclusive
    tokens: int

    def to_dict(self) -> dict:
        return {
            "section": self.title,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "tokens": self.tokens,
        }


def word_count(text: str) -> int:
    return len(text.split())


def line_count(text: str) -> int:
    return len(text.splitlines())


def approx_tokens(text: str) -> int:
    """Approximate token count (~1.3 tokens per whitespace-delimited word)."""
    return max(0, round(word_count(text) * 1.3))


def requires_section_map(body: str) -> bool:
    """Return True when the body exceeds the long-form thresholds (SCHEMA-005)."""
    return word_count(body) > WORD_THRESHOLD or line_count(body) > LINE_THRESHOLD


def build_section_map(body: str) -> List[SectionMapEntry]:
    """Parse H2 sections and return a Section Map (Document Card) of the body.

    Code-fence aware: a ``## `` line inside a fenced code block (``` or ~~~)
    is content, not a section heading.
    """
    lines = body.splitlines()
    entries: List[SectionMapEntry] = []
    current_title: Optional[str] = None
    current_start: int = 0
    fence_marker: Optional[str] = None

    def close(prev_end: int) -> None:
        nonlocal current_title
        if current_title is not None:
            entries.append(
                SectionMapEntry(
                    title=current_title,
                    start_line=current_start,
                    end_line=prev_end,
                    tokens=approx_tokens("\n".join(lines[current_start - 1 : prev_end])),
                )
            )
            current_title = None

    for idx, line in enumerate(lines):
        lineno = idx + 1
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if fence_marker is None:
                fence_marker = marker
            elif marker == fence_marker:
                fence_marker = None
            continue
        if fence_marker is None and line.startswith("## "):
            close(lineno - 1)
            current_title = line[3:].strip()
            current_start = lineno

    close(len(lines))

    return entries


def extract_section(body: str, heading: str) -> Optional[str]:
    """Return the body text under the H2 section named ``heading`` (or None)."""
    entries = build_section_map(body)
    lines = body.splitlines()
    for entry in entries:
        if entry.title == heading:
            return "\n".join(lines[entry.start_line : entry.end_line]).strip()
    return None


def extract_lines(body: str, start: int, end: int) -> Optional[str]:
    """Return the 1-indexed inclusive line slice ``start..end`` of the body."""
    lines = body.splitlines()
    if start < 1 or end < start:
        return None
    if start > len(lines):
        return None
    end = min(end, len(lines))
    return "\n".join(lines[start - 1 : end])


def parse_line_range(spec: str) -> Optional[tuple[int, int]]:
    """Parse a ``N`` or ``N-M`` line-range string into an inclusive (start, end) pair."""
    spec = spec.strip()
    if "-" in spec:
        left, right = spec.split("-", 1)
        try:
            return int(left), int(right)
        except ValueError:
            return None
    try:
        n = int(spec)
        return n, n
    except ValueError:
        return None
