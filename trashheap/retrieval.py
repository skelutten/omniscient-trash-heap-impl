"""Baseline hybrid retrieval engine (RETRIEVAL.md §9, RET-001..RET-005, D82, D93, D94).

Executes 8-step layered retrieval:
1. Query understanding
2. Pre-filter (scope, object_type, domain, facets, validity, status, min_confidence)
3. Initial seed retrieval (BM25 lexical + exact ID lookup -> top-k seeds)
4. Graph expansion (BFS with deterministic neighbor ordering §9.2, max_depth, max_neighbors)
5. Epistemic post-filter & N-way conflict resolution (§9.3)
6. Hybrid RRF fusion (§9.1)
7. Final scoring & tie-breaking (FinalScore DESC -> node_id ASC)
8. Self-describing evidence bundle construction matching examples/evidence_bundle.json
"""

import math
import re
from collections import deque
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from trashheap.corpus import Corpus
from trashheap.models import KnowledgeObject
from trashheap.registry.loader import LoadedRegistries
from trashheap.vector.protocol import Embedder
from trashheap.vector.store import VectorHit, VectorIndex

RETRIEVAL_VERSION = "1.0.0"
RANKING_POLICY_VERSION = "1.0.0"
RELATION_REGISTRY_VERSION = "3.8.10"

# Stage 1 & Stage 2 Refusal Reason Codes (specs/RETRIEVAL.md §9.6, RET-006..RET-008)
UNGROUNDED_DESCRIPTOR = "UNGROUNDED_DESCRIPTOR"
NO_ADMISSIBLE_PATH = "NO_ADMISSIBLE_PATH"
EMPTY_BODY_TERMINAL = "EMPTY_BODY_TERMINAL"
SUPERSEDED_EVIDENCE = "SUPERSEDED_EVIDENCE"
INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

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

DEFAULT_RETRIEVAL_PARAMS: Dict[str, Any] = {
    "seed_top_k": 10,
    "max_depth": 2,
    "max_neighbors_per_node": 25,
    "max_expanded_nodes": 200,
    "max_results": 20,
    "min_confidence": 0.0,
    "min_relevance": 0.0,
    "valid_at": None,
    "include_out_of_validity": False,
    "include_cross_scope": False,
    "include_drafts": False,
    "include_deprecated": False,
    "facet_match_mode": "any",
    "conflict_strategy": "epistemic_then_confidence",
    "enable_vector": False,
    "retrieval_mode": "canonical",
    "enforce_structural_gates": False,
}

CATEGORY_PRIORITY: Dict[str, int] = {
    "structural": 1,
    "dependency": 2,
    "engineering": 3,
    "evolution": 4,
    "derivation": 5,
    "verification": 6,
    "epistemic": 7,
    "procedural": 8,
    "documentation": 9,
    "semantic": 10,
}

EPISTEMIC_RANKS: Dict[str, Dict[str, int]] = {
    "verification": {
        "formal_proof": 4,
        "peer_verified": 3,
        "self_verified": 2,
        "unverified": 1,
        "falsified": 0,
    },
    "authority": {
        "normative": 4,
        "authoritative": 3,
        "informative": 2,
        "advisory": 1,
        "deprecated": 0,
    },
    "consensus": {
        "accepted": 2,
        "proposed": 1,
        "contested": 0,
    },
    "evidence": {
        "observed": 3,
        "derived": 2,
        "inferred": 1,
        "postulated": 0,
    },
}


def tokenize(text: str) -> List[str]:
    """Deterministic tokenization into lowercased words."""
    return [w.lower() for w in re.findall(r"\b[A-Za-z0-9_]+\b", text)]


