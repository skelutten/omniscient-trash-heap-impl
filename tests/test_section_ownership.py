"""Tests for Section Ownership, byte-verbatim preservation, and E051 fail-closed behavior (OWN-001..003, BODY-003..004, E051)."""

import pytest

from trashheap.authoring import (
    SectionOwnershipError,
    extract_notes_section,
    regenerate_page,
)


def test_notes_extraction_and_preservation():
    """OWN-002: Human ## Notes section preserved byte-for-byte."""
    body = """# My Document Title

## Summary
Machine generated summary.

## Notes
- User note 1
- User note 2
  - Nested point

## Application & Methodology
Step 1.
"""
    raw_notes, count = extract_notes_section(body)
    assert count == 1
    assert "## Notes\n- User note 1\n- User note 2\n  - Nested point\n\n" == raw_notes


def test_unmodified_regeneration_idempotency():
    """OWN-003: Unmodified regeneration yields byte-identical output."""
    existing_page = """---
id: ENG-SPC-CORE-0001
---

# Title

## Summary
The normative technical specification.

## Notes
User custom insights that MUST NEVER be lost.
"""
    updated_sections = {
        "Summary": "The normative technical specification.",
    }
    regenerated = regenerate_page(existing_page, updated_sections)
    # Re-regenerating should be identical
    regenerated_twice = regenerate_page(regenerated, updated_sections)
    assert regenerated == regenerated_twice


def test_e051_unknown_section_fails_closed():
    """BODY-003 / E051: Unknown non-Notes heading aborts compilation fail-closed."""
    existing_page = """---
id: ENG-SPC-CORE-0001
---

## Summary
A summary.

## CustomUnregisteredSection
Custom machine section not in template.
"""
    updated_sections = {"Summary": "Updated summary"}
    with pytest.raises(SectionOwnershipError) as exc:
        regenerate_page(existing_page, updated_sections)
    assert exc.value.code == "E051"
    assert "Unrecognized non-Notes section" in exc.value.message


def test_e051_multiple_notes_sections_fails_closed():
    """OWN-002 / E051: At most one ## Notes section permitted."""
    existing_page = """---
id: ENG-SPC-CORE-0001
---

## Summary
A summary.

## Notes
Notes 1

## Notes
Notes 2
"""
    updated_sections = {"Summary": "Updated summary"}
    with pytest.raises(SectionOwnershipError) as exc:
        regenerate_page(existing_page, updated_sections)
    assert exc.value.code == "E051"
    assert "Multiple '## Notes' sections" in exc.value.message


def test_body_004_conflict_overwrite():
    """BODY-004: Manually modified machine sections require explicit allow_conflict_overwrite=True."""
    existing_page = """---
id: ENG-SPC-CORE-0001
---

## Summary
Original machine summary that a human modified manually.

## Notes
My notes.
"""
    updated_sections = {"Summary": "New compiler summary generated from data."}

    # 1. Fails without overwrite flag
    with pytest.raises(SectionOwnershipError) as exc:
        regenerate_page(existing_page, updated_sections, allow_conflict_overwrite=False)
    assert exc.value.code == "E051"
    assert "BODY-004" in exc.value.message

    # 2. Succeeds with explicit allow_conflict_overwrite=True
    regenerated = regenerate_page(existing_page, updated_sections, allow_conflict_overwrite=True)
    assert "New compiler summary generated from data." in regenerated
    assert "My notes." in regenerated
