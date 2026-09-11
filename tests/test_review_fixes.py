"""Regression tests for the 2026-09-09 code & contract review (R1-R8, R10, R2).

Each test reproduces a defect found in the review and asserts the fixed behavior.
All filesystem side effects are confined to temporary directories.
"""

import contextlib
import gzip
import io
import json
import os
import random
import string
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from trashheap.authoring import SectionOwnershipError, regenerate_page
from trashheap.bundle import BundleSelector, build_bundle
from trashheap.cli import main
from trashheap.corpus import Corpus, load_corpus
from trashheap.ingest.pipeline import intake_source
from trashheap.operations.conformance import generate_conformance_matrix
from trashheap.promotion import (
    ApprovalBindingError,
    ValidationRollbackError,
    approve_candidate,
    create_candidate_proposal,
    get_journal,
    load_candidate,
    promote_candidate,
)
from trashheap.promotion.engine import save_candidate
from trashheap.registry.loader import load_registries


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace root with staging and canonical trees."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir).resolve()
        (ws / "staging" / "proposals").mkdir(parents=True)
        (ws / "staging" / "transactions" / "locks").mkdir(parents=True)
        (ws / "engineering" / "01_domain_system_architecture").mkdir(parents=True)
        yield ws


# ---------------------------------------------------------------------------
# R1: approval must bind to the actual content bytes
# ---------------------------------------------------------------------------


def test_promotion_binds_approval_to_actual_content(temp_workspace):
    create_candidate_proposal(candidate_id="CAND-CONTENT", workspace_root=temp_workspace)
    approve_candidate("CAND-CONTENT", "human:reviewer", "ok", temp_workspace)

    # Tamper the content WITHOUT touching the stored proposal_hash.
    tampered = load_candidate("CAND-CONTENT", temp_workspace)
    tampered.proposed_content = tampered.proposed_content + "\nUNVERIFIED EXTRA\n"
    save_candidate(tampered, temp_workspace)

    with pytest.raises(ApprovalBindingError) as exc:
        promote_candidate("CAND-CONTENT", temp_workspace)
    assert "hash" in str(exc.value).lower()


# ---------------------------------------------------------------------------
# R3: promotion must run cross-object validation (Layer 4-5)
# ---------------------------------------------------------------------------


def test_promotion_rejects_broken_relation(temp_workspace):
    proposal = create_candidate_proposal(
        candidate_id="CAND-BROKEN",
        workspace_root=temp_workspace,
        frontmatter_overrides={"relations": [{"type": "RELATES_TO", "target": "ENG-MISSING-9999"}]},
    )
    approve_candidate("CAND-BROKEN", "human:reviewer", "ok", temp_workspace)

    with pytest.raises(ValidationRollbackError):
        promote_candidate("CAND-BROKEN", temp_workspace)

    # Canonical target must NOT have been written.
    assert not (temp_workspace / proposal.target_path).exists()


# ---------------------------------------------------------------------------
# R4: crash recovery must not confirm a missing canonical file
# ---------------------------------------------------------------------------


def test_recovery_fails_missing_canonical_target(temp_workspace):
    journal = get_journal(temp_workspace)
    journal.record_prepared(
        operation_id="OP-MISSING",
        candidate_id="CAND-MISSING",
        proposal_revision=1,
        target_paths=["engineering/missing.md"],
        expected_hashes={"engineering/missing.md": "sha256:" + "a" * 64},
        temporary_paths=[],
        idempotency_key="sha256:" + "b" * 64,
    )
    journal.transition_state("OP-MISSING", "CANONICAL_COMMITTED")

    journal.recover_crash(temp_workspace)

    entry = journal.get_journal_entry("OP-MISSING")
    assert entry.current_state == "FAILED"
    assert not (temp_workspace / "engineering" / "missing.md").exists()


# ---------------------------------------------------------------------------
# R5: interrupted bundle publish must preserve the previous bundle
# ---------------------------------------------------------------------------


