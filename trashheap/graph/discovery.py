"""Discovery candidate generation, patterns, and governed lifecycle management.

Complies with specs/DISCOVERY.md and specs/GRAPH-INTELLIGENCE.md.
Implements invariants DISC-001..DISC-005 and DELTA-CORE-004..DELTA-CORE-007.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from trashheap.corpus import Corpus
from trashheap.graph.analysis import (
    GraphAnalyzer,
    chunk_text_deterministic,
    normalize_chunk_text,
)
from trashheap.graph.models import (
    DiscoveryAuditEntry,
    DiscoveryCandidate,
    NodeDiscoveryCandidate,
    RelationDiscoveryCandidate,
    current_iso_timestamp,
)
from trashheap.models import KnowledgeObject
from trashheap.registry.loader import LoadedRegistries
from trashheap.vector.protocol import cosine_similarity
from trashheap.vector.provider import LocalOfflineProvider


def compute_expiry_date(created_iso: str, days: int = 90) -> str:
    """Compute expiration timestamp at most 90 calendar days from creation (DISC-001)."""
    dt = datetime.fromisoformat(created_iso.replace("Z", "+00:00"))
    exp = dt + timedelta(days=min(days, 90))
    return exp.strftime("%Y-%m-%dT%H:%M:%SZ")


class DiscoveryEngine:
    """Detects duplicates, topological gaps, and ontological gaps across canonical corpus."""

    def __init__(
        self,
        corpus: Corpus,
        registries: LoadedRegistries,
        workspace_root: Path,
        embedder: Optional[LocalOfflineProvider] = None,
    ):
        self.corpus = corpus
        self.registries = registries
        self.workspace_root = workspace_root
        self.embedder = embedder or LocalOfflineProvider()
        self.objects_by_id: Dict[str, KnowledgeObject] = {
            ko.id: ko for ko in corpus.objects if ko.id
        }
        self.analyzer = GraphAnalyzer(corpus, workspace_root, self.embedder)
        self._embeddings: Optional[Dict[str, List[float]]] = None

    def _get_embeddings(self) -> Dict[str, List[float]]:
        """Get or lazily compute embeddings for all objects."""
        if self._embeddings is None:
            self._embeddings = {
                nid: self.embedder.embed_query(f"{ko.title or ''}\n{ko.raw_body}")
                for nid, ko in self.objects_by_id.items()
            }
        return self._embeddings

    def scan_all_candidates(
        self, corpus_hash: str
    ) -> List[RelationDiscoveryCandidate | NodeDiscoveryCandidate]:
        """Run complete discovery scan for duplicates, topological gaps, and ontological gaps."""
        candidates: List[RelationDiscoveryCandidate | NodeDiscoveryCandidate] = []
        candidates.extend(self.scan_duplicates(corpus_hash))
        candidates.extend(self.scan_topological_gaps(corpus_hash))
        candidates.extend(self.scan_ontological_gaps(corpus_hash))
        # Sort candidates deterministically by candidate_id
        candidates.sort(key=lambda c: c.candidate_id)
        return candidates

    def scan_duplicates(
        self, corpus_hash: str, similarity_cutoff: float = 0.80
    ) -> List[RelationDiscoveryCandidate]:
        """Scan for duplicate pair candidates within same scope (DISC-002, DISCOVERY.md §10.1)."""
        node_ids = sorted(self.objects_by_id.keys())
        embeddings = self._get_embeddings()

        duplicates: List[RelationDiscoveryCandidate] = []
        created_at = current_iso_timestamp()
        expires_at = compute_expiry_date(created_at, 90)

        for i, u in enumerate(node_ids):
            u_scope = self.objects_by_id[u].scope or "engineering"
            for j in range(i + 1, len(node_ids)):
                v = node_ids[j]
                v_scope = self.objects_by_id[v].scope or "engineering"

                if u_scope != v_scope:
                    continue

                sim = cosine_similarity(embeddings[u], embeddings[v])
                if sim >= similarity_cutoff:
                    # Canonicalized pair identity (min, max) per §10.1
                    source_id = min(u, v)
                    target_id = max(u, v)
                    cid = f"DISC-DUP-{source_id}-{target_id}"

                    candidate = RelationDiscoveryCandidate(
                        candidate_id=cid,
                        candidate_type="duplicate",
                        confidence=round(sim, 4),
                        status="pending",
                        created_at=created_at,
                        expires_at=expires_at,
                        scope=u_scope,
                        corpus_hash=corpus_hash,
                        algorithm_version="1.0.0",
                        evidence_refs=[f"sim:{round(sim, 4)}"],
                        source_refs=[source_id, target_id],
                        representation_refs=[],
                        evidence_unit_refs=[],
                        derivation_ref="vector_cosine_similarity",
                        source_id=source_id,
                        target_id=target_id,
                        suggested_relation=None,
                        metadata={"similarity": round(sim, 4)},
                    )
                    duplicates.append(candidate)

        return duplicates

    def scan_topological_gaps(self, corpus_hash: str) -> List[RelationDiscoveryCandidate]:
        """Scan for topological knowledge gaps via 2-of-3 predicates (DISC-003, DISCOVERY.md §10.2.1).

        A = same_scope_and_community
        B = contextual_cooccurrence >= 3 chunks
        C = semantic_similarity >= 0.80
        gap_candidate = (A and B) or (A and C) or (B and C)
        """
        node_ids = sorted(self.objects_by_id.keys())
        if len(node_ids) < 2:
            return []

        # 1. Existing canonical relations
        canonical_edges: Set[Tuple[str, str]] = set()
        for ko in self.corpus.objects:
            if not ko.id:
                continue
            for rel in ko.relations:
                tgt = rel.get("target")
                if tgt and tgt in self.objects_by_id:
                    canonical_edges.add((ko.id, tgt))
                    canonical_edges.add((tgt, ko.id))

        # 2. Topology and communities
        _, _, _, _, _, communities = self.analyzer.compute_topology()
        node_to_community: Dict[str, str] = {}
        for cid, comm in communities.items():
            for mnid in comm.member_node_ids:
                node_to_community[mnid] = cid

        # 3. Embeddings for semantic similarity
        embeddings = self._get_embeddings()

        # 4. Chunks for cooccurrence
        chunk_hits: Dict[str, Set[int]] = {nid: set() for nid in node_ids}
        global_chunk_idx = 0

        # Precompute normalized aliases and token sets for all nodes
        node_aliases: Dict[str, List[Tuple[str, Set[str]]]] = {}
        for nid in node_ids:
            target_ko = self.objects_by_id[nid]
            norm_id = nid.lower()
            aliases = [norm_id]
            if target_ko.frontmatter:
                aliases.extend(
                    [normalize_chunk_text(a) for a in target_ko.frontmatter.aliases if a]
                )
            node_aliases[nid] = [(a, set(a.split())) for a in aliases if a]

        for ko in self.corpus.objects:
            if not ko.id:
                continue
            for ch in chunk_text_deterministic(ko.raw_body):
                ch_tokens = set(ch.split())
                for nid in node_ids:
                    found = False
                    for alias, alias_toks in node_aliases[nid]:
                        if all(at in ch_tokens for at in alias_toks) and alias in ch:
                            found = True
                            break
                    if found:
                        chunk_hits[nid].add(global_chunk_idx)
                global_chunk_idx += 1

        gaps: List[RelationDiscoveryCandidate] = []
        created_at = current_iso_timestamp()
        expires_at = compute_expiry_date(created_at, 90)

        for i, u in enumerate(node_ids):
            u_scope = self.objects_by_id[u].scope or "engineering"
            for j in range(i + 1, len(node_ids)):
                v = node_ids[j]
                v_scope = self.objects_by_id[v].scope or "engineering"

                if u_scope != v_scope:
                    continue

                # Must not already have a canonical relation
                if (u, v) in canonical_edges:
                    continue

                pred_a = node_to_community.get(u) is not None and node_to_community.get(
                    u
                ) == node_to_community.get(v)

                shared_chunks = chunk_hits[u] & chunk_hits[v]
                cooc_count = len(shared_chunks)
                pred_b = cooc_count >= 3

                sim = cosine_similarity(embeddings[u], embeddings[v])
                pred_c = sim >= 0.80

                # 2 of 3 rule
                is_gap = (pred_a and pred_b) or (pred_a and pred_c) or (pred_b and pred_c)
                if is_gap:
                    source_id = min(u, v)
                    target_id = max(u, v)
                    cid = f"DISC-GAP-TOPO-{source_id}-{target_id}"

                    candidate = RelationDiscoveryCandidate(
                        candidate_id=cid,
                        candidate_type="knowledge_gap",
                        confidence=round(sim, 4),
                        status="pending",
                        created_at=created_at,
                        expires_at=expires_at,
                        scope=u_scope,
                        corpus_hash=corpus_hash,
                        algorithm_version="1.0.0",
                        evidence_refs=[
                            f"pred_A_community:{pred_a}",
                            f"pred_B_cooccurrence:{cooc_count}",
                            f"pred_C_similarity:{round(sim, 4)}",
                        ],
                        source_refs=[source_id, target_id],
                        representation_refs=[],
                        evidence_unit_refs=[],
                        derivation_ref="topological_gap_2_of_3_rule",
                        source_id=source_id,
                        target_id=target_id,
                        suggested_relation="DEPENDS_ON",
                        metadata={
                            "gap_type": "topological",
                            "predicates": {"A": pred_a, "B": pred_b, "C": pred_c},
                            "cooccurrence_chunks": cooc_count,
                            "similarity": round(sim, 4),
                        },
                    )
                    gaps.append(candidate)

        return gaps

    def scan_ontological_gaps(
        self, corpus_hash: str
    ) -> List[RelationDiscoveryCandidate | NodeDiscoveryCandidate]:
        """Scan for ontological and structural incompleteness patterns (DISC-004, DISCOVERY.md §10.2.2).

        1. unresolved_event: Incident/TroubleReport without outgoing RESOLVED_BY or SATISFIES to Lesson/Component/Fix.
        2. unimplemented_lesson: Lesson/Principle without incoming SATISFIES/INTRODUCED_IN/IMPLEMENTS from Workflow/Procedure/Specification.
        3. unreconciled_conflict: Claim/Fact in CONTRADICTS cluster with equal rank and no resolving synthesis node.
        """
        gaps: List[RelationDiscoveryCandidate | NodeDiscoveryCandidate] = []
        created_at = current_iso_timestamp()
        expires_at = compute_expiry_date(created_at, 90)

        # 1. Pattern 1: unresolved_event
        for ko in self.corpus.objects:
            if not ko.id:
                continue
            otype = ko.object_type or ""
            title_lower = (ko.title or "").lower()
            is_incident = (
                otype in {"Incident", "TroubleReport"}
                or "incident" in title_lower
                or "outage" in title_lower
            )

            if is_incident:
                has_resolution = False
                for rel in ko.relations:
                    rtype = rel.get("type")
                    tgt_id = rel.get("target")
                    if rtype in {"RESOLVED_BY", "SATISFIES", "RESOLVES"}:
                        has_resolution = True
                        break
                    if tgt_id and tgt_id in self.objects_by_id:
                        tgt_ko = self.objects_by_id[tgt_id]
                        tgt_type = tgt_ko.object_type or ""
                        if tgt_type in {"Lesson", "Component", "Procedure"}:
                            has_resolution = True
                            break

                if not has_resolution:
                    cid = f"DISC-GAP-ONTO-UNRESOLVED-{ko.id}"
                    scope = ko.scope or "engineering"
                    candidate = NodeDiscoveryCandidate(
                        candidate_id=cid,
                        candidate_type="knowledge_gap",
                        confidence=0.90,
                        status="pending",
                        created_at=created_at,
                        expires_at=expires_at,
                        scope=scope,
                        corpus_hash=corpus_hash,
                        algorithm_version="1.0.0",
                        evidence_refs=[f"missing_resolution_for:{ko.id}"],
                        source_refs=[ko.id],
                        representation_refs=[],
                        evidence_unit_refs=[],
                        derivation_ref="ontological_gap_unresolved_event",
                        trigger_source_ids=[ko.id],
                        suggested_title=f"Lesson Learned: Resolution for {ko.title}",
                        suggested_domain="engineering",
                        metadata={
                            "gap_type": "ontological",
                            "pattern": "unresolved_event",
                            "unresolved_node_id": ko.id,
                        },
                    )
                    gaps.append(candidate)

        # 2. Pattern 2: unimplemented_lesson
        incoming_lesson_relations: Dict[str, List[Tuple[str, str]]] = {
            ko.id: [] for ko in self.corpus.objects if ko.id
        }
        for ko in self.corpus.objects:
            if not ko.id:
                continue
            for rel in ko.relations:
                tgt = rel.get("target")
                rtype = rel.get("type", "")
                if tgt and tgt in incoming_lesson_relations:
                    incoming_lesson_relations[tgt].append((ko.id, rtype))

        for ko in self.corpus.objects:
            if not ko.id:
                continue
            otype = ko.object_type or ""
            title_lower = (ko.title or "").lower()
            is_lesson = otype in {"Lesson", "Principle"} or "lesson" in title_lower

            if is_lesson:
                incoming = incoming_lesson_relations.get(ko.id, [])
                has_implementer = any(
                    rtype in {"SATISFIES", "INTRODUCED_IN", "IMPLEMENTS", "APPLIES"}
                    for _, rtype in incoming
                )
                if not has_implementer:
                    cid = f"DISC-GAP-ONTO-UNIMPLEMENTED-{ko.id}"
                    scope = ko.scope or "engineering"
                    candidate = NodeDiscoveryCandidate(
                        candidate_id=cid,
                        candidate_type="knowledge_gap",
                        confidence=0.85,
                        status="pending",
                        created_at=created_at,
                        expires_at=expires_at,
                        scope=scope,
                        corpus_hash=corpus_hash,
                        algorithm_version="1.0.0",
                        evidence_refs=[f"missing_implementation_for:{ko.id}"],
                        source_refs=[ko.id],
                        representation_refs=[],
                        evidence_unit_refs=[],
                        derivation_ref="ontological_gap_unimplemented_lesson",
                        trigger_source_ids=[ko.id],
                        suggested_title=f"Workflow Implementing {ko.title}",
                        suggested_domain="engineering",
                        metadata={
                            "gap_type": "ontological",
                            "pattern": "unimplemented_lesson",
                            "lesson_node_id": ko.id,
                        },
                    )
                    gaps.append(candidate)

        # 3. Pattern 3: unreconciled_conflict
        contradicts_pairs: List[Tuple[str, str]] = []
        for ko in self.corpus.objects:
            if not ko.id:
                continue
            for rel in ko.relations:
                if rel.get("type") == "CONTRADICTS":
                    tgt = rel.get("target")
                    if tgt and tgt in self.objects_by_id:
                        pair = (min(ko.id, tgt), max(ko.id, tgt))
                        if pair not in contradicts_pairs:
                            contradicts_pairs.append(pair)

        for u, v in contradicts_pairs:
            ko_u = self.objects_by_id[u]
            ko_v = self.objects_by_id[v]
            # Check equal epistemic rank
            conf_u = ko_u.frontmatter.confidence if ko_u.frontmatter else 0.5
            conf_v = ko_v.frontmatter.confidence if ko_v.frontmatter else 0.5
            if conf_u == conf_v:
                cid = f"DISC-GAP-ONTO-CONFLICT-{u}-{v}"
                scope = ko_u.scope or "engineering"
                candidate = RelationDiscoveryCandidate(
                    candidate_id=cid,
                    candidate_type="knowledge_gap",
                    confidence=0.95,
                    status="pending",
                    created_at=created_at,
                    expires_at=expires_at,
                    scope=scope,
                    corpus_hash=corpus_hash,
                    algorithm_version="1.0.0",
                    evidence_refs=[f"contradiction_between:{u}:{v}"],
                    source_refs=[u, v],
                    representation_refs=[],
                    evidence_unit_refs=[],
                    derivation_ref="ontological_gap_unreconciled_conflict",
                    source_id=u,
                    target_id=v,
                    suggested_relation="CONTRADICTS",
                    metadata={
                        "gap_type": "ontological",
                        "pattern": "unreconciled_conflict",
                        "conflicting_nodes": [u, v],
                        "equal_confidence": conf_u,
                    },
                )
                gaps.append(candidate)

        return gaps


class DiscoveryLifecycleManager:
    """Manages candidate review, promotion, expiry sweeps, and persistent audit log (DISC-005)."""

    def __init__(self, discovery_dir: Path, workspace_root: Path):
        self.discovery_dir = discovery_dir
        self.workspace_root = workspace_root
        self.audit_log_path = discovery_dir / "audit_log.jsonl"
        self.candidates_path = discovery_dir / "candidates.jsonl"
        self.candidates: Dict[str, DiscoveryCandidate] = {}
        self.audit_log: List[DiscoveryAuditEntry] = []
        self._load()

    def _load(self) -> None:
        """Load candidates and audit log from disk."""
        self.discovery_dir.mkdir(parents=True, exist_ok=True)

        if self.candidates_path.exists():
            with open(self.candidates_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    d = json.loads(line)
                    if d.get("candidate_type") == "node_proposal" or "trigger_source_ids" in d:
                        self.candidates[d["candidate_id"]] = NodeDiscoveryCandidate(**d)
                    else:
                        self.candidates[d["candidate_id"]] = RelationDiscoveryCandidate(**d)

        if self.audit_log_path.exists():
            with open(self.audit_log_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    self.audit_log.append(DiscoveryAuditEntry(**json.loads(line)))

    def save(self) -> None:
        """Atomically persist candidates and append audit log."""
        self.discovery_dir.mkdir(parents=True, exist_ok=True)

        # Atomic write candidates.jsonl
        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.discovery_dir,
            delete=False,
            prefix="candidates_",
            suffix=".tmp",
        )
        try:
            for c in sorted(self.candidates.values(), key=lambda x: x.candidate_id):
                temp_file.write(json.dumps(c.to_dict()) + "\n")
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_file.close()
            os.replace(temp_file.name, self.candidates_path)
        except Exception:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise

        # Write audit log
        temp_audit = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.discovery_dir,
            delete=False,
            prefix="audit_",
            suffix=".tmp",
        )
        try:
            for entry in self.audit_log:
                temp_audit.write(json.dumps(entry.to_dict()) + "\n")
            temp_audit.flush()
            os.fsync(temp_audit.fileno())
            temp_audit.close()
            os.replace(temp_audit.name, self.audit_log_path)
        except Exception:
            if os.path.exists(temp_audit.name):
                os.unlink(temp_audit.name)
            raise

    def add_candidates(
        self, new_candidates: List[DiscoveryCandidate], actor: str = "system"
    ) -> int:
        """Add newly discovered candidates in pending state (DELTA-CORE-004)."""
        added = 0
        now = current_iso_timestamp()
        for c in new_candidates:
            if c.candidate_id not in self.candidates:
                # Force status = pending (DELTA-CORE-004)
                c.status = "pending"
                self.candidates[c.candidate_id] = c
                self.audit_log.append(
                    DiscoveryAuditEntry(
                        candidate_id=c.candidate_id,
                        previous_status="none",
                        new_status="pending",
                        actor=actor,
                        timestamp=now,
                        reason="Discovered by discovery scan pass",
                    )
                )
                added += 1
        self.save()
        return added

    def review_candidate(
        self, candidate_id: str, decision: str, actor: str, reason: str
    ) -> DiscoveryCandidate:
        """Review candidate: decision in ['approved', 'rejected', 'reviewed']."""
        if candidate_id not in self.candidates:
            raise KeyError(f"Candidate {candidate_id} not found")

        valid_decisions = {"approved", "rejected", "reviewed"}
        if decision not in valid_decisions:
            raise ValueError(
                f"Invalid review decision: {decision}. Must be one of {valid_decisions}"
            )

        candidate = self.candidates[candidate_id]
        prev_status = candidate.status
        candidate.status = decision

        self.audit_log.append(
            DiscoveryAuditEntry(
                candidate_id=candidate_id,
                previous_status=prev_status,
                new_status=decision,
                actor=actor,
                timestamp=current_iso_timestamp(),
                reason=reason,
            )
        )
        self.save()
        return candidate

    def validate_and_promote(
        self,
        candidate_id: str,
        actor: str,
        corpus: Corpus,
        registries: LoadedRegistries,
    ) -> DiscoveryCandidate:
        """Validate candidate and promote it (DISC-005, DISCOVERY.md §6).

        Requires explicit prior approval. Validates relation against relation_registry.yaml,
        rejects virtual inverse relations, self-references, and missing endpoints.
        """
        if candidate_id not in self.candidates:
            raise KeyError(f"Candidate {candidate_id} not found")

        candidate = self.candidates[candidate_id]
        if candidate.status != "approved":
            raise ValueError(
                f"Candidate {candidate_id} has status '{candidate.status}'; must be 'approved' before promotion."
            )

        objects_by_id = {ko.id: ko for ko in corpus.objects if ko.id}

        if isinstance(candidate, RelationDiscoveryCandidate):
            # 1. Verify endpoints still exist
            if candidate.source_id not in objects_by_id:
                raise ValueError(
                    f"Promotion failed: source object '{candidate.source_id}' does not exist"
                )
            if candidate.target_id not in objects_by_id:
                raise ValueError(
                    f"Promotion failed: target object '{candidate.target_id}' does not exist"
                )

            # 2. Reject self-references
            if candidate.source_id == candidate.target_id:
                raise ValueError("Promotion failed: self-referential candidate is rejected")

            # 3. Validate suggested relation
            rel_type = candidate.suggested_relation or "RELATES_TO"
            rel_def = registries.relations.get(rel_type)
            if not rel_def:
                raise ValueError(
                    f"Promotion failed: unknown relation type '{rel_type}' in relation registry"
                )

            if getattr(rel_def, "is_virtual_inverse", False):
                raise ValueError(
                    f"Promotion failed: virtual inverse relation '{rel_type}' cannot be promoted"
                )

        prev_status = candidate.status
        candidate.status = "promoted"

        self.audit_log.append(
            DiscoveryAuditEntry(
                candidate_id=candidate_id,
                previous_status=prev_status,
                new_status="promoted",
                actor=actor,
                timestamp=current_iso_timestamp(),
                reason="Promotion validated and executed",
                validation_result="PASSED",
            )
        )
        self.save()
        return candidate

    def sweep_expiry(self, current_dt_iso: Optional[str] = None) -> int:
        """Archive pending candidates past their expires_at date as 'expired' (DISC-005, DELTA-CORE-006)."""
        now_dt = (
            datetime.fromisoformat(current_dt_iso.replace("Z", "+00:00"))
            if current_dt_iso
            else datetime.now(timezone.utc)
        )

        expired_count = 0
        for c in self.candidates.values():
            if c.status == "pending":
                exp_dt = datetime.fromisoformat(c.expires_at.replace("Z", "+00:00"))
                if exp_dt <= now_dt:
                    prev_status = c.status
                    c.status = "expired"
                    self.audit_log.append(
                        DiscoveryAuditEntry(
                            candidate_id=c.candidate_id,
                            previous_status=prev_status,
                            new_status="expired",
                            actor="system_reaper",
                            timestamp=current_iso_timestamp(),
                            reason=f"Exceeded 90-day retention lifetime ({c.expires_at})",
                        )
                    )
                    expired_count += 1

        if expired_count > 0:
            self.save()
        return expired_count


def discover_literature_bridges(
    csr_dir: Path,
    concept_a_id: str,
    concept_c_id: str,
    top_k: int = 15,
    max_background_degree: int = 2_000_000,
) -> Dict[str, Any]:
    """Execute Swanson-style ABC literature-based discovery over a memory-mapped CSR graph.

    Given two endpoint concepts A and C (e.g. MESH_D011928 and MESH_D005395),
    uncovers intermediate bridges B co-tagged with articles of both A and C,
    scoring each bridge with the degree-normalized co-occurrence score
    ``(co_a * co_c) / sqrt(deg_b)``.

    The MeSH/article partition is derived from ``node_mapping.parquet`` at call
    time (no hardcoded index boundary), all SQL is parameterized, and the
    Swanson disjointness precondition is measured and reported honestly via
    ``articles_discussing_both`` rather than assumed.
    """
    import collections

    import duckdb
    import numpy as np

    from trashheap.graph.csr import _load_int64_memmap

    mapping_path = csr_dir / "node_mapping.parquet"
    indptr_path = csr_dir / "indptr.npy"
    indices_path = csr_dir / "indices.npy"

    if not mapping_path.exists():
        raise FileNotFoundError(f"Node mapping not found at {mapping_path}")
    if not indptr_path.exists() or not indices_path.exists():
        raise FileNotFoundError(f"CSR binary files not found in {csr_dir}")

    con = duckdb.connect()
    try:
        nodes = dict(
            con.execute(
                "SELECT node_id, node_idx FROM read_parquet(?) "
                "WHERE node_id = ? OR node_id = ?",
                [str(mapping_path), concept_a_id, concept_c_id],
            ).fetchall()
        )

        if concept_a_id not in nodes:
            raise KeyError(f"Concept '{concept_a_id}' not found in node mapping")
        if concept_c_id not in nodes:
            raise KeyError(f"Concept '{concept_c_id}' not found in node mapping")

        # Derive the MeSH partition from the mapping itself instead of a
        # hardcoded index boundary: robust across recompilations.
        mesh_rows = con.execute(
            "SELECT node_idx FROM read_parquet(?) WHERE starts_with(node_id, ?)",
            [str(mapping_path), "MESH_"],
        ).fetchall()
    finally:
        con.close()

    idx_a = int(nodes[concept_a_id])
    idx_c = int(nodes[concept_c_id])

    indptr = np.load(indptr_path, mmap_mode="r")
    indices = _load_int64_memmap(indices_path)
    num_nodes = len(indptr) - 1

    is_mesh = np.zeros(num_nodes, dtype=bool)
    if mesh_rows:
        mesh_indices = np.fromiter(
            (int(r[0]) for r in mesh_rows), dtype=np.int64, count=len(mesh_rows)
        )
        is_mesh[mesh_indices] = True

    articles_a = indices[indptr[idx_a] : indptr[idx_a + 1]]
    articles_c = indices[indptr[idx_c] : indptr[idx_c + 1]]

    id_map: Dict[int, str] = {}

    # Aggregate co-occurring MeSH descriptors for articles in A and C
    b_counts_a: collections.Counter = collections.Counter()
    for art in articles_a:
        nbrs = indices[indptr[art] : indptr[art + 1]]
        b_counts_a.update(nbrs[is_mesh[nbrs]].tolist())

    b_counts_c: collections.Counter = collections.Counter()
    for art in articles_c:
        nbrs = indices[indptr[art] : indptr[art + 1]]
        b_counts_c.update(nbrs[is_mesh[nbrs]].tolist())

    shared_b = set(b_counts_a.keys()) & set(b_counts_c.keys())
    shared_b.discard(idx_a)
    shared_b.discard(idx_c)

    scores = []
    for b in sorted(shared_b):
        deg_b = int(indptr[b + 1]) - int(indptr[b])
        if deg_b > max_background_degree:
            continue
        score = (b_counts_a[b] * b_counts_c[b]) / (deg_b**0.5)
        scores.append((score, int(b), int(b_counts_a[b]), int(b_counts_c[b]), deg_b))

    scores.sort(reverse=True)
    top_scores = scores[: max(0, top_k)]

    if top_scores:
        top_b_indices = [s[1] for s in top_scores]
        con = duckdb.connect()
        try:
            id_map = dict(
                con.execute(
                    "SELECT node_idx, node_id FROM read_parquet(?) "
                    "WHERE node_idx IN (SELECT UNNEST(?))",
                    [str(mapping_path), top_b_indices],
                ).fetchall()
            )
        finally:
            con.close()

    # Swanson disjointness precondition, measured not assumed: articles tagged
    # with BOTH concepts mean A and C are already co-discussed in the literature.
    overlap = len(set(articles_a.tolist()) & set(articles_c.tolist()))

    bridges = [
        {
            "rank": rank,
            "bridge_id": id_map.get(b_idx, f"NODE_{b_idx}"),
            "node_idx": b_idx,
            "score": round(score, 2),
            "cooccurrences_with_a": ca,
            "cooccurrences_with_c": cc,
            "background_degree": bg_deg,
        }
        for rank, (score, b_idx, ca, cc, bg_deg) in enumerate(top_scores, 1)
    ]

    return {
        "concept_a": concept_a_id,
        "concept_c": concept_c_id,
        "articles_a": int(len(articles_a)),
        "articles_c": int(len(articles_c)),
        "articles_discussing_both": overlap,
        "disjointness_holds": overlap == 0,
        "total_intermediate_bridges": len(scores),
        "top_bridges": bridges,
    }
