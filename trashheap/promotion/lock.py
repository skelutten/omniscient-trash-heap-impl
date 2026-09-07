"""OS-level advisory file locking for canonical promotion (§9.1, INGEST-CORE-015)."""

import fcntl
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from trashheap.promotion.exceptions import LockTimeoutError


@contextmanager
def canonical_promotion_lock(
    lock_path: Path,
    timeout_seconds: float = 10.0,
    poll_interval: float = 0.05,
) -> Generator[None, None, None]:
    """Acquire exclusive OS-level advisory lock with timeout."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    start_time = time.time()
    acquired = False

    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except (BlockingIOError, OSError):
                if time.time() - start_time >= timeout_seconds:
                    raise LockTimeoutError(
                        f"Timed out after {timeout_seconds}s waiting for canonical promotion lock: {lock_path}"
                    )
                time.sleep(poll_interval)
        yield
    finally:
        if acquired:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
        try:
            os.close(fd)
        except OSError:
            pass

