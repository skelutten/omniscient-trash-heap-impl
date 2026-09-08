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
        frontmatter_overrides={
            "relations": [{"type": "RELATES_TO", "target": "ENG-MISSING-9999"}]
        },
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
    build_bundle(Corpus(tmp_path / "corpus"), BundleSelector("BND-TEST", "Test"), output, registries)
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
    (ws / "tests" / "test_linter.py").write_text("def test_negative_control():\n    assert False\n", encoding="utf-8")

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
