"""Filesystem durability utilities: atomic writes and advisory file locking.

Single implementation of the tmp-file + fsync + ``os.replace`` + directory-fsync
pattern that was previously duplicated in 9+ modules, plus a generic
``flock``-based mutual-exclusion context manager.
"""

from __future__ import annotations

import fcntl
import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Union


def _fsync_directory(directory: Path) -> None:
    """fsync a directory so a rename inside it survives a crash (best effort)."""
    try:
        dir_fd = os.open(str(directory), os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(dir_fd)
    except OSError:
        pass
    finally:
        os.close(dir_fd)


def atomic_write_bytes(path: Union[str, Path], data: bytes) -> None:
    """Write ``data`` to ``path`` atomically (tmp + fsync + os.replace + dir fsync)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    _fsync_directory(path.parent)


def atomic_write_text(path: Union[str, Path], text: str, encoding: str = "utf-8") -> None:
    """Write ``text`` to ``path`` atomically with durable ordering."""
    atomic_write_bytes(path, text.encode(encoding))


class FileLockTimeout(TimeoutError):
    """Raised when an advisory file lock cannot be acquired within the timeout."""


@contextmanager
def file_lock(
    lock_path: Union[str, Path],
    timeout_seconds: float = 10.0,
    poll_interval: float = 0.05,
) -> Generator[None, None, None]:
    """Acquire an exclusive OS-level advisory lock (flock) with timeout."""
    lock_path = Path(lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    start_time = time.monotonic()
    acquired = False
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except (BlockingIOError, OSError):
                if time.monotonic() - start_time >= timeout_seconds:
                    raise FileLockTimeout(
                        f"Timed out after {timeout_seconds}s waiting for lock: {lock_path}"
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
