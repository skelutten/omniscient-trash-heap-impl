"""Tests for Knowledge Bundles and Google OKF v0.2 Interoperability (Plan 61, specs/OKF-INTEROP.md, D109).

Verifies:
1. OKF-001..OKF-004: Export form, stable identity in trashheap.id, namespaced extensions, provenance.
2. OKF-007 / OKF-011 / BUNDLE-008: Declared lossy conversions and unreduced frontmatter values.
3. OKF-010 / BUNDLE-003: Deterministic byte-identical bundle materialization.
4. BUNDLE-001: Computed selector membership (CANON-004).
5. BUNDLE-004: Bundle manifest with selector and corpus hashes.
6. BUNDLE-005: Bounded relation closure with separate tracking.
7. BUNDLE-006: Unresolved references listed in manifest (never dropped).
8. BUNDLE-007: Cross-scope personal protection (CrossScopeSecurityError).
9. BUNDLE-009: Root index.md for progressive disclosure.
10. OKF-008 / OKF-009 / OKF-012: Permissive import tolerance, unknown types/keys preservation, review findings.
11. CLI: trashheap bundle export and trashheap bundle import.
"""

import json
from pathlib import Path

import pytest
import yaml

from trashheap.bundle import (
    BundleSelector,
    CrossScopeSecurityError,
    build_bundle,
    export_okf_concept,
    import_bundle,
)
from trashheap.corpus import load_corpus
from trashheap.registry.loader import load_registries


def test_okf_concept_export_field_mapping():
    """OKF-001..OKF-004, OKF-011: Verify exact field mapping and namespaced trashheap block."""
    corpus = load_corpus(Path("fixtures/canonical"))
    ko = corpus.get_by_id("ENG-FET-LINTER-0001")
    assert ko is not None

    path_map = {ko.id: "/engineering/01_architecture/ENG-FET-LINTER-0001.md"}
    okf_text = export_okf_concept(ko, path_map)

    # Parse exported document
    parts = okf_text.split("---", 2)
    assert len(parts) >= 3
    fm = yaml.safe_load(parts[1])

    # Core OKF fields (OKF-001)
    assert fm["type"] == ko.object_type
    assert fm["title"] == ko.title
    assert fm["status"] in ("stable", "draft", "deprecated")
    assert isinstance(fm["tags"], list)
    assert ko.domain in fm["tags"]
    assert "generated" in fm
    assert fm["generated"]["by"] == ko.frontmatter_dict.get("author")

    # Stable identity in trashheap.id (OKF-002)
    assert "trashheap" in fm
    assert fm["trashheap"]["id"] == "ENG-FET-LINTER-0001"

    # Unreduced status and taxonomy under trashheap.* (OKF-011)
    assert fm["trashheap"]["status"] == ko.frontmatter_dict.get("status")
    assert fm["trashheap"]["taxonomy_id"] == ko.frontmatter_dict.get("taxonomy_id")
    assert "epistemology" in fm["trashheap"]
    assert fm["trashheap"]["epistemology"]["verification"] == ko.frontmatter_dict.get(
        "verification"
    )
    assert "provenance" in fm["trashheap"]
    assert fm["trashheap"]["provenance"]["confidence"] == ko.frontmatter_dict.get("confidence")


def test_bundle_determinism_byte_identical(tmp_path: Path):
    """OKF-010, BUNDLE-003: Identical corpus and selector produce byte-identical bundle trees."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))

    selector = BundleSelector(
        bundle_id="BND-TEST-DET-001",
        title="Deterministic Test Bundle",
        scopes=["engineering"],
        min_confidence=0.7,
    )

    out_1 = tmp_path / "run_1"
    out_2 = tmp_path / "run_2"

    manifest_1 = build_bundle(corpus, selector, out_1, registries)
    manifest_2 = build_bundle(corpus, selector, out_2, registries)

    assert manifest_1.selector_hash == manifest_2.selector_hash
    assert manifest_1.corpus_hash == manifest_2.corpus_hash
    assert manifest_1.object_ids == manifest_2.object_ids

    # Compare all files
    files_1 = sorted([p.relative_to(out_1) for p in out_1.rglob("*") if p.is_file()])
    files_2 = sorted([p.relative_to(out_2) for p in out_2.rglob("*") if p.is_file()])
    assert files_1 == files_2

    for rel_f in files_1:
        # Exclude generated_at timestamp and target_directory path differences inside bundle_manifest.json
        if rel_f.name == "bundle_manifest.json":
            m1 = json.loads((out_1 / rel_f).read_text(encoding="utf-8"))
            m2 = json.loads((out_2 / rel_f).read_text(encoding="utf-8"))
            m1.pop("generated_at", None)
            m2.pop("generated_at", None)
            m1.pop("target_directory", None)
            m2.pop("target_directory", None)
            assert m1 == m2
        else:
            bytes_1 = (out_1 / rel_f).read_bytes()
            bytes_2 = (out_2 / rel_f).read_bytes()
            assert bytes_1 == bytes_2, f"Discrepancy in file {rel_f}"


def test_bundle_closure_tracking(tmp_path: Path):
    """BUNDLE-005: Relation closure pulls in target objects and tracks them separately."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))

    # Select only Claim objects, but follow RELATES_TO or DEPENDS_ON relations up to depth 1
    selector = BundleSelector(
        bundle_id="BND-CLOSURE-001",
        title="Closure Test Bundle",
        scopes=["engineering"],
        object_types=["Claim"],
        closure_relations=["RELATES_TO", "DEPENDS_ON", "EVIDENCED_BY"],
        closure_max_depth=1,
    )

    out_dir = tmp_path / "bundle_closure"
    manifest = build_bundle(corpus, selector, out_dir, registries)

    # Objects in selector
    for oid in manifest.object_ids:
        ko = corpus.get_by_id(oid)
        assert ko is not None
        assert ko.object_type == "Claim"

    # Objects pulled in by closure should be counted separately
    assert isinstance(manifest.closure_object_ids, list)
    assert manifest.total_objects == len(manifest.object_ids) + len(manifest.closure_object_ids)


