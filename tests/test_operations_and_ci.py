"""Tests for operational lifecycle, connectors, retention, and CI conformance (Plan 05).

Verifies:
1. Inode-safe cursor tracking and stream rotation recovery (specs/INGEST-ADAPTERS.md §3.1).
2. Connector and Adapter acquisition pipeline (specs/INGEST-ADAPTERS.md §3.1).
3. Filesystem durability tier detection and optional dependencies (specs/INGEST-ADAPTERS.md §3.2).
4. Deterministic TTL-Reaper retention pass and invariant protection (specs/INGEST-STAGING.md §7.3).
5. Passive staleness and knowledge debt metrics calculation (specs/INGEST-STAGING.md §7.3.2).
6. Conformance matrix projection and SPEC_STATUS.md drift detection (D90, CONFORM-001).
7. Performance baseline benchmark and scale transition criteria (SCALE-001).
8. Non-interactive CLI operations subcommands with deterministic exit codes.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from trashheap.cli import main
from trashheap.constants import ExitCode
from trashheap.operations import (
    CursorStore,
    DirectoryConnector,
    DocumentAdapter,
    FileConnector,
    TrajectoryAdapter,
    TTLReaper,
    calculate_knowledge_debt,
    detect_spec_drift,
    generate_conformance_matrix,
    inspect_environment,
    run_benchmark,
)
from trashheap.promotion.models import CandidateProposal

# ============================================================================
# 1. Inode-Safe Cursor Tracking Tests
# ============================================================================


def test_cursor_store_initial_read_and_incremental_append(tmp_path: Path):
    """Test initial read of full file followed by incremental append reading only new bytes."""
    db_path = tmp_path / "cursors.db"
    store = CursorStore(db_path)

    log_file = tmp_path / "events.log"
    log_file.write_text("line 1\nline 2\n", encoding="utf-8")

    # Initial read
    new_bytes, cursor = store.check_and_read_new_bytes(log_file)
    assert new_bytes == b"line 1\nline 2\n"
    assert cursor.byte_offset == len(b"line 1\nline 2\n")

    # No change read
    new_bytes2, cursor2 = store.check_and_read_new_bytes(log_file)
    assert new_bytes2 == b""
    assert cursor2.byte_offset == cursor.byte_offset

    # Append new data
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("line 3\n")

    new_bytes3, cursor3 = store.check_and_read_new_bytes(log_file)
    assert new_bytes3 == b"line 3\n"
    assert cursor3.byte_offset == len(b"line 1\nline 2\nline 3\n")


def test_cursor_store_handles_truncation_and_rotation(tmp_path: Path):
    """Test cursor resets to offset 0 on file truncation or file rotation."""
    db_path = tmp_path / "cursors.db"
    store = CursorStore(db_path)

    log_file = tmp_path / "stream.log"
    log_file.write_text("first chunk of data", encoding="utf-8")

    store.check_and_read_new_bytes(log_file)

    # 1. Truncation: overwrite with shorter file
    log_file.write_text("short", encoding="utf-8")
    new_bytes, cursor = store.check_and_read_new_bytes(log_file)
    assert new_bytes == b"short"
    assert cursor.byte_offset == 5

    # 2. Rotation: delete and recreate file (new inode)
    log_file.unlink()
    log_file.write_text("brand new rotated file", encoding="utf-8")
    new_bytes2, cursor2 = store.check_and_read_new_bytes(log_file)
    assert new_bytes2 == b"brand new rotated file"
    assert cursor2.byte_offset == len(b"brand new rotated file")


# ============================================================================
# 2. Connectors and Adapters Tests
# ============================================================================


def test_file_connector_and_document_adapter(tmp_path: Path):
    """Test FileConnector capturing raw bytes and DocumentAdapter staging via CSCC."""
    doc_path = tmp_path / "article.md"
    doc_path.write_text("# Knowledge Engineering\n\nContent here.", encoding="utf-8")

    connector = FileConnector(doc_path)
    payloads = list(connector.acquire())
    assert len(payloads) == 1
    p = payloads[0]
    assert p.content_bytes == b"# Knowledge Engineering\n\nContent here."
    assert p.content_hash.startswith("sha256:")

    # Adapt and ingest
    adapter = DocumentAdapter()
    res = adapter.normalize_and_ingest(p, workspace_root=tmp_path)
    assert res.envelope.category.lower() == "artifact"
    assert res.evidence_unit_path.exists()
    assert (tmp_path / "raw" / "sources").exists()


def test_directory_connector_and_trajectory_adapter(tmp_path: Path):
    """Test DirectoryConnector glob scanning and TrajectoryAdapter staging."""
    trace_dir = tmp_path / "traces"
    trace_dir.mkdir()
    (trace_dir / "step1.json").write_text('{"step": 1}', encoding="utf-8")
    (trace_dir / "step2.json").write_text('{"step": 2}', encoding="utf-8")
    (trace_dir / ".hidden.json").write_text('{"hidden": true}', encoding="utf-8")

    connector = DirectoryConnector(trace_dir, pattern="*.json")
    payloads = list(connector.acquire())
    assert len(payloads) == 2
    assert {Path(p.source_path).name for p in payloads} == {"step1.json", "step2.json"}

    adapter = TrajectoryAdapter(agent_runtime="antigravity")
    res = adapter.normalize_and_ingest(payloads[0], workspace_root=tmp_path)
    assert res.envelope.category.lower() == "event"
    assert res.envelope.source_type == "agent_trajectory"


# ============================================================================
# 3. Environment Durability Matrix Tests
# ============================================================================


def test_inspect_environment_native_posix(tmp_path: Path):
    """Test environment inspection identifies POSIX and standard dependencies."""
    report = inspect_environment(tmp_path)
    assert report.atomic_rename_supported is True
    assert report.fsync_durability_supported is True
    assert report.sqlite_available is True
    assert report.filesystem_tier in {"Tier 1 (Production)", "Tier 2 (Degraded)"}


def test_inspect_environment_wsl2_drvfs_detection(tmp_path: Path):
    """Test WSL2 DrvFs mount detection downgrades tier to Tier 2 (Degraded)."""
    fake_drvfs_path = Path("/mnt/c/Users/Developer/workspace")
    report = inspect_environment(fake_drvfs_path)
    assert report.filesystem_tier == "Tier 2 (Degraded)"
    assert "WSL2 DrvFs" in report.summary


# ============================================================================
# 4. Deterministic Retention & TTL-Reaper Tests
# ============================================================================


def test_ttl_reaper_lifecycle_and_invariants(tmp_path: Path):
    """Test TTL reaper expires pending proposals, purges after grace period, and protects approved ones."""
    now = datetime(2026, 9, 7, 12, 0, 0, tzinfo=timezone.utc)
    old_date = (now - timedelta(days=200)).isoformat()  # older than 180d TTL
    very_old_date = (now - timedelta(days=220)).isoformat()  # older than 180 + 7d grace

    props_dir = tmp_path / "staging" / "proposals"
    props_dir.mkdir(parents=True)

    # 1. Pending candidate older than TTL (should expire)
    c_pending = CandidateProposal(
        candidate_id="CAN-PENDING-001",
        proposal_revision=1,
        created_at=old_date,
        state="pending",
        source_revision="sha256:" + "a" * 64,
        target_path="engineering/old.md",
        proposed_frontmatter={
            "id": "KO-OLD",
            "title": "Old Pending",
            "object_type": "pattern",
            "scope": "engineering",
            "domain": "software_engineering",
            "taxonomy_path": "01. Engineering",
        },
        proposed_body="# Old",
        proposed_content="---\nid: KO-OLD\n---\n# Old",
        proposal_hash="sha256:" + "b" * 64,
        source_refs=["SRC-001"],
        representation_refs=["REP-001"],
    )
    (props_dir / "CAN-PENDING-001.yaml").write_text(
        yaml.dump(c_pending.model_dump()), encoding="utf-8"
    )

    # 2. Approved candidate older than TTL (MUST NEVER EXPIRE per §7.3.1 invariant)
    c_approved = CandidateProposal(
        candidate_id="CAN-APPROVED-002",
        proposal_revision=1,
        created_at=old_date,
        state="approved",
        source_revision="sha256:" + "c" * 64,
        target_path="engineering/approved.md",
        proposed_frontmatter={
            "id": "KO-APP",
            "title": "Approved Doc",
            "object_type": "pattern",
            "scope": "engineering",
            "domain": "software_engineering",
            "taxonomy_path": "01. Engineering",
        },
        proposed_body="# Approved",
        proposed_content="---\nid: KO-APP\n---\n# Approved",
        proposal_hash="sha256:" + "d" * 64,
        source_refs=["SRC-002"],
        representation_refs=["REP-002"],
    )
    (props_dir / "CAN-APPROVED-002.yaml").write_text(
        yaml.dump(c_approved.model_dump()), encoding="utf-8"
    )

    # 3. Already expired candidate older than TTL + grace_days (should be purged)
    c_expired = CandidateProposal(
        candidate_id="CAN-EXPIRED-003",
        proposal_revision=1,
        created_at=very_old_date,
        state="expired",
        source_revision="sha256:" + "e" * 64,
        target_path="engineering/dead.md",
        proposed_frontmatter={
            "id": "KO-DEAD",
            "title": "Dead Doc",
            "object_type": "pattern",
            "scope": "engineering",
            "domain": "software_engineering",
            "taxonomy_path": "01. Engineering",
        },
        proposed_body="# Dead",
        proposed_content="---\nid: KO-DEAD\n---\n# Dead",
        proposal_hash="sha256:" + "f" * 64,
        source_refs=["SRC-003"],
        representation_refs=["REP-003"],
    )
    (props_dir / "CAN-EXPIRED-003.yaml").write_text(
        yaml.dump(c_expired.model_dump()), encoding="utf-8"
    )

    reaper = TTLReaper(workspace_root=tmp_path, ttl_days=180, grace_days=7)
    results = reaper.run_reap_cycle(now=now)

    assert results["expired_count"] == 1
    assert results["purged_count"] == 1

    # Verify pending was expired
    c_pending_loaded = yaml.safe_load(
        (props_dir / "CAN-PENDING-001.yaml").read_text(encoding="utf-8")
    )
    assert c_pending_loaded["state"] == "expired"

    # Verify approved was NOT expired
    c_approved_loaded = yaml.safe_load(
        (props_dir / "CAN-APPROVED-002.yaml").read_text(encoding="utf-8")
    )
    assert c_approved_loaded["state"] == "approved"

    # Verify tombstoned file was purged
    assert not (props_dir / "CAN-EXPIRED-003.yaml").exists()

    # Verify audit log exists
    audit_file = tmp_path / "staging" / "transactions" / "reaper_audit.jsonl"
    assert audit_file.exists()
    lines = [
        json.loads(line) for line in audit_file.read_text(encoding="utf-8").splitlines() if line
    ]
    assert len(lines) == 2


# ============================================================================
# 5. Passive Staleness & Knowledge Debt Tests
# ============================================================================


def test_calculate_knowledge_debt(tmp_path: Path):
    """Test knowledge debt metrics calculation."""
    now = datetime(2026, 9, 7, 12, 0, 0, tzinfo=timezone.utc)
    props_dir = tmp_path / "staging" / "proposals"
    props_dir.mkdir(parents=True)

    c1 = CandidateProposal(
        candidate_id="CAN-1",
        proposal_revision=1,
        created_at=(now - timedelta(days=179)).isoformat(),
        state="pending",
        source_revision="sha256:" + "1" * 64,
        target_path="p1.md",
        proposed_frontmatter={
            "id": "KO-1",
            "title": "P1",
            "object_type": "pattern",
            "scope": "engineering",
            "domain": "software_engineering",
            "taxonomy_path": "01. Engineering",
        },
        proposed_body="# 1",
        proposed_content="---\nid: KO-1\n---\n# 1",
        proposal_hash="sha256:" + "2" * 64,
        source_refs=[],
        representation_refs=[],
    )
    (props_dir / "CAN-1.yaml").write_text(yaml.dump(c1.model_dump()), encoding="utf-8")

    report = calculate_knowledge_debt(tmp_path, ttl_days=180, now=now)
    assert report.pending_backlog_count == 1
    assert report.oldest_item_age_days >= 178.0
    assert report.expiry_warning is True


# ============================================================================
# 6. Conformance Matrix & Drift Detector Tests (D90, CONFORM-001)
# ============================================================================


def test_conformance_matrix_generation(tmp_path: Path):
    """Test generating conformance projection matrix with all 5 evidence fields."""
    root = Path(__file__).resolve().parent.parent
    out_file = tmp_path / "conformance_matrix.yaml"

    matrix = generate_conformance_matrix(root, output_path=out_file)
    assert matrix.summary["total_families"] == 37
    assert matrix.summary["conformance_tested"] >= 30
    assert matrix.summary["unimplemented"] <= 5

    assert out_file.exists()
    with open(out_file, "r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    assert loaded["evidence_type"] == "generated_projection"
    assert len(loaded["families"]) == 37


def test_detect_spec_drift_clean_checkout():
    """Test that active repository passes SPEC_STATUS.md drift check with zero errors."""
    root = Path(__file__).resolve().parent.parent
    drift = detect_spec_drift(root)
    assert drift.passed is True, (
        f"Drift errors found: {[f.message for f in drift.findings if f.level == 'ERROR']}"
    )


# ============================================================================
# 7. Performance Benchmark Tests (SCALE-001)
# ============================================================================


def test_run_benchmark_scale_assessment():
    """Test performance baseline measurement over canonical fixtures."""
    root = Path(__file__).resolve().parent.parent
    report = run_benchmark(root)

    assert report.corpus_document_count >= 20
    assert report.parse_ms_per_doc > 0.0
    assert report.lint_ms_per_doc > 0.0
    assert report.retrieval_mean_query_ms > 0.0
    assert report.lint_finding_count == 0  # Canonical fixtures produce zero diagnostics

    assessment = report.scale_transition_assessment
    assert assessment["governing_invariant"] == "SCALE-001"
    assert assessment["evidence_type"] == "measured_baseline"
    assert assessment["status"] == "within_baseline_limits"


# ============================================================================
# 8. CLI Operations Subcommands Integration Tests
# ============================================================================


def test_cli_status(capsys):
    """Test trashheap status command."""
    code = main(["status", "--json"])
    assert code == ExitCode.SUCCESS
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["status"] == "ok"
    assert "environment" in data
    assert "knowledge_debt" in data


def test_cli_reap(tmp_path: Path, capsys):
    """Test trashheap reap command."""
    code = main(["reap", "--workspace-root", str(tmp_path), "--json"])
    assert code == ExitCode.SUCCESS
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["status"] == "reaped"


def test_cli_conformance_and_check(tmp_path: Path, capsys):
    """Test trashheap conformance and --check command."""
    out_yaml = tmp_path / "matrix.yaml"
    code = main(["conformance", "--output", str(out_yaml), "--check", "--json"])
    assert code == ExitCode.SUCCESS
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["status"] == "checked"
    assert data["drift"]["passed"] is True


def test_cli_benchmark(capsys):
    """Test trashheap benchmark command."""
    code = main(["benchmark", "--json"])
    assert code == ExitCode.SUCCESS
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["status"] == "ok"
    assert data["benchmark"]["corpus_document_count"] >= 20
