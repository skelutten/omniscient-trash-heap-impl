"""Tests for slugification, ancestor chain, cycle detection, and directory resolution (TAX-002, TAX-003, TAX-006)."""

import pytest

from trashheap.slug import ancestor_chain, normalize_segment, slugify_text, taxonomy_id_to_directory


def test_slugify_text():
    assert slugify_text("Domain & System Architecture") == "domain_system_architecture"
    assert slugify_text("AI-Assisted Software Engineering!") == "ai_assisted_software_engineering"
    assert slugify_text("Örebro & København") == "orebro_kobenhavn"


def test_normalize_segment():
    assert normalize_segment("01. Domain & System Architecture") == "01_domain_system_architecture"
    assert (
        normalize_segment("07.04. AI-Assisted Software Engineering")
        == "07_04_ai_assisted_software_engineering"
    )
    assert normalize_segment("No Number Prefix") == "no_number_prefix"


def test_ancestor_chain_and_directory():
    tax_dict = {
        "TX-ENG-01": {
            "name": "01. Domain & System Architecture",
            "parent_id": None,
            "scope": "engineering",
        },
        "TX-ENG-01-01": {
            "name": "01.01. Core Platform Architecture",
            "parent_id": "TX-ENG-01",
            "scope": "engineering",
        },
    }

    chain = ancestor_chain(tax_dict, "TX-ENG-01-01")
    assert chain == ["01. Domain & System Architecture", "01.01. Core Platform Architecture"]

    dir_path = taxonomy_id_to_directory(tax_dict, "engineering", "TX-ENG-01-01")
    assert dir_path == "engineering/01_domain_system_architecture/01_01_core_platform_architecture/"


def test_ancestor_chain_cycle_detection():
    """TAX-006 / E024: Cycle detected in taxonomy hierarchy."""
    cyclic_tax_dict = {
        "NODE-A": {"name": "Node A", "parent_id": "NODE-B", "scope": "engineering"},
        "NODE-B": {"name": "Node B", "parent_id": "NODE-A", "scope": "engineering"},
    }
    with pytest.raises(ValueError) as exc:
        ancestor_chain(cyclic_tax_dict, "NODE-A")
    assert "Taxonomy cycle detected" in str(exc.value)


def test_ancestor_chain_missing_parent():
    """TAX-005 / E018: Missing parent node."""
    broken_tax_dict = {
        "NODE-A": {"name": "Node A", "parent_id": "NODE-MISSING", "scope": "engineering"},
    }
    with pytest.raises(KeyError):
        ancestor_chain(broken_tax_dict, "NODE-A")
