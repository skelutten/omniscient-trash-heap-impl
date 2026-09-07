"""Deterministic test double for vector embedding seams (Plan 90 Phase V1, D79).

Enforces the Honest Modality Rule:
A test double (is_double = True) is strictly forbidden from claiming the vector
modality in evidence bundles; bundles report vector as absent.
"""

import hashlib
import re
from typing import List

from trashheap.vector.protocol import (
    Embedder,
    EmbeddingIdentity,
    normalize_vector,
)

WORD_RE = re.compile(r"[a-z0-9_]+")


class DeterministicDouble(Embedder):
    """Deterministic, offline embedding test double using hashed n-gram projections."""

    def __init__(self, dimension: int = 384, model_name: str = "deterministic-double-v1"):
        self._dimension = dimension
        self._model_name = model_name
        self._identity = EmbeddingIdentity(
            model_name=self._model_name,
            dimension=self._dimension,
            is_double=True,  # STRICT: Honest Modality Rule (D79)
            provider="test_double",
            fingerprint=f"double:{model_name}:{dimension}",
        )

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def identity(self) -> EmbeddingIdentity:
        return self._identity

    def _embed_text(self, text: str) -> List[float]:
        """Compute deterministic unit-norm pseudo-embedding via token hashing."""
        vec = [0.0] * self._dimension
        tokens = WORD_RE.findall(text.lower())
        if not tokens:
            # Return uniform unit vector
            val = 1.0 / (self._dimension**0.5)
            return [val] * self._dimension

        for tok in tokens:
            # Hash token into bucket and sign
            h = hashlib.sha256(tok.encode("utf-8")).digest()
            idx = int.from_bytes(h[:4], "big") % self._dimension
            sign = 1.0 if h[4] % 2 == 0 else -1.0
            vec[idx] += sign

            # Also hash bigrams if available
            if len(tok) >= 3:
                for i in range(len(tok) - 2):
                    sub = tok[i : i + 3]
                    h_sub = hashlib.sha256(sub.encode("utf-8")).digest()
                    s_idx = int.from_bytes(h_sub[:4], "big") % self._dimension
                    s_sign = 0.5 if h_sub[4] % 2 == 0 else -0.5
                    vec[s_idx] += s_sign

        return normalize_vector(vec)

    def embed_query(self, text: str) -> List[float]:
        return self._embed_text(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(t) for t in texts]