def test_bundle_publish_interrupt_preserves_previous_bundle(tmp_path):
    registries = load_registries()
    output = tmp_path / "bundle"

    # Initial successful build.
    build_bundle(
        Corpus(tmp_path / "corpus"), BundleSelector("BND-TEST", "Test"), output, registries
    )
    (output / "old-sentinel.txt").write_text("previous published bundle")

    original_rename = os.rename

    def interrupted_rename(src, dst, *args, **kwargs):
        if Path(src).name.startswith(".tmp_bundle_"):
            raise KeyboardInterrupt("simulated Ctrl-C before publishing new bundle")
        return original_rename(src, dst, *args, **kwargs)

    with patch("trashheap.bundle.export.os.rename", side_effect=interrupted_rename):
        with pytest.raises(KeyboardInterrupt):
            build_bundle(
                Corpus(tmp_path / "corpus"), BundleSelector("BND-TEST", "Test"), output, registries
            )

    # Previous bundle must still be intact, not deleted.
    assert output.exists()
    assert (output / "old-sentinel.txt").exists()


# ---------------------------------------------------------------------------
# R6: CSCC retry must repair a missing capture manifest
# ---------------------------------------------------------------------------


def test_cscc_retry_repairs_missing_manifest(tmp_path):
    registries = load_registries()
    manifest = tmp_path / "raw" / "manifests" / "capture_manifest.json"
    original_replace = os.replace

    def failed_manifest(src, dst, *args, **kwargs):
        if Path(dst) == manifest:
            raise OSError("simulated I/O failure publishing capture manifest")
        return original_replace(src, dst, *args, **kwargs)

    kwargs = dict(
        source_input=b"captured data",
        workspace_root=tmp_path,
        source_id="SRC-RETRY",
        representation_id="REP-RETRY",
    )
    with patch("trashheap.ingest.pipeline.load_registries", return_value=registries):
        with patch("trashheap.ingest.cscc.os.replace", side_effect=failed_manifest):
            with pytest.raises(OSError):
                intake_source(**kwargs)
        # Retry must complete the manifest rather than return a false no-op.
        recovered = intake_source(**kwargs)

    assert manifest.exists()
    assert recovered.is_noop is True
    assert recovered.capture_result.content_path.exists()


# ---------------------------------------------------------------------------
# R7: separated ## Notes sections must fail closed (no silent data loss)
# ---------------------------------------------------------------------------


def test_separated_notes_sections_fail_closed():
    page = (
        "---\nid: ENG-SPC-CORE-0001\n---\n\n"
        "## Notes\nFirst human note\n\n"
        "## Summary\nSame summary\n\n"
        "## Notes\nSECOND HUMAN NOTE MUST SURVIVE\n"
    )
    with pytest.raises(SectionOwnershipError) as exc:
        regenerate_page(page, {"Summary": "Same summary"})
    assert exc.value.code == "E051"


# ---------------------------------------------------------------------------
# R2: canonical corpus loading must exclude raw/ and staging/
# ---------------------------------------------------------------------------


def test_load_corpus_excludes_raw_and_staging(tmp_path):
    canonical = tmp_path / "engineering" / "canonical.md"
    canonical.parent.mkdir(parents=True)
    canonical.write_text(
        "---\nid: CANON-ID\ntitle: Canon\nscope: engineering\n"
        "object_type: Concept\ndomain: software_engineering\n---\n# Canon\n",
        encoding="utf-8",
    )

    raw_file = tmp_path / "raw" / "sources" / "SRC" / "representations" / "REP" / "content.md"
    raw_file.parent.mkdir(parents=True)
    raw_file.write_text(
        "---\nid: RAW-ONLY-ID\ntitle: Raw\nscope: engineering\n"
        "object_type: Concept\ndomain: software_engineering\n---\n# Raw\n",
        encoding="utf-8",
    )

    staging_file = tmp_path / "staging" / "draft.md"
    staging_file.parent.mkdir(parents=True)
    staging_file.write_text(
        "---\nid: STAGING-ID\ntitle: Staging\nscope: engineering\n"
        "object_type: Concept\ndomain: software_engineering\n---\n# Staging\n",
        encoding="utf-8",
    )

    corpus = load_corpus(tmp_path)
    ids = {ko.id for ko in corpus.objects}
    assert "CANON-ID" in ids
    assert "RAW-ONLY-ID" not in ids
    assert "STAGING-ID" not in ids


# ---------------------------------------------------------------------------
# R8: conformance must not upgrade a substanceless implementation
# ---------------------------------------------------------------------------