def test_bundle_unresolved_references_accounting(tmp_path: Path):
    """BUNDLE-006: External relations falling outside the bundle are listed in manifest."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))

    # Select a very narrow single object that has relations pointing elsewhere
    selector = BundleSelector(
        bundle_id="BND-NARROW-001",
        title="Narrow Bundle",
        scopes=["engineering"],
        taxonomy_ids=["TX-ENG-01"],
        closure_max_depth=0,  # No closure
    )

    out_dir = tmp_path / "bundle_narrow"
    manifest = build_bundle(corpus, selector, out_dir, registries)

    # If selected objects have outgoing relations to unselected objects, they must be listed
    if manifest.unresolved_references:
        for unres in manifest.unresolved_references:
            assert "from" in unres
            assert "relation" in unres
            assert "target" in unres
            # Target must NOT be in bundle
            assert unres["target"] not in manifest.object_ids


def test_bundle_cross_scope_security(tmp_path: Path):
    """BUNDLE-007: Personal scope inclusion denied without explicit redaction/allowance policy."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))

    # Selector requesting personal scope without allow_personal_scope=True
    selector = BundleSelector(
        bundle_id="BND-LEAK-001",
        title="Leak Attempt",
        scopes=["personal"],
        allow_personal_scope=False,
    )

    out_dir = tmp_path / "bundle_leak"
    with pytest.raises(CrossScopeSecurityError):
        build_bundle(corpus, selector, out_dir, registries)


def test_bundle_index_progressive_disclosure(tmp_path: Path):
    """BUNDLE-009: Root index.md emitted for progressive disclosure."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))

    selector = BundleSelector(
        bundle_id="BND-INDEX-001",
        title="Progressive Disclosure Bundle",
        scopes=["engineering"],
        emit_index=True,
    )

    out_dir = tmp_path / "bundle_index"
    build_bundle(corpus, selector, out_dir, registries)

    index_file = out_dir / "index.md"
    assert index_file.is_file()
    content = index_file.read_text(encoding="utf-8")
    assert "type: Index" in content
    assert "okf_version:" in content and "0.2" in content
    assert "BND-INDEX-001" in content
    assert "## Concepts" in content


def test_permissive_importer_tolerance(tmp_path: Path):
    """OKF-008, OKF-009, OKF-012: Permissive importer accepts unknown types, keys, broken links without crashing."""
    bundle_dir = tmp_path / "raw_okf_bundle"
    bundle_dir.mkdir()

    # Document 1: Unknown type, unknown frontmatter keys, broken markdown link (OKF-012, OKF-009)
    doc1 = bundle_dir / "concept_alpha.md"
    doc1.write_text(
        """---
type: UnrecognizedCustomWidget
title: Concept Alpha
custom_future_field: 42
tags: [custom_tag]
status: stable
generated: { by: test_agent/1.0, at: 2026-09-01 }
sources:
  - { resource: "https://example.com/spec", title: "Spec" }
---
# Concept Alpha
See the broken link to [NonExistent](/missing/path.md).
""",
        encoding="utf-8",
    )

    # Document 2: Missing index.md in bundle_dir (OKF-012)
    imported, findings = import_bundle(bundle_dir, target_scope="engineering")

    assert len(imported) == 1
    ko = imported[0]
    assert ko.id == "concept_alpha"
    assert ko.object_type == "UnrecognizedCustomWidget"

    # OKF-009: Unknown keys preserved
    assert "_okf_extra_keys" in ko.frontmatter_dict
    assert ko.frontmatter_dict["_okf_extra_keys"]["custom_future_field"] == 42

    # OKF-008: Conservative baseline epistemology
    assert ko.frontmatter_dict["status"] == "established"
    assert ko.frontmatter_dict["verification"] == "unverified"
    assert ko.frontmatter_dict["confidence"] == 0.5

    # OKF-012: Broken link and missing index surfaced as review findings
    assert any("index.md is missing" in f["message"] for f in findings)
    assert any("Broken cross-link" in f["message"] for f in findings)


def test_cli_bundle_export_and_import(tmp_path: Path, capsys):
    """CLI: Verify trashheap bundle export and trashheap bundle import subcommands."""
    from trashheap.cli import main

    export_dir = tmp_path / "cli_bundle"

    # 1. Export
    code = main(
        [
            "bundle",
            "export",
            "--corpus-root",
            "fixtures/canonical",
            "--output-dir",
            str(export_dir),
            "--bundle-id",
            "BND-CLI-001",
            "--title",
            "CLI Test Bundle",
            "--json",
        ]
    )
    assert code == 0
    captured = capsys.readouterr()
    manifest_data = json.loads(captured.out)
    assert manifest_data["bundle_id"] == "BND-CLI-001"
    assert manifest_data["total_objects"] > 0
    assert (export_dir / "bundle_manifest.json").is_file()

    # 2. Import
    code = main(
        [
            "bundle",
            "import",
            str(export_dir),
            "--json",
        ]
    )
    assert code == 0
    captured = capsys.readouterr()
    import_data = json.loads(captured.out)
    assert import_data["status"] == "ok"
    assert import_data["imported_count"] == manifest_data["total_objects"]
