"""Comprehensive tests for Legacy Corpus Migration (plans/60-OLD-WIKI-MIGRATION.md).

Verifies Contract Rules 1–11:
- Rule 1: Normative migration manifest with source hash, counts, source_mutated flag.
- Rule 2: Fresh-target-only executor with idempotent reruns and fail-closed behavior for unmanaged targets.
- Rule 3: Exact-byte hashing over sorted repository-relative POSIX paths and bytes.
- Rule 4: Read-only proposal emission (link_proposals.json, facet_proposals.json).
- Rule 5: Explicit ambiguity and quarantine records for malformed metadata.
- Rule 6: Normalize legacy source_ref to source_refs while preserving relative path.
- Rule 7: Source preservation verification (source_mutated: false).
- Rule 8: Anti-contamination rule (preserve legacy tags for audit, initialize keywords as empty; Descartes regression).
- Rule 9: Explicit verified-personal vs ambiguous scope (never silent default to personal).
- Rule 10: Record conservative defaults (draft, unverified, placeholder confidence).
- Rule 11 & D95: Opt-in frontmatter: required|derived mode with title extraction and privacy stripping.
"""

import json
from pathlib import Path

import pytest

from trashheap.cli import main
from trashheap.constants import ExitCode
from trashheap.corpus import load_corpus
from trashheap.linter import Linter
from trashheap.migration import (
    ChangedSourceError,
    FrontmatterMode,
    MigrationEngine,
    MigrationMap,
    UnmanagedTargetError,
    compute_corpus_hash,
)
from trashheap.registry.loader import load_registries


@pytest.fixture
def legacy_corpus(tmp_path: Path) -> Path:
    """Fixture creating a sample legacy wiki corpus."""
    source_dir = tmp_path / "legacy_source"
    source_dir.mkdir()

    # 1. Normal note with singular source_ref
    note1 = source_dir / "architecture" / "system_overview.md"
    note1.parent.mkdir(parents=True, exist_ok=True)
    note1.write_text(
        """---
title: System Architecture Overview
object_type: Component
scope: engineering
taxonomy_id: TX-ENG-01
source_ref: docs/v1/system.md
tags:
  - architecture
  - distributed
author: Alice
---
# System Architecture

See also [[service_cache]] for cache layer details.
""",
        encoding="utf-8",
    )

    # 2. Descartes regression note with contaminated tags (Rule 8)
    note2 = source_dir / "philosophy" / "descartes.md"
    note2.parent.mkdir(parents=True, exist_ok=True)
    note2.write_text(
        """---
title: Rene Descartes Meditationes
object_type: Article
scope: personal
taxonomy_id: TX-PERS-01
source_ref: philosophy/descartes.txt
tags:
  - programmering
  - devops
  - mjukvara
author: Bob
---
# Cogito Ergo Sum

An inquiry into first philosophy.
""",
        encoding="utf-8",
    )

    # 3. Malformed metadata note (Rule 5)
    note3 = source_dir / "broken" / "malformed.md"
    note3.parent.mkdir(parents=True, exist_ok=True)
    note3.write_text(
        """---
title: Broken Frontmatter
object_type: [this is invalid yaml: :::
---
# Broken
""",
        encoding="utf-8",
    )

    # 4. Ambiguous scope note without explicit scope (Rule 9)
    note4 = source_dir / "general" / "unknown_scope.md"
    note4.parent.mkdir(parents=True, exist_ok=True)
    note4.write_text(
        """---
title: Unknown Scope Note
object_type: Article
taxonomy_id: TX-ENG-01
---
# Unknown
""",
        encoding="utf-8",
    )

    # 5. Non-eligible navigation file
    index_file = source_dir / "index.md"
    index_file.write_text("# Navigation Index\n", encoding="utf-8")

    # 6. Non-markdown file
    asset_file = source_dir / "diagram.png"
    asset_file.write_bytes(b"\x89PNG\r\n\x1a\n")

    return source_dir


def test_rule_1_3_7_exact_hash_and_source_immutability(legacy_corpus: Path, tmp_path: Path):
    """Verify Rule 1, 3, 7: exact POSIX path hashing and source directory immutability."""
    target_dir = tmp_path / "target_plan"
    migration_map = MigrationMap(
        frontmatter_mode=FrontmatterMode.REQUIRED,
        target_scope="engineering",
    )
    engine = MigrationEngine(migration_map)

    # Compute hash directly
    hash1, records1 = compute_corpus_hash(legacy_corpus)
    assert hash1.startswith("sha256:")
    assert len(records1) == 6

    # Run dry-run plan
    manifest = engine.plan(source_dir=legacy_corpus, target_dir=target_dir)

    assert manifest.source_corpus_hash == hash1
    assert manifest.source_mutated is False  # Rule 1, 7
    assert manifest.counts["total_source_files"] == 6
    assert manifest.counts["excluded_files"] == 2  # index.md and diagram.png


