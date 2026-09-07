"""Opt-in Parquet and DuckDB discovery staging backend (INGEST-STAGING.md §7, §9, plans/93)."""

import hashlib
import json
import os
import re
import sqlite3
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from trashheap.staging.backend import StagingBackend, check_parquet_dependencies
from trashheap.staging.models import (
    TARGET_SCHEMAS,
    BackendAvailability,
    BackendType,
    CommitIdentity,
    CommitResult,
    DSCPIntegrityError,
    ParquetMigrationError,
    ParquetProposalRecord,
    StagingManifest,
    StagingTableInfo,
    current_iso_timestamp,
)

_SAFE_PATH_RE = re.compile(r"^[A-Za-z0-9_./~-]+$")


def _safe_delete(path: Path) -> None:
    """Safely remove a file without raising if missing."""
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass


def _validated_sql_path(path: Path) -> str:
    """Fail-closed path validation before interpolation into DuckDB SQL (E114)."""
    raw_str = str(path)
    if ".." in path.parts or not _SAFE_PATH_RE.match(raw_str):
        raise DSCPIntegrityError(f"Disallowed path in DSCP operation: {raw_str!r} [E114]")
    resolved_str = str(path.resolve() if not raw_str.startswith("~") else path)
    if ".." in Path(resolved_str).parts or not _SAFE_PATH_RE.match(resolved_str):
        raise DSCPIntegrityError(f"Disallowed path in DSCP operation: {resolved_str!r} [E114]")
    return resolved_str


