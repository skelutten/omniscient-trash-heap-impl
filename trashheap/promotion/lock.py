"""OS-level advisory file locking for canonical promotion (§9.1, INGEST-CORE-015).

Thin domain wrapper around the generic :func:`trashheap.fsutil.file_lock`,
mapping the generic timeout to the promotion-specific exception type.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from trashheap.fsutil import FileLockTimeout, file_lock
from trashheap.promotion.exceptions import LockTimeoutError


@contextmanager
def canonical_promotion_lock(
    lock_path: Path,
    timeout_seconds: float = 10.0,
    poll_interval: float = 0.05,
) -> Generator[None, None, None]:
    """Acquire exclusive OS-level advisory lock with timeout."""
    try:
        with file_lock(lock_path, timeout_seconds=timeout_seconds, poll_interval=poll_interval):
            yield
    except FileLockTimeout as exc:
        raise LockTimeoutError(
            f"Timed out after {timeout_seconds}s waiting for canonical promotion lock: {lock_path}"
        ) from exc