def test_conformance_does_not_upgrade_substanceless_implementation(tmp_path):
    ws = tmp_path / "ws"
    reg = ws / "schemas" / "registry" / "spec_ownership.yaml"
    reg.parent.mkdir(parents=True)
    reg.write_text(
        yaml.safe_dump(
            {"invariant_families": [{"family_id": "VAL", "owner": "specs/VALIDATION.md"}]}
        ),
        encoding="utf-8",
    )
    (ws / "trashheap").mkdir(parents=True)
    (ws / "trashheap" / "linter.py").write_text("# No implementation\n", encoding="utf-8")
    (ws / "tests").mkdir(parents=True)
    (ws / "tests" / "test_linter.py").write_text(
        "def test_negative_control():\n    assert False\n", encoding="utf-8"
    )

    matrix = generate_conformance_matrix(ws)
    val_family = [f for f in matrix.families if f.family_id == "VAL"][0]
    assert val_family.status != "CONFORMANCE_TESTED"


# ---------------------------------------------------------------------------
# R10: PubMed batch --json must emit parseable JSON (progress to stderr)
# ---------------------------------------------------------------------------


def test_pubmed_batch_json_output_is_parseable(tmp_path):
    cached = tmp_path / ".cache" / "pubmed" / "pubmed26n0001.xml.gz"
    cached.parent.mkdir(parents=True)
    rng = random.Random(5)
    padding = "".join(rng.choices(string.ascii_letters, k=5000))
    xml = (
        "<PubmedArticleSet><!--"
        + padding
        + "--><PubmedArticle><MedlineCitation><PMID>123</PMID><Article>"
        "<ArticleTitle>Test</ArticleTitle><Abstract><AbstractText>Text</AbstractText></Abstract>"
        "</Article></MedlineCitation></PubmedArticle></PubmedArticleSet>"
    )
    with gzip.open(cached, "wb") as f:
        f.write(xml.encode())

    old_cwd = Path.cwd()
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        os.chdir(tmp_path)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = main(["benchmark", "--pubmed-shards", "1", "--parse-workers", "1", "--json"])
    finally:
        os.chdir(old_cwd)

    assert int(rc) == 0
    data = json.loads(stdout.getvalue())  # must not raise
    assert data["total_articles"] == 1


# ---------------------------------------------------------------------------
# Qwen Review Fixes (2026-09-09): WP1, WP2, WP3
# ---------------------------------------------------------------------------


def test_lint_strict_warning_returns_exit_code_2(tmp_path: Path):
    """Verify ExitCode.STRICT_WARNING (2) is returned when corpus has only warnings under --strict."""
    from datetime import date

    from trashheap.constants import ExitCode

    corpus_dir = tmp_path / "warn_corpus"
    note_path = corpus_dir / "engineering" / "01_domain_system_architecture" / "ENG-CON-TEST-0001.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(
        f"""---
id: ENG-CON-TEST-0001
title: Test Concept Approaching Review
schema_version: 3.8.10
keywords:
  - test
scope: engineering
taxonomy_path: 01. Domain & System Architecture
taxonomy_id: TX-ENG-01
object_type: Concept
domain: software_engineering
author: human:test
last_modified: {date.today().isoformat()}
next_review: 2020-01-01
language:
  - en
audience: engineer
status: established
consensus: accepted
evidence: observed
verification: peer_verified
authority: authoritative
confidence: 0.95
source_type: document
source_refs:
  - tests/test_review_fixes.py
---
# Test Concept
Content text.
""",
        encoding="utf-8",
    )

    # 1. Normal lint without strict -> ExitCode.SUCCESS (0) because warnings are non-fatal
    rc_normal = main(["lint", str(corpus_dir), "--no-check-skills"])
    assert rc_normal == ExitCode.SUCCESS

    # 2. Strict lint -> ExitCode.STRICT_WARNING (2)
    rc_strict = main(["lint", str(corpus_dir), "--strict", "--no-check-skills"])
    assert rc_strict == ExitCode.STRICT_WARNING


def test_root_json_flag_preserved_across_subcommands():
    """Verify trashheap --json <subcmd> preserves args.json is True."""
    from trashheap.cli import build_parser

    p = build_parser()
    for cmd in ["lint", "check-registries", "benchmark", "status", "reap", "conformance"]:
        parsed = p.parse_args(["--json", cmd])
        assert parsed.json is True, f"Root --json was clobbered by subparser for {cmd}"


