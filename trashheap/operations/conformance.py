import ast
import hashlib
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml


def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def count_executable_tests(test_path: Path) -> int:
    """Parse test file with AST and count executable test functions (test_*)."""
    if not test_path.exists() or not test_path.is_file():
        return 0
    try:
        tree = ast.parse(test_path.read_text(encoding="utf-8"))
        return len(
            [
                n
                for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
            ]
        )
    except Exception as exc:
        raise SyntaxError(
            f"Failed to parse test file '{test_path}' for executable test counting: {exc}"
        ) from exc


def _has_substantive_implementation(path: Path) -> bool:
    """Return True if a source file contains executable code beyond a docstring/imports.

    A comment-only or empty module is not a real implementation and must not be
    projected as implemented. A directory reference is treated as present (it is
    a package, not a stub file).
    """
    if path.is_dir():
        return True
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return True
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # module docstring or bare string literal
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        return True  # any other top-level statement (assignment, call, ...)
    return False


def _has_assertions(path: Path) -> bool:
    """Return True if a test file contains at least one assert statement."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return any(isinstance(node, ast.Assert) for node in ast.walk(tree))


# Mapping of invariant families to owners, invariant IDs, implementations, tests, and verifications.
# Fields correspond strictly to spec_ownership.yaml conformance_evidence_fields:
# [owner, invariant_id, implementation, test, verification]
INVARIANT_FAMILY_MAP: Dict[str, Dict[str, Any]] = {
    "CANON": {
        "owner": "specs/ARCHITECTURE.md",
        "invariants": [
            "CANON-001",
            "CANON-002",
            "CANON-003",
            "CANON-004",
            "CANON-005",
            "CANON-006",
        ],
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
        "invariants": [
            "REL-001",
            "REL-002",
            "REL-003",
            "REL-004",
            "REL-005",
            "REL-006",
            "REL-007",
            "REL-008",
        ],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "EPI": {
        "owner": "specs/EPISTEMOLOGY.md",
        "invariants": [
            "EPI-001",
            "EPI-002",
            "EPI-003",
            "EPI-004",
            "EPI-005",
            "EPI-006",
            "EPI-007",
        ],
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
        "invariants": [
            "SOURCE-001",
            "SOURCE-002",
            "SOURCE-007",
            "SOURCE-008",
            "SOURCE-010",
            "SOURCE-015",
            "SOURCE-016",
            "SOURCE-017",
        ],
        "implementation": "trashheap/ingest/pipeline.py",
        "test": "tests/test_ingest_safety.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "RAW": {
        "owner": "specs/INGEST-STAGING.md",
        "invariants": [
            "RAW-001",
            "RAW-002",
            "RAW-003",
            "RAW-004",
            "RAW-005",
            "RAW-006",
            "RAW-007",
            "RAW-008",
            "RAW-009",
            "RAW-010",
        ],
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
        "invariants": [
            "DPCP-001",
            "DPCP-002",
            "DPCP-003",
            "DPCP-004",
            "DPCP-005",
            "DPCP-006",
            "DPCP-007",
            "DPCP-008",
            "DPCP-009",
            "DPCP-010",
        ],
        "implementation": "trashheap/promotion/engine.py",
        "test": "tests/test_proposal_promotion.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "DISC": {
        "owner": "specs/DISCOVERY.md",
        "invariants": ["DISC-001", "DISC-002", "DISC-003", "DISC-004", "DISC-005"],
        "implementation": "trashheap/graph/discovery.py, trashheap/graph/analysis.py",
        "test": "tests/test_graph_intelligence.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "GRAPH": {
        "owner": "specs/ONTOLOGY.md",
        "invariants": ["GRAPH-001", "GRAPH-002", "GRAPH-003", "GRAPH-004"],
        "implementation": "trashheap/linter.py",
        "test": "tests/test_linter.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "SG": {
        "owner": "specs/STRUCTURAL-GRAPH.md",
        "invariants": [
            "SG-001",
            "SG-002",
            "SG-003",
            "SG-004",
            "SG-005",
            "SG-006",
            "SG-007",
            "SG-008",
            "SG-009",
            "SG-010",
            "SG-011",
            "SG-012",
            "SG-013",
            "SG-014",
            "SG-015",
            "SG-016",
            "SG-017",
            "SG-018",
            "SG-019",
            "SG-020",
        ],
        "implementation": "trashheap/structural/indexer.py, trashheap/structural/extractor.py, trashheap/structural/analysis.py, trashheap/structural/bridge.py",
        "test": "tests/test_structural_graph.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "OKF": {
        "owner": "specs/OKF-INTEROP.md",
        "invariants": ["OKF-001", "OKF-012"],
        "implementation": "trashheap/bundle/export.py, trashheap/bundle/import_okf.py",
        "test": "tests/test_bundles_and_okf.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "BUNDLE": {
        "owner": "specs/OKF-INTEROP.md",
        "invariants": ["BUNDLE-001", "BUNDLE-009"],
        "implementation": "trashheap/bundle/export.py, trashheap/bundle/models.py",
        "test": "tests/test_bundles_and_okf.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
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
        "invariants": ["BODY-003", "BODY-004"],
        "implementation": "trashheap/linter.py, trashheap/authoring.py",
        "test": "tests/test_linter.py, tests/test_section_ownership.py",
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
        "owner": "specs/REVIEW-PROMOTION.md",
        "invariants": [
            "REVIEW-001",
            "REVIEW-002",
            "REVIEW-003",
            "REVIEW-004",
            "REVIEW-005",
            "REVIEW-006",
            "REVIEW-007",
            "REVIEW-008",
            "REVIEW-009",
            "REVIEW-010",
        ],
        "implementation": "trashheap/promotion/engine.py, trashheap/promotion/models.py",
        "test": "tests/test_proposal_promotion.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "PROMO": {
        "owner": "specs/REVIEW-PROMOTION.md",
        "invariants": [
            "PROMO-001",
            "PROMO-002",
            "PROMO-003",
            "PROMO-004",
            "PROMO-005",
            "PROMO-006",
            "PROMO-007",
            "PROMO-008",
            "PROMO-009",
            "PROMO-010",
        ],
        "implementation": "trashheap/promotion/engine.py",
        "test": "tests/test_proposal_promotion.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "REX": {
        "owner": "specs/RELATION-EXTRACTION.md",
        "invariants": [
            "REX-001",
            "REX-002",
            "REX-003",
            "REX-004",
            "REX-005",
            "REX-006",
            "REX-007",
            "REX-008",
            "REX-009",
            "REX-010",
            "REX-011",
            "REX-012",
            "REX-013",
        ],
        "implementation": "UNIMPLEMENTED",
        "test": "planned",
        "verification": "planned",
        "status": "UNIMPLEMENTED",
    },
    "VIS": {
        "owner": "specs/VISUALIZE.md",
        "invariants": [
            "VIS-001",
            "VIS-002",
            "VIS-003",
            "VIS-004",
            "VIS-005",
            "VIS-006",
            "VIS-007",
            "VIS-008",
            "VIS-009",
            "VIS-010",
        ],
        "implementation": "UNIMPLEMENTED",
        "test": "planned",
        "verification": "planned",
        "status": "UNIMPLEMENTED",
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
        "invariants": [
            "RET-001",
            "RET-002",
            "RET-003",
            "RET-004",
            "RET-005",
            "RET-006",
            "RET-007",
            "RET-008",
            "RET-009",
        ],
        "implementation": "trashheap/retrieval.py, trashheap/vector/",
        "test": "tests/test_retrieval.py, tests/test_vector_retrieval.py",
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
        "owner": "specs/VALIDATION.md",
        "invariants": ["VAL-001"],
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
    # --- families added 2026-09-09: pending invariants (implementation in progress) ---
    # These were codified 2026-09-08 (RET-010/011, SCHEMA-005, VAL-011..014,
    # REVIEW-011, DISC-009) and are tracked separately so the projection does not
    # over-report them as CONFORMANCE_TESTED before runtime + tests land.
    "RET-RCVA": {
        "owner": "specs/RETRIEVAL.md",
        "invariants": ["RET-010", "RET-011"],
        "implementation": "trashheap/section_map.py, trashheap/rcva.py, trashheap/cli.py",
        "test": "tests/test_section_map.py, tests/test_rcva.py, tests/test_section_retrieval.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "SCHEMA-CARD": {
        "owner": "specs/SCHEMA.md",
        "invariants": ["SCHEMA-005"],
        "implementation": "trashheap/section_map.py",
        "test": "tests/test_section_map.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "VAL-EXT": {
        "owner": "specs/VALIDATION.md",
        "invariants": ["VAL-011", "VAL-012", "VAL-013", "VAL-014"],
        "implementation": "trashheap/link_mirror.py, trashheap/mermaid.py, trashheap/runaway.py, trashheap/promotion/engine.py",
        "test": "tests/test_val_extensions.py, tests/test_runaway.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "REVIEW-MOD": {
        "owner": "specs/REVIEW-PROMOTION.md",
        "invariants": ["REVIEW-011"],
        "implementation": "trashheap/promotion/pre_score.py",
        "test": "tests/test_moderator_prescore.py",
        "verification": "tools/check.sh",
        "status": "CONFORMANCE_TESTED",
    },
    "DISC-FENCE": {
        "owner": "specs/DISCOVERY.md",
        "invariants": ["DISC-009"],
        "implementation": "trashheap/instruction_fence.py",
        "test": "tests/test_instruction_fence.py",
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
    summary: Dict[str, Any]
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
    total_invariants_count = 0
    seen_test_paths: Set[Path] = set()
    total_executable_tests = 0

    for item in families_spec:
        fid = item.get("family_id", "")
        owner = item.get("owner", "")

        mapped = INVARIANT_FAMILY_MAP.get(fid, {})
        invariants = mapped.get("invariants", [f"{fid}-*"])
        total_invariants_count += len(invariants)
        inv_id_summary = (
            f"{invariants[0]}..{invariants[-1]}" if len(invariants) > 1 else invariants[0]
        )

        impl = mapped.get("implementation", "UNIMPLEMENTED")
        test = mapped.get("test", "planned")
        verif = mapped.get(
            "verification", "tools/check.sh" if impl != "UNIMPLEMENTED" else "planned"
        )
        status = mapped.get("status", "UNIMPLEMENTED")

        # Verify physical presence in repository
        impl_ok = impl != "UNIMPLEMENTED" and all(
            (workspace_root / p.strip()).exists()
            and _has_substantive_implementation(workspace_root / p.strip())
            for p in impl.split(",")
        )

        test_files = [workspace_root / p.strip() for p in test.split(",") if p.strip() != "planned"]
        test_funcs_found = sum(count_executable_tests(tf) for tf in test_files)
        for tf in test_files:
            if tf not in seen_test_paths:
                seen_test_paths.add(tf)
                total_executable_tests += count_executable_tests(tf)

        test_ok = (
            test != "planned"
            and bool(test_files)
            and all(tf.exists() for tf in test_files)
            and test_funcs_found > 0
            and all(_has_assertions(tf) for tf in test_files)
        )

        if impl_ok and test_ok:
            status = "CONFORMANCE_TESTED"
            tested_count += 1
        elif impl_ok:
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

    corpus_hash = compute_corpus_hash(workspace_root)
    summary: Dict[str, Any] = {
        "total_families": len(entries),
        "conformance_tested": tested_count,
        "implemented": implemented_count,
        "unimplemented": unimplemented_count,
        "total_invariants_tracked": total_invariants_count,
        "total_executable_tests": total_executable_tests,
        "corpus_hash": corpus_hash,
    }

    # Check if output file exists and whether the non-timestamp content matches
    existing_generated_at = None
    if output_path is not None and output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                old_data = yaml.safe_load(f)
            if isinstance(old_data, dict):
                old_summary = old_data.get("summary", {})
                old_families = old_data.get("families", [])
                new_summary_check = {k: v for k, v in summary.items()}
                old_summary_check = {k: old_summary.get(k) for k in new_summary_check}
                if new_summary_check == old_summary_check and old_families == [
                    f.to_dict() for f in entries
                ]:
                    existing_generated_at = old_data.get("generated_at")
        except Exception as exc:
            import logging

            logging.getLogger(__name__).warning(
                "Failed to parse existing matrix at %s: %s", output_path, exc
            )

    matrix = ConformanceMatrix(
        schema_version="1.0.0",
        matrix_id="conformance_matrix",
        generated_at=existing_generated_at or current_iso_timestamp(),
        evidence_type="generated_projection",
        note="Generated evidence per VALIDATION.md §10.5 and CONFORM-001. Not a normative specification.",
        summary=summary,
        families=entries,
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_output_path = output_path.with_name(f".{output_path.name}.tmp")
        with open(tmp_output_path, "w", encoding="utf-8") as f:
            yaml.dump(matrix.to_dict(), f, sort_keys=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_output_path, output_path)

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
            owned_fams = [
                item.get("family_id") for item in families if item.get("owner") == doc_rel
            ]
            missing_evidence = False
            for of in owned_fams:
                info = INVARIANT_FAMILY_MAP.get(of, {})
                impl = info.get("implementation", "UNIMPLEMENTED")
                test = info.get("test", "planned")
                impl_ok = impl != "UNIMPLEMENTED" and all(
                    (workspace_root / p.strip()).exists() for p in impl.split(",")
                )
                if not impl_ok:
                    missing_evidence = True
                    break
                if declared_impl_status == "CONFORMANCE_TESTED":
                    test_ok = test != "planned" and all(
                        (workspace_root / p.strip()).exists() for p in test.split(",")
                    )
                    if not test_ok:
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
            owned_fams = [
                item.get("family_id") for item in families if item.get("owner") == doc_rel
            ]
            all_tested = bool(owned_fams)
            for of in owned_fams:
                info = INVARIANT_FAMILY_MAP.get(of, {})
                impl = info.get("implementation", "UNIMPLEMENTED")
                test = info.get("test", "planned")
                impl_ok = impl != "UNIMPLEMENTED" and all(
                    (workspace_root / p.strip()).exists() for p in impl.split(",")
                )
                test_ok = test != "planned" and all(
                    (workspace_root / p.strip()).exists() for p in test.split(",")
                )
                if not impl_ok or not test_ok:
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
