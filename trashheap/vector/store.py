"""Vector index store with multi-chunk max-over-chunks aggregation (Plan 90 Phase V2, D81)."""

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from trashheap.corpus import Corpus
from trashheap.vector.chunking import chunk_markdown
from trashheap.vector.protocol import (
    Embedder,
    EmbeddingIdentity,
    cosine_similarity,
    is_unit_norm,
)


@dataclass
class VectorHit:
    """Individual vector search hit with passage attribution (D81)."""

    node_id: str
    score: float
    chunk_index: int
    passage_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "score": round(self.score, 6),
            "chunk_index": self.chunk_index,
            "passage_text": self.passage_text[:200] if self.passage_text else "",
        }


class VectorIndex:
    """In-memory multi-chunk vector index with deterministic max-aggregation."""

    def __init__(self):
        # node_id -> List of (chunk_index, vector, chunk_text)
        self.chunk_records: Dict[str, List[Tuple[int, List[float], str]]] = {}
        self.fingerprint: str = ""
        self.embedder_identity: Optional[EmbeddingIdentity] = None
        self.corpus_hash: str = ""

    def build(self, corpus: Corpus, embedder: Embedder) -> None:
        """Build vector index over all Knowledge Objects in corpus."""
        self.chunk_records.clear()
        self.embedder_identity = embedder.identity

        # Compute corpus hash for index freshness tracking (CANON-003)
        h_corp = hashlib.sha256()
        all_texts: List[str] = []
        metadata_records: List[Tuple[str, int, str]] = []  # (node_id, chunk_index, chunk_text)

        for ko in corpus.objects:
            if not ko.id:
                continue
            h_corp.update(ko.id.encode("utf-8"))
            h_corp.update(ko.raw_body.encode("utf-8"))

            chunks = chunk_markdown(ko.raw_body)
            for c in chunks:
                metadata_records.append((ko.id, c.chunk_index, c.text))
                all_texts.append(c.text)

        self.corpus_hash = f"sha256:{h_corp.hexdigest()}"

        if not all_texts:
            self.fingerprint = f"vector_idx:empty:{self.corpus_hash}"
            return

        # Generate embeddings batch
        vectors = embedder.embed_documents(all_texts)
        if len(vectors) != len(all_texts):
            raise ValueError("Embedder returned vector count mismatch")

        # Defensive validation fail-closed (D80)
        for i, vec in enumerate(vectors):
            if len(vec) != embedder.dimension:
                raise ValueError(
                    f"Vector dimension mismatch at index {i}: {len(vec)} != {embedder.dimension}"
                )
            if not is_unit_norm(vec):
                raise ValueError(f"Vector at index {i} is not unit-normalized (||v|| != 1.0)")

        # Store chunk records
        for (node_id, chunk_idx, text), vec in zip(metadata_records, vectors):
            if node_id not in self.chunk_records:
                self.chunk_records[node_id] = []
            self.chunk_records[node_id].append((chunk_idx, vec, text))

        # Fingerprint index: model identity + corpus hash + dimension
        h_idx = hashlib.sha256()
        h_idx.update(self.corpus_hash.encode("utf-8"))
        h_idx.update(embedder.identity.model_name.encode("utf-8"))
        h_idx.update(str(embedder.dimension).encode("utf-8"))
        self.fingerprint = f"sha256:{h_idx.hexdigest()}"

    def score_query(
        self,
        query: str,
        embedder: Embedder,
        candidate_ids: Optional[Set[str]] = None,
        top_k: Optional[int] = 10,
    ) -> List[VectorHit]:
        """Score query against corpus using max-over-chunks aggregation (D81).

        score(q, d) = max_c cosine(q, d_c)
        """
        if not self.chunk_records or not query.strip():
            return []

        q_vec = embedder.embed_query(query)
        # Defensive validation
        if len(q_vec) != embedder.dimension:
            raise ValueError(
                f"Query vector dimension mismatch: {len(q_vec)} != {embedder.dimension}"
            )
        if not is_unit_norm(q_vec):
            raise ValueError("Query vector is not unit-normalized")

        hits: List[VectorHit] = []
        target_ids = (
            set(self.chunk_records.keys())
            if candidate_ids is None
            else (candidate_ids & set(self.chunk_records.keys()))
        )

        for node_id in target_ids:
            chunks = self.chunk_records[node_id]
            if not chunks:
                continue

            # Multi-Chunk Max-Over-Chunks Aggregation (D81)
            best_score = 0.0
            best_chunk_idx = 0
            best_passage = ""

            for chunk_idx, vec, text in chunks:
                sim = cosine_similarity(q_vec, vec, already_normalized=True)
                if sim > best_score:
                    best_score = sim
                    best_chunk_idx = chunk_idx
                    best_passage = text

            if best_score > 0.0:
                hits.append(
                    VectorHit(
                        node_id=node_id,
                        score=best_score,
                        chunk_index=best_chunk_idx,
                        passage_text=best_passage,
                    )
                )

        # Sort: score DESC -> node_id ASC
        sorted_hits = sorted(hits, key=lambda h: (-h.score, h.node_id))
        return sorted_hits[:top_k] if top_k is not None else sorted_hits

    def score_query_mean_pooled(
        self,
        query: str,
        embedder: Embedder,
        candidate_ids: Optional[Set[str]] = None,
        top_k: Optional[int] = 10,
    ) -> List[VectorHit]:
        """Alternative scoring baseline using mean-pooling for measurement comparison (SCALE-001)."""
        if not self.chunk_records or not query.strip():
            return []

        q_vec = embedder.embed_query(query)
        # Defensive validation (identical contract to score_query)
        if len(q_vec) != embedder.dimension:
            raise ValueError(
                f"Query vector dimension mismatch: {len(q_vec)} != {embedder.dimension}"
            )
        if not is_unit_norm(q_vec):
            raise ValueError("Query vector is not unit-normalized")

        hits: List[VectorHit] = []
        target_ids = (
            set(self.chunk_records.keys())
            if candidate_ids is None
            else (candidate_ids & set(self.chunk_records.keys()))
        )

        for node_id in target_ids:
            chunks = self.chunk_records[node_id]
            if not chunks:
                continue

            # Compute mean vector over all chunks
            dim = embedder.dimension
            mean_vec = [0.0] * dim
            for _, vec, _ in chunks:
                for d in range(dim):
                    mean_vec[d] += vec[d]
            c_len = float(len(chunks))
            mean_vec = [x / c_len for x in mean_vec]

            sim = cosine_similarity(q_vec, mean_vec, already_normalized=False)
            if sim > 0.0:
                hits.append(VectorHit(node_id=node_id, score=sim, chunk_index=0, passage_text=""))

        sorted_hits = sorted(hits, key=lambda h: (-h.score, h.node_id))
        return sorted_hits[:top_k] if top_k is not None else sorted_hits

    def check_freshness(self, corpus: Corpus, embedder: Embedder) -> Tuple[bool, Optional[str]]:
        """Check index freshness against current corpus and embedder (D84).

        Returns (is_fresh, stale_reason).
        """
        if not self.embedder_identity:
            return False, "uninitialized"
        if self.embedder_identity.model_name != embedder.identity.model_name:
            return False, "model change"
        if self.embedder_identity.dimension != embedder.dimension:
            return False, "dimension mismatch"

        h_corp = hashlib.sha256()
        for ko in corpus.objects:
            if not ko.id:
                continue
            h_corp.update(ko.id.encode("utf-8"))
            h_corp.update(ko.raw_body.encode("utf-8"))
        curr_corpus_hash = f"sha256:{h_corp.hexdigest()}"

        if self.corpus_hash != curr_corpus_hash:
            return False, "corpus change"

        return True, None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize index to deterministic JSON-compatible dictionary."""
        return {
            "schema_version": "1.0.0",
            "fingerprint": self.fingerprint,
            "corpus_hash": self.corpus_hash,
            "model_name": self.embedder_identity.model_name if self.embedder_identity else "",
            "dimension": self.embedder_identity.dimension if self.embedder_identity else 0,
            "is_double": self.embedder_identity.is_double if self.embedder_identity else False,
            "records": {
                node_id: [
                    {"chunk_index": c_idx, "vector": vec, "text": text}
                    for c_idx, vec, text in chunks
                ]
                for node_id, chunks in sorted(self.chunk_records.items())
            },
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Hydrate index from serialized dictionary with fail-closed validation (D80).

        Mirrors the defensive checks in :meth:`build`: every restored vector
        must match the serialized dimension and be unit-normalized within
        tolerance. Raises ValueError on any violation before mutating state, so
        a corrupt index is never partially hydrated.
        """
        fingerprint = data.get("fingerprint", "")
        corpus_hash = data.get("corpus_hash", "")
        m_name = data.get("model_name", "")
        dim = data.get("dimension", 0)
        is_double = data.get("is_double", False)

        restored_records: Dict[str, List[Tuple[int, List[float], str]]] = {}
        for node_id, chunks in data.get("records", {}).items():
            restored_chunks: List[Tuple[int, List[float], str]] = []
            for c in chunks:
                vec = c["vector"]
                if len(vec) != dim:
                    raise ValueError(
                        f"Vector dimension mismatch for node '{node_id}' chunk "
                        f"{c['chunk_index']}: {len(vec)} != {dim}"
                    )
                if not is_unit_norm(vec):
                    raise ValueError(
                        f"Vector for node '{node_id}' chunk {c['chunk_index']} "
                        f"is not unit-normalized (||v|| != 1.0)"
                    )
                restored_chunks.append((c["chunk_index"], vec, c["text"]))
            restored_records[node_id] = restored_chunks

        self.fingerprint = fingerprint
        self.corpus_hash = corpus_hash
        self.embedder_identity = EmbeddingIdentity(
            model_name=m_name,
            dimension=dim,
            is_double=is_double,
            provider="restored",
            fingerprint=fingerprint,
        )
        self.chunk_records = restored_records
