"""Tests for atomic entity rename and backlink propagation across Markdown files and graph.json (FR-8, AC-3)."""

import json
from pathlib import Path

from trashheap.rename import rename_entity


def test_atomic_rename_and_backlink_propagation(tmp_path: Path):
    """AC-3: Renaming an entity updates all backlinks atomically with zero broken references."""
    # Create two interrelated knowledge objects
    doc_a = tmp_path / "ENG-PRD-LLMWIKI-0001.md"
    doc_b = tmp_path / "ENG-FET-LINTER-0001.md"

    doc_a.write_text(
        """---
id: ENG-PRD-LLMWIKI-0001
title: Product
aliases: []
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Product
domain: runtime_frameworks
evidence: observed
verification: formal_proof
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 1.0
status: established
lifecycle: ongoing
relations: []
---
# Product
Reference to self or notes.
""",
        encoding="utf-8",
    )

    doc_b.write_text(
        """---
id: ENG-FET-LINTER-0001
title: Feature
aliases: []
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Feature
domain: runtime_frameworks
evidence: observed
verification: self_verified
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 1.0
status: established
lifecycle: delivered
toolchain: [pytest]
relations:
  - {type: PART_OF, target: ENG-PRD-LLMWIKI-0001}
---
# Feature
Contains a wiki link: [[ENG-PRD-LLMWIKI-0001]] in text.
""",
        encoding="utf-8",
    )

    # Also create a graph.json
    graph_path = tmp_path / "graph.json"
    graph_data = {
        "schema_version": "1.0.0",
        "nodes": {
            "ENG-PRD-LLMWIKI-0001": {"title": "Product"},
            "ENG-FET-LINTER-0001": {"title": "Feature"},
        },
        "adjacency": {
            "ENG-FET-LINTER-0001": [{"type": "PART_OF", "target": "ENG-PRD-LLMWIKI-0001"}],
        },
    }
    graph_path.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")

    # Rename ENG-PRD-LLMWIKI-0001 -> ENG-PRD-LLMWIKI-0009
    rename_entity(
        corpus_root=tmp_path,
        old_id="ENG-PRD-LLMWIKI-0001",
        new_id="ENG-PRD-LLMWIKI-0009",
        graph_path=graph_path,
    )

    # 1. Old target file is removed, new target file exists
    assert not doc_a.exists()
    new_doc_a = tmp_path / "ENG-PRD-LLMWIKI-0009.md"
    assert new_doc_a.exists()

    content_a = new_doc_a.read_text(encoding="utf-8")
    assert "id: ENG-PRD-LLMWIKI-0009" in content_a
    assert "ENG-PRD-LLMWIKI-0001" in content_a  # Added to aliases

    # 2. Referencing file updated both relation target and wiki-link
    content_b = doc_b.read_text(encoding="utf-8")
    assert "target: ENG-PRD-LLMWIKI-0009" in content_b
    assert "[[ENG-PRD-LLMWIKI-0009]]" in content_b
    assert "ENG-PRD-LLMWIKI-0001" not in content_b

    # 3. graph.json updated
    assert graph_path.exists()
    updated_graph = json.loads(graph_path.read_text(encoding="utf-8"))
    assert "ENG-PRD-LLMWIKI-0009" in updated_graph["nodes"]
    assert "ENG-PRD-LLMWIKI-0001" not in updated_graph["nodes"]
    adj_targets = [r["target"] for r in updated_graph["adjacency"]["ENG-FET-LINTER-0001"]]
    assert "ENG-PRD-LLMWIKI-0009" in adj_targets
