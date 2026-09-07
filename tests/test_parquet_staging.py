"""Comprehensive tests for Opt-in Parquet/DuckDB Staging Backend (plans/93-OPT-IN-PARQUET-STAGING.md).

Verifies:
- Dependency detection & degraded reporting (never substitute SQLite while claiming Parquet conformance).
- Dual-engine schema migrations (PRAGMA user_version 1 -> 2 -> 3) and schema_version.json.
- Safe SQL path validation & path traversal prevention (_validated_sql_path, E114).
- Parquet schema reconciliation (reconcile_parquet_schema, E111) without data loss.
- DSCP commit (commit_staged_parquet): bootstrap, atomic merge, fsync durability.
- DSCP idempotency & collision detection: same hash no-op, divergent hash E114.
- Crash recovery CP-1 through CP-6 (recover_pending_dscp_transactions).
- Atomic manifest generation (staging/discovery/state/manifest.json).
- Dual-backend equivalence verification & synchronization.
- CLI staging subcommands (status, sync, verify-equivalence, manifest, recover).
"""

import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from trashheap.cli import main
from trashheap.constants import ExitCode
from trashheap.promotion.models import CandidateProposal
from trashheap.staging import (
    BackendType,
    BaselineStagingBackend,
    DSCPIntegrityError,
    ParquetMigrationError,
    ParquetProposalRecord,
    ParquetStagingBackend,
    StagingBackendStatus,
    check_parquet_dependencies,
    get_staging_backend,
    reconcile_parquet_schema,
    run_schema_migrations,
    sync_baseline_to_parquet,
    verify_backend_equivalence,
)
from trashheap.staging.parquet import _validated_sql_path


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Create a temporary workspace directory."""
    ws = tmp_path / "workspace"
    ws.mkdir(parents=True, exist_ok=True)
    return ws


def test_dependency_detection_and_degraded_reporting():
    """Verify DuckDB/PyArrow availability check and fail-closed degraded mode."""
    # 1. Normal environment: dependencies available
    avail = check_parquet_dependencies()
    assert avail.available is True
    assert avail.status == StagingBackendStatus.READY
    assert avail.duckdb_version is not None
    assert avail.pyarrow_version is not None

    # 2. Simulated missing dependency: reports degraded
    with patch("builtins.__import__", side_effect=ImportError("No module named 'duckdb'")):
        sim_avail = check_parquet_dependencies()
        assert sim_avail.available is False
        assert sim_avail.status == StagingBackendStatus.DEGRADED
        assert "missing" in sim_avail.error_detail

    # 3. Plan 93 Gate: Never substitute SQLite while claiming Parquet conformance
    with patch("trashheap.staging.backend.check_parquet_dependencies") as mock_check:
        from trashheap.staging.models import BackendAvailability

        mock_check.return_value = BackendAvailability(
            available=False,
            backend=BackendType.PARQUET,
            status=StagingBackendStatus.DEGRADED,
            error_detail="Simulated missing DuckDB",
        )
        with pytest.raises(RuntimeError, match="Never substitute SQLite while claiming Parquet conformance"):
            get_staging_backend(BackendType.PARQUET, require_available=True)


def test_safe_sql_path_validation(tmp_path: Path):
    """Verify fail-closed SQL path validation and path traversal rejection (_validated_sql_path, E114)."""
    valid_path = tmp_path / "discovery" / "concept_proposals.parquet"
    assert _validated_sql_path(valid_path) == str(valid_path.resolve())

    # Path traversal rejection
    traversal_path = Path("/tmp/../etc/passwd")
    with pytest.raises(DSCPIntegrityError, match=r"\[E114\]"):
        _validated_sql_path(traversal_path)

    # Disallowed characters rejection
    bad_chars_path = Path("/tmp/evil';DROP TABLE users;--.parquet")
    with pytest.raises(DSCPIntegrityError, match=r"\[E114\]"):
        _validated_sql_path(bad_chars_path)


def test_dual_engine_schema_migrations(workspace: Path):
    """Verify type-safe dual-engine evolution (PRAGMA user_version 1->2->3) and schema_version.json."""
    db_path = workspace / "staging" / "transactions" / "staging_state.sqlite3"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    discovery_root = workspace / "staging" / "discovery"

    conn = sqlite3.connect(str(db_path))
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 0

    run_schema_migrations(conn, discovery_root)

    # Verify SQLite schema
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 3

    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert "ingestion_watermarks" in tables
    assert "promotion_journal" in tables
    assert "used_replay_nonces" in tables
    assert "commit_transactions" in tables

    # Verify Parquet discovery tables bootstrapped
    assert (discovery_root / "concept_proposals.parquet").exists()
    assert (discovery_root / "ambiguous_scope.parquet").exists()
    assert (discovery_root / "rejected_low_quality.parquet").exists()

    # Verify schema_version.json
    version_file = discovery_root / "state" / "schema_version.json"
    assert version_file.exists()
    data = json.loads(version_file.read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.5.2"
    assert data["sqlite_user_version"] == 3
    conn.close()


def test_parquet_schema_reconciliation(workspace: Path):
    """Verify Parquet schema evolution and null-tolerant reconciliation without data loss (E111)."""
    table_path = workspace / "test_legacy.parquet"

    # Create legacy table with fewer columns
    legacy_data = [
        {
            "proposal_id": "PROP-LEGACY-1",
            "status": "pending",
            "input_sha256": "sha256:legacyhash11111111111111111111111111111111111111111111111111111111",
        }
    ]
    legacy_table = pa.Table.from_pylist(legacy_data)
    pq.write_table(legacy_table, table_path)

    # Reconcile to concept_proposals schema
    reconcile_parquet_schema(table_path, target_version="0.5.2", table_type="concept_proposals")

    import duckdb

    conn = duckdb.connect()
    sql_path = _validated_sql_path(table_path)
    res = conn.execute(f"SELECT proposal_id, status, schema_version, inferred_scope FROM parquet_scan('{sql_path}')").fetchall()
    conn.close()

    assert len(res) == 1
    assert res[0][0] == "PROP-LEGACY-1"
    assert res[0][1] == "pending"
    assert res[0][2] == "0.5.2"  # added default
    assert res[0][3] == "ambiguous"  # added default


def test_dscp_commit_and_idempotency(workspace: Path):
    """Verify DSCP commit, idempotency, and collision rejection (commit_staged_parquet, E114)."""
    backend = ParquetStagingBackend(workspace)
    backend.run_migrations()

    record1 = ParquetProposalRecord(
        proposal_id="PROP-001",
        input_sha256="sha256:1111111111111111111111111111111111111111111111111111111111111111",
        status="pending",
        inferred_scope="engineering",
        inferred_domain="distributed_systems",
    )

    # 1. First commit
    res1 = backend.commit_proposal(record1, target_table="concept_proposals")
    assert res1.is_noop is False
    assert backend.count_proposals("concept_proposals") == 1

    # 2. Idempotent re-commit with identical hash -> no-op
    res2 = backend.commit_proposal(record1, target_table="concept_proposals")
    assert res2.is_noop is True
    assert backend.count_proposals("concept_proposals") == 1

    # 3. Collision with divergent hash -> raises DSCPIntegrityError (E114)
    record_collision = ParquetProposalRecord(
        proposal_id="PROP-001",
        input_sha256="sha256:2222222222222222222222222222222222222222222222222222222222222222",
        status="pending",
        inferred_scope="engineering",
    )
    with pytest.raises(DSCPIntegrityError, match=r"\[E114\]"):
        backend.commit_proposal(record_collision, target_table="concept_proposals")


def test_crash_recovery_cp1(workspace: Path):
    """Verify Crash CP-1 Recovery: pending commit with missing tmp file marks FAILED."""
    backend = ParquetStagingBackend(workspace)
    backend.run_migrations()

    # Simulate CP-1: row inserted with PENDING_COMMIT, but tmp file missing
    missing_tmp = workspace / "staging" / "transactions" / ".tmp_proposals_missing.parquet"
    with backend._get_state_conn() as conn:
        conn.execute(
            """
            INSERT INTO commit_transactions (
                staging_tx_id, proposal_id, input_sha256, target_table,
                staging_tmp_path, status, created_at, updated_at
            ) VALUES ('tx_cp1', 'PROP-CP1', 'sha256:cp1', 'concept_proposals', ?, 'PENDING_COMMIT', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
            """,
            (str(missing_tmp),),
        )
        conn.commit()

    res = backend.recover_transactions()
    assert res["failed"] == 1
    assert res["committed"] == 0

    with backend._get_state_conn() as conn:
        status = conn.execute("SELECT status FROM commit_transactions WHERE staging_tx_id='tx_cp1'").fetchone()[0]
        assert status == "FAILED"


def test_crash_recovery_cp2_cp3(workspace: Path):
    """Verify Crash CP-2 / CP-3 Recovery: pending commit with existing tmp file completes commit."""
    backend = ParquetStagingBackend(workspace)
    backend.run_migrations()

    tmp_parquet = workspace / "staging" / "transactions" / ".tmp_proposals_cp2.parquet"
    record = {
        "proposal_id": "PROP-CP2",
        "input_sha256": "sha256:cp2hash",
        "status": "pending",
        "schema_version": "0.5.2",
    }
    pq.write_table(pa.Table.from_pylist([record]), tmp_parquet)

    with backend._get_state_conn() as conn:
        conn.execute(
            """
            INSERT INTO commit_transactions (
                staging_tx_id, proposal_id, input_sha256, target_table,
                staging_tmp_path, status, created_at, updated_at
            ) VALUES ('tx_cp2', 'PROP-CP2', 'sha256:cp2hash', 'concept_proposals', ?, 'PENDING_COMMIT', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
            """,
            (str(tmp_parquet),),
        )
        conn.commit()

    res = backend.recover_transactions()
    assert res["committed"] == 1

    # Verify committed in target parquet
    p = backend.get_proposal("PROP-CP2", "concept_proposals")
    assert p is not None
    assert p["proposal_id"] == "PROP-CP2"
    assert not tmp_parquet.exists()


def test_crash_recovery_cp4_cp5(workspace: Path):
    """Verify Crash CP-4 / CP-5 Recovery: pending commit already committed in target marks COMMITTED."""
    backend = ParquetStagingBackend(workspace)
    backend.run_migrations()

    # First commit normally
    record = ParquetProposalRecord(
        proposal_id="PROP-CP4",
        input_sha256="sha256:cp4hash",
        status="pending",
    )
    backend.commit_proposal(record, target_table="concept_proposals")

    # Simulate crash before SQLite update: insert new tx as PENDING_COMMIT
    dummy_tmp = workspace / "staging" / "transactions" / ".tmp_proposals_cp4_dummy.parquet"
    dummy_tmp.write_bytes(b"dummy")

    with backend._get_state_conn() as conn:
        conn.execute(
            """
            INSERT INTO commit_transactions (
                staging_tx_id, proposal_id, input_sha256, target_table,
                staging_tmp_path, status, created_at, updated_at
            ) VALUES ('tx_cp4', 'PROP-CP4', 'sha256:cp4hash', 'concept_proposals', ?, 'PENDING_COMMIT', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
            """,
            (str(dummy_tmp),),
        )
        conn.commit()

    res = backend.recover_transactions()
    assert res["committed"] == 1
    assert not dummy_tmp.exists()


def test_crash_recovery_cp6(workspace: Path):
    """Verify Crash CP-6: error during schema migration leaves original intact."""
    file_path = workspace / "concept_proposals.parquet"
    initial_data = [{"proposal_id": "P-ORIGINAL", "input_sha256": "sha256:orig"}]
    pq.write_table(pa.Table.from_pylist(initial_data), file_path)

    # Force error during schema reconciliation by using invalid target
    with pytest.raises(ParquetMigrationError):
        reconcile_parquet_schema(file_path, target_version="0.5.2", table_type="nonexistent_table")

    # Original file remains untouched
    assert file_path.exists()
    import duckdb

    res = duckdb.sql(f"SELECT proposal_id FROM parquet_scan('{file_path}')").fetchall()
    assert res == [("P-ORIGINAL",)]


def test_atomic_manifest_emission(workspace: Path):
    """Verify atomic staging manifest generation (staging/discovery/state/manifest.json)."""
    backend = ParquetStagingBackend(workspace)
    backend.run_migrations()

    backend.commit_proposal(
        ParquetProposalRecord(
            proposal_id="PROP-ENG-1",
            input_sha256="sha256:eng1",
            status="pending",
            inferred_scope="engineering",
        ),
        target_table="concept_proposals",
    )

    backend.commit_proposal(
        ParquetProposalRecord(
            proposal_id="PROP-AMBIG-1",
            input_sha256="sha256:ambig1",
            status="pending",
            inferred_scope="ambiguous",
        ),
        target_table="ambiguous_scope",
    )

    manifest = backend.emit_manifest()
    assert manifest.backend == "parquet"
    assert manifest.total_proposals == 2
    assert "concept_proposals" in manifest.tables
    assert "ambiguous_scope" in manifest.tables

    manifest_file = workspace / "staging" / "discovery" / "state" / "manifest.json"
    assert manifest_file.exists()
    disk_manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert disk_manifest["total_proposals"] == 2
    assert disk_manifest["tables"]["concept_proposals"]["row_count"] == 1


def test_dual_backend_equivalence_and_sync(workspace: Path):
    """Verify baseline-to-parquet sync and equivalence verification."""
    baseline = BaselineStagingBackend(workspace)
    parquet = ParquetStagingBackend(workspace)

    # Stage proposal in baseline
    cand = CandidateProposal(
        candidate_id="CAND-001",
        state="pending",
        source_revision="sha256:1111111111111111111111111111111111111111111111111111111111111111",
        target_path="engineering/01_arch/CAND-001.md",
        proposed_frontmatter={"scope": "engineering", "domain": "software_engineering", "taxonomy_id": "TX-ENG-01"},
        proposed_body="System design content",
        proposed_content="---\nscope: engineering\n---\n\nSystem design content\n",
        proposal_hash="sha256:1111111111111111111111111111111111111111111111111111111111111111",
    )
    from trashheap.promotion.engine import save_candidate

    save_candidate(cand, workspace)
    assert baseline.count_proposals() == 1

    # Before sync: not equivalent
    report1 = verify_backend_equivalence(baseline, parquet)
    assert report1.is_equivalent is False
    assert "CAND-001" in report1.missing_in_parquet

    # Sync
    synced = sync_baseline_to_parquet(baseline, parquet)
    assert synced == 1

    # After sync: equivalent!
    report2 = verify_backend_equivalence(baseline, parquet)
    assert report2.is_equivalent is True
    assert report2.baseline_count == 1
    assert report2.parquet_count == 1
    assert report2.matched_ids == ["CAND-001"]
    assert len(report2.diffs) == 0


def test_cli_staging_commands(workspace: Path, capsys: pytest.CaptureFixture):
    """Verify CLI staging subcommands (status, sync, verify-equivalence, manifest, recover)."""
    # 1. Status
    code = main(["staging", "status", "--json", "--workspace-root", str(workspace)])
    assert code == ExitCode.SUCCESS
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["status"] == "ready"
    assert data["duckdb_version"] is not None

    # 2. Stage candidate in baseline
    cand = CandidateProposal(
        candidate_id="CLI-PROP-1",
        state="pending",
        source_revision="sha256:2222222222222222222222222222222222222222222222222222222222222222",
        target_path="engineering/01_arch/CLI-PROP-1.md",
        proposed_frontmatter={"scope": "engineering", "domain": "software_engineering"},
        proposed_body="CLI Body",
        proposed_content="---\nscope: engineering\n---\n\nCLI Body\n",
        proposal_hash="sha256:2222222222222222222222222222222222222222222222222222222222222222",
    )
    from trashheap.promotion.engine import save_candidate

    save_candidate(cand, workspace)

    # 3. Sync CLI
    code_sync = main(["staging", "sync", "--workspace-root", str(workspace)])
    assert code_sync == ExitCode.SUCCESS
    out_sync = capsys.readouterr().out
    assert "Synchronized 1 proposal(s)" in out_sync

    # 4. Equivalence CLI
    code_eq = main(["staging", "verify-equivalence", "--workspace-root", str(workspace)])
    assert code_eq == ExitCode.SUCCESS
    out_eq = capsys.readouterr().out
    assert "equivalent" in out_eq

    # 5. Manifest CLI
    code_man = main(["staging", "manifest", "--workspace-root", str(workspace)])
    assert code_man == ExitCode.SUCCESS
    out_man = capsys.readouterr().out
    assert "manifest emitted" in out_man

    # 6. Recover CLI
    code_rec = main(["staging", "recover", "--workspace-root", str(workspace)])
    assert code_rec == ExitCode.SUCCESS
    out_rec = capsys.readouterr().out
    assert "recovery executed" in out_rec
