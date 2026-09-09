"""Filesystem durability matrix and dependency status inspection (specs/INGEST-ADAPTERS.md §3.2)."""

import platform
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class EnvironmentReport:
    """Durability and dependency capabilities report."""

    os_system: str
    filesystem_tier: str  # "Tier 1 (Production)", "Tier 2 (Degraded)", "Unsupported"
    atomic_rename_supported: bool
    fsync_durability_supported: bool
    duckdb_available: bool
    git_lfs_available: bool
    sqlite_available: bool
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "os_system": self.os_system,
            "filesystem_tier": self.filesystem_tier,
            "atomic_rename_supported": self.atomic_rename_supported,
            "fsync_durability_supported": self.fsync_durability_supported,
            "duckdb_available": self.duckdb_available,
            "git_lfs_available": self.git_lfs_available,
            "sqlite_available": self.sqlite_available,
            "summary": self.summary,
        }


def inspect_environment(workspace_root: Path) -> EnvironmentReport:
    """Inspect environment for crash durability tier and optional dependency availability."""
    sys_name = platform.system()
    ws_str = str(workspace_root.resolve())

    # Detect filesystem durability tier (§3.2)
    if ws_str.startswith("/mnt/c/") or ws_str.startswith("/mnt/d/"):
        fs_tier = "Tier 2 (Degraded)"
        summary = "WSL2 DrvFs mount detected; atomic visibility not guaranteed across processes."
    elif sys_name in {"Linux", "Darwin"}:
        fs_tier = "Tier 1 (Production)"
        summary = "Native POSIX filesystem with atomic rename and fsync durability."
    else:
        fs_tier = "Unsupported"
        summary = f"Operating system '{sys_name}' lacks POSIX durability guarantees."

    # Inspect optional dependencies
    try:
        import duckdb  # noqa: F401

        duckdb_ok = True
    except ImportError:
        duckdb_ok = False

    git_lfs_ok = shutil.which("git-lfs") is not None
    sqlite_ok = True  # python standard library

    is_tier_1 = fs_tier == "Tier 1 (Production)"

    return EnvironmentReport(
        os_system=sys_name,
        filesystem_tier=fs_tier,
        atomic_rename_supported=is_tier_1,
        fsync_durability_supported=is_tier_1,
        duckdb_available=duckdb_ok,
        git_lfs_available=git_lfs_ok,
        sqlite_available=sqlite_ok,
        summary=summary,
    )
