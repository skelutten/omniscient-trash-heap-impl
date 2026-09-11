"""Link mirroring check (VAL-011, the Redundancy Rule).

Every semantic relationship declared in frontmatter ``relations`` MUST also be
mirrored as a valid Markdown link in the document body prose. This module
provides the deterministic check as a pure function so it can be tested and
wired into the linter (W016) without mutating anything.

Matching is exact at the identifier level: a relation target ``T`` is mirrored
by a link whose target equals ``T``, whose path basename (minus ``.md`` and any
``#anchor``) equals ``T``, or by a wikilink ``[[T]]`` / ``[[T|label]]``.
Substring matching is deliberately avoided so that ``ENG-COMP-1`` is never
considered mirrored by a link to ``ENG-COMP-10``.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

_INLINE_LINK = re.compile(r"\]\(([^)\s]+)")
_REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
_WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def _link_stem(target: str) -> str:
    base = target.split("#", 1)[0].rsplit("/", 1)[-1]
    if base.endswith(".md"):
        base = base[: -len(".md")]
    return base


def extract_link_targets(body: str) -> set:
    """Return the set of link targets referenced in ``body``.

    Covers inline links ``[text](target)``, reference links ``[id]: target``,
    and wikilinks ``[[target]]`` / ``[[target|label]]``.
    """
    targets: set = set()
    for m in _INLINE_LINK.finditer(body):
        targets.add(m.group(1))
    for m in _REFERENCE_LINK.finditer(body):
        targets.add(m.group(1))
    for m in _WIKILINK.finditer(body):
        targets.add(m.group(1).strip())
    return targets


def is_target_mirrored(target: str, link_targets: set) -> bool:
    """Exact identifier-level match of ``target`` against extracted link targets."""
    for lt in link_targets:
        if lt == target or _link_stem(lt) == target:
            return True
    return False


def check_link_mirroring(body: str, relations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return findings for each relation target not mirrored as a body link.

    Each finding is a plain dict (code/field/message/suggestion) so it can be
    surfaced by any caller or consumed by the linter as W016.
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
        if not is_target_mirrored(target, link_targets):
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