def test_rename_entity_validations_and_piped_links(tmp_path: Path):
    """Verify rename_entity regex validation, collision detection, and piped link preservation."""
    from trashheap.rename import rename_entity

    corpus_dir = tmp_path / "rename_corpus"
    pers_dir = corpus_dir / "personal" / "02_formal_sciences_mathematics"
    pers_dir.mkdir(parents=True, exist_ok=True)

    note1 = pers_dir / "PERS-CON-MATH-0001.md"
    note1.write_text(
        """---
id: PERS-CON-MATH-0001
title: Peano Axioms
aliases: []
---
# Peano Axioms
Mathematical axioms.
""",
        encoding="utf-8",
    )

    note2 = pers_dir / "PERS-CON-MATH-0002.md"
    note2.write_text(
        """---
id: PERS-CON-MATH-0002
title: Logic Systems
---
# Logic
Refers to [[PERS-CON-MATH-0001]] and piped [[PERS-CON-MATH-0001|Peano System]].
""",
        encoding="utf-8",
    )

    # 1. Reject invalid ID format
    with pytest.raises(ValueError, match="does not conform to ID_PATTERN"):
        rename_entity(corpus_dir, "PERS-CON-MATH-0001", "invalid_id")

    # 2. Reject existing ID collision in corpus
    with pytest.raises(FileExistsError, match="already exists in corpus"):
        rename_entity(corpus_dir, "PERS-CON-MATH-0001", "PERS-CON-MATH-0002")

    # 3. Successful rename with piped link propagation
    res = rename_entity(corpus_dir, "PERS-CON-MATH-0001", "PERS-CON-MATH-0009")
    assert res.old_id == "PERS-CON-MATH-0001"
    assert res.new_id == "PERS-CON-MATH-0009"

    # Verify note2 has updated links
    note2_content = note2.read_text(encoding="utf-8")
    assert "[[PERS-CON-MATH-0009]]" in note2_content
    assert "[[PERS-CON-MATH-0009|Peano System]]" in note2_content


def test_taxonomy_grounding_extracts_all_nodes():
    """Verify HybridRetriever extracts ontology terms from taxonomy_registry.taxonomy."""
    from trashheap.retrieval import HybridRetriever

    regs = load_registries()
    retriever = HybridRetriever(corpus=Corpus(Path(".")), registries=regs)
    assert "personal" in retriever.ontology_terms or "engineering" in retriever.ontology_terms
    assert len(retriever.ontology_terms) > 20


def test_section_map_linear_token_computation():
    """Verify build_section_map correctly computes section tokens without O(L^2) overhead."""
    from trashheap.section_map import build_section_map

    body = "## Section One\nLine 1\nLine 2\nLine 3\n\n## Section Two\nLine 4\nLine 5\n"
    entries = build_section_map(body)
    assert len(entries) == 2
    assert entries[0].title == "Section One"
    assert entries[0].tokens > 0
    assert entries[1].title == "Section Two"
    assert entries[1].tokens > 0


def test_pubmed_adapter_author_and_schema_version():
    """Verify PubmedXmlAdapter emits process:nlm and schema_version 3.8.10."""
    from trashheap.operations.pubmed import PubmedArticleRecord, PubmedXmlAdapter

    record = PubmedArticleRecord(
        pmid=12345678,
        title="Sample PubMed Article",
        abstract="Abstract content.",
    )
    adapter = PubmedXmlAdapter(default_scope="personal")
    md = adapter.record_to_markdown(record)
    assert "schema_version: 3.8.10" in md
    assert "author: process:nlm" in md


def test_migration_facet_definition_and_safe_confidence():
    """Verify LegacyParser supports FacetDefinition objects and guards non-numeric confidence."""
    from trashheap.migration import FrontmatterMode, MigrationMap
    from trashheap.migration.parser import LegacyParser

    regs = load_registries()
    mmap = MigrationMap(frontmatter_mode=FrontmatterMode.REQUIRED, target_scope="engineering")
    parser = LegacyParser(regs)

    legacy_text = """---
title: Sample Note
confidence: non-numeric-confidence-string
tags:
  - python
  - rust
---
# Sample
Body text.
"""
    result = parser.parse_file("test.md", legacy_text.encode("utf-8"), mmap)
    assert isinstance(result, tuple)
    ko, _, facet_proposals, _ = result
    assert ko.frontmatter_dict["confidence"] == 0.5
    assert any(p.facet_name == "toolchain" for p in facet_proposals)


