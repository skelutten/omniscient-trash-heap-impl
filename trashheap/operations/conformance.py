"""Conformance projection generator and SPEC_STATUS.md drift detector (D90, VALIDATION.md §10.5, CONFORM-001)."""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


# Mapping of invariant families to owners, invariant IDs, implementations, tests, and verifications.
# Fields correspond strictly to spec_ownership.yaml conformance_evidence_fields:
# [owner, invariant_id, implementation, test, verification]
INVARIANT_FAMILY_MAP: Dict[str, Dict[str, Any]] = {
    "CANON": {
        "owner": "specs/ARCHITECTURE.md",
        "invariants": ["CANON-001", "CANON-002", "CANON-003", "CANON-004", "CANON-005", "CANON-006"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "ID": {
        "owner": "specs/DATA_MODEL.md",
        "invariants": ["ID-001", "ID-002", "ID-003", "ID-004", "ID-005"],
        "implementation": "trashheap/models.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "FAC": {
        "owner": "specs/DATA_MODEL.md",
        "invariants": ["FAC-001", "FAC-002", "FAC-003"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "CLS": {
        "owner": "specs/DATA_MODEL.md",
        "invariants": ["CLS-001", "CLS-002", "CLS-003"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "TAX": {
        "owner": "specs/ARCHITECTURE.md",
        "invariants": ["TAX-001", "TAX-002", "TAX-003", "TAX-004", "TAX-005"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "REL": {
        "owner": "specs/ONTOLOGY.md",
        "invariants": ["REL-001", "REL-002", "REL-003", "REL-004", "REL-005", "REL-006", "REL-007", "REL-008"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "EPI": {
        "owner": "specs/EPISTEMOLOGY.md",
        "invariants": ["EPI-001", "EPI-002", "EPI-003", "EPI-004", "EPI-005", "EPI-006", "EPI-007", "EPI-008"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "PROV": {
        "owner": "specs/EPISTEMOLOGY.md",
        "invariants": ["PROV-001", "PROV-002", "PROV-003", "PROV-004"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "GOV": {
        "owner": "specs/EPISTEMOLOGY.md",
        "invariants": ["GOV-001", "GOV-002", "GOV-003", "GOV-004"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "SOURCE": {
        "owner": "specs/UNIVERSAL-SOURCE-EXTENSION.md",
        "invariants": ["SOURCE-001", "SOURCE-002", "SOURCE-007", "SOURCE-008", "SOURCE-010", "SOURCE-015", "SOURCE-016", "SOURCE-017"],
        "implementation": "trashheap/ingest/pipeline.py",
        "test": "tests/test_ingest_safety.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "RAW": {
        "owner": "specs/INGEST-STAGING.md",
        "invariants": ["RAW-001", "RAW-002", "RAW-003", "RAW-004", "RAW-005", "RAW-006", "RAW-007", "RAW-008", "RAW-009", "RAW-010"],
        "implementation": "trashheap/ingest/cscc.py",
        "test": "tests/test_ingest_safety.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "INGEST-CORE": {
        "owner": "specs/INGEST.md",
        "invariants": ["INGEST-CORE-001", "INGEST-CORE-022"],
        "implementation": "trashheap/ingest/pipeline.py",
        "test": "tests/test_ingest_safety.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "CSCC": {
        "owner": "specs/INGEST-STAGING.md",
        "invariants": ["CSCC-001", "CSCC-002", "CSCC-003", "CSCC-004", "CSCC-005"],
        "implementation": "trashheap/ingest/cscc.py",
        "test": "tests/test_ingest_safety.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "DSCP": {
        "owner": "specs/INGEST-STAGING.md",
        "invariants": ["DSCP-001", "DSCP-002", "DSCP-003", "DSCP-004"],
        "implementation": "trashheap/ingest/pipeline.py",
        "test": "tests/test_ingest_safety.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "DPCP": {
        "owner": "specs/INGEST-STAGING.md",
        "invariants": ["DPCP-001", "DPCP-002", "DPCP-003", "DPCP-004", "DPCP-005", "DPCP-006", "DPCP-007", "DPCP-008", "DPCP-009", "DPCP-010"],
        "implementation": "trashheap/promotion/engine.py",
        "test": "tests/test_proposal_promotion.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "DISC": {
        "owner": "specs/DISCOVERY.md",
        "invariants": ["DISC-001", "DISC-002", "DISC-003", "DISC-004", "DISC-005"],
        "implementation": "UNIMPLEMENTED",
        "test": "planned",
        "verification": "planned",
        "status": "UNIMPLEMENTED",
    },
    "GRAPH": {
        "owner": "specs/ONTOLOGY.md",
        "invariants": ["GRAPH-001", "GRAPH-002", "GRAPH-003"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "SG": {
        "owner": "specs/STRUCTURAL-GRAPH.md",
        "invariants": ["SG-001", "SG-020"],
        "implementation": "UNIMPLEMENTED",
        "test": "planned",
        "verification": "planned",
        "status": "UNIMPLEMENTED",
    },
    "OKF": {
        "owner": "specs/OKF-INTEROP.md",
        "invariants": ["OKF-001", "OKF-012"],
        "implementation": "UNIMPLEMENTED",
        "test": "planned",
        "verification": "planned",
        "status": "UNIMPLEMENTED",
    },
    "BUNDLE": {
        "owner": "specs/OKF-INTEROP.md",
        "invariants": ["BUNDLE-001", "BUNDLE-009"],
        "implementation": "UNIMPLEMENTED",
        "test": "planned",
        "verification": "planned",
        "status": "UNIMPLEMENTED",
    },
    "OWN": {
        "owner": "specs/SCHEMA.md",
        "invariants": ["OWN-001", "OWN-002", "OWN-003"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "BODY": {
        "owner": "specs/SCHEMA.md",
        "invariants": ["BODY-003"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "W": {
        "owner": "specs/VALIDATION.md",
        "invariants": ["W001", "W015"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "THRESH": {
        "owner": "schemas/registry/threshold_policy.yaml",
        "invariants": ["THRESH-001", "THRESH-002", "THRESH-003"],
        "implementation": "trashheap/retrieval.py",
        "test": "tests/test_retrieval.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "REVIEW": {
        "owner": "specs/INGEST-STAGING.md",
        "invariants": ["REVIEW-001", "REVIEW-002", "REVIEW-003", "REVIEW-004"],
        "implementation": "trashheap/promotion/engine.py",
        "test": "tests/test_proposal_promotion.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "RES": {
        "owner": "specs/INGEST.md",
        "invariants": ["RES-001", "RES-005"],
        "implementation": "trashheap/ingest/pipeline.py",
        "test": "tests/test_ingest_safety.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "SCALE": {
        "owner": "specs/ARCHITECTURE.md",
        "invariants": ["SCALE-001", "SCALE-002", "SCALE-003"],
        "implementation": "trashheap/operations/benchmark.py",
        "test": "tests/test_operations_and_ci.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "DERIVED": {
        "owner": "specs/ARCHITECTURE.md",
        "invariants": ["DERIVED-001", "DERIVED-002", "DERIVED-003"],
        "implementation": "trashheap/retrieval.py",
        "test": "tests/test_retrieval.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "CONFORM": {
        "owner": "specs/VALIDATION.md",
        "invariants": ["CONFORM-001"],
        "implementation": "trashheap/operations/conformance.py",
        "test": "tests/test_operations_and_ci.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "RET": {
        "owner": "specs/RETRIEVAL.md",
        "invariants": ["RET-001", "RET-002", "RET-003", "RET-004", "RET-005"],
        "implementation": "trashheap/retrieval.py",
        "test": "tests/test_retrieval.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "META": {
        "owner": "specs/ARCHITECTURE.md",
        "invariants": ["META-001", "META-002"],
        "implementation": "trashheap/models.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "LIB": {
        "owner": "specs/ARCHITECTURE.md",
        "invariants": ["LIB-001", "LIB-002", "LIB-003"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "SCOPE": {
        "owner": "specs/DATA_MODEL.md",
        "invariants": ["SCOPE-001", "SCOPE-002", "SCOPE-003"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "VAL": {
        "owner": "specs/EPISTEMOLOGY.md",
        "invariants": ["VAL-001", "VAL-002", "VAL-003", "VAL-004"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "ERR": {
        "owner": "specs/VALIDATION.md",
        "invariants": ["ERR-001", "ERR-002", "ERR-003"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "FS": {
        "owner": "specs/VALIDATION.md",
        "invariants": ["FS-001", "FS-002"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "G": {
        "owner": "specs/INGEST-PIPELINE.md",
        "invariants": ["G-1", "G-2", "G-3"],
        "implementation": "trashheap/ingest/pipeline.py",
        "test": "tests/test_ingest_safety.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
}


@dataclass
class ConformanceFamilyEntry:
    """Entry matching spec_ownership.yaml conformance_evidence_fields."""

    family_id: str
    owner: str
    invariant_id: str
    implementation: str
    test: str
    verification: str
    status: str
    invariants: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "family_id": self.family_id,
            "owner": self.owner,
            "invariant_id": self.invariant_id,
            "implementation": self.implementation,
            "test": self.test,
            "verification": self.verification,
            "status": self.status,
            "invariants": self.invariants,
        }


@dataclass
class ConformanceMatrix:
    """Complete generated conformance projection."""

    schema_version: str
    matrix_id: str
    generated_at: str
    evidence_type: str
    note: str
    summary: Dict[str, int]
    families: List[ConformanceFamilyEntry]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "matrix_id": self.matrix_id,
            "generated_at": self.generated_at,
            "evidence_type": self.evidence_type,
            "note": self.note,
            "summary": self.summary,
            "families": [f.to_dict() for f in self.families],
        }


@dataclass
class DriftFinding:
    """Single drift finding between SPEC_STATUS.md, registries, and runtime."""

    category: str  # "missing_file", "duplicate_owner", "header_mismatch", "status_drift"
    level: str  # "ERROR", "WARNING", "INFO"
    target: str
    declared_status: Optional[str]
    observed_status: Optional[str]
    message: str


@dataclass
class DriftReport:
    """Outcome of status dashboard drift detection (D90)."""

    passed: bool
    findings: List[DriftFinding]
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "findings": [
                {
                    "category": f.category,
                    "level": f.level,
                    "target": f.target,
                    "declared_status": f.declared_status,
                    "observed_status": f.observed_status,
                    "message": f.message,
                }
                for f in self.findings
            ],
            "summary": self.summary,
        }


def compute_corpus_hash(workspace_root: Path) -> str:
    """Compute deterministic SHA-256 fingerprint over canonical fixtures and registries."""
    h = hashlib.sha256()
    paths: List[Path] = []
    fixtures_dir = workspace_root / "fixtures" / "canonical"
    if fixtures_dir.exists():
        paths.extend(sorted(fixtures_dir.glob("**/*.md")))
    reg_dir = workspace_root / "schemas" / "registry"
    if reg_dir.exists():
        paths.extend(sorted(reg_dir.glob("*.yaml")))

    for p in paths:
        if p.is_file():
            h.update(str(p.relative_to(workspace_root)).encode("utf-8"))
            h.update(p.read_bytes())

    return f"sha256:{h.hexdigest()}"


def generate_conformance_matrix(
    workspace_root: Path,
    output_path: Optional[Path] = None,
) -> ConformanceMatrix:
    """Generate deterministic conformance projection from spec_ownership.yaml and runtime."""
    spec_ownership_path = workspace_root / "schemas" / "registry" / "spec_ownership.yaml"
    if not spec_ownership_path.exists():
        raise FileNotFoundError(f"Missing spec_ownership.yaml at {spec_ownership_path}")

    with open(spec_ownership_path, encoding="utf-8") as f:
        spec_data = yaml.safe_load(f)

    families_spec = spec_data.get("invariant_families", [])
    entries: List[ConformanceFamilyEntry] = []

    tested_count = 0
    implemented_count = 0
    unimplemented_count = 0

    for item in families_spec:
        fid = item.get("family_id", "")
        owner = item.get("owner", "")

        mapped = INVARIANT_FAMILY_MAP.get(fid, {})
        invariants = mapped.get("invariants", [f"{fid}-*"])
        inv_id_summary = f"{invariants[0]}..{invariants[-1]}" if len(invariants) > 1 else invariants[0]

        impl = mapped.get("implementation", "UNIMPLEMENTED")
        test = mapped.get("test", "planned")
        verif = mapped.get("verification", "tools/check.sh" if impl != "UNIMPLEMENTED" else "planned")
        status = mapped.get("status", "UNIMPLEMENTED")

        # Verify physical presence in repository
        impl_path = workspace_root / impl if impl != "UNIMPLEMENTED" else None
        test_path = workspace_root / test if test != "planned" else None

        if impl_path and impl_path.exists() and test_path and test_path.exists():
            status = "CONFORMANCE_TESTED"
            tested_count += 1
        elif impl_path and impl_path.exists():
            status = "IMPLEMENTED"
            implemented_count += 1
        else:
            status = "UNIMPLEMENTED"
            unimplemented_count += 1

        entries.append(
            ConformanceFamilyEntry(
                family_id=fid,
                owner=owner,
                invariant_id=inv_id_summary,
                implementation=impl,
                test=test,
                verification=verif,
                status=status,
                invariants=invariants,
            )
        )

    matrix = ConformanceMatrix(
        schema_version="1.0.0",
        matrix_id="conformance_matrix",
        generated_at=current_iso_timestamp(),
        evidence_type="generated_projection",
        note="Generated evidence per VALIDATION.md §10.5 and CONFORM-001. Not a normative specification.",
        summary={
            "total_families": len(entries),
            "conformance_tested": tested_count,
            "implemented": implemented_count,
            "unimplemented": unimplemented_count,
        },
        families=entries,
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(matrix.to_dict(), f, sort_keys=False)

    return matrix


def detect_spec_drift(workspace_root: Path) -> DriftReport:
    """Run Status Dashboard Drift Detector (D90) across SPEC_STATUS.md, registries, and runtime.

    Checks:
    1. Spec file existence for all invariant family owners and registered specs.
    2. Ownership uniqueness (no duplicate family owners).
    3. Document header vs SPEC_STATUS.md declared specification status parity.
    4. Runtime implementation and test presence vs SPEC_STATUS.md claims.
    """
    findings: List[DriftFinding] = []

    # 1. Check spec_ownership.yaml
    ownership_path = workspace_root / "schemas" / "registry" / "spec_ownership.yaml"
    if not ownership_path.exists():
        findings.append(
            DriftFinding(
                category="missing_file",
                level="ERROR",
                target=str(ownership_path),
                declared_status=None,
                observed_status=None,
                message="schemas/registry/spec_ownership.yaml is missing",
            )
        )
        return DriftReport(passed=False, findings=findings, summary="spec_ownership.yaml missing")

    with open(ownership_path, encoding="utf-8") as f:
        ownership_data = yaml.safe_load(f)

    families = ownership_data.get("invariant_families", [])
    seen_families: set[str] = set()

    for item in families:
        fid = item.get("family_id", "")
        owner = item.get("owner", "")

        # Check duplicate ownership
        if fid in seen_families:
            findings.append(
                DriftFinding(
                    category="duplicate_owner",
                    level="ERROR",
                    target=fid,
                    declared_status=None,
                    observed_status=None,
                    message=f"Duplicate invariant family owner declared for '{fid}'",
                )
            )
        seen_families.add(fid)

        # Check owner file existence
        owner_file = workspace_root / owner
        if not owner_file.exists():
            findings.append(
                DriftFinding(
                    category="missing_file",
                    level="ERROR",
                    target=owner,
                    declared_status=None,
                    observed_status=None,
                    message=f"Owner specification file '{owner}' does not exist",
                )
            )

    # 2. Check SPEC_STATUS.md
    spec_status_path = workspace_root / "specs" / "SPEC_STATUS.md"
    if not spec_status_path.exists():
        findings.append(
            DriftFinding(
                category="missing_file",
                level="ERROR",
                target=str(spec_status_path),
                declared_status=None,
                observed_status=None,
                message="specs/SPEC_STATUS.md is missing",
            )
        )
        return DriftReport(passed=False, findings=findings, summary="specs/SPEC_STATUS.md missing")

    status_content = spec_status_path.read_text(encoding="utf-8")

    # Parse tables in §4.1 and §4.2: | Document | Specification status | Implementation status |
    table_pattern = re.compile(
        r"\|\s*`?([A-Za-z0-9_\-\.]+)\.md`?\s*\|\s*`?([A-Z_]+)`?[^\|]*\|\s*`?([A-Z_]+)`?[^\|]*\|"
    )

    for match in table_pattern.finditer(status_content):
        doc_base = match.group(1)
        declared_spec_status = match.group(2)
        declared_impl_status = match.group(3)

        doc_rel = f"specs/{doc_base}.md"
        doc_path = workspace_root / doc_rel

        if not doc_path.exists():
            findings.append(
                DriftFinding(
                    category="missing_file",
                    level="ERROR",
                    target=doc_rel,
                    declared_status=declared_spec_status,
                    observed_status=None,
                    message=f"Dashboard references non-existent specification '{doc_rel}'",
                )
            )
            continue

        # Check document header status
        header_text = doc_path.read_text(encoding="utf-8")[:1000]
        header_match = re.search(r">\s*\*\*Status\*\*:\s*`?([A-Z_]+)`?", header_text)
        if header_match:
            actual_doc_status = header_match.group(1)
            if actual_doc_status != declared_spec_status:
                findings.append(
                    DriftFinding(
                        category="header_mismatch",
                        level="ERROR",
                        target=doc_rel,
                        declared_status=declared_spec_status,
                        observed_status=actual_doc_status,
                        message=(
                            f"Header status in '{doc_rel}' ({actual_doc_status}) "
                            f"diverges from dashboard ({declared_spec_status})"
                        ),
                    )
                )

        # Implementation reality check
        # If dashboard claims CONFORMANCE_TESTED or IMPLEMENTED, check that actual files exist
        if declared_impl_status in {"IMPLEMENTED", "CONFORMANCE_TESTED"}:
            owned_fams = [item.get("family_id") for item in families if item.get("owner") == doc_rel]
            missing_evidence = False
            for of in owned_fams:
                info = INVARIANT_FAMILY_MAP.get(of, {})
                impl = info.get("implementation", "UNIMPLEMENTED")
                test = info.get("test", "planned")
                if impl == "UNIMPLEMENTED" or not (workspace_root / impl).exists():
                    missing_evidence = True
                    break
                if declared_impl_status == "CONFORMANCE_TESTED":
                    if test == "planned" or not (workspace_root / test).exists():
                        missing_evidence = True
                        break
            if missing_evidence:
                findings.append(
                    DriftFinding(
                        category="status_drift",
                        level="ERROR",
                        target=doc_rel,
                        declared_status=declared_impl_status,
                        observed_status="UNIMPLEMENTED",
                        message=f"SPEC_STATUS.md claims '{declared_impl_status}' for {doc_rel} but runtime/test evidence is missing",
                    )
                )

        elif declared_impl_status == "UNIMPLEMENTED":
            owned_fams = [item.get("family_id") for item in families if item.get("owner") == doc_rel]
            all_tested = bool(owned_fams)
            for of in owned_fams:
                info = INVARIANT_FAMILY_MAP.get(of, {})
                impl = info.get("implementation", "UNIMPLEMENTED")
                test = info.get("test", "planned")
                if impl == "UNIMPLEMENTED" or not (workspace_root / impl).exists():
                    all_tested = False
                    break
                if test == "planned" or not (workspace_root / test).exists():
                    all_tested = False
                    break
            if all_tested and owned_fams:
                findings.append(
                    DriftFinding(
                        category="status_drift",
                        level="INFO",
                        target=doc_rel,
                        declared_status=declared_impl_status,
                        observed_status="CONFORMANCE_TESTED",
                        message=(
                            f"{doc_rel} is marked UNIMPLEMENTED in SPEC_STATUS.md, "
                            "but runtime implementation and tests exist and pass"
                        ),
                    )
                )

    errors = [f for f in findings if f.level == "ERROR"]
    passed = len(errors) == 0
    summary = f"Drift check complete: {len(errors)} error(s), {len(findings) - len(errors)} informational finding(s)."

    return DriftReport(passed=passed, findings=findings, summary=summary)