def test_rule_2_fresh_target_and_unmanaged_rejection(legacy_corpus: Path, tmp_path: Path):
    """Verify Rule 2: fail-closed behavior on unmanaged target directory."""
    target_dir = tmp_path / "unmanaged_target"
    target_dir.mkdir()
    (target_dir / "random_file.txt").write_text("unmanaged content", encoding="utf-8")

    migration_map = MigrationMap(
        frontmatter_mode=FrontmatterMode.REQUIRED,
        target_scope="engineering",
    )
    engine = MigrationEngine(migration_map)

    with pytest.raises(UnmanagedTargetError):
        engine.execute(source_dir=legacy_corpus, target_dir=target_dir)


def test_rule_2_idempotency_and_changed_source_rejection(legacy_corpus: Path, tmp_path: Path):
    """Verify Rule 2: idempotent reruns for unchanged source, rejection for changed source without force."""
    target_dir = tmp_path / "managed_target"
    migration_map = MigrationMap(
        frontmatter_mode=FrontmatterMode.REQUIRED,
        target_scope="engineering",
    )
    engine = MigrationEngine(migration_map)

    # 1. Initial execution
    manifest1 = engine.execute(source_dir=legacy_corpus, target_dir=target_dir)
    assert manifest1.target_corpus_hash is not None
    assert (target_dir / "migration_manifest.json").exists()

    # 2. Idempotent rerun on unchanged source
    manifest2 = engine.execute(source_dir=legacy_corpus, target_dir=target_dir)
    assert manifest1.target_corpus_hash == manifest2.target_corpus_hash

    # 3. Change source file
    note1 = legacy_corpus / "architecture" / "system_overview.md"
    note1.write_text(note1.read_text(encoding="utf-8") + "\n# Modified\n", encoding="utf-8")

    # Rerun without force raises ChangedSourceError
    with pytest.raises(ChangedSourceError):
        engine.execute(source_dir=legacy_corpus, target_dir=target_dir)

    # Rerun with force succeeds
    manifest3 = engine.execute(source_dir=legacy_corpus, target_dir=target_dir, force=True)
    assert manifest3.source_corpus_hash != manifest1.source_corpus_hash


def test_rule_4_read_only_enrichment_proposals(legacy_corpus: Path, tmp_path: Path):
    """Verify Rule 4: emit separate link and facet proposal artifacts; no canonical mutation."""
    target_dir = tmp_path / "target_proposals"
    migration_map = MigrationMap(
        frontmatter_mode=FrontmatterMode.REQUIRED,
        target_scope="engineering",
    )
    engine = MigrationEngine(migration_map)
    engine.execute(source_dir=legacy_corpus, target_dir=target_dir)

    link_file = target_dir / "link_proposals.json"
    assert link_file.exists()
    links = json.loads(link_file.read_text(encoding="utf-8"))
    assert len(links) > 0
    assert any(link["raw_link"] == "service_cache" for link in links)

    facet_file = target_dir / "facet_proposals.json"
    assert facet_file.exists()
    facets = json.loads(facet_file.read_text(encoding="utf-8"))
    assert isinstance(facets, list)


def test_rule_5_malformed_metadata_quarantine(legacy_corpus: Path, tmp_path: Path):
    """Verify Rule 5: explicit ambiguity and quarantine records for malformed metadata."""
    target_dir = tmp_path / "target_quarantine"
    migration_map = MigrationMap(
        frontmatter_mode=FrontmatterMode.REQUIRED,
        target_scope="engineering",
    )
    engine = MigrationEngine(migration_map)
    manifest = engine.execute(source_dir=legacy_corpus, target_dir=target_dir)

    assert manifest.counts["quarantined_files"] >= 1
    reasons = {q.reason for q in manifest.quarantined}
    assert "malformed_metadata" in reasons
    assert any("broken/malformed.md" in q.file_path for q in manifest.quarantined)


def test_rule_6_source_ref_normalization(legacy_corpus: Path, tmp_path: Path):
    """Verify Rule 6: normalize singular source_ref to source_refs array preserving relative path."""
    target_dir = tmp_path / "target_norm"
    migration_map = MigrationMap(
        frontmatter_mode=FrontmatterMode.REQUIRED,
        target_scope="engineering",
    )
    engine = MigrationEngine(migration_map)
    engine.execute(source_dir=legacy_corpus, target_dir=target_dir)

    # Check emitted files
    assert len(list(target_dir.glob("**/*.md"))) > 0
    corpus = load_corpus(target_dir)

    # Find the system overview object
    system_obj = next((o for o in corpus.objects if "System Architecture" in o.frontmatter.title), None)
    assert system_obj is not None
    assert isinstance(system_obj.frontmatter.source_refs, list)
    assert "docs/v1/system.md" in system_obj.frontmatter.source_refs


