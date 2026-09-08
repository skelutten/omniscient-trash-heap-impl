"""Smoke tests for trashheap package import and CLI entry points."""

import subprocess
import sys

import trashheap
from trashheap.constants import VERSION


def test_package_import():
    """Verify trashheap package imports cleanly and has version."""
    assert trashheap.__version__ == VERSION
    assert trashheap.__version__ == "3.8.10"


def test_cli_version():
    """Verify CLI --version outputs expected version and exit code 0."""
    res = subprocess.run(
        [sys.executable, "-m", "trashheap.cli", "--version"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert f"trashheap {VERSION}" in res.stdout


def test_cli_help():
    """Verify CLI help works."""
    res = subprocess.run(
        [sys.executable, "-m", "trashheap.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "trashheap" in res.stdout
    assert "check-registries" in res.stdout


def test_cli_bogus_flag_exit_code():
    """K2: Invalid CLI argument must return CONFIG_OR_ARG_ERROR (exit 3), not 2."""
    from trashheap.cli import main
    from trashheap.constants import ExitCode

    code = main(["--bogus-flag"])
    assert code == ExitCode.CONFIG_OR_ARG_ERROR
    assert code == 3

