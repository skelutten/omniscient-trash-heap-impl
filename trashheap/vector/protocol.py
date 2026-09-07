"""Embedding protocols, identity records, and vector similarity metrics (Plan 90, D79, D81)."""

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, Sequence, runtime_checkable


@dataclass(frozen=True)
class EmbeddingIdentity:
    """Identity watermark for an embedder instance (D79, D82)."""

    model_name: str
    dimension: int
    is_double: bool = False
    provider: str = "offline"
    fingerprint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "is_double": self.is_double,
            "provider": self.provider,
            "fingerprint": self.fingerprint,
        }


@runtime_checkable
class Embedder(Protocol):
    """Protocol for offline vector embedding models (D79, RET-005)."""

    @property
    def dimension(self) -> int:
        """Return embedding vector dimension."""
        ...

    @property
    def identity(self) -> EmbeddingIdentity:
        """Return embedding identity record."""
        ...

    def embed_query(self, text: str) -> List[float]:
        """Compute normalized vector embedding for a single search query."""
        ...

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute normalized vector embeddings for a list of document passages."""
        ...


def is_unit_norm(vector: Sequence[float], tolerance: float = 1e-3) -> bool:
    """Check if a vector has unit Euclidean norm (||v|| ≈ 1.0)."""
    norm_sq = sum(x * x for x in vector)
    return abs(math.sqrt(norm_sq) - 1.0) <= tolerance


def normalize_vector(vector: Sequence[float]) -> List[float]:
    """Normalize a float vector to unit Euclidean length (L2 norm)."""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0.0:
        return [0.0] * len(vector)
    return [x / norm for x in vector]


def cosine_similarity(
    vec_a: Sequence[float],
    vec_b: Sequence[float],
    already_normalized: bool = True,
) -> float:
    """Compute cosine similarity with strict 0.0 sign-convention floor (D81).

    Discards negative cosine similarity. Does NOT apply arbitrary thresholds.
    """
    if len(vec_a) != len(vec_b):
        raise ValueError(f"Vector dimension mismatch: {len(vec_a)} != {len(vec_b)}")

    if already_normalized:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
    else:
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b)) / (norm_a * norm_b)

    # 0.0 sign-convention floor per D81 / RETRIEVAL.md §9.1
    return max(0.0, float(dot))
