"""Deterministic slugification and path resolution (ARCHITECTURE.md §1.3, TAX-002, TAX-003, TAX-007)."""

import re
import unicodedata
from typing import Any, Dict, List, Optional

SEGMENT_RE = re.compile(r"^(?P<prefix>\d+(?:\.\d+)*\.?)\s*(?P<text>.*)$")


def ascii_fold(text: str) -> str:
    """Fold Unicode characters to ASCII equivalents."""
    replacements = {
        "ø": "o",
        "Ø": "o",
        "æ": "ae",
        "Æ": "ae",
        "å": "a",
        "Å": "a",
        "ä": "a",
        "Ä": "a",
        "ö": "o",
        "Ö": "o",
        "ü": "u",
        "Ü": "u",
        "ß": "ss",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def slugify_text(text: str) -> str:
    """Canonical text slugification (ARCHITECTURE.md §1.3)."""
    text = ascii_fold(text).lower()
    text = re.sub(r"[&/,\-()]+", "_", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def normalize_segment(segment: str) -> str:
    """Normalize a taxonomy node name segment preserving numeric prefix."""
    segment = segment.strip()
    match = SEGMENT_RE.match(segment)
    if match:
        prefix = match.group("prefix").rstrip(".")
        # Replace internal dots with underscores for path segments
        prefix = prefix.replace(".", "_")
        text = slugify_text(match.group("text"))
        if text:
            return f"{prefix}_{text}"
        return prefix
    return slugify_text(segment)


def ancestor_chain(registry_by_id: Dict[str, Any], taxonomy_id: str) -> List[str]:
    """Resolve ancestor chain from leaf to root; returns root-to-leaf list of node names.

    Raises ValueError on cycles (TAX-006 / E024) or KeyError on missing parent (E018).
    """
    chain: List[str] = []
    seen: set[str] = set()
    current: Optional[str] = taxonomy_id

    while current is not None:
        if current in seen:
            raise ValueError(f"Taxonomy cycle detected at node: {current}")
        seen.add(current)
        if current not in registry_by_id:
            raise KeyError(f"Missing taxonomy node: {current}")
        node = registry_by_id[current]
        chain.append(node["name"])
        current = node.get("parent_id")

    return list(reversed(chain))


def taxonomy_id_to_directory(registry_by_id: Dict[str, Any], scope: str, taxonomy_id: str) -> str:
    """Deterministically compute directory path for a taxonomy node (TAX-002).

    Format: <scope>/<normalized-ancestor-chain>/
    """
    if taxonomy_id not in registry_by_id:
        raise KeyError(f"Taxonomy ID '{taxonomy_id}' not found in registry")

    node = registry_by_id[taxonomy_id]
    if node.get("scope") != scope:
        raise ValueError(
            f"Node scope '{node.get('scope')}' does not match requested scope '{scope}'"
        )

    chain_names = ancestor_chain(registry_by_id, taxonomy_id)
    normalized = [normalize_segment(name) for name in chain_names]
    return f"{scope}/" + "/".join(normalized) + "/"