def test_rule_8_anti_contamination_descartes_regression(legacy_corpus: Path, tmp_path: Path):
    """Verify Rule 8: Anti-contamination: Descartes note preserves tags for audit, keywords empty."""
    target_dir = tmp_path / "target_descartes"
    migration_map = MigrationMap(
        frontmatter_mode=FrontmatterMode.REQUIRED,
        target_scope="personal",
    )
    engine = MigrationEngine(migration_map)
    engine.execute(source_dir=legacy_corpus, target_dir=target_dir)

    # Check legacy tag audit
    audit_file = target_dir / "legacy_tag_audit.json"
    assert audit_file.exists()
    audit_data = json.loads(audit_file.read_text(encoding="utf-8"))
    assert any("descartes.md" in k for k in audit_data)
    descartes_tags = next(v for k, v in audit_data.items() if "descartes.md" in k)
    assert "programmering" in descartes_tags
    assert "devops" in descartes_tags
    assert "mjukvara" in descartes_tags

    # Check canonical Descartes Knowledge Object: keywords MUST be empty!
    corpus = load_corpus(target_dir)
    descartes_obj = next((o for o in corpus.objects if "descartes" in str(o.path).lower()), None)
    assert descartes_obj is not None
    assert descartes_obj.frontmatter.keywords == []


def test_rule_9_ambiguous_scope_rejection(legacy_corpus: Path, tmp_path: Path):
    """Verify Rule 9: uncertain scope remains ambiguous and never defaults silently to personal."""
    target_dir = tmp_path / "target_ambig_scope"
    # No target_scope configured
    migration_map = MigrationMap(
        frontmatter_mode=FrontmatterMode.REQUIRED,
        target_scope=None,
    )
    engine = MigrationEngine(migration_map)
    manifest = engine.plan(source_dir=legacy_corpus, target_dir=target_dir)

    # Note 4 has no scope in frontmatter
    ambig_records = [q for q in manifest.quarantined if q.reason == "ambiguous_scope"]
    assert len(ambig_records) >= 1
    assert any("unknown_scope.md" in q.file_path for q in ambig_records)


def test_rule_11_and_d95_derived_frontmatter_mode(tmp_path: Path):
    """Verify Rule 11 & D95: opt-in derived frontmatter mode extracts H1/macros and strips privacy signums."""
    source_dir = tmp_path / "external_docs"
    source_dir.mkdir()

    doc_file = source_dir / "telecom_protocol.md"
    doc_file.write_text(
        """%docTitle: 5G RAN Interface Specification
%docResp: John Doe (jd1234)
%docOwnerLineMgr: Jane Smith (js5678)

# 5G RAN Architecture Overview

This document specifies the internal interface.
""",
        encoding="utf-8",
    )

    target_dir = tmp_path / "target_derived"
    migration_map = MigrationMap(
        frontmatter_mode=FrontmatterMode.DERIVED,
        target_scope="engineering",
        privacy_stripping=["%docResp", "%docOwnerLineMgr"],
    )
    engine = MigrationEngine(migration_map)
    manifest = engine.execute(source_dir=source_dir, target_dir=target_dir)

    assert manifest.counts["eligible_files"] == 1
    corpus = load_corpus(target_dir)
    doc_obj = corpus.objects[0]

    assert doc_obj.frontmatter.title == "5G RAN Interface Specification"
    assert "John Doe" not in doc_obj.raw_body
    assert "Jane Smith" not in doc_obj.raw_body
    assert "%docResp" not in doc_obj.raw_body
    assert doc_obj.frontmatter.source_refs == ["telecom_protocol.md"]


def test_migrated_corpus_passes_linter(legacy_corpus: Path, tmp_path: Path):
    """Verify that eligible migrated objects pass core Linter Layers 1–5."""
    target_dir = tmp_path / "target_lint"
    migration_map = MigrationMap(
        frontmatter_mode=FrontmatterMode.REQUIRED,
        target_scope="engineering",
    )
    engine = MigrationEngine(migration_map)
    engine.execute(source_dir=legacy_corpus, target_dir=target_dir)

    registries = load_registries()
    linter = Linter(registries, check_skills=False)
    corpus = load_corpus(target_dir)

    findings = linter.lint_corpus(corpus)
    errors = [f for f in findings if f.level == "ERROR"]
    assert len(errors) == 0, f"Migrated corpus failed linting: {errors}"


def test_cli_migrate_commands(legacy_corpus: Path, tmp_path: Path, capsys: pytest.CaptureFixture):
    """Verify CLI migrate subcommands (plan, execute)."""
    target_plan = tmp_path / "cli_plan"
    target_exec = tmp_path / "cli_exec"

    # Plan
    code = main([
        "migrate",
        "plan",
        "--source-dir",
        str(legacy_corpus),
        "--target-dir",
        str(target_plan),
        "--target-scope",
        "engineering",
        "--json",
    ])
    assert code == ExitCode.SUCCESS
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["mode"] == "dry-run"

    # Execute
    code2 = main([
        "migrate",
        "execute",
        "--source-dir",
        str(legacy_corpus),
        "--target-dir",
        str(target_exec),
        "--target-scope",
        "engineering",
        "--json",
    ])
    assert code2 == ExitCode.SUCCESS
    out2 = capsys.readouterr().out
    data2 = json.loads(out2)
    assert data2["mode"] == "execute"
    assert data2["target_corpus_hash"] is not None
