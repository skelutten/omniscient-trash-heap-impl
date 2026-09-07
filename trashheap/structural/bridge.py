"""Bridge relations between Knowledge Objects and Structural Nodes (SG-013, §15.5).

Normative rules:
- SG-013: Bridge relations SHALL be derived, typed and reviewable; they MUST NOT create canonical relations automatically.
- Bridge edges follow the Discovery lifecycle (status: pending | reviewed | approved | rejected).
"""

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from trashheap.corpus import Corpus
from trashheap.structural.models import BridgeEdge, DerivationMetadata, StructuralNode


class BridgeEngine:
    """Discovers and manages bridge edges between canonical Knowledge Objects and structural nodes."""

    def __init__(self, workspace_root: Path, cache_dir: Optional[Path] = None):
        self.workspace_root = Path(workspace_root)
        self.cache_dir = Path(cache_dir) if cache_dir else self.workspace_root / ".trashheap" / "cache" / "structural"
        self.bridges: Dict[str, BridgeEdge] = {}

    def load_bridges(self) -> None:
        """Load persisted bridges from disk."""
        bridge_file = self.cache_dir / "bridges.json"
        if not bridge_file.exists():
            return

        try:
            with open(bridge_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.bridges = {k: BridgeEdge.model_validate(v) for k, v in data.items()}
        except Exception:
            self.bridges = {}

    def discover_bridges(
        self,
        corpus: Corpus,
        structural_nodes: Dict[str, StructuralNode],
        source_revision: str = "HEAD",
    ) -> List[BridgeEdge]:
        """Discover candidate bridge edges connecting Knowledge Objects to structural code nodes.

        SG-013: Bridge edges are derived and pending review; no canonical files are mutated.
        """
        discovered: List[BridgeEdge] = []

        # Index structural nodes by relative path and by qualified symbol
        path_to_nodes: Dict[str, List[StructuralNode]] = {}
        symbol_to_nodes: Dict[str, List[StructuralNode]] = {}

        for n in structural_nodes.values():
            path_to_nodes.setdefault(n.path, []).append(n)
            if n.qualified_name:
                symbol_to_nodes.setdefault(n.qualified_name, []).append(n)

        derivation_proto = {
            "mode": "extracted",
            "extractor": "ast",
            "extractor_version": "0.1.0",
            "grammar_version": "Python 3.13",
            "source_revision": source_revision,
        }

        for ko in corpus.objects:
            body_text = ko.body
            source_refs = getattr(ko.frontmatter, "source_refs", []) or []

            # 1. Check direct file path mentions in source_refs or body
            candidate_paths: set[str] = set()
            for ref in source_refs:
                for p in path_to_nodes:
                    if p in ref:
                        candidate_paths.add(p)

            for p in path_to_nodes:
                if re.search(r"\b" + re.escape(p) + r"\b", body_text):
                    candidate_paths.add(p)

            for p in candidate_paths:
                file_node_id = f"repo=canonical;path={p}"
                if file_node_id in structural_nodes:
                    b_id = f"bridge#{ko.id}#{file_node_id}#represented_by"
                    b_edge = BridgeEdge(
                        bridge_id=b_id,
                        knowledge_object_id=ko.id,
                        structural_node_id=file_node_id,
                        bridge_type="represented_by",
                        derivation=DerivationMetadata(
                            **derivation_proto,
                            source_file=p,
                        ),
                        status="pending",
                    )
                    discovered.append(b_edge)

            # 2. Check symbol mentions
            for sym, nodes in symbol_to_nodes.items():
                if len(sym) >= 4 and re.search(r"\b" + re.escape(sym) + r"\b", body_text):
                    for sn in nodes:
                        b_type = "tested_by" if sn.node_type.value == "TEST" else "documents"
                        b_id = f"bridge#{ko.id}#{sn.node_id}#{b_type}"
                        b_edge = BridgeEdge(
                            bridge_id=b_id,
                            knowledge_object_id=ko.id,
                            structural_node_id=sn.node_id,
                            bridge_type=b_type,
                            derivation=DerivationMetadata(
                                **derivation_proto,
                                source_file=sn.path,
                            ),
                            status="pending",
                        )
                        discovered.append(b_edge)

        # Merge with existing without overwriting reviewed statuses
        for b in discovered:
            if b.bridge_id not in self.bridges:
                self.bridges[b.bridge_id] = b

        self.save_bridges()
        return list(self.bridges.values())

    def review_bridge(self, bridge_id: str, new_status: str) -> Optional[BridgeEdge]:
        """Update review status of a bridge edge (pending -> approved | rejected).

        SG-013: Does NOT modify canonical files.
        """
        if bridge_id not in self.bridges:
            return None

        if new_status not in ("pending", "reviewed", "approved", "rejected"):
            raise ValueError(f"Invalid bridge status: {new_status}")

        bridge = self.bridges[bridge_id]
        updated = bridge.model_copy(update={"status": new_status})
        self.bridges[bridge_id] = updated
        self.save_bridges()
        return updated

    def save_bridges(self) -> None:
        """Persist bridges atomically to cache."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        payload = {k: v.model_dump() for k, v in sorted(self.bridges.items())}

        with tempfile.NamedTemporaryFile("w", dir=self.cache_dir, delete=False, encoding="utf-8") as tf:
            json.dump(payload, tf, indent=2, sort_keys=True)
            temp_p = Path(tf.name)
        os.replace(temp_p, self.cache_dir / "bridges.json")
