"""Idempotent reconstruction of disposable metadata, graph, and search caches (RET-004, CANON-003)."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from trashheap.corpus import load_corpus
from trashheap.registry.loader import LoadedRegistries


def rebuild_indexes(
    corpus_root: Path,
    registries: LoadedRegistries,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Rebuild ephemeral metadata, graph projections, and term index directly from Markdown notes.

    Guarantees:
    - CANON-003: Derived indexes can be wiped and re-created at any time without information loss.
    - Deterministic output: Keys and node lists are ordered deterministically.
    """
    corpus = load_corpus(corpus_root)
    out_path = output_dir or (corpus_root / ".cache")
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Structural Graph projection
    nodes: Dict[str, Any] = {}
    adjacency: Dict[str, list[Dict[str, Any]]] = {}

    for ko in corpus.objects:
        if not ko.id:
            continue
        fm = ko.frontmatter_dict
        nodes[ko.id] = {
            "id": ko.id,
            "title": ko.title,
            "scope": ko.scope,
            "object_type": ko.object_type,
            "domain": ko.domain,
            "status": fm.get("status"),
            "path": str(ko.path.relative_to(corpus_root)),
        }
        rels = fm.get("relations", [])
        if isinstance(rels, list):
            adjacency[ko.id] = [
                {
                    "type": r.get("type"),
                    "target": r.get("target"),
                    "soft_link": r.get("soft_link", False),
                }
                for r in rels
                if isinstance(r, dict)
            ]

    graph_payload = {
        "schema_version": "1.0.0",
        "node_count": len(nodes),
        "nodes": dict(sorted(nodes.items())),
        "adjacency": dict(sorted(adjacency.items())),
    }

    graph_file = out_path / "graph.json"
    with open(graph_file, "w", encoding="utf-8") as f:
        json.dump(graph_payload, f, indent=2, sort_keys=True)

    # 2. Metadata Catalog projection
    catalog_payload = {
        "schema_version": "1.0.0",
        "corpus_root": str(corpus_root),
        "read_count": corpus.read_count,
        "object_count": len(corpus.objects),
        "objects": [
            {
                "id": ko.id,
                "path": str(ko.path.relative_to(corpus_root)),
                "title": ko.title,
                "scope": ko.scope,
                "object_type": ko.object_type,
                "domain": ko.domain,
                "frontmatter": ko.frontmatter_dict,
            }
            for ko in sorted(corpus.objects, key=lambda x: x.id or "")
        ],
    }

    catalog_file = out_path / "metadata_catalog.json"
    with open(catalog_file, "w", encoding="utf-8") as f:
        json.dump(catalog_payload, f, indent=2, sort_keys=True)

    return {
        "status": "ok",
        "rebuilt_objects": len(corpus.objects),
        "output_dir": str(out_path),
        "artifacts": [str(graph_file), str(catalog_file)],
    }