def commit_staged_parquet(
    target_path: Path,
    tmp_path: Path,
    identity: CommitIdentity,
) -> bool:
    """Deduplicates and merges temporary Parquet data into the target table under DSCP (§3.3).

    Returns True if a new row was merged, or False if an exact duplicate no-op occurred.
    """
    import duckdb

    target_sql = _validated_sql_path(target_path)
    tmp_sql = _validated_sql_path(tmp_path)
    temp_target = (
        target_path.parent
        / f".tmp_commit_{target_path.stem}_{identity.proposal_id}.parquet"
    )
    temp_target_sql = _validated_sql_path(temp_target)

    # 1. Check whether the identity already exists in the target table (parameterized)
    existing_check = []
    if target_path.exists():
        existing_check = duckdb.sql(
            f"""
            SELECT proposal_id, input_sha256
            FROM parquet_scan('{target_sql}')
            WHERE proposal_id = ?
            ORDER BY proposal_id
            LIMIT 1
            """,
            params=[identity.proposal_id],
        ).fetchall()

    if existing_check:
        existing_sha = existing_check[0][1]
        if existing_sha == identity.input_sha256:
            # Exact same identity and content -> No-op idempotency
            _safe_delete(tmp_path)
            return False
        else:
            raise DSCPIntegrityError(
                f"Identity collision for proposal_id '{identity.proposal_id}' "
                f"with divergent hash: existing={existing_sha}, new={identity.input_sha256}. [E114]"
            )

    # 2. Bootstrap: if target file is missing, create it empty with target schema
    if not target_path.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        duckdb.sql(f"""
            COPY (
                SELECT * FROM parquet_scan('{tmp_sql}') WHERE FALSE
            ) TO '{target_sql}' (FORMAT PARQUET)
        """)

    # 3. Perform atomic merge via DuckDB
    duckdb.sql(f"""
        COPY (
            SELECT * FROM parquet_scan('{target_sql}')
            UNION ALL BY NAME
            SELECT * FROM parquet_scan('{tmp_sql}')
        ) TO '{temp_target_sql}' (FORMAT PARQUET)
    """)

    # 4. Crash-durable commit (fsync sequence per §3.2)
    with open(temp_target, "rb") as f:
        os.fsync(f.fileno())
    os.replace(temp_target, target_path)

    try:
        parent_fd = os.open(str(target_path.parent), os.O_RDONLY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    except Exception:
        pass

    _safe_delete(tmp_path)
    return True


def reconcile_parquet_schema(
    file_path: Path,
    target_version: str = "0.5.2",
    table_type: str = "concept_proposals",
) -> None:
    """Null-tolerant schema reconciliation across Parquet discovery tables (INGEST-CORE-009, E111)."""
    import duckdb

    if table_type not in TARGET_SCHEMAS:
        raise ParquetMigrationError(f"Unknown table type '{table_type}' in schema reconciliation")

    expected_columns = TARGET_SCHEMAS[table_type]
    file_sql = _validated_sql_path(file_path)

    if not file_path.exists():
        # Bootstrap empty table with full expected schema
        file_path.parent.mkdir(parents=True, exist_ok=True)
        select_expr = ", ".join(f"{default_val} AS {name}" for name, _, default_val in expected_columns)
        duckdb.sql(f"COPY (SELECT {select_expr} WHERE FALSE) TO '{file_sql}' (FORMAT PARQUET)")
        return

    # Table exists; inspect columns
    try:
        desc = duckdb.sql(f"DESCRIBE SELECT * FROM parquet_scan('{file_sql}')").fetchall()
        existing_cols = {row[0]: row[1] for row in desc}
    except Exception as e:
        raise ParquetMigrationError(f"Failed to describe existing table at {file_path}: {e}")

    # Build select expressions for all expected columns
    needs_rewrite = False
    col_exprs: List[str] = []
    for col_name, col_type, default_val in expected_columns:
        if col_name not in existing_cols:
            needs_rewrite = True
            col_exprs.append(f"{default_val} AS {col_name}")
        else:
            current_type = existing_cols[col_name]
            if current_type != col_type and not (col_type == "TIMESTAMPTZ" and "TIMESTAMP" in current_type):
                needs_rewrite = True
                col_exprs.append(f"TRY_CAST({col_name} AS {col_type}) AS {col_name}")
            else:
                col_exprs.append(col_name)

    if not needs_rewrite and len(existing_cols) == len(expected_columns):
        return

    tmp_migration = file_path.parent / f".tmp_migration_{file_path.stem}.parquet"
    tmp_sql = _validated_sql_path(tmp_migration)

    try:
        projection_sql = ", ".join(col_exprs)
        duckdb.sql(f"""
            COPY (
                SELECT {projection_sql} FROM parquet_scan('{file_sql}')
            ) TO '{tmp_sql}' (FORMAT PARQUET)
        """)

        with open(tmp_migration, "rb") as f:
            os.fsync(f.fileno())
        os.replace(tmp_migration, file_path)

    except Exception as e:
        _safe_delete(tmp_migration)
        raise ParquetMigrationError(f"Parquet schema migration failed for {file_path}: {e}")


def run_schema_migrations(state_db_conn: sqlite3.Connection, discovery_root: Path) -> None:
    """Execute type-safe dual-engine schema evolution (INGEST-STAGING.md §7.2, INGEST-CORE-017)."""
    current_version = state_db_conn.execute("PRAGMA user_version").fetchone()[0]

    if current_version < 1:
        state_db_conn.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_watermarks (
                source_type VARCHAR NOT NULL,
                file_path VARCHAR NOT NULL PRIMARY KEY,
                inode BIGINT NOT NULL DEFAULT 0,
                last_processed_offset BIGINT NOT NULL DEFAULT 0,
                last_processed_mtime DOUBLE NOT NULL,
                file_sha256 VARCHAR NOT NULL,
                proposal_id VARCHAR NOT NULL DEFAULT '',
                target_table VARCHAR NOT NULL DEFAULT 'concept_proposals',
                status VARCHAR NOT NULL,
                staging_tx_id VARCHAR NOT NULL,
                staging_tmp_path VARCHAR NOT NULL DEFAULT '',
                processed_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
        state_db_conn.execute("""
            CREATE TABLE IF NOT EXISTS promotion_journal (
                journal_id VARCHAR PRIMARY KEY,
                proposal_id VARCHAR NOT NULL,
                state VARCHAR NOT NULL,
                staged_files TEXT NOT NULL,
                target_paths TEXT NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
        state_db_conn.execute("PRAGMA user_version = 1;")
        current_version = 1

    if current_version < 2:
        state_db_conn.execute("""
            CREATE TABLE IF NOT EXISTS used_replay_nonces (
                nonce VARCHAR PRIMARY KEY,
                used_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
        state_db_conn.execute("PRAGMA user_version = 2;")
        current_version = 2

    if current_version < 3:
        state_db_conn.execute("""
            CREATE TABLE IF NOT EXISTS commit_transactions (
                staging_tx_id VARCHAR PRIMARY KEY,
                proposal_id VARCHAR NOT NULL,
                input_sha256 VARCHAR NOT NULL,
                target_table VARCHAR NOT NULL CHECK (target_table IN (
                    'concept_proposals', 'ambiguous_scope', 'rejected_low_quality')),
                staging_tmp_path VARCHAR NOT NULL,
                status VARCHAR NOT NULL DEFAULT 'PENDING_COMMIT' CHECK (status IN (
                    'PENDING_COMMIT', 'COMMITTED', 'FAILED')),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
        state_db_conn.execute("""
            INSERT OR IGNORE INTO commit_transactions (
                staging_tx_id, proposal_id, input_sha256, target_table,
                staging_tmp_path, status, created_at, updated_at)
            SELECT staging_tx_id, proposal_id, file_sha256, target_table,
                   staging_tmp_path, status, processed_at, processed_at
            FROM ingestion_watermarks
            WHERE staging_tx_id <> '' AND status IN (
                'PENDING_COMMIT', 'FAILED');
        """)
        state_db_conn.execute("PRAGMA user_version = 3;")

    # Reconcile Parquet schemas
    for table_name in [
        "concept_proposals",
        "ambiguous_scope",
        "rejected_low_quality",
    ]:
        reconcile_parquet_schema(
            discovery_root / f"{table_name}.parquet",
            target_version="0.5.2",
            table_type=table_name,
        )

    version_file = discovery_root / "state" / "schema_version.json"
    version_file.parent.mkdir(parents=True, exist_ok=True)
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "schema_version": "0.5.2",
                "sqlite_user_version": 3,
                "migrated_at": time.time(),
            },
            f,
            indent=2,
        )


def recover_pending_dscp_transactions(
    state_db_conn: sqlite3.Connection,
    discovery_root: Path,
) -> Dict[str, int]:
    """Execute deterministic DSCP recovery pass (INGEST-ADAPTERS.md §3.3)."""
    import duckdb

    target_map = {
        "concept_proposals": discovery_root / "concept_proposals.parquet",
        "ambiguous_scope": discovery_root / "ambiguous_scope.parquet",
        "rejected_low_quality": discovery_root / "rejected_low_quality.parquet",
    }

    cursor = state_db_conn.execute("""
        SELECT staging_tx_id, staging_tmp_path, target_table,
               input_sha256, proposal_id
        FROM commit_transactions
        WHERE status = 'PENDING_COMMIT'
        ORDER BY created_at
    """)
    pending_rows = cursor.fetchall()

    counts = {"committed": 0, "failed": 0, "total_pending": len(pending_rows)}

    for tx_id, tmp_path_str, target_table, input_sha256, proposal_id in pending_rows:
        target_path = target_map.get(target_table)
        if target_path is None:
            raise DSCPIntegrityError(
                f"Unknown target_table '{target_table}' in commit_transactions "
                f"(staging_tx_id={tx_id}). [E114]"
            )

        tmp_path = Path(tmp_path_str)
        identity = CommitIdentity(
            proposal_id=proposal_id,
            input_sha256=input_sha256,
            target_table=target_table,
        )

        already_committed = False
        if target_path.exists():
            target_sql = _validated_sql_path(target_path)
            res = duckdb.sql(
                f"""
                SELECT COUNT(*) FROM parquet_scan('{target_sql}')
                WHERE proposal_id = ? AND input_sha256 = ?
                """,
                params=[identity.proposal_id, identity.input_sha256],
            ).fetchone()
            if res and res[0] > 0:
                already_committed = True

        if already_committed:
            # CP-4 / CP-5 Recovery
            _safe_delete(tmp_path)
            state_db_conn.execute(
                "UPDATE commit_transactions SET status='COMMITTED', "
                "updated_at=CURRENT_TIMESTAMP WHERE staging_tx_id=?",
                (tx_id,),
            )
            counts["committed"] += 1
        elif tmp_path.exists():
            # CP-2 / CP-3 Recovery
            commit_staged_parquet(target_path, tmp_path, identity)
            state_db_conn.execute(
                "UPDATE commit_transactions SET status='COMMITTED', "
                "updated_at=CURRENT_TIMESTAMP WHERE staging_tx_id=?",
                (tx_id,),
            )
            counts["committed"] += 1
        else:
            # CP-1 Recovery
            state_db_conn.execute(
                "UPDATE commit_transactions SET status='FAILED', "
                "updated_at=CURRENT_TIMESTAMP WHERE staging_tx_id=?",
                (tx_id,),
            )
            counts["failed"] += 1

    state_db_conn.commit()
    return counts


class ParquetStagingBackend(StagingBackend):
    """Opt-in DuckDB and Parquet discovery staging backend (INGEST-STAGING.md §7, §9)."""

    def __init__(self, workspace_root: Optional[Path] = None):
        super().__init__(workspace_root)
        self.discovery_root = self.workspace_root / "staging" / "discovery"
        self.transactions_dir = self.workspace_root / "staging" / "transactions"
        self.state_db_path = self.transactions_dir / "staging_state.sqlite3"

        self.discovery_root.mkdir(parents=True, exist_ok=True)
        self.transactions_dir.mkdir(parents=True, exist_ok=True)

    @property
    def backend_type(self) -> BackendType:
        return BackendType.PARQUET

    def is_available(self) -> bool:
        return check_parquet_dependencies().available

    def get_status(self) -> BackendAvailability:
        return check_parquet_dependencies()

    def _get_state_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.state_db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=FULL;")
        return conn

    def run_migrations(self) -> None:
        """Execute dual-engine migrations."""
        with self._get_state_conn() as conn:
            run_schema_migrations(conn, self.discovery_root)

    def recover_transactions(self) -> Dict[str, int]:
        """Sweep orphan tmp files and recover pending DSCP transactions."""
        # 1. Startup orphan sweep (§9.2): unlink dangling .tmp_commit_* and .tmp_proposals_*
        now_ts = time.time()
        for pattern in [".tmp_commit_*.parquet", ".tmp_proposals_*.parquet"]:
            for f in self.discovery_root.glob(pattern):
                try:
                    if now_ts - f.stat().st_mtime > 900:  # older than 15m
                        _safe_delete(f)
                except Exception:
                    pass
            for f in self.transactions_dir.glob(pattern):
                try:
                    if now_ts - f.stat().st_mtime > 900:
                        _safe_delete(f)
                except Exception:
                    pass

        # 2. Recover pending transactions
        with self._get_state_conn() as conn:
            return recover_pending_dscp_transactions(conn, self.discovery_root)

    def commit_proposal(
        self,
        record: ParquetProposalRecord,
        target_table: str = "concept_proposals",
    ) -> CommitResult:
        """Atomically commit a proposal to target Parquet table under DSCP."""
        import pyarrow as pa
        import pyarrow.parquet as pq

        if not self.is_available():
            raise RuntimeError("Parquet staging backend dependencies are not available")

        # Ensure schema migrations ran
        self.run_migrations()

        valid_tables = ["concept_proposals", "ambiguous_scope", "rejected_low_quality"]
        if target_table not in valid_tables:
            raise DSCPIntegrityError(f"Invalid target_table '{target_table}' for Parquet staging [E114]")

        target_path = self.discovery_root / f"{target_table}.parquet"
        tx_id = f"tx_{uuid.uuid4().hex[:12]}"
        tmp_parquet = self.transactions_dir / f".tmp_proposals_{tx_id}.parquet"

        # Prepare PyArrow single-row table
        record_dict = record.model_dump()
        if record_dict.get("expires_at") is None:
            # Set default TTL per table
            days = 180 if target_table == "ambiguous_scope" else 90
            record_dict["expires_at"] = (
                (datetime.now(timezone.utc) + timedelta(days=days))
                .replace(microsecond=0)
                .isoformat()
            )

        pa_table = pa.Table.from_pylist([record_dict])
        pq.write_table(pa_table, tmp_parquet)

        # Fsync tmp file
        with open(tmp_parquet, "rb") as f:
            os.fsync(f.fileno())

        now_iso = current_iso_timestamp()
        identity = CommitIdentity(
            proposal_id=record.proposal_id,
            input_sha256=record.input_sha256,
            target_table=target_table,
        )

        # Register transaction in SQLite
        with self._get_state_conn() as conn:
            conn.execute(
                """
                INSERT INTO commit_transactions (
                    staging_tx_id, proposal_id, input_sha256, target_table,
                    staging_tmp_path, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'PENDING_COMMIT', ?, ?);
                """,
                (tx_id, identity.proposal_id, identity.input_sha256, target_table, str(tmp_parquet), now_iso, now_iso),
            )
            conn.commit()

        # Execute DSCP merge
        try:
            merged = commit_staged_parquet(target_path, tmp_parquet, identity)
            with self._get_state_conn() as conn:
                conn.execute(
                    "UPDATE commit_transactions SET status='COMMITTED', updated_at=? WHERE staging_tx_id=?",
                    (current_iso_timestamp(), tx_id),
                )
                conn.commit()
            return CommitResult(
                proposal_id=record.proposal_id,
                input_sha256=record.input_sha256,
                target_table=target_table,
                is_noop=not merged,
            )
        except Exception:
            with self._get_state_conn() as conn:
                conn.execute(
                    "UPDATE commit_transactions SET status='FAILED', updated_at=? WHERE staging_tx_id=?",
                    (current_iso_timestamp(), tx_id),
                )
                conn.commit()
            raise

    def get_proposal(
        self,
        proposal_id: str,
        target_table: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        import duckdb

        tables_to_search = [target_table] if target_table else [
            "concept_proposals",
            "ambiguous_scope",
            "rejected_low_quality",
        ]

        for t_name in tables_to_search:
            t_path = self.discovery_root / f"{t_name}.parquet"
            if not t_path.exists():
                continue
            sql_path = _validated_sql_path(t_path)
            conn = duckdb.connect()
            try:
                rows = conn.execute(
                    f"SELECT * FROM parquet_scan('{sql_path}') WHERE proposal_id = ? ORDER BY proposal_id LIMIT 1",
                    [proposal_id],
                ).fetchall()
                if rows:
                    cols = [c[0] for c in conn.description]
                    res = dict(zip(cols, rows[0]))
                    res["_target_table"] = t_name
                    return res
            finally:
                conn.close()

        return None

    def list_proposals(
        self,
        target_table: str = "concept_proposals",
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        import duckdb

        t_path = self.discovery_root / f"{target_table}.parquet"
        if not t_path.exists():
            return []

        sql_path = _validated_sql_path(t_path)
        conn = duckdb.connect()
        try:
            query = f"SELECT * FROM parquet_scan('{sql_path}')"
            params = []
            if status_filter is not None:
                query += " WHERE status = ?"
                params.append(status_filter)
            query += " ORDER BY created_at, proposal_id"

            if params:
                rows = conn.execute(query, params).fetchall()
            else:
                rows = conn.execute(query).fetchall()
            cols = [c[0] for c in conn.description]
            return [dict(zip(cols, r)) for r in rows]
        finally:
            conn.close()

    def count_proposals(self, target_table: Optional[str] = None) -> int:
        import duckdb

        tables = [target_table] if target_table else [
            "concept_proposals",
            "ambiguous_scope",
            "rejected_low_quality",
        ]
        total = 0
        conn = duckdb.connect()
        try:
            for t_name in tables:
                t_path = self.discovery_root / f"{t_name}.parquet"
                if t_path.exists():
                    sql_path = _validated_sql_path(t_path)
                    res = conn.execute(f"SELECT COUNT(*) FROM parquet_scan('{sql_path}')").fetchone()
                    if res:
                        total += res[0]
        finally:
            conn.close()
        return total

    def emit_manifest(self) -> StagingManifest:
        """Emit an atomic staging manifest with row counts and exact-byte file hashes."""
        import duckdb

        self.run_migrations()
        tables: Dict[str, StagingTableInfo] = {}
        total = 0
        counts_by_status: Dict[str, int] = {}
        counts_by_scope: Dict[str, int] = {}

        conn = duckdb.connect()
        try:
            for t_name in ["concept_proposals", "ambiguous_scope", "rejected_low_quality"]:
                t_path = self.discovery_root / f"{t_name}.parquet"
                if not t_path.exists():
                    continue

                rel_path = f"staging/discovery/{t_name}.parquet"
                sql_path = _validated_sql_path(t_path)
                desc = conn.execute(f"DESCRIBE SELECT * FROM parquet_scan('{sql_path}')").fetchall()
                cols = [row[0] for row in desc]

                # Row count
                cnt = conn.execute(f"SELECT COUNT(*) FROM parquet_scan('{sql_path}')").fetchone()[0]
                total += cnt

                # Status and scope counts
                if "status" in cols:
                    status_rows = conn.execute(
                        f"SELECT status, COUNT(*) FROM parquet_scan('{sql_path}') GROUP BY status"
                    ).fetchall()
                    for st, count in status_rows:
                        counts_by_status[st] = counts_by_status.get(st, 0) + count
                elif "rejection_reason" in cols:
                    counts_by_status["rejected"] = counts_by_status.get("rejected", 0) + cnt

                if "inferred_scope" in cols:
                    scope_rows = conn.execute(
                        f"SELECT inferred_scope, COUNT(*) FROM parquet_scan('{sql_path}') GROUP BY inferred_scope"
                    ).fetchall()
                    for sc, count in scope_rows:
                        counts_by_scope[sc] = counts_by_scope.get(sc, 0) + count

                file_bytes = t_path.read_bytes()
                h = hashlib.sha256(file_bytes).hexdigest()

                tables[t_name] = StagingTableInfo(
                    table_name=t_name,
                    relative_path=rel_path,
                    row_count=cnt,
                    file_sha256=f"sha256:{h}",
                    size_bytes=len(file_bytes),
                    columns=cols,
                )
        finally:
            conn.close()

        manifest = StagingManifest(
            schema_version="0.5.2",
            backend="parquet",
            tables=tables,
            total_proposals=total,
            counts_by_status=counts_by_status,
            counts_by_scope=counts_by_scope,
            generated_at=current_iso_timestamp(),
        )

        manifest_path = self.discovery_root / "state" / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_manifest = self.discovery_root / "state" / ".manifest.json.tmp"

        with open(tmp_manifest, "w", encoding="utf-8") as f:
            f.write(json.dumps(manifest.model_dump(), indent=2, sort_keys=True))
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_manifest, manifest_path)
        return manifest
