"""Durable Promotion Commit Protocol (DPCP) SQLite Journal (specs/REVIEW-PROMOTION.md §4, INGEST-STAGING.md §9)."""

import json
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from trashheap.promotion.models import compute_content_sha256


def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class JournalRecord:
    operation_id: str
    candidate_id: str
    proposal_revision: int
    current_state: str
    target_paths: List[str]
    expected_hashes: Dict[str, str]
    temporary_paths: List[str]
    created_at: str
    updated_at: str
    idempotency_key: str
    error_message: Optional[str] = None


class DPCPJournal:
    """SQLite-backed crash-safe journal for DPCP transactions."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=FULL;")
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dpcp_journal (
                    operation_id TEXT PRIMARY KEY,
                    candidate_id TEXT NOT NULL,
                    proposal_revision INTEGER NOT NULL,
                    current_state TEXT NOT NULL,
                    target_paths TEXT NOT NULL,
                    expected_hashes TEXT NOT NULL,
                    temporary_paths TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    error_message TEXT
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dpcp_idempotency (
                    idempotency_key TEXT PRIMARY KEY,
                    operation_id TEXT NOT NULL,
                    candidate_id TEXT NOT NULL,
                    proposal_revision INTEGER NOT NULL,
                    content_hash TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)

    def record_prepared(
        self,
        operation_id: str,
        candidate_id: str,
        proposal_revision: int,
        target_paths: List[str],
        expected_hashes: Dict[str, str],
        temporary_paths: List[str],
        idempotency_key: str,
    ) -> None:
        now = current_iso_timestamp()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO dpcp_journal (
                    operation_id, candidate_id, proposal_revision, current_state,
                    target_paths, expected_hashes, temporary_paths,
                    created_at, updated_at, idempotency_key
                ) VALUES (?, ?, ?, 'PREPARED', ?, ?, ?, ?, ?, ?);
                """,
                (
                    operation_id,
                    candidate_id,
                    proposal_revision,
                    json.dumps(target_paths),
                    json.dumps(expected_hashes),
                    json.dumps(temporary_paths),
                    now,
                    now,
                    idempotency_key,
                ),
            )

    def transition_state(
        self, operation_id: str, new_state: str, error_message: Optional[str] = None
    ) -> None:
        now = current_iso_timestamp()
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE dpcp_journal
                SET current_state = ?, updated_at = ?, error_message = coalesce(?, error_message)
                WHERE operation_id = ?;
                """,
                (new_state, now, error_message, operation_id),
            )

    def record_idempotency_success(
        self,
        idempotency_key: str,
        operation_id: str,
        candidate_id: str,
        proposal_revision: int,
        content_hash: str,
        result_dict: Dict[str, Any],
    ) -> None:
        now = current_iso_timestamp()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO dpcp_idempotency (
                    idempotency_key, operation_id, candidate_id, proposal_revision,
                    content_hash, result_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    idempotency_key,
                    operation_id,
                    candidate_id,
                    proposal_revision,
                    content_hash,
                    json.dumps(result_dict),
                    now,
                ),
            )

    def get_idempotency_entry(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.execute(
                "SELECT * FROM dpcp_idempotency WHERE idempotency_key = ?;", (idempotency_key,)
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "idempotency_key": row["idempotency_key"],
                "operation_id": row["operation_id"],
                "candidate_id": row["candidate_id"],
                "proposal_revision": row["proposal_revision"],
                "content_hash": row["content_hash"],
                "result": json.loads(row["result_json"]),
                "created_at": row["created_at"],
            }

    def get_journal_entry(self, operation_id: str) -> Optional[JournalRecord]:
        with self._get_conn() as conn:
            cur = conn.execute(
                "SELECT * FROM dpcp_journal WHERE operation_id = ?;", (operation_id,)
            )
            row = cur.fetchone()
            if not row:
                return None
            return JournalRecord(
                operation_id=row["operation_id"],
                candidate_id=row["candidate_id"],
                proposal_revision=row["proposal_revision"],
                current_state=row["current_state"],
                target_paths=json.loads(row["target_paths"]),
                expected_hashes=json.loads(row["expected_hashes"]),
                temporary_paths=json.loads(row["temporary_paths"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                idempotency_key=row["idempotency_key"],
                error_message=row["error_message"],
            )

    def list_uncompleted_journals(self) -> List[JournalRecord]:
        with self._get_conn() as conn:
            cur = conn.execute(
                "SELECT * FROM dpcp_journal WHERE current_state NOT IN ('COMPLETED', 'FAILED');"
            )
            rows = cur.fetchall()
            return [
                JournalRecord(
                    operation_id=r["operation_id"],
                    candidate_id=r["candidate_id"],
                    proposal_revision=r["proposal_revision"],
                    current_state=r["current_state"],
                    target_paths=json.loads(r["target_paths"]),
                    expected_hashes=json.loads(r["expected_hashes"]),
                    temporary_paths=json.loads(r["temporary_paths"]),
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                    idempotency_key=r["idempotency_key"],
                    error_message=r["error_message"],
                )
                for r in rows
            ]

    def recover_crash(self, workspace_root: Path) -> List[Dict[str, Any]]:
        """Recover incomplete journal entries and purge orphan temporary directories (§9.2, PROMO-008)."""
        recovery_log = []
        uncompleted = self.list_uncompleted_journals()

        for j in uncompleted:
            if j.current_state in {"PREPARED", "TEMPORARY_OUTPUT_WRITTEN", "VALIDATED"}:
                # Crash before atomic rename: purge temporary paths and fail
                for tmp_p in j.temporary_paths:
                    tp = Path(tmp_p)
                    if tp.exists():
                        if tp.is_dir():
                            shutil.rmtree(tp, ignore_errors=True)
                        else:
                            tp.unlink(missing_ok=True)
                self.transition_state(
                    j.operation_id,
                    "FAILED",
                    error_message="Recovered from pre-commit crash; aborted and cleaned temporary files",
                )
                recovery_log.append(
                    {
                        "operation_id": j.operation_id,
                        "action": "rolled_back",
                        "reason": "crash_pre_commit",
                    }
                )
            elif j.current_state == "CANONICAL_COMMITTED":
                # PROMO-008: verify canonical files actually exist and still match
                # the expected hashes before confirming the commit. A missing or
                # divergent target is a crash/inconsistency, not a completed commit.
                all_present = True
                for tp, expected_hash in j.expected_hashes.items():
                    target_path = workspace_root / tp
                    if not target_path.exists():
                        all_present = False
                        break
                    actual_hash = compute_content_sha256(
                        target_path.read_text(encoding="utf-8")
                    )
                    if actual_hash != expected_hash:
                        all_present = False
                        break

                if all_present:
                    self.transition_state(
                        j.operation_id,
                        "COMPLETED",
                        error_message="Recovered from post-commit crash; canonical files confirmed",
                    )
                    recovery_log.append(
                        {
                            "operation_id": j.operation_id,
                            "action": "completed",
                            "reason": "crash_post_commit",
                        }
                    )
                else:
                    self.transition_state(
                        j.operation_id,
                        "FAILED",
                        error_message=(
                            "Recovered post-commit state but canonical target is "
                            "missing or its hash no longer matches"
                        ),
                    )
                    recovery_log.append(
                        {
                            "operation_id": j.operation_id,
                            "action": "failed",
                            "reason": "canonical_file_missing_or_mismatch",
                        }
                    )

        # Sweep orphan .tmp_promo_* folders in staging/transactions
        transactions_dir = workspace_root / "staging" / "transactions"
        if transactions_dir.exists():
            for orphan in transactions_dir.glob(".tmp_promo_*"):
                shutil.rmtree(orphan, ignore_errors=True)
                recovery_log.append(
                    {
                        "orphan_dir": str(orphan),
                        "action": "purged_orphan_directory",
                    }
                )

        return recovery_log