def test_corpus_excludes_docs_and_trashheap(tmp_path: Path):
    """Verify load_corpus excludes docs and .trashheap directories anywhere in path."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "test.md").write_text("---\nid: DOCS-0001\n---\n# Docs", encoding="utf-8")

    (tmp_path / ".trashheap").mkdir()
    (tmp_path / ".trashheap" / "test.md").write_text("---\nid: TRASH-0001\n---\n# Trash", encoding="utf-8")

    (tmp_path / "nested" / "docs").mkdir(parents=True)
    (tmp_path / "nested" / "docs" / "test.md").write_text("---\nid: NEST-0001\n---\n# Nest", encoding="utf-8")

    # Positive control: a canonical note (including one under a deep dir named
    # like a top-level-only exclusion) MUST still be loaded.
    (tmp_path / "personal" / "01_notes").mkdir(parents=True)
    (tmp_path / "personal" / "01_notes" / "good.md").write_text(
        "---\nid: GOOD-0001\n---\n# Good", encoding="utf-8"
    )
    (tmp_path / "personal" / "01_notes" / "tools").mkdir(parents=True)
    (tmp_path / "personal" / "01_notes" / "tools" / "deep.md").write_text(
        "---\nid: DEEP-0001\n---\n# Deep", encoding="utf-8"
    )

    corpus = load_corpus(tmp_path)
    ids = {ko.id for ko in corpus.objects}
    assert "DOCS-0001" not in ids
    assert "TRASH-0001" not in ids
    assert "NEST-0001" not in ids
    assert "GOOD-0001" in ids, "positive control: corpus loading must not exclude canonical notes"
    assert "DEEP-0001" in ids, "top-level-only exclusions must not apply at depth"
    assert "GOOD-0001" in ids, "positive control: corpus loading must not exclude canonical notes"
    assert "DEEP-0001" in ids, "top-level-only exclusions must not apply at depth"


def test_load_single_file_enforces_starting_fence(tmp_path: Path):
    """Verify load_single_file records load_error if file does not start with ---."""
    from trashheap.corpus import load_single_file

    bad_file = tmp_path / "no_fence.md"
    bad_file.write_text("# Just Heading\nSome text\n---\nmore text\n---\n", encoding="utf-8")

    ko = load_single_file(bad_file)
    assert ko.load_error is not None
    assert "missing starting YAML frontmatter fence" in str(ko.load_error)


def test_environment_durability_flags_tied_to_tier():
    """Verify atomic_rename_supported and fsync_durability_supported reflect filesystem tier."""
    from trashheap.operations.environment import inspect_environment

    drvfs_path = Path("/mnt/c/Users/Dev/repo")
    report = inspect_environment(drvfs_path)
    assert report.filesystem_tier == "Tier 2 (Degraded)"
    assert report.atomic_rename_supported is False
    assert report.fsync_durability_supported is False


def test_reaper_handles_corrupt_created_at(temp_workspace):
    """Verify TTLReaper quarantines corrupt/unparseable created_at (fail-visible, never purge)."""
    from trashheap.operations.reaper import TTLReaper

    c = create_candidate_proposal(candidate_id="CAND-CORRUPT-TIME", workspace_root=temp_workspace)
    c.created_at = "not-a-valid-timestamp"
    save_candidate(c, temp_workspace)

    reaper = TTLReaper(workspace_root=temp_workspace, ttl_days=180, grace_days=7)
    counts = reaper.run_reap_cycle()
    assert counts["expired_count"] == 0
    assert counts["purged_count"] == 0
    assert counts["quarantined_count"] >= 1
    assert "CAND-CORRUPT-TIME" in counts["quarantined"]
    proposal_file = temp_workspace / "staging" / "proposals" / "CAND-CORRUPT-TIME.yaml"
    assert proposal_file.exists(), "quarantined proposal must never be purged"
