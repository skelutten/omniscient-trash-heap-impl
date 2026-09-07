"""Opt-in vector retrieval subsystem (Plan 90, D79–D84)."""

from trashheap.vector.chunking import ChunkRecord, chunk_markdown, strip_frontmatter
from trashheap.vector.double import DeterministicDouble
from trashheap.vector.protocol import (
    Embedder,
    EmbeddingIdentity,
    cosine_similarity,
    is_unit_norm,
    normalize_vector,
)
from trashheap.vector.provider import LocalOfflineProvider
from trashheap.vector.store import VectorHit, VectorIndex

__all__ = [
    "Embedder",
    "EmbeddingIdentity",
    "cosine_similarity",
    "is_unit_norm",
    "normalize_vector",
    "DeterministicDouble",
    "ChunkRecord",
    "chunk_markdown",
    "strip_frontmatter",
    "VectorHit",
    "VectorIndex",
    "LocalOfflineProvider",
]
