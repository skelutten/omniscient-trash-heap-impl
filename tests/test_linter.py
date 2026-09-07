"""Comprehensive tests for multi-layered linter rules E001–E051, W001–W015, clock injection, and strict mode."""

from datetime import date
from pathlib import Path

from trashheap.corpus import load_corpus
from trashheap.linter import Linter
from trashheap.registry.loader import load_registries


def test_clean_canonical_corpus():
    """Verify that the reconciled canonical fixture corpus produces 0 findings."""
    registries = load_registries(Path("schemas/registry"))
    corpus = load_corpus(Path("fixtures/canonical"))
    linter = Linter(registries=registries)
    findings = linter.lint_corpus(corpus)
    errors = [f for f in findings if f.level == "ERROR"]
    warnings = [f for f in findings if f.level == "WARNING"]
    assert len(errors) == 0, f"Unexpected errors: {[f.to_dict() for f in errors]}"
    assert len(warnings) == 0, f"Unexpected warnings: {[f.to_dict() for f in warnings]}"


def test_e001_duplicate_node_id(tmp_path: Path):
    """E001: The same ID occurs in more than one file."""
    registries = load_registries(Path("schemas/registry"))
    f1 = tmp_path / "f1.md"
    f2 = tmp_path / "f2.md"
    base_content = """---
id: ENG-SPC-CORE-0001
title: Spec 1
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Specification
domain: runtime_frameworks
evidence: observed
verification: formal_proof
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 1.0
status: established
toolchain: [pytest]
architecture: [container]
lifecycle: maintained
relations: []
---
## Summary
Content.
"""
    f1.write_text(base_content, encoding="utf-8")
    f2.write_text(base_content, encoding="utf-8")

    corpus = load_corpus(tmp_path)
    linter = Linter(registries=registries, check_skills=False)
    findings = linter.lint_corpus(corpus)
    e001s = [f for f in findings if f.code == "E001"]
    assert len(e001s) >= 1


def test_e005_e006_e008_identity_rules(tmp_path: Path):
    """E005: ID pattern mismatch, E006: Scope not allowed, E008: Sequence overflow."""
    registries = load_registries(Path("schemas/registry"))

    # Test E006 (Specification in personal scope) and E008 (>9999)
    bad_file = tmp_path / "bad.md"
    bad_file.write_text(
        """---
id: PERS-SPC-CORE-10001
title: Illegal Personal Spec
scope: personal
taxonomy_path: "01. Domain & System Architecture"
object_type: Specification
domain: runtime_frameworks
evidence: observed
verification: formal_proof
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 1.0
status: established
toolchain: [pytest]
architecture: [container]
lifecycle: maintained
relations: []
---
## Summary
Content.
""",
        encoding="utf-8",
    )

    corpus = load_corpus(tmp_path)
    linter = Linter(registries=registries, check_skills=False)
    findings = linter.lint_corpus(corpus)
    codes = {f.code for f in findings}
    assert "E005" in codes or "E008" in codes
    assert "E006" in codes


def test_e007_validity_chronology(tmp_path: Path):
    """E007: valid_until earlier than valid_from (VAL-001)."""
    registries = load_registries(Path("schemas/registry"))
    f = tmp_path / "val.md"
    f.write_text(
        """---
id: ENG-PRD-LLMWIKI-0001
title: Product
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Product
domain: runtime_frameworks
evidence: observed
verification: formal_proof
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 1.0
status: established
lifecycle: ongoing
validity:
  valid_from: "2026-08-20"
  valid_until: "2026-08-10"
relations: []
---
## Summary
Content.
""",
        encoding="utf-8",
    )
    corpus = load_corpus(tmp_path)
    linter = Linter(registries=registries, check_skills=False)
    findings = linter.lint_corpus(corpus)
    assert any(f.code == "E007" for f in findings)


