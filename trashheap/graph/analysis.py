"""Deterministic graph metrics, chunking, and derived edge analysis.

Complies with specs/GRAPH-INTELLIGENCE.md §7.1, §12 (Phase 2), and specs/GRAPH-RETRIEVAL.md §8.
"""

import re
import unicodedata
from collections import deque
from pathlib import Path
from typing import Dict, List, Set, Tuple

from trashheap.corpus import Corpus
from trashheap.graph.models import (
    Community,
    DerivationMetadata,
    DerivedEdge,
    NodeMetrics,
)
from trashheap.models import KnowledgeObject
from trashheap.vector.protocol import cosine_similarity
from trashheap.vector.provider import LocalOfflineProvider


def normalize_chunk_text(text: str) -> str:
    """Normalize text with Unicode NFKC, lowercased, whitespace collapsed (§7.1)."""
    normalized = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"\s+", " ", normalized).strip()


def chunk_text_deterministic(
    text: str, chunk_size: int = 500, overlap: int = 50
) -> List[str]:
    """Deterministic character-based chunking window per GRAPH-INTELLIGENCE.md §7.1.

    Windows are consecutive chunk_size-codepoint windows with overlap;
    the final short window is retained.
    """
    normalized = normalize_chunk_text(text)
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: List[str] = []
    step = chunk_size - overlap
    if step <= 0:
        step = chunk_size

    pos = 0
    total_len = len(normalized)
    while pos < total_len:
        end = min(pos + chunk_size, total_len)
        chunks.append(normalized[pos:end])
        if end == total_len:
            break
        pos += step

    return chunks


def normalize_source_refs(refs: List[str]) -> Set[str]:
    """Normalize provenance source refs: strip, lowercase, collapse internal whitespace."""
    out: Set[str] = set()
    for r in refs:
        if not r:
            continue
        cleaned = re.sub(r"\s+", " ", r.strip().lower())
        if cleaned:
            out.add(cleaned)
    return out


