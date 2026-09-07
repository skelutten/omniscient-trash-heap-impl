"""Tests for registry loading, validation, and error detection."""

import json
from pathlib import Path

from trashheap.cli import main
from trashheap.constants import ExitCode
from trashheap.registry.loader import load_registries
from trashheap.registry.models import (
    InvariantFamilyOwnership,
    SpecOwnershipModel,
    ThresholdEntry,
    ThresholdPolicyModel,
)
from trashheap.registry.validator import (
    validate_cross_registries,
    validate_spec_ownership,
    validate_threshold_policy,
)


def test_all_registries_load():
    """Verify all 10 canonical registries load without error."""
    loaded = load_registries()
    assert len(loaded.object_types) == 25
    assert len(loaded.domains) > 0
    assert len(loaded.relations) == 30
    assert len(loaded.taxonomy) > 0
    assert len(loaded.facets) > 0
    assert len(loaded.raw) == 10


def test_spec_ownership_validation():
    """Verify spec_ownership has single owners and existing file paths."""
    repo_root = Path.cwd()
    loaded = load_registries()
    findings = validate_spec_ownership(loaded.spec_ownership, repo_root)
    errors = [f for f in findings if f.level == "ERROR"]
    assert len(errors) == 0, f"Expected 0 errors, got: {errors}"


def test_spec_ownership_duplicate_detection():
    """Verify duplicate family owner raises E080."""
    repo_root = Path.cwd()
    loaded = load_registries()
    duplicated_families = list(loaded.spec_ownership.invariant_families)
    duplicated_families.append(
        InvariantFamilyOwnership(family_id="CANON", owner="specs/ARCHITECTURE.md")
    )
    mock_spec = SpecOwnershipModel(
        schema_version="0.2.0",
        registry_id="spec_ownership",
        status="declarative_only",
        invariant_families=duplicated_families,
        validation=loaded.spec_ownership.validation,
    )
    findings = validate_spec_ownership(mock_spec, repo_root)
    codes = [f.code for f in findings]
    assert "E080" in codes


def test_spec_ownership_missing_file_detection():
    """Verify unknown owner file raises E081."""
    repo_root = Path.cwd()
    loaded = load_registries()
    bad_families = list(loaded.spec_ownership.invariant_families)
    bad_families.append(InvariantFamilyOwnership(family_id="FAKE", owner="specs/DOES_NOT_EXIST.md"))
    mock_spec = SpecOwnershipModel(
        schema_version="0.2.0",
        registry_id="spec_ownership",
        status="declarative_only",
        invariant_families=bad_families,
        validation=loaded.spec_ownership.validation,
    )
    findings = validate_spec_ownership(mock_spec, repo_root)
    codes = [f.code for f in findings]
    assert "E081" in codes


def test_threshold_policy_validation():
    """Verify threshold policy entries are unique and owner files exist."""
    repo_root = Path.cwd()
    loaded = load_registries()
    findings = validate_threshold_policy(loaded.threshold_policy, repo_root)
    errors = [f for f in findings if f.level == "ERROR"]
    assert len(errors) == 0, f"Expected 0 errors, got: {errors}"


def test_threshold_policy_duplicate_detection():
    """Verify duplicate threshold ID raises E082."""
    repo_root = Path.cwd()
    loaded = load_registries()
    entries = list(loaded.threshold_policy.thresholds)
    entries.append(
        ThresholdEntry(
            threshold_id="RETRIEVAL-MAX-DEPTH",
            decision_domain="graph_expansion",
            value=2,
            unit="hops",
            owner="specs/RETRIEVAL.md",
        )
    )
    mock_policy = ThresholdPolicyModel(
        schema_version="0.1.0",
        policy_id="threshold_policy",
        thresholds=entries,
        rules=loaded.threshold_policy.rules,
    )
    findings = validate_threshold_policy(mock_policy, repo_root)
    codes = [f.code for f in findings]
    assert "E082" in codes


def test_cross_registry_validation():
    """Verify entire canonical registry set passes cross-validation."""
    repo_root = Path.cwd()
    loaded = load_registries()
    findings = validate_cross_registries(loaded, repo_root)
    errors = [f for f in findings if f.level == "ERROR"]
    assert len(errors) == 0, f"Expected 0 errors, got: {errors}"


def test_cli_check_registries(capsys):
    """Verify CLI command check-registries runs successfully."""
    exit_code = main(["check-registries"])
    assert exit_code == ExitCode.SUCCESS
    captured = capsys.readouterr()
    assert "All 10 YAML registries loaded and verified successfully" in captured.out


def test_cli_check_registries_json(capsys):
    """Verify CLI command check-registries --json outputs valid JSON."""
    exit_code = main(["check-registries", "--json"])
    assert exit_code == ExitCode.SUCCESS
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "passed"
    assert data["summary"]["errors"] == 0
    assert data["summary"]["passed"] is True
