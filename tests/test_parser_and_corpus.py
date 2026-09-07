"""Tests for Frontmatter model, categories, extra=forbid, and one-read corpus loader."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from trashheap.constants import METADATA_CATEGORIES
from trashheap.corpus import load_corpus
from trashheap.models import FrontmatterModel


def test_frontmatter_valid():
    data = {
        "id": "ENG-SPC-CORE-0001",
        "title": "Deterministic Core Specification",
        "schema_version": "3.8.10",
        "scope": "engineering",
        "taxonomy_path": "01. Domain & System Architecture",
        "taxonomy_id": "TX-ENG-01",
        "object_type": "Specification",
        "domain": "runtime_frameworks",
        "evidence": "observed",
        "verification": "formal_proof",
        "authority": "normative",
        "consensus": "accepted",
        "source_type": "internal_document",
        "source_refs": ["specs/ARCHITECTURE.md"],
        "author": "human:daniel",
        "last_modified": "2026-08-27",
        "next_review": "2027-02-17",
        "confidence": 1.0,
        "status": "established",
        "toolchain": ["pytest"],
        "architecture": ["container"],
        "lifecycle": "maintained",
        "relations": [{"type": "DEFINES", "target": "ENG-PRT-PROMO-0001"}],
    }
    model = FrontmatterModel.model_validate(data)
    assert model.id == "ENG-SPC-CORE-0001"
    assert model.scope == "engineering"
    assert len(model.relations) == 1


def test_frontmatter_extra_field_forbidden():
    """META-002: Extra unallocated fields MUST be rejected by Pydantic."""
    data = {
        "id": "ENG-SPC-CORE-0001",
        "title": "Deterministic Core Specification",
        "scope": "engineering",
        "taxonomy_path": "01. Domain & System Architecture",
        "object_type": "Specification",
        "domain": "runtime_frameworks",
        "evidence": "observed",
        "verification": "formal_proof",
        "authority": "normative",
        "consensus": "accepted",
        "source_type": "internal_document",
        "source_refs": ["specs/ARCHITECTURE.md"],
        "author": "human:daniel",
        "last_modified": "2026-08-27",
        "next_review": "2027-02-17",
        "confidence": 1.0,
        "status": "established",
        "random_unallocated_field": "illegal_value",
    }
    with pytest.raises(ValidationError) as exc:
        FrontmatterModel.model_validate(data)
    assert "random_unallocated_field" in str(exc.value)


def test_nine_metadata_categories():
    """META-001: Exactly 9 categories defined in constants."""
    assert len(METADATA_CATEGORIES) == 9
    expected_categories = {
        "IDENTITY",
        "ORGANIZATION",
        "CLASSIFICATION",
        "FACETS",
        "EPISTEMOLOGY",
        "PROVENANCE",
        "TEMPORAL",
        "GOVERNANCE",
        "ONTOLOGY",
    }
    assert set(METADATA_CATEGORIES.keys()) == expected_categories


def test_one_read_corpus_loader(tmp_path: Path):
    """Work package 2: Each file is read and parsed exactly once."""
    for i in range(5):
        file_path = tmp_path / f"test_{i}.md"
        file_path.write_text(
            f"""---
id: PERS-NOT-2026-000{i + 1}
title: Note {i}
scope: personal
taxonomy_path: "01. Domain"
object_type: Note
domain: computer_science
evidence: observed
verification: self_verified
authority: informal
consensus: accepted
source_type: note
source_refs: ["note://test"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 0.9
status: draft
relations: []
---
## Summary
Test note content.
""",
            encoding="utf-8",
        )

    corpus = load_corpus(tmp_path)
    assert len(corpus) == 5
    assert corpus.read_count == 5, f"Expected exactly 5 reads, got {corpus.read_count}"
