"""Inode-safe cursor tracking for connectors and stream rotation (specs/INGEST-ADAPTERS.md §3.1)."""

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CursorState:
    """Cursor record binding offset to file inode, hash, and mtime."""

    source_path: str
    inode: int
    byte_offset: int
    mtime: float
    file_sha256: str
    updated_at: str


class CursorStore:
    """SQLite-backed cursor store for tracking ingestion offsets across file rotations."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ingestion_cursors (
                    source_path TEXT PRIMARY KEY,
                    inode INTEGER NOT NULL,
                    byte_offset INTEGER NOT NULL,
                    mtime REAL NOT NULL,
                    file_sha256 TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

    def get_cursor(self, source_path: str) -> Optional[CursorState]:
        with self._get_conn() as conn:
            cur = conn.execute("SELECT * FROM ingestion_cursors WHERE source_path = ?;", (source_path,))
            row = cur.fetchone()
            if not row:
                return None
            return CursorState(
                source_path=row["source_path"],
                inode=row["inode"],
                byte_offset=row["byte_offset"],
                mtime=row["mtime"],
                file_sha256=row["file_sha256"],
                updated_at=row["updated_at"],
            )

    def update_cursor(
        self,
        source_path: str,
        inode: int,
        byte_offset: int,
        mtime: float,
        file_sha256: str,
    ) -> CursorState:
        now = current_iso_timestamp()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO ingestion_cursors (
                    source_path, inode, byte_offset, mtime, file_sha256, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (source_path, inode, byte_offset, mtime, file_sha256, now),
            )
        return CursorState(
            source_path=source_path,
            inode=inode,
            byte_offset=byte_offset,
            mtime=mtime,
            file_sha256=file_sha256,
            updated_at=now,
        )

    def check_and_read_new_bytes(self, target_path: Path) -> tuple[bytes, CursorState]:
        """Read newly appended bytes from target_path while handling rotation and truncation."""
        stat = target_path.stat()
        curr_inode = stat.st_ino
        curr_mtime = stat.st_mtime
        curr_size = stat.st_size

        cursor = self.get_cursor(str(target_path))
        start_offset = 0

        if cursor:
            # Check for file rotation (inode change) or truncation (size shrunk)
            if cursor.inode == curr_inode and curr_size >= cursor.byte_offset:
                if cursor.byte_offset > 0:
                    with open(target_path, "rb") as f:
                        prefix_bytes = f.read(cursor.byte_offset)
                    prefix_hash = f"sha256:{hashlib.sha256(prefix_bytes).hexdigest()}"
                    # Inode numbers can be recycled immediately by OS upon file unlink/recreation.
                    # Verify that prefix hash matches the recorded file_sha256.
                    if prefix_hash == cursor.file_sha256:
                        start_offset = cursor.byte_offset
                    else:
                        start_offset = 0
                else:
                    start_offset = 0
            else:
                # File rotated or truncated: reset to beginning
                start_offset = 0

        with open(target_path, "rb") as f:
            f.seek(start_offset)
            new_bytes = f.read()

        # Compute whole-file sha256 for integrity watermark
        with open(target_path, "rb") as f:
            whole_hash = f"sha256:{hashlib.sha256(f.read()).hexdigest()}"

        new_cursor = self.update_cursor(
            source_path=str(target_path),
            inode=curr_inode,
            byte_offset=curr_size,
            mtime=curr_mtime,
            file_sha256=whole_hash,
        )
        return new_bytes, new_cursor
