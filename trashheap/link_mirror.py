"""Link mirroring check (VAL-011, the Redundancy Rule).

Every semantic relationship declared in frontmatter ``relations`` MUST also be
mirrored as a valid Markdown link in the document body prose. This module
provides the deterministic check as a pure function so it can be tested and
wired into strict-mode validation without mutating anything.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


def extract_link_targets(body: str) -> set:
    """Return the set of Markdown link targets referenced in ``body``.

    Covers inline links ``[text](target)`` and reference links ``[id]: target``.
    """
    targets: set = set()
    for m in re.finditer(r"\]\(([^)\s]+)", body):
        targets.add(m.group(1))
    for m in re.finditer(r"^\s*\[[^\]]+\]:\s*(\S+)", body, re.MULTILINE):
        targets.add(m.group(1))
    return targets


def check_link_mirroring(body: str, relations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return findings for each relation target not mirrored as a body link.

    Each finding is a plain dict (code/field/message/suggestion) so it can be
    surfaced by any caller or consumed by the linter in strict mode.
    """
    if not isinstance(relations, list) or not relations:
        return []

    link_targets = extract_link_targets(body)
    findings: List[Dict[str, Any]] = []
    for rel in relations:
        if not isinstance(rel, dict):
            continue
        target = rel.get("target", "")
        if not target:
            continue
        if not any(target in lt for lt in link_targets):
            findings.append(
                {
                    "code": "W016",
                    "field": "relations",
                    "message": (
                        f"Relation target '{target}' is not mirrored as a Markdown "
                        "link in the body prose (VAL-011)"
                    ),
                    "suggestion": (
                        f"Add a Markdown link such as '[{target}](./path/{target}.md)' "
                        "to the body prose"
                    ),
                }
            )
    return findings
