"""Opt-in graph-enhanced retrieval scoring.

Complies with specs/GRAPH-RETRIEVAL.md §9.
Implements phi1..phi6 feature computation for Layer 7 graph modality.
"""

from typing import Dict, List, Set, Tuple

from trashheap.graph.analysis import GraphAnalyzer, normalize_source_refs


class GraphFeatureScorer:
    """Calculates 6-part phi graph retrieval features per specs/GRAPH-RETRIEVAL.md §9."""

    def __init__(self, analyzer: GraphAnalyzer):
        self.analyzer = analyzer
        (
            self.out_adj,
            self.in_deg,
            self.out_deg,
            self.total_deg,
            self.comp_map,
            self.communities,
        ) = analyzer.compute_topology()
        self.distances = analyzer.compute_bounded_distances(max_depth=3)

        # Community lookup
        self.node_to_community: Dict[str, str] = {}
        for cid, comm in self.communities.items():
            for mnid in comm.member_node_ids:
                self.node_to_community[mnid] = cid

        # Source refs lookup for proximity
        self.source_refs: Dict[str, Set[str]] = {}
        for nid, ko in analyzer.objects_by_id.items():
            srefs = []
            if ko.frontmatter:
                srefs = ko.frontmatter.source_refs
            elif "source_refs" in ko.frontmatter_dict:
                srefs = ko.frontmatter_dict.get("source_refs", [])
            self.source_refs[nid] = normalize_source_refs(srefs)

    def score_candidate(
        self, candidate_id: str, seed_nodes: List[str]
    ) -> Tuple[float, Dict[str, float]]:
        """Compute (graph_feature_score, feature_breakdown) for candidate against seed set."""
        if not seed_nodes:
            # Degraded: zero seed nodes
            return 0.0, {
                "phi1": 0.0,
                "phi2": 0.0,
                "phi3": 0.0,
                "phi4": 0.0,
                "phi5": 0.0,
                "phi6": 0.0,
                "total_score": 0.0,
            }

        # phi1: max over seeds of 1 / (1 + dist_canon(s, c))
        phi1 = 0.0
        for s in seed_nodes:
            dist = self.distances.get(s, {}).get(candidate_id)
            if dist is not None:
                phi1 = max(phi1, 1.0 / (1.0 + dist))

        # phi2: path score (1.0 if reachability exists within bounded limits, else 0.0)
        phi2 = 1.0 if phi1 > 0.0 else 0.0

        # phi3: max over seeds of proximity(s, c) = min(1.0, |shared_sources| / 5)
        phi3 = 0.0
        c_refs = self.source_refs.get(candidate_id, set())
        for s in seed_nodes:
            s_refs = self.source_refs.get(s, set())
            shared = len(c_refs & s_refs)
            phi3 = max(phi3, min(1.0, shared / 5.0))

        # phi4: 1 if c and at least one seed belong to same community, else 0
        c_comm = self.node_to_community.get(candidate_id)
        phi4 = 1.0 if (c_comm is not None and any(self.node_to_community.get(s) == c_comm for s in seed_nodes)) else 0.0

        # phi5: PPR (0.0 when disabled)
        phi5 = 0.0

        # phi6: min(1.0, total_degree(c) / degree_normalization (50))
        tot_deg = self.total_deg.get(candidate_id, 0)
        phi6 = min(1.0, tot_deg / 50.0)

        # Policy weights per §9
        w_phi1 = 0.30
        w_phi2 = 0.20
        w_phi3 = 0.15
        w_phi4 = 0.10
        w_phi5 = 0.15
        w_phi6 = 0.10

        total_score = round(
            w_phi1 * phi1
            + w_phi2 * phi2
            + w_phi3 * phi3
            + w_phi4 * phi4
            + w_phi5 * phi5
            + w_phi6 * phi6,
            6,
        )

        breakdown = {
            "phi1_distance": round(phi1, 4),
            "phi2_path_score": round(phi2, 4),
            "phi3_proximity": round(phi3, 4),
            "phi4_community": round(phi4, 4),
            "phi5_ppr": round(phi5, 4),
            "phi6_degree": round(phi6, 4),
            "total_score": total_score,
        }

        return total_score, breakdown
