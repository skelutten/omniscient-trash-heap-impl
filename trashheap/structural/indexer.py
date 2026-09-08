"""Structural Knowledge Graph indexer (SG-006, SG-007, SG-008, SG-009, SG-015, SG-020)."""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from trashheap.structural.extractor import ASTExtractor, compute_content_hash
from trashheap.structural.models import (
    CoverageReport,
    StructuralEdge,
    StructuralGraphManifest,
    StructuralNode,
)


class StructuralGraphIndexer:
    """Deterministic, idempotent structural graph indexer."""

    def __init__(
        self,
        repo_root: Path,
        repo_name: str = "canonical",
        cache_dir: Optional[Path] = None,
        extractor: Optional[ASTExtractor] = None,
    ):
        self.repo_root = Path(repo_root)
        self.repo_name = repo_name
        self.cache_dir = (
            Path(cache_dir) if cache_dir else self.repo_root / ".trashheap" / "cache" / "structural"
        )
        self.extractor = extractor or ASTExtractor(repo_name=repo_name)

        self.nodes: Dict[str, StructuralNode] = {}
        self.edges: Dict[str, StructuralEdge] = {}
        self.file_hashes: Dict[str, str] = {}  # rel_path -> content_hash
        self.unresolved_refs: List[Dict[str, str]] = []
        self.failed_files: List[Dict[str, str]] = []

    def scan_files(self, patterns: Optional[List[str]] = None) -> List[Path]:
        """Scan repository for source files, ignoring non-code directories."""
        if patterns is None:
            patterns = ["**/*.py"]

        matched: List[Path] = []
        ignored_dirs = {
            ".git",
            ".venv",
            "__pycache__",
            ".pytest_cache",
            ".trashheap",
            "build",
            "dist",
        }

        for pat in patterns:
            for p in self.repo_root.glob(pat):
                if not p.is_file():
                    continue
                # Skip ignored directories
                parts = set(p.relative_to(self.repo_root).parts)
                if parts.intersection(ignored_dirs):
                    continue
                matched.append(p)

        return sorted(matched)

    def load_existing_index(self) -> bool:
        """Load persisted index from cache directory if available."""
        graph_file = self.cache_dir / "graph.json"
        if not graph_file.exists():
            return False

        try:
            with open(graph_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.nodes = {
                k: StructuralNode.model_validate(v) for k, v in data.get("nodes", {}).items()
            }
            self.edges = {
                k: StructuralEdge.model_validate(v) for k, v in data.get("edges", {}).items()
            }
            self.file_hashes = data.get("file_hashes", {})
            if "manifest" in data:
                self.manifest = StructuralGraphManifest.model_validate(data["manifest"])
            return True
        except Exception:
            return False

    def index(
        self,
        source_revision: str = "HEAD",
        incremental: bool = False,
        file_patterns: Optional[List[str]] = None,
    ) -> Tuple[StructuralGraphManifest, CoverageReport]:
        """Index or re-index codebase.

        SG-006: Incremental indexing SHALL be idempotent and produce identical graph to full re-indexing.
        SG-008: Change detection via content hash, never only mtime.
        SG-009: Invalidate derived edges for removed/changed inputs before publishing.
        """
        all_candidate_paths = self.scan_files(file_patterns)

        if incremental and not self.nodes:
            self.load_existing_index()

        if not incremental:
            self.nodes.clear()
            self.edges.clear()
            self.file_hashes.clear()
            self.unresolved_refs.clear()
            self.failed_files.clear()
            self.manifest = None

        current_files: Dict[str, bytes] = {}
        current_hashes: Dict[str, str] = {}

        for p in all_candidate_paths:
            rel = str(p.relative_to(self.repo_root))
            content = p.read_bytes()
            current_files[rel] = content
            current_hashes[rel] = compute_content_hash(content)

        if incremental:
            # SG-009: Detect deleted files and remove associated nodes and edges
            deleted_files = set(self.file_hashes.keys()) - set(current_hashes.keys())
            for deleted in deleted_files:
                self._remove_file_derived_artifacts(deleted)
                self.file_hashes.pop(deleted, None)

        # Process changed or added files
        for rel, content in sorted(current_files.items()):
            prev_hash = self.file_hashes.get(rel)
            curr_hash = current_hashes[rel]

            if incremental and prev_hash == curr_hash:
                # Content hash unchanged; retain cached nodes & edges (SG-008)
                continue

            # SG-009: Changed input -> invalidate previous derived nodes and edges
            if incremental and prev_hash is not None:
                self._remove_file_derived_artifacts(rel)

            # Extract from file
            nodes, edges, unres, failure = self.extractor.extract_file(
                rel_path=rel,
                content_bytes=content,
                source_revision=source_revision,
            )

            if failure:
                # SG-020: Explicit degradation tracking
                self.failed_files.append(failure)
            else:
                for n in nodes:
                    self.nodes[n.node_id] = n
                for e in edges:
                    self.edges[e.edge_id] = e
                self.unresolved_refs.extend(unres)

            self.file_hashes[rel] = curr_hash

        # Compute aggregate corpus hash
        aggregate_hasher = hashlib.sha256()
        for rel_p in sorted(self.file_hashes.keys()):
            aggregate_hasher.update(rel_p.encode("utf-8"))
            aggregate_hasher.update(self.file_hashes[rel_p].encode("utf-8"))
        aggregate_hash = f"sha256:{aggregate_hasher.hexdigest()}"

        manifest_kwargs = {
            "schema_version": "0.1.0",
            "revision": source_revision,
            "aggregate_hash": aggregate_hash,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
        }
        if incremental and self.manifest and self.manifest.aggregate_hash == aggregate_hash:
            manifest_kwargs["generated_at"] = self.manifest.generated_at

        manifest = StructuralGraphManifest(**manifest_kwargs)
        self.manifest = manifest

        coverage = CoverageReport(
            total_files_scanned=len(all_candidate_paths),
            indexed_files=len(all_candidate_paths) - len(self.failed_files),
            total_nodes=len(self.nodes),
            total_edges=len(self.edges),
            unresolved_references=self.unresolved_refs,
            failed_files=self.failed_files,
            parser=self.extractor.PARSER_NAME,
            parser_version=self.extractor.PARSER_VERSION,
            grammar_version=self.extractor.GRAMMAR_VERSION,
        )

        # SG-009: Publish atomically via temp file + replace
        self.publish(manifest, coverage)

        return manifest, coverage

    def _remove_file_derived_artifacts(self, rel_path: str) -> None:
        """Invalidate nodes and edges derived from a specific file (SG-009)."""
        nodes_to_remove: Set[str] = {
            node_id for node_id, n in self.nodes.items() if n.path == rel_path
        }
        for nid in nodes_to_remove:
            self.nodes.pop(nid, None)

        edges_to_remove: Set[str] = {
            edge_id
            for edge_id, e in self.edges.items()
            if e.source_id in nodes_to_remove
            or e.target_id in nodes_to_remove
            or e.derivation.source_file == rel_path
        }
        for eid in edges_to_remove:
            self.edges.pop(eid, None)

    def publish(self, manifest: StructuralGraphManifest, coverage: CoverageReport) -> None:
        """Publish graph.json and coverage.json atomically (SG-009)."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        graph_payload = {
            "manifest": manifest.model_dump(),
            "nodes": {k: v.model_dump() for k, v in sorted(self.nodes.items())},
            "edges": {k: v.model_dump() for k, v in sorted(self.edges.items())},
            "file_hashes": dict(sorted(self.file_hashes.items())),
        }

        # Write graph.json atomically
        with tempfile.NamedTemporaryFile(
            "w", dir=self.cache_dir, delete=False, encoding="utf-8"
        ) as tf:
            json.dump(graph_payload, tf, indent=2, sort_keys=True)
            temp_graph = Path(tf.name)
        os.replace(temp_graph, self.cache_dir / "graph.json")

        # Write coverage.json atomically
        with tempfile.NamedTemporaryFile(
            "w", dir=self.cache_dir, delete=False, encoding="utf-8"
        ) as tf:
            json.dump(coverage.model_dump(), tf, indent=2, sort_keys=True)
            temp_cov = Path(tf.name)
        os.replace(temp_cov, self.cache_dir / "coverage.json")
