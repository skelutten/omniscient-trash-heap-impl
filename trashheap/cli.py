"""Command-line interface for The Omniscient Trash Heap (trashheap)."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from trashheap.constants import VERSION, ExitCode
from trashheap.registry.loader import RegistryLoadError, load_registries
from trashheap.registry.validator import RegistryFinding, validate_cross_registries


def build_parser() -> argparse.ArgumentParser:
    """Build root CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="trashheap",
        description="The Omniscient Trash Heap: deterministic knowledge compiler and verification system",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"trashheap {VERSION}",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Command: check-registries
    check_reg_parser = subparsers.add_parser(
        "check-registries",
        help="Validate all 10 YAML registry schemas and cross-registry consistency",
    )
    check_reg_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output",
    )
    check_reg_parser.add_argument(
        "--registry-dir",
        type=str,
        default=None,
        help="Custom path to schemas/registry directory",
    )
    check_reg_parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Root repository directory for resolving spec ownership paths",
    )

    return parser


def format_findings_text(findings: List[RegistryFinding]) -> str:
    """Format findings for human-readable terminal output."""
    lines = []
    errors = [f for f in findings if f.level == "ERROR"]
    warnings = [f for f in findings if f.level == "WARNING"]

    for f in findings:
        prefix = "❌ ERROR" if f.level == "ERROR" else "⚠️ WARNING"
        field_str = f" in [{f.field}]" if f.field else ""
        lines.append(f"{prefix} ({f.code}) {f.registry}{field_str}: {f.message}")
        if f.suggestion:
            lines.append(f"   Suggestion: {f.suggestion}")

    lines.append(f"\nSummary: {len(errors)} error(s), {len(warnings)} warning(s)")
    return "\n".join(lines)


def format_findings_json(findings: List[RegistryFinding], passed: bool) -> str:
    """Format findings as deterministic machine-readable JSON."""
    data: Dict[str, Any] = {
        "status": "passed" if passed else "failed",
        "errors": [
            {
                "code": f.code,
                "registry": f.registry,
                "field": f.field,
                "message": f.message,
                "suggestion": f.suggestion,
            }
            for f in findings
            if f.level == "ERROR"
        ],
        "warnings": [
            {
                "code": f.code,
                "registry": f.registry,
                "field": f.field,
                "message": f.message,
                "suggestion": f.suggestion,
            }
            for f in findings
            if f.level == "WARNING"
        ],
        "summary": {
            "errors": sum(1 for f in findings if f.level == "ERROR"),
            "warnings": sum(1 for f in findings if f.level == "WARNING"),
            "passed": passed,
        },
    }
    return json.dumps(data, indent=2, sort_keys=True)


def handle_check_registries(args: argparse.Namespace) -> int:
    """Handle check-registries command execution."""
    reg_dir = args.registry_dir or "schemas/registry"
    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()

    try:
        loaded = load_registries(reg_dir)
    except FileNotFoundError as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return ExitCode.NOT_FOUND
    except RegistryLoadError as e:
        if args.json:
            print(
                json.dumps({"status": "error", "message": str(e), "registry": e.filename}, indent=2)
            )
        else:
            print(f"Registry load error ({e.filename}): {e.message}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR

    findings = validate_cross_registries(loaded, repo_root)
    errors = [f for f in findings if f.level == "ERROR"]
    passed = len(errors) == 0

    if args.json:
        print(format_findings_json(findings, passed))
    else:
        if passed:
            print("✓ All 10 YAML registries loaded and verified successfully.")
        else:
            print(format_findings_text(findings), file=sys.stderr)

    return ExitCode.SUCCESS if passed else ExitCode.VALIDATION_ERROR


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point returning integer exit code."""
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        parser.print_help()
        return ExitCode.SUCCESS

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else ExitCode.CONFIG_OR_ARG_ERROR

    if args.command == "check-registries":
        return handle_check_registries(args)
    else:
        parser.print_help()
        return ExitCode.SUCCESS


if __name__ == "__main__":
    sys.exit(main())
