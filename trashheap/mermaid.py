"""Mermaid degradation & auto-heal (VAL-012).

When a generated or ingested Mermaid diagram fails basic syntax validation, the
compiler MUST NOT crash; it MUST degrade the block in place to a `` ```text ``
fence prefixed with an explicit diagnostic marker, surfacing the failure for an
automated self-healing pass on the next compilation cycle.
"""

from __future__ import annotations

import re
from typing import List, Tuple

LINT_FAILURE_MARKER = "<!-- LINT_FAILURE: mermaid syntax error: {reason} -->"

# Recognised Mermaid diagram directives (first token of a diagram body).
MERMAID_DIRECTIVES = {
    "graph",
    "flowchart",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "gantt",
    "pie",
    "journey",
    "mindmap",
    "timeline",
    "quadrantChart",
    "xychart",
    "C4Context",
    "C4Container",
    "C4Component",
    "C4Dynamic",
    "C4Deployment",
    "gitGraph",
    "requirementDiagram",
    "sankey",
    "block",
}

_MERMAID_FENCE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def extract_mermaid_blocks(body: str) -> List[dict]:
    """Return every ```mermaid fenced block with its inner content."""
    blocks: List[dict] = []
    for m in _MERMAID_FENCE.finditer(body):
        blocks.append({"inner": m.group(1), "start": m.start(), "end": m.end()})
    return blocks


def validate_mermaid_block(inner: str) -> Tuple[bool, str]:
    """Deterministic basic syntax check of a Mermaid diagram body."""
    stripped = inner.strip()
    if not stripped:
        return False, "empty diagram"
    first_line = stripped.splitlines()[0].strip()
    if not any(first_line.startswith(d) for d in sorted(MERMAID_DIRECTIVES, key=len, reverse=True)):
        return False, f"unrecognized diagram directive {first_line!r}"
    for open_c, close_c in (("{", "}"), ("[", "]"), ("(", ")")):
        if stripped.count(open_c) != stripped.count(close_c):
            return False, f"unbalanced {open_c}{close_c} delimiters"
    return True, ""


def degrade_mermaid_block(inner: str, reason: str) -> str:
    """Return the degraded ```text block with the diagnostic marker."""
    return LINT_FAILURE_MARKER.format(reason=reason) + "\n```text\n" + inner.strip() + "\n```"


def degrade_broken_mermaid_blocks(body: str) -> str:
    """Rewrite ``body``, degrading every broken ```mermaid block in place."""
    out = body

    def repl(m: re.Match) -> str:
        inner = m.group(1)
        ok, reason = validate_mermaid_block(inner)
        if ok:
            return m.group(0)
        return degrade_mermaid_block(inner, reason)

    return _MERMAID_FENCE.sub(repl, out)
