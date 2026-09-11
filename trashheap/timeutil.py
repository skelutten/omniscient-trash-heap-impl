"""Canonical time utilities (single source of truth for timestamps).

Replaces the previously duplicated ``current_iso_timestamp`` helpers (9 copies,
3 divergent formats). The canonical format is UTC, second precision, ``Z``
suffix: ``2026-09-09T18:00:00Z``. It is deterministic-friendly (stable width,
lexicographically sortable) and round-trips through ``datetime.fromisoformat``
on Python >= 3.11.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

CANONICAL_TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def current_iso_timestamp() -> str:
    """Return the current UTC time as a canonical ``...Z`` timestamp string."""
    return datetime.now(timezone.utc).strftime(CANONICAL_TS_FORMAT)


def parse_iso_timestamp(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp (``Z`` suffix or ``+00:00``) to aware UTC.

    Returns ``None`` when the value is missing or unparseable, so callers can
    apply an explicit, documented fallback policy instead of crashing.
    """
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