class GraphAnalyzer:
    """Computes deterministic graph topology, node metrics, communities, and derived edges."""

    def __init__(
        self,
        corpus: Corpus,
        workspace_root: Path,
        embedder: LocalOfflineProvider | None = None,
    ):
        self.corpus = corpus
        self.workspace_root = workspace_root
        self.embedder = embedder or LocalOfflineProvider()
        self.objects_by_id: Dict[str, KnowledgeObject] = {
            ko.id: ko for ko in corpus.objects if ko.id
        }

    def compute_topology(
        self,
    ) -> Tuple[
        Dict[str, Set[str]],
        Dict[str, int],
        Dict[str, int],
        Dict[str, int],
        Dict[str, str],
        Dict[str, Community],
    ]:
        """Compute adjacency, in/out/total degree, connected components, and per-scope communities."""
        node_ids = sorted(self.objects_by_id.keys())
        out_adj: Dict[str, Set[str]] = {nid: set() for nid in node_ids}
        in_adj: Dict[str, Set[str]] = {nid: set() for nid in node_ids}
        scope_map: Dict[str, str] = {
            nid: (self.objects_by_id[nid].scope or "engineering")
            for nid in node_ids
        }

        # Build adjacency over canonical relations
        for ko in self.corpus.objects:
            if not ko.id:
                continue
            for rel in ko.relations:
                target = rel.get("target")
                if target and target in self.objects_by_id:
                    out_adj[ko.id].add(target)
                    in_adj[target].add(ko.id)

        in_degree = {nid: len(in_adj[nid]) for nid in node_ids}
        out_degree = {nid: len(out_adj[nid]) for nid in node_ids}
        total_degree = {nid: in_degree[nid] + out_degree[nid] for nid in node_ids}

        # Connected components (undirected BFS over canonical edges, sorted)
        undirected_adj: Dict[str, Set[str]] = {
            nid: (out_adj[nid] | in_adj[nid]) for nid in node_ids
        }
        visited: Set[str] = set()
        component_map: Dict[str, str] = {}
        comp_idx = 0

        for nid in node_ids:
            if nid not in visited:
                comp_idx += 1
                comp_id = f"comp_{comp_idx:03d}"
                queue = deque([nid])
                visited.add(nid)
                while queue:
                    curr = queue.popleft()
                    component_map[curr] = comp_id
                    for neighbor in sorted(undirected_adj[curr]):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

        # Per-scope community partition (GRAPH-INTELLIGENCE.md §4: community_partition: per_scope)
        communities: Dict[str, Community] = {}
        nodes_by_scope: Dict[str, List[str]] = {}
        for nid, sc in scope_map.items():
            nodes_by_scope.setdefault(sc, []).append(nid)

        for sc, sc_nodes in sorted(nodes_by_scope.items()):
            sc_visited: Set[str] = set()
            comm_num = 0
            for snid in sorted(sc_nodes):
                if snid not in sc_visited:
                    comm_num += 1
                    comm_id = f"comm_{sc}_{comm_num:03d}"
                    comm_members: List[str] = []
                    q = deque([snid])
                    sc_visited.add(snid)
                    while q:
                        curr = q.popleft()
                        comm_members.append(curr)
                        for neighbor in sorted(undirected_adj[curr]):
                            if neighbor in sc_nodes and neighbor not in sc_visited:
                                sc_visited.add(neighbor)
                                q.append(neighbor)
                    communities[comm_id] = Community(
                        community_id=comm_id,
                        scope=sc,
                        level=0,
                        member_node_ids=sorted(comm_members),
                    )

        return out_adj, in_degree, out_degree, total_degree, component_map, communities

    def compute_bounded_distances(
        self, max_depth: int = 3
    ) -> Dict[str, Dict[str, int]]:
        """Compute all-pairs shortest path distance up to max_depth using BFS."""
        node_ids = sorted(self.objects_by_id.keys())
        out_adj: Dict[str, Set[str]] = {nid: set() for nid in node_ids}
        for ko in self.corpus.objects:
            if not ko.id:
                continue
            for rel in ko.relations:
                target = rel.get("target")
                if target and target in self.objects_by_id:
                    out_adj[ko.id].add(target)

        distances: Dict[str, Dict[str, int]] = {}
        for src in node_ids:
            dist: Dict[str, int] = {src: 0}
            queue = deque([(src, 0)])
            while queue:
                curr, d = queue.popleft()
                if d >= max_depth:
                    continue
                for nxt in sorted(out_adj[curr]):
                    if nxt not in dist:
                        dist[nxt] = d + 1
                        queue.append((nxt, d + 1))
            distances[src] = dist
        return distances

    def compute_node_metrics(self) -> Dict[str, NodeMetrics]:
        """Calculate complete topological NodeMetrics for every canonical object."""
        (
            out_adj,
            in_deg,
            out_deg,
            tot_deg,
            comp_map,
            communities,
        ) = self.compute_topology()
        distances = self.compute_bounded_distances(max_depth=3)

        # Invert community mapping
        node_to_community: Dict[str, str] = {}
        for cid, comm in communities.items():
            for mnid in comm.member_node_ids:
                node_to_community[mnid] = cid

        metrics: Dict[str, NodeMetrics] = {}
        for nid, ko in sorted(self.objects_by_id.items()):
            sc = ko.scope or "engineering"
            metrics[nid] = NodeMetrics(
                node_id=nid,
                scope=sc,
                in_degree=in_deg[nid],
                out_degree=out_deg[nid],
                total_degree=tot_deg[nid],
                component_id=comp_map.get(nid, "comp_unknown"),
                community_id=node_to_community.get(nid, f"comm_{sc}_none"),
                distances=distances.get(nid, {}),
            )
        return metrics

    def compute_derived_edges(
        self,
        corpus_hash: str,
        min_edge_strength: float = 0.15,
        semantic_cutoff: float = 0.75,
        min_cooccurrence_chunks: int = 2,
    ) -> List[DerivedEdge]:
        """Compute derived edges per specs/GRAPH-RETRIEVAL.md §8 with explicit 4-part weights."""
        node_ids = sorted(self.objects_by_id.keys())
        if len(node_ids) < 2:
            return []

        # 1. Embeddings for semantic similarity
        embeddings: Dict[str, List[float]] = {}
        for nid, ko in self.objects_by_id.items():
            text = f"{ko.title or ''}\n{ko.raw_body}"
            embeddings[nid] = self.embedder.embed_query(text)

        # 2. Source refs for proximity
        source_refs_map: Dict[str, Set[str]] = {}
        for nid, ko in self.objects_by_id.items():
            srefs = []
            if ko.frontmatter:
                srefs = ko.frontmatter.source_refs
            elif "source_refs" in ko.frontmatter_dict:
                srefs = ko.frontmatter_dict.get("source_refs", [])
            source_refs_map[nid] = normalize_source_refs(srefs)

        # 3. Chunks for cooccurrence
        # Build mapping from node_id to all chunks in the entire corpus that contain node_id or its aliases
        chunk_hits_by_node: Dict[str, Set[int]] = {nid: set() for nid in node_ids}
        global_chunk_idx = 0

        for ko in self.corpus.objects:
            if not ko.id:
                continue
            chunks = chunk_text_deterministic(ko.raw_body)
            for ch in chunks:
                ch_tokens = set(ch.split())
                for nid in node_ids:
                    target_ko = self.objects_by_id[nid]
                    # Check if nid appears in chunk
                    norm_id = nid.lower()
                    aliases = [norm_id]
                    if target_ko.frontmatter:
                        aliases.extend(
                            [normalize_chunk_text(a) for a in target_ko.frontmatter.aliases if a]
                        )

                    found = False
                    for alias in aliases:
                        if not alias:
                            continue
                        alias_toks = alias.split()
                        # All tokens must be in chunk tokens (fast check)
                        if all(at in ch_tokens for at in alias_toks) and alias in ch:
                            found = True
                            break
                    if found:
                        chunk_hits_by_node[nid].add(global_chunk_idx)
                global_chunk_idx += 1

        # 4. Canonical edges lookup
        canonical_edges: Set[Tuple[str, str]] = set()
        for ko in self.corpus.objects:
            if not ko.id:
                continue
            for rel in ko.relations:
                tgt = rel.get("target")
                if tgt and tgt in self.objects_by_id:
                    canonical_edges.add((ko.id, tgt))

        # 5. Compute scores across pairs within same scope (GRAPH-INTELLIGENCE.md §4)
        derived_edges: List[DerivedEdge] = []
        w_canon = 0.50
        w_sim = 0.20
        w_prox = 0.15
        w_cooc = 0.15

        for i, u in enumerate(node_ids):
            u_scope = self.objects_by_id[u].scope or "engineering"
            for j in range(i + 1, len(node_ids)):
                v = node_ids[j]
                v_scope = self.objects_by_id[v].scope or "engineering"

                # Scope isolation: no cross-scope edges unless policy allows (DELTA-CORE-007)
                if u_scope != v_scope:
                    continue

                canon_exists = (u, v) in canonical_edges or (v, u) in canonical_edges
                canon_score = 1.0 if canon_exists else 0.0

                sim = cosine_similarity(embeddings[u], embeddings[v])
                sim_score = sim if sim >= semantic_cutoff else 0.0

                shared_refs = source_refs_map[u] & source_refs_map[v]
                prox_score = min(1.0, len(shared_refs) / 5.0)

                shared_chunks = chunk_hits_by_node[u] & chunk_hits_by_node[v]
                cooc_count = len(shared_chunks)
                cooc_score = (
                    min(1.0, cooc_count / 10.0)
                    if cooc_count >= min_cooccurrence_chunks
                    else 0.0
                )

                final_score = min(
                    1.0,
                    max(
                        0.0,
                        w_canon * canon_score
                        + w_sim * sim_score
                        + w_prox * prox_score
                        + w_cooc * cooc_score,
                    ),
                )

                if final_score >= min_edge_strength:
                    edge_id = f"d_edge_{u}_{v}_1.0.0"
                    ev_refs = sorted(list(shared_refs))
                    edge = DerivedEdge(
                        edge_id=edge_id,
                        source_id=u,
                        target_id=v,
                        canonical_edge_exists=canon_exists,
                        component_scores={
                            "canonical": canon_score,
                            "similarity": round(sim_score, 4),
                            "proximity": round(prox_score, 4),
                            "cooccurrence": round(cooc_score, 4),
                        },
                        final_score=final_score,
                        scope=u_scope,
                        corpus_hash=corpus_hash,
                        algorithm_version="1.0.0",
                        policy_version="1.0.0",
                        derivation=DerivationMetadata(
                            mode="extracted" if canon_exists else "inferred",
                            extractor="graph_delta",
                            confidence=round(final_score, 4),
                        ),
                        evidence_refs=ev_refs,
                    )
                    derived_edges.append(edge)

        # Sort deterministically by (-final_score, edge_id)
        derived_edges.sort(key=lambda e: (-e.final_score, e.edge_id))
        return derived_edges