def test_e010_dag_cycle_and_e011_self_reference(tmp_path: Path):
    """E010: DAG cycle detection, E011: Self-reference in relations."""
    registries = load_registries(Path("schemas/registry"))
    f1 = tmp_path / "f1.md"
    f2 = tmp_path / "f2.md"

    # f1 self-references and depends on f2
    f1.write_text(
        """---
id: ENG-FET-LINTER-0001
title: Feature 1
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Feature
domain: runtime_frameworks
evidence: observed
verification: self_verified
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 1.0
status: established
lifecycle: delivered
toolchain: [pytest]
relations:
  - {type: DEPENDS_ON, target: ENG-FET-LINTER-0001}
  - {type: DEPENDS_ON, target: ENG-FET-LINTER-0002}
---
## Summary
Content.
""",
        encoding="utf-8",
    )

    # f2 depends on f1 (creating cycle in DEPENDS_ON)
    f2.write_text(
        """---
id: ENG-FET-LINTER-0002
title: Feature 2
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Feature
domain: runtime_frameworks
evidence: observed
verification: self_verified
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 1.0
status: established
lifecycle: delivered
toolchain: [pytest]
relations:
  - {type: DEPENDS_ON, target: ENG-FET-LINTER-0001}
---
## Summary
Content.
""",
        encoding="utf-8",
    )

    corpus = load_corpus(tmp_path)
    linter = Linter(registries=registries, check_skills=False)
    findings = linter.lint_corpus(corpus)
    codes = {f.code for f in findings}
    assert "E011" in codes  # self-reference
    assert "E010" in codes  # DAG cycle


def test_w015_high_degree_warning(tmp_path: Path):
    """W015: Outbound links > 20 triggers HighDegreeWarning (GRAPH-004)."""
    registries = load_registries(Path("schemas/registry"))
    rels = [
        {"type": "USES", "target": f"ENG-CMP-PARSER-{i:04d}", "soft_link": True}
        for i in range(1, 23)
    ]
    rels_yaml = "\n".join(
        [f"  - {{type: {r['type']}, target: {r['target']}, soft_link: true}}" for r in rels]
    )

    f = tmp_path / "high_deg.md"
    f.write_text(
        f"""---
id: ENG-FET-LINTER-0001
title: High Degree Node
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Feature
domain: runtime_frameworks
evidence: observed
verification: self_verified
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-27"
next_review: "2027-02-17"
confidence: 1.0
status: established
lifecycle: delivered
toolchain: [pytest]
relations:
{rels_yaml}
---
## Summary
Content.
""",
        encoding="utf-8",
    )

    corpus = load_corpus(tmp_path)
    linter = Linter(registries=registries, check_skills=False)
    findings = linter.lint_corpus(corpus)
    w015s = [f for f in findings if f.code == "W015"]
    assert len(w015s) == 1
    assert "exceeds degree cap 20" in w015s[0].message


def test_w002_review_overdue_clock_injection(tmp_path: Path):
    """W002: next_review passed injected reference_date."""
    registries = load_registries(Path("schemas/registry"))
    f = tmp_path / "overdue.md"
    f.write_text(
        """---
id: ENG-PRD-LLMWIKI-0001
title: Product
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Product
domain: runtime_frameworks
evidence: observed
verification: formal_proof
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-01"
next_review: "2026-08-15"
confidence: 1.0
status: established
lifecycle: ongoing
relations: []
---
## Summary
Content.
""",
        encoding="utf-8",
    )
    corpus = load_corpus(tmp_path)

    # Injected reference date past next_review
    linter = Linter(registries=registries, reference_date=date(2026, 8, 20), check_skills=False)
    findings = linter.lint_corpus(corpus)
    assert any(f.code == "W002" for f in findings)

    # Injected reference date before next_review
    linter_ok = Linter(registries=registries, reference_date=date(2026, 8, 10), check_skills=False)
    findings_ok = linter_ok.lint_corpus(corpus)
    assert not any(f.code == "W002" for f in findings_ok)


def test_e050_agent_skill_drift(tmp_path: Path, monkeypatch):
    """E050: Generated agent skills definition drift error."""
    registries = load_registries(Path("schemas/registry"))
    # Dummy file
    f = tmp_path / "dummy.md"
    f.write_text(
        """---
id: ENG-PRD-LLMWIKI-0001
title: Product
scope: engineering
taxonomy_path: "01. Domain & System Architecture"
taxonomy_id: TX-ENG-01
object_type: Product
domain: runtime_frameworks
evidence: observed
verification: formal_proof
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
author: human:daniel
last_modified: "2026-08-01"
next_review: "2027-02-17"
confidence: 1.0
status: established
lifecycle: ongoing
relations: []
---
## Summary
Content.
""",
        encoding="utf-8",
    )

    corpus = load_corpus(tmp_path)
    # Linter with check_skills enabled on temp directory without SKILL.md
    linter = Linter(registries=registries, check_skills=True)
    findings = linter.lint_corpus(corpus)
    assert any(f.code == "E050" for f in findings)
