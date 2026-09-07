"""Tests for trashheap init / new subcommand and scaffolding logic."""

import json
import tempfile
from pathlib import Path

from trashheap.cli import main
from trashheap.constants import ExitCode
from trashheap.corpus import load_corpus
from trashheap.init import init_wiki
from trashheap.linter import Linter
from trashheap.registry.loader import load_registries


def test_init_wiki_programmatic():
    """Verify programmatic initialization of a new Knowledge Library."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "my-wiki"
        res = init_wiki(target, name="Test Vault", author="human:alice")
        assert res["status"] == "ok"
        assert res["name"] == "Test Vault"
        assert target.exists()

        # Check schemas were copied
        reg_dir = target / "schemas" / "registry"
        assert (reg_dir / "object_registry.yaml").exists()
        assert (reg_dir / "taxonomy_registry.yaml").exists()
        assert (reg_dir / "relation_registry.yaml").exists()

        # Check Agent Skills
        skill_file = target / ".agents" / "skills" / "trashheap" / "SKILL.md"
        assert skill_file.exists()

        # Check starter note
        seed_note = target / "personal" / "07_computer_science_ai_it_security" / "PERS-DOC-WELCOME-0001.md"
        assert seed_note.exists()
        assert "Welcome to Test Vault" in seed_note.read_text(encoding="utf-8")
        assert "author: human:alice" in seed_note.read_text(encoding="utf-8")

        # Check .gitignore
        gitignore = target / ".gitignore"
        assert gitignore.exists()
        assert ".trashheap/" in gitignore.read_text(encoding="utf-8")

        # Check README.md
        readme = target / "README.md"
        assert readme.exists()
        assert "Test Vault" in readme.read_text(encoding="utf-8")

        # Verify full lint conformance on clean wiki
        regs = load_registries(reg_dir)
        corpus = load_corpus(target)
        assert len(corpus) == 1
        linter = Linter(registries=regs)
        findings = linter.lint_corpus(corpus)
        errors = [f for f in findings if f.level == "ERROR"]
        warnings = [f for f in findings if f.level == "WARNING"]
        assert len(errors) == 0, f"Unexpected errors: {errors}"
        assert len(warnings) == 0, f"Unexpected warnings: {warnings}"


def test_init_cli_flow(capsys):
    """Verify trashheap init CLI command with text and json outputs."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "cli-wiki"
        # 1. Run via CLI
        code = main(["init", str(target), "--name", "CLI Vault"])
        assert code == ExitCode.SUCCESS

        # 2. Non-empty without --force should fail
        code_fail = main(["init", str(target)])
        assert code_fail == ExitCode.CONFIG_OR_ARG_ERROR

        # 3. Non-empty with --force should succeed
        code_force = main(["init", str(target), "--force"])
        assert code_force == ExitCode.SUCCESS

        # Clear captured stdout from previous steps
        _ = capsys.readouterr()

        # 4. JSON output
        target_json = Path(td) / "json-wiki"
        code_json = main(["init", str(target_json), "--json"])
        assert code_json == ExitCode.SUCCESS
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "ok"
        assert "created_files" in data