class BM25Index:
    """Okapi BM25 index with k1=1.5 and b=0.75."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len: Dict[str, int] = {}
        self.doc_freq: Dict[str, int] = {}
        self.doc_term_freq: Dict[str, Dict[str, int]] = {}
        self.corpus_size = 0
        self.avg_doc_len = 0.0

    def index(self, objects: List[KnowledgeObject]) -> None:
        self.doc_len.clear()
        self.doc_freq.clear()
        self.doc_term_freq.clear()
        total_len = 0
        self.corpus_size = len(objects)
        if self.corpus_size == 0:
            return

        for ko in objects:
            if not ko.id:
                continue
            # Frontmatter stripped; title + aliases + keywords + raw body
            parts = [ko.title or "", ko.title or ""]
            if ko.frontmatter:
                parts.extend(ko.frontmatter.aliases)
                parts.extend(ko.frontmatter.keywords)
            parts.append(ko.raw_body)
            tokens = tokenize(" ".join(parts))
            length = len(tokens)
            self.doc_len[ko.id] = length
            total_len += length

            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_term_freq[ko.id] = tf

            for t in tf.keys():
                self.doc_freq[t] = self.doc_freq.get(t, 0) + 1

        self.avg_doc_len = total_len / self.corpus_size if self.corpus_size > 0 else 1.0

    def score(self, query: str) -> Dict[str, float]:
        query_tokens = tokenize(query)
        scores: Dict[str, float] = {}
        if not query_tokens or self.corpus_size == 0:
            return scores

        for token in query_tokens:
            if token not in self.doc_freq:
                continue
            df = self.doc_freq[token]
            idf = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)
            if idf < 0:
                idf = 0.0

            for doc_id, tf_map in self.doc_term_freq.items():
                if token not in tf_map:
                    continue
                tf = tf_map[token]
                doc_len = self.doc_len.get(doc_id, self.avg_doc_len)
                num = tf * (self.k1 + 1.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                term_score = idf * (num / denom)
                scores[doc_id] = scores.get(doc_id, 0.0) + term_score

        return scores


def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """Normalize raw scores to [0.0, 1.0] (THRESH-001)."""
    if not scores:
        return {}
    max_score = max(scores.values())
    if max_score <= 0.0:
        return {k: 0.0 for k in scores}
    return {k: round(v / max_score, 6) for k, v in scores.items()}


def extract_body_excerpt(raw_body: str, max_chars: int = 250) -> str:
    """Extract first meaningful sentence or non-heading paragraph."""
    lines = raw_body.splitlines()
    for line in lines:
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        if len(cleaned) > max_chars:
            return cleaned[:max_chars].rstrip() + "..."
        return cleaned
    return ""


def epistemic_conflict_key(ko: KnowledgeObject) -> Tuple[Any, ...]:
    """Evaluate formal conflict vector K(d) per RETRIEVAL.md §9.3."""
    fm = ko.frontmatter_dict
    v_str = fm.get("verification", "")
    a_str = fm.get("authority", "")
    c_str = fm.get("consensus", "")
    e_str = fm.get("evidence", "")

    v_val = EPISTEMIC_RANKS["verification"].get(v_str, 0)
    a_val = EPISTEMIC_RANKS["authority"].get(a_str, 0)
    c_val = EPISTEMIC_RANKS["consensus"].get(c_str, 0)
    e_val = EPISTEMIC_RANKS["evidence"].get(e_str, 0)

    conf = float(fm.get("confidence", 0.0))
    last_verified = str(fm.get("last_verified") or "")

    node_id = ko.id or ""
    # Lowest Node-ID wins last tie-breaker: tuple of negative ASCII values
    id_neg_ascii = tuple(-ord(ch) for ch in node_id)

    return (v_val, a_val, c_val, e_val, conf, last_verified, id_neg_ascii)


def prepare_scoring_window(
    text: str,
    title: Optional[str] = None,
    max_tokens: int = 512,
    chars_per_token: int = 4,
) -> str:
    """Prepare a section-aware scoring window defending against the Truncation Trap (RET-009).

    Rather than blindly slicing text[:max_tokens], this preserves document opening
    and explicitly extracts trailing conclusion/findings/summary sections.
    """
    max_chars = max_tokens * chars_per_token
    if len(text) <= max_chars:
        return text

    conclusion_patterns = [
        r"(?i)(##+\s*(conclusions?|findings?|discussion|summary).*)",
        r"(?i)(\n(conclusions?|findings?):\s*.*)",
    ]
    conclusion_match = None
    for pat in conclusion_patterns:
        m = re.search(pat, text)
        if m:
            conclusion_match = m
            break

    half_budget = max_chars // 2
    if conclusion_match:
        conc_start = conclusion_match.start()
        conc_text = text[conc_start:]
        if len(conc_text) > half_budget:
            conc_text = conc_text[:half_budget]
        opening_budget = max_chars - len(conc_text) - 10
        opening_text = text[:opening_budget].rstrip()
        return f"{opening_text}\n\n[...]\n\n{conc_text.lstrip()}"

    opening = text[:half_budget].rstrip()
    trailing = text[-half_budget:].lstrip()
    return f"{opening}\n\n[...]\n\n{trailing}"


def evaluate_stage_2_refusal(
    evidence_bundle: Dict[str, Any],
    claim_entailment_score: Optional[float] = None,
    calibrated_confidence: Optional[float] = None,
    min_entailment: float = 0.5,
    min_confidence: float = 0.65,
) -> Dict[str, Any]:
    """Evaluate Stage 2 propositional refusal gates (RET-007, specs/RETRIEVAL.md §9.6).

    A non-empty graph path certifies topological aboutness, NOT propositional truth.
    Stage 2 evaluates candidate claim entailment and calibrated model confidence.
    """
    if evidence_bundle.get("retrieval_status") == "REFUSED":
        return evidence_bundle.get("refusal") or {"stage": 1, "status": "REFUSED"}

    entailment_passed = True
    if claim_entailment_score is not None and claim_entailment_score < min_entailment:
        entailment_passed = False

    confidence_passed = True
    if calibrated_confidence is not None and calibrated_confidence < min_confidence:
        confidence_passed = False

    if not entailment_passed or not confidence_passed:
        return {
            "status": "REFUSED",
            "stage": 2,
            "type": "propositional",
            "reason": INSUFFICIENT_EVIDENCE,
            "message": "Passage evidence fails propositional entailment or calibrated confidence threshold",
            "gates": {
                "claim_entailment": {
                    "passed": entailment_passed,
                    "score": claim_entailment_score,
                    "threshold": min_entailment,
                },
                "calibrated_confidence": {
                    "passed": confidence_passed,
                    "confidence": calibrated_confidence,
                    "threshold": min_confidence,
                },
            },
        }

    return {
        "status": "ADMISSIBLE",
        "stage": 2,
        "gates": {
            "claim_entailment": {"passed": True, "score": claim_entailment_score},
            "calibrated_confidence": {"passed": True, "score": calibrated_confidence},
        },
    }


class HybridRetriever:
    """Hybrid RRF retriever for Knowledge Objects."""

    def __init__(
        self,
        corpus: Corpus,
        registries: LoadedRegistries,
        vector_index: Optional[VectorIndex] = None,
        embedder: Optional[Embedder] = None,
        workspace_root: Optional[Path] = None,
    ):
        self.corpus = corpus
        self.registries = registries
        self.vector_index = vector_index
        self.embedder = embedder
        self.workspace_root = workspace_root or Path(".")
        self.bm25_index = BM25Index(k1=1.5, b=0.75)
        self.bm25_index.index(self.corpus.objects)

        # Build fast relation lookup: node_id -> list of relation dicts
        self.relations_by_source: Dict[str, List[Dict[str, Any]]] = {}
        # Also build relation categories lookup from registry
        self.rel_categories: Dict[str, str] = {
            r_type: r.category for r_type, r in self.registries.relation_registry.relations.items()
        }

        for ko in self.corpus.objects:
            if not ko.id:
                continue
            rels = ko.frontmatter_dict.get("relations", [])
            if isinstance(rels, list):
                self.relations_by_source[ko.id] = [r for r in rels if isinstance(r, dict)]

        # Lazy CSR graph projection
        self._csr_projection: Optional[Any] = None

        # Build vocabulary for Stage 1 ontology grounding gate (RET-006)
        self.ontology_terms: Set[str] = set()
        for ko in self.corpus.objects:
            if ko.id:
                self.ontology_terms.add(ko.id.lower())
            if ko.title:
                for token in tokenize(ko.title):
                    if token not in STOPWORDS and len(token) > 2:
                        self.ontology_terms.add(token)
            if ko.frontmatter:
                for kw in ko.frontmatter.keywords:
                    for token in tokenize(kw):
                        if token not in STOPWORDS and len(token) > 2:
                            self.ontology_terms.add(token)
                for alias in ko.frontmatter.aliases:
                    for token in tokenize(alias):
                        if token not in STOPWORDS and len(token) > 2:
                            self.ontology_terms.add(token)
                if ko.frontmatter.taxonomy_path:
                    for part in ko.frontmatter.taxonomy_path.split("/"):
                        for token in tokenize(part):
                            if token not in STOPWORDS and len(token) > 2:
                                self.ontology_terms.add(token)

        if hasattr(self.registries, "taxonomy_registry") and self.registries.taxonomy_registry:
            for term in getattr(self.registries.taxonomy_registry, "taxonomies", {}).keys():
                for token in tokenize(str(term)):
                    if token not in STOPWORDS and len(token) > 2:
                        self.ontology_terms.add(token)

    @property
    def csr(self):
        if self._csr_projection is None:
            from trashheap.graph.csr import CsrGraphProjection

            self._csr_projection = CsrGraphProjection.build_from_corpus(self.corpus, directed=False)
        return self._csr_projection

    def retrieve(
        self,
        query: str,
        cli_params: Optional[Dict[str, Any]] = None,
        config_params: Optional[Dict[str, Any]] = None,
        vector_index: Optional[VectorIndex] = None,
        embedder: Optional[Embedder] = None,
    ) -> Dict[str, Any]:
        """Execute hybrid search pipeline with D94 per-parameter precedence."""
        cli_params = cli_params or {}
        config_params = config_params or {}
        v_index = vector_index if vector_index is not None else self.vector_index
        v_embedder = embedder if embedder is not None else self.embedder

        # 1. Parameter Resolution & Origin Tracking (D94)
        parameters_used: Dict[str, Any] = {}
        parameters_origin: Dict[str, str] = {}

        all_param_keys = (
            set(DEFAULT_RETRIEVAL_PARAMS.keys())
            | set(config_params.keys())
            | set(cli_params.keys())
        )
        for key in all_param_keys:
            if key in cli_params and cli_params[key] is not None:
                parameters_used[key] = cli_params[key]
                parameters_origin[key] = "cli"
            elif key in config_params and config_params[key] is not None:
                parameters_used[key] = config_params[key]
                parameters_origin[key] = "config"
            elif key in DEFAULT_RETRIEVAL_PARAMS:
                parameters_used[key] = DEFAULT_RETRIEVAL_PARAMS[key]
                parameters_origin[key] = "default"

        # If vector_index and embedder are explicitly provided and enable_vector not in CLI/config, default to True
        if v_index is not None and v_embedder is not None:
            if "enable_vector" not in cli_params and "enable_vector" not in config_params:
                parameters_used["enable_vector"] = True
                parameters_origin["enable_vector"] = "default"

        enable_vector = bool(parameters_used.get("enable_vector", False))
        retrieval_mode = str(parameters_used.get("retrieval_mode", "canonical"))

        scope_filter = parameters_used.get("scope")
        object_type_filter = parameters_used.get("object_type")
        domain_filter = parameters_used.get("domain")
        facet_filter = parameters_used.get("facet_filter", {})
        facet_match_mode = parameters_used.get("facet_match_mode", "any")
        valid_at_str = parameters_used.get("valid_at")
        include_out_of_validity = parameters_used.get("include_out_of_validity", False)
        include_drafts = parameters_used.get("include_drafts", False)
        include_deprecated = parameters_used.get("include_deprecated", False)
        min_confidence = float(parameters_used.get("min_confidence", 0.0))
        min_relevance = float(parameters_used.get("min_relevance", 0.0))
        seed_top_k = int(parameters_used.get("seed_top_k", 10))
        max_depth = int(parameters_used.get("max_depth", 2))
        max_neighbors_per_node = int(parameters_used.get("max_neighbors_per_node", 25))
        max_expanded_nodes = int(parameters_used.get("max_expanded_nodes", 200))
        max_results = int(parameters_used.get("max_results", 20))

        # 2. Scope, Facet & Validity Pre-filter
        valid_at_date: Optional[date] = None
        if valid_at_str:
            try:
                valid_at_date = date.fromisoformat(valid_at_str)
            except ValueError:
                pass

        eligible_objects: Dict[str, KnowledgeObject] = {}
        for ko in self.corpus.objects:
            if not ko.id:
                continue
            fm = ko.frontmatter_dict

            # Scope
            if scope_filter and ko.scope != scope_filter:
                continue
            # Object type
            if object_type_filter:
                if isinstance(object_type_filter, list):
                    if ko.object_type not in object_type_filter:
                        continue
                elif ko.object_type != object_type_filter:
                    continue
            # Domain
            if domain_filter and ko.domain != domain_filter:
                continue
            # Status
            status = fm.get("status", "")
            if status == "draft" and not include_drafts:
                continue
            if status == "deprecated" and not include_deprecated:
                continue
            # Confidence
            conf = float(fm.get("confidence", 0.0))
            if conf < min_confidence:
                continue
            # Validity
            if valid_at_date and not include_out_of_validity:
                val = fm.get("validity")
                if isinstance(val, dict):
                    v_from = val.get("valid_from")
                    v_until = val.get("valid_until")
                    if v_from:
                        try:
                            d_from = date.fromisoformat(str(v_from))
                            if valid_at_date < d_from:
                                continue
                        except ValueError:
                            pass
                    if v_until:
                        try:
                            d_until = date.fromisoformat(str(v_until))
                            if valid_at_date > d_until:
                                continue
                        except ValueError:
                            pass
            # Facet filter
            if facet_filter:
                match_results = []
                for f_key, expected_vals in facet_filter.items():
                    if not isinstance(expected_vals, list):
                        expected_vals = [expected_vals]
                    act_val = fm.get(f_key)
                    if isinstance(act_val, list):
                        matched = bool(set(act_val) & set(expected_vals))
                    else:
                        matched = act_val in expected_vals
                    match_results.append(matched)

                if facet_match_mode == "all" and not all(match_results):
                    continue
                if facet_match_mode == "any" and not any(match_results):
                    continue

            eligible_objects[ko.id] = ko

        # Modality check: Honest Modality Rule (D79) and Degraded Fallback (D84)
        vector_active = False
        if enable_vector and v_index is not None and v_embedder is not None:
            if not v_embedder.identity.is_double:
                vector_active = True

        # 3. Initial Seed Retrieval (BM25 + direct ID lookup + Vector)
        raw_bm25_scores = self.bm25_index.score(query)
        # Filter to eligible objects
        bm25_scores = {
            nid: score for nid, score in raw_bm25_scores.items() if nid in eligible_objects
        }
        norm_bm25_scores = normalize_scores(bm25_scores)

        # Direct node ID query boost
        exact_id_hits = [nid for nid in eligible_objects if nid.lower() in query.lower()]
        for eh in exact_id_hits:
            norm_bm25_scores[eh] = 1.0

        # Sort candidate seeds deterministically: score DESC, node_id ASC
        sorted_seeds = sorted(norm_bm25_scores.keys(), key=lambda x: (-norm_bm25_scores[x], x))
        seed_nodes = sorted_seeds[:seed_top_k]

        vector_hits_dict: Dict[str, VectorHit] = {}
        if vector_active and v_index is not None and v_embedder is not None:
            # Score eligible objects (Governance pre-filter D81)
            raw_v_hits = v_index.score_query(
                query=query,
                embedder=v_embedder,
                candidate_ids=set(eligible_objects.keys()),
                top_k=None,
            )
            for h in raw_v_hits:
                if h.score > 0.0:  # 0.0 sign-convention floor (D81)
                    vector_hits_dict[h.node_id] = h

            sorted_v_seeds = [
                h.node_id
                for h in sorted(vector_hits_dict.values(), key=lambda x: (-x.score, x.node_id))
            ][:seed_top_k]

            combined_seeds = list(seed_nodes)
            for vs in sorted_v_seeds:
                if vs not in combined_seeds:
                    combined_seeds.append(vs)
            seed_nodes = combined_seeds

        # 4. Graph Expansion (BFS §9.2)
        visited_depth: Dict[str, int] = {}
        for s in seed_nodes:
            visited_depth[s] = 0

        queue: deque[Tuple[str, int]] = deque([(s, 0) for s in seed_nodes])
        graph_consulted = max_depth > 0
        graph_reached = False

        if graph_consulted and seed_nodes:
            while queue and len(visited_depth) < max_expanded_nodes:
                curr_node, curr_depth = queue.popleft()
                if curr_depth >= max_depth:
                    continue

                raw_neighbors = self.relations_by_source.get(curr_node, [])

                # Deterministic selection rule (§9.2):
                # key(r) = (priority(category(r)), type(r), target(r))
                def neighbor_key(r: Dict[str, Any]) -> Tuple[int, str, str]:
                    rtype = r.get("type", "")
                    cat = self.rel_categories.get(rtype, "semantic")
                    prio = CATEGORY_PRIORITY.get(cat, 99)
                    return (prio, rtype, r.get("target", ""))

                sorted_neighbors = sorted(raw_neighbors, key=neighbor_key)
                selected_neighbors = sorted_neighbors[:max_neighbors_per_node]

                for r in selected_neighbors:
                    target = r.get("target")
                    if not target or target not in eligible_objects:
                        continue
                    if target not in visited_depth:
                        visited_depth[target] = curr_depth + 1
                        graph_reached = True
                        queue.append((target, curr_depth + 1))
                        if len(visited_depth) >= max_expanded_nodes:
                            break

        # Compute graph raw scores
        graph_raw_scores: Dict[str, float] = {}
        graph_features_map: Dict[str, Dict[str, float]] = {}
        if retrieval_mode == "graph_enhanced":
            from trashheap.graph.analysis import GraphAnalyzer
            from trashheap.graph.retrieval import GraphFeatureScorer

            analyzer = GraphAnalyzer(self.corpus, self.workspace_root)
            scorer = GraphFeatureScorer(analyzer)
            for nid in visited_depth.keys():
                score, feat_breakdown = scorer.score_candidate(nid, seed_nodes)
                graph_raw_scores[nid] = score
                graph_features_map[nid] = feat_breakdown
        else:
            for nid, depth in visited_depth.items():
                graph_raw_scores[nid] = 1.0 / (1.0 + depth)

        norm_graph_scores = normalize_scores(graph_raw_scores)

        # 5. Modalities derivation (D82, D93)
        modalities_available: List[str] = ["bm25"]
        modalities_absent: List[str] = []

        if max_depth == 0:
            modalities_absent.append("graph")
        else:
            modalities_available.append("graph")

        if vector_active:
            modalities_available.append("vector")
        else:
            modalities_absent.append("vector")

        # 6. Hybrid RRF Fusion (§9.1)
        # Candidates set = seeds + bm25 hits + vector hits + graph expansion
        all_candidate_ids: Set[str] = set(seed_nodes) | set(norm_bm25_scores.keys())
        if vector_active:
            all_candidate_ids.update(vector_hits_dict.keys())
        if graph_reached:
            all_candidate_ids.update(visited_depth.keys())

        # Build rankings
        # BM25 rank (1-indexed)
        sorted_bm25 = sorted(
            [
                nid
                for nid in all_candidate_ids
                if nid in norm_bm25_scores and norm_bm25_scores[nid] > 0
            ],
            key=lambda x: (-norm_bm25_scores[x], x),
        )
        bm25_ranks = {nid: idx + 1 for idx, nid in enumerate(sorted_bm25)}

        # Vector rank (1-indexed) — only if vector_active (D81)
        vector_ranks: Dict[str, int] = {}
        if vector_active and vector_hits_dict:
            sorted_vector = sorted(
                [
                    nid
                    for nid in all_candidate_ids
                    if nid in vector_hits_dict and vector_hits_dict[nid].score > 0
                ],
                key=lambda x: (-vector_hits_dict[x].score, x),
            )
            vector_ranks = {nid: idx + 1 for idx, nid in enumerate(sorted_vector)}

        # Graph rank (1-indexed) — only participates if graph_reached is True (D93)
        graph_ranks: Dict[str, int] = {}
        if graph_reached:
            sorted_graph = sorted(
                [nid for nid in all_candidate_ids if nid in visited_depth],
                key=lambda x: (-norm_graph_scores[x], x),
            )
            graph_ranks = {nid: idx + 1 for idx, nid in enumerate(sorted_graph)}

        # Weights and parameters
        k_rrf = 60
        w_bm25 = 0.4
        w_vector = 0.4
        w_graph = 0.2

        rrf_scores: Dict[str, float] = {}
        matched_by_map: Dict[str, List[str]] = {}
        signals_map: Dict[str, Dict[str, Any]] = {}

        for nid in all_candidate_ids:
            score_rrf = 0.0
            matched = []
            signals: Dict[str, Any] = {"bm25": None, "vector": None, "graph": None}

            # BM25 modality
            if nid in bm25_ranks:
                rank = bm25_ranks[nid]
                contrib = round(w_bm25 / (k_rrf + rank), 7)
                score_rrf += contrib
                matched.append("bm25")
                signals["bm25"] = {
                    "raw_score": norm_bm25_scores[nid],
                    "rank": rank,
                    "rrf_contribution": contrib,
                }

            # Vector modality (D81, D82)
            if vector_active and nid in vector_ranks:
                rank = vector_ranks[nid]
                v_hit = vector_hits_dict[nid]
                contrib = round(w_vector / (k_rrf + rank), 7)
                score_rrf += contrib
                matched.append("vector")
                signals["vector"] = {
                    "raw_score": round(v_hit.score, 6),
                    "rank": rank,
                    "rrf_contribution": contrib,
                    "chunk_index": v_hit.chunk_index,
                }

            # Graph modality (only if graph_reached per D93)
            if graph_reached and nid in graph_ranks:
                rank = graph_ranks[nid]
                contrib = round(w_graph / (k_rrf + rank), 7)
                score_rrf += contrib
                matched.append("graph")
                sig = {
                    "raw_score": norm_graph_scores[nid],
                    "rank": rank,
                    "rrf_contribution": contrib,
                }
                if retrieval_mode == "graph_enhanced" and nid in graph_features_map:
                    sig["features"] = graph_features_map[nid]
                signals["graph"] = sig

            rrf_scores[nid] = round(score_rrf, 7)
            matched_by_map[nid] = matched
            signals_map[nid] = signals

        # Sort candidates: FinalScore DESC -> node_id ASC
        sorted_candidates = sorted(all_candidate_ids, key=lambda x: (-rrf_scores[x], x))

        candidate_count = len(sorted_candidates)

        # 7. N-Way Conflict Resolution (§9.3)
        # Detect mutual CONTRADICTS relations among candidates
        contradicts_adj: Dict[str, Set[str]] = {nid: set() for nid in sorted_candidates}
        for nid in sorted_candidates:
            rels = self.relations_by_source.get(nid, [])
            for r in rels:
                if r.get("type") == "CONTRADICTS":
                    target = r.get("target")
                    if target in contradicts_adj:
                        contradicts_adj[nid].add(target)
                        contradicts_adj[target].add(nid)

        # Form connected components
        visited_clusters: Set[str] = set()
        suppressed_nodes_list: List[Dict[str, Any]] = []
        winner_conflict_info: Dict[str, Dict[str, Any]] = {}
        nodes_to_suppress: Set[str] = set()

        for nid in sorted_candidates:
            if nid in visited_clusters or not contradicts_adj[nid]:
                continue
            # BFS to find component
            cluster: List[str] = []
            c_queue = deque([nid])
            visited_clusters.add(nid)
            while c_queue:
                curr = c_queue.popleft()
                cluster.append(curr)
                for neighbor in contradicts_adj[curr]:
                    if neighbor not in visited_clusters:
                        visited_clusters.add(neighbor)
                        c_queue.append(neighbor)

            if len(cluster) >= 2:
                # Rank cluster nodes using formal vector key K(d)
                winner_id = max(cluster, key=lambda x: epistemic_conflict_key(eligible_objects[x]))
                losers = [x for x in cluster if x != winner_id]

                winner_conflict_info[winner_id] = {
                    "detected": True,
                    "conflicting_node_id": losers[0],
                    "conflicting_relation_type": "CONTRADICTS",
                    "conflict_resolution": "epistemic_then_confidence",
                }

                for loser_id in losers:
                    nodes_to_suppress.add(loser_id)
                    loser_obj = eligible_objects[loser_id]
                    loser_fm = loser_obj.frontmatter_dict
                    refs = loser_fm.get("source_refs", [])
                    ref = refs[0] if refs else None
                    suppressed_nodes_list.append(
                        {
                            "node_id": loser_id,
                            "reason": "conflict_lower_epistemic_rank",
                            "conflicting_node_id": winner_id,
                            "epistemology": {
                                "evidence": loser_fm.get("evidence"),
                                "verification": loser_fm.get("verification"),
                                "authority": loser_fm.get("authority"),
                                "consensus": loser_fm.get("consensus"),
                            },
                            "provenance": {
                                "source_type": loser_fm.get("source_type"),
                                "source_ref": ref,
                                "confidence": loser_fm.get("confidence"),
                                "last_verified": str(loser_fm.get("last_verified"))
                                if loser_fm.get("last_verified")
                                else None,
                            },
                        }
                    )

        # Filter out suppressed nodes & min_relevance
        surviving_candidates: List[str] = []
        for nid in sorted_candidates:
            if nid in nodes_to_suppress:
                continue
            if rrf_scores[nid] < min_relevance:
                continue
            surviving_candidates.append(nid)

        # Evaluate Stage 1 Structural Refusal Gates (specs/RETRIEVAL.md §9.6, RET-006, RET-007)
        # Gate 1: Ontology Grounding Gate
        query_tokens = [t for t in tokenize(query) if t not in STOPWORDS and len(t) > 2]
        grounded_terms = [t for t in query_tokens if t in self.ontology_terms]
        grounding_passed = len(grounded_terms) > 0 if query_tokens else True

        # Gate 2: Path Admissibility Gate
        mentioned_nids = [t.upper() for t in tokenize(query) if t.upper() in self.csr.node_to_int]
        path_admissibility_passed = True
        if len(mentioned_nids) >= 2:
            has_any_path = False
            for i in range(len(mentioned_nids)):
                for j in range(i + 1, len(mentioned_nids)):
                    if self.csr.has_path(
                        mentioned_nids[i],
                        mentioned_nids[j],
                        max_depth=parameters_used.get("max_depth", 2),
                    ):
                        has_any_path = True
                        break
                if has_any_path:
                    break
            path_admissibility_passed = has_any_path

        # Gate 3: Terminal Validity Gate
        terminal_validity_passed = True
        if surviving_candidates:
            valid_terminals = [
                nid
                for nid in surviving_candidates
                if eligible_objects[nid].raw_body and eligible_objects[nid].raw_body.strip()
            ]
            terminal_validity_passed = len(valid_terminals) > 0

        # Gate 4: Retraction / Supersession Gate
        retraction_passed = True
        if surviving_candidates:
            active_candidates = []
            for nid in surviving_candidates:
                ko_obj = eligible_objects[nid]
                status_str = (ko_obj.frontmatter_dict.get("status") or "").lower()
                is_superseded = status_str in ["superseded", "retracted"]
                out_rels = self.relations_by_source.get(nid, [])
                if any(r.get("type") in ["SUPERSEDED_BY", "INVALIDATED_BY"] for r in out_rels):
                    is_superseded = True
                if not is_superseded:
                    active_candidates.append(nid)
            retraction_passed = len(active_candidates) > 0

        stage_1_passed = (
            grounding_passed
            and path_admissibility_passed
            and terminal_validity_passed
            and retraction_passed
        )
        refusal_reason = None
        refusal_message = None
        if not grounding_passed:
            refusal_reason = UNGROUNDED_DESCRIPTOR
            refusal_message = "Query concepts failed ontology grounding in registered taxonomy"
        elif not path_admissibility_passed:
            refusal_reason = NO_ADMISSIBLE_PATH
            refusal_message = "No admissible graph path connects the grounded concepts within maximum traversal depth"
        elif not terminal_validity_passed:
            refusal_reason = EMPTY_BODY_TERMINAL
            refusal_message = (
                "All retrieved terminal candidate nodes contain empty or unquotable bodies"
            )
        elif not retraction_passed:
            refusal_reason = SUPERSEDED_EVIDENCE
            refusal_message = (
                "All candidate evidence nodes are superseded or retracted without active successors"
            )

        enforce_refusal = parameters_used.get("enforce_structural_gates", False)
        if enforce_refusal and not stage_1_passed:
            retrieval_status = "REFUSED"
            refusal = {
                "stage": 1,
                "type": "structural",
                "reason": refusal_reason,
                "message": refusal_message,
                "gates": {
                    "ontology_grounding": grounding_passed,
                    "path_admissibility": path_admissibility_passed,
                    "terminal_validity": terminal_validity_passed,
                    "retraction_supersession": retraction_passed,
                },
            }
            final_node_ids = []
        else:
            retrieval_status = "ADMISSIBLE"
            refusal = None
            final_node_ids = surviving_candidates[:max_results]

        # 8. Build Evidence Bundle Nodes
        evidence_bundle_nodes: List[Dict[str, Any]] = []
        subgraph_nodes_set = set(final_node_ids)

        for nid in final_node_ids:
            ko = eligible_objects[nid]
            fm = ko.frontmatter_dict
            refs = fm.get("source_refs", [])
            ref = refs[0] if refs else None
            conf_info = winner_conflict_info.get(nid, {})

            # Extract facets
            facets: Dict[str, Any] = {}
            for f_key in [
                "toolchain",
                "prog_language",
                "language",
                "audience",
                "architecture",
                "lifecycle",
                "test_level",
            ]:
                if f_key in fm and fm[f_key] is not None:
                    facets[f_key] = fm[f_key]

            # Extract validity
            val_dict = fm.get("validity") or {}
            validity_info = {
                "valid_from": str(val_dict.get("valid_from"))
                if val_dict.get("valid_from")
                else None,
                "valid_until": str(val_dict.get("valid_until"))
                if val_dict.get("valid_until")
                else None,
            }

            # Subgraph relations within bundle
            raw_rels = self.relations_by_source.get(nid, [])
            subgraph_rels = [
                {"type": r.get("type"), "target": r.get("target")}
                for r in raw_rels
                if r.get("target") in subgraph_nodes_set or r.get("type") == "CONTRADICTS"
            ]

            score_components = {
                "bm25_raw": norm_bm25_scores.get(nid, 0.0),
                "vector_raw": round(vector_hits_dict[nid].score, 6)
                if vector_active and nid in vector_hits_dict
                else (
                    0.0 if vector_active else None
                ),  # D82: absent modalities report null, never 0.0
                "graph_raw": norm_graph_scores.get(nid)
                if graph_reached and nid in visited_depth
                else (None if not graph_reached else 0.0),
                "rrf_score": rrf_scores[nid],
                "reranker_score": rrf_scores[nid],  # D83: defaults to RRF
                "final": rrf_scores[nid],
                "scoring_window": prepare_scoring_window(
                    ko.raw_body, title=ko.title, max_tokens=512
                ),
            }

            node_entry: Dict[str, Any] = {
                "node_id": nid,
                "title": ko.title or "",
                "scope": ko.scope or "",
                "taxonomy_path": fm.get("taxonomy_path", ""),
                "taxonomy_id": fm.get("taxonomy_id"),
                "object_type": ko.object_type or "",
                "domain": ko.domain or "",
                "status": fm.get("status", ""),
                "epistemology": {
                    "evidence": fm.get("evidence"),
                    "verification": fm.get("verification"),
                    "authority": fm.get("authority"),
                    "consensus": fm.get("consensus"),
                },
                "facets": facets,
                "validity": validity_info,
                "matched_by": matched_by_map.get(nid, []),
                "score_components": score_components,
                "retrieval_signals": signals_map.get(nid, {}),
                "conflict_detected": conf_info.get("detected", False),
                "conflicting_node_id": conf_info.get("conflicting_node_id"),
                "provenance": {
                    "source_type": fm.get("source_type"),
                    "source_ref": ref,
                    "confidence": fm.get("confidence"),
                    "last_verified": str(fm.get("last_verified"))
                    if fm.get("last_verified")
                    else None,
                },
                "subgraph_relations": subgraph_rels,
                "body_excerpt": extract_body_excerpt(ko.raw_body),
                "path": str(
                    Path(ko.path).relative_to(self.corpus.root)
                    if ko.path and Path(ko.path).is_relative_to(self.corpus.root)
                    else (
                        Path(ko.path).relative_to(self.workspace_root)
                        if ko.path and Path(ko.path).is_relative_to(self.workspace_root)
                        else (Path(ko.path).name if ko.path else None)
                    )
                )
                if ko.path
                else None,
            }

            if parameters_used.get("include_body"):
                node_entry["body"] = ko.raw_body

            if conf_info.get("detected"):
                node_entry["conflicting_relation_type"] = conf_info.get("conflicting_relation_type")
                node_entry["conflict_resolution"] = conf_info.get("conflict_resolution")

            if vector_active and nid in vector_hits_dict:
                node_entry["passage_attribution"] = {
                    "chunk_index": vector_hits_dict[nid].chunk_index,
                    "passage_text": vector_hits_dict[nid].passage_text[:200]
                    if vector_hits_dict[nid].passage_text
                    else "",
                }

            evidence_bundle_nodes.append(node_entry)

        return {
            "query": query,
            "retrieval_version": RETRIEVAL_VERSION,
            "ranking_policy_version": RANKING_POLICY_VERSION,
            "relation_registry_version": RELATION_REGISTRY_VERSION,
            "retrieval_mode": retrieval_mode,
            "retrieval_status": retrieval_status,
            "refusal": refusal,
            "stage_1_structural_gates": {
                "status": "PASSED" if stage_1_passed else "FAILED",
                "reason": refusal_reason,
                "message": refusal_message,
                "gates": {
                    "ontology_grounding": {
                        "passed": grounding_passed,
                        "grounded_terms": grounded_terms,
                    },
                    "path_admissibility": {
                        "passed": path_admissibility_passed,
                    },
                    "terminal_validity": {
                        "passed": terminal_validity_passed,
                    },
                    "retraction_supersession": {
                        "passed": retraction_passed,
                    },
                },
            },
            "modalities_available": modalities_available,
            "modalities_absent": modalities_absent,
            "parameters_used": parameters_used,
            "parameters_origin": parameters_origin,
            "candidate_count": candidate_count,
            "returned_count": len(evidence_bundle_nodes),
            "suppressed_count": len(suppressed_nodes_list),
            "cross_scope_redactions_applied": False,
            "evidence_bundle": evidence_bundle_nodes,
            "suppressed_nodes": suppressed_nodes_list,
        }
