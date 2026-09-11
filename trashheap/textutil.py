"""Shared deterministic text utilities: tokenization, stopwords, content tokens.

Single source of truth for the lexical primitives used by the retrieval index
(BM25), the RCVA entailment proxy (RET-011) and the moderator pre-score
(REVIEW-011), so the three can never drift apart.
"""

from __future__ import annotations

import re
from typing import List, Set

STOPWORDS: Set[str] = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "if",
    "then",
    "else",
    "when",
    "at",
    "from",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "of",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "once",
    "here",
    "there",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "can",
    "will",
    "just",
    "should",
    "now",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "would",
    "could",
    "role",
    "play",
}

_TOKEN_RE = re.compile(r"\b[A-Za-z0-9_]+\b")

#: Token pattern that additionally preserves hyphens and dashes inside a token,
#: so canonical node IDs (``ENG-COMP-1234-2024``) survive as single tokens.
_ID_TOKEN_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_-]*")


def tokenize(text: str) -> List[str]:
    """Deterministic tokenization into lowercased words."""
    return [w.lower() for w in _TOKEN_RE.findall(text)]


def tokenize_with_ids(text: str) -> List[str]:
    """Tokenize while preserving hyphenated identifiers as whole tokens."""
    return [w.lower() for w in _ID_TOKEN_RE.findall(text)]


def content_tokens(text: str) -> Set[str]:
    """Lowercased alphanumeric tokens with stopwords removed (entailment proxy)."""
    return {t for t in tokenize(text) if t not in STOPWORDS}
