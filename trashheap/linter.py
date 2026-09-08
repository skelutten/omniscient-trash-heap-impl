"""Deterministic Multi-Layered Linter enforcing formal error and warning codes.

Follows VALIDATION.md §10–12 and all system invariants (META-001–RET-005).
"""

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from trashheap.constants import (
    ACTOR_PATTERN,
    DOMAIN_TAG_PATTERN,
    ID_PATTERN,
    METADATA_CATEGORIES,
    YEAR_TAG_PATTERN,
)
from trashheap.corpus import Corpus
from trashheap.models import KnowledgeObject
from trashheap.registry.loader import LoadedRegistries
from trashheap.slug import taxonomy_id_to_directory


@dataclass
class Finding:
    """Formal finding contract (VALIDATION.md §10.1, D24)."""

    code: str
    field: Optional[str]
    message: str
    suggestion: Optional[str] = None
    file: Optional[str] = None
    line: Optional[int] = None
    level: str = "ERROR"  # "ERROR" or "WARNING"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "field": self.field,
            "message": self.message,
            "suggestion": self.suggestion,
            "file": self.file,
            "line": self.line,
            "level": self.level,
        }


# Known template headings across Type A-D (SCHEMA.md §7, OWN-001, OWN-002)
KNOWN_TEMPLATE_HEADINGS = {
    # Type A: Deep Summary
    "Source Introduction",
    "Core Thesis",
    "Central Ideas & Models",
    "Application & Methodology",
    "Critical Nuance & Limitations",
    "Reflection & Contemporary Context",
    "Summary",
    # Type B: Concept Article
    "Introduction & Definition",
    "Core Theory & Underlying Models",
    "Contradictions & Perspectives",
    "Practical Application",
    "Limitations & Pitfalls",
    "Cross-References & Synthesis",
    # Type C: Method Handbook
    "Purpose & Goal",
    "Prerequisites",
    "Step-by-Step Methodology",
    "Best Practices & Tips",
    "Common Mistakes & Troubleshooting",
    "Measurability & Evaluation",
    # Type D: Architectural Sequence
    "Trigger & Context",
    "Participants",
    "Chronological Message Flow",
    "Failure Modes & Fallbacks",
    "Observability & Tracing",
    # Human Notes (OWN-002)
    "Notes",
    # Derived References
    "Derived Graph References",
}

# Engineering-only object types (DATA_MODEL.md §3.1, ID-005)
ENGINEERING_ONLY_TYPES = {
    "Specification",
    "Product",
    "Feature",
    "Requirement",
    "Component",
    "WorkPackage",
    "Interface",
    "Protocol",
    "Incident",
    "TroubleReport",
    "Sequence",
}


class Linter:
    """Multi-layered conformance linter."""

    def __init__(
        self,
        registries: LoadedRegistries,
        reference_date: Optional[date] = None,
        strict: bool = False,
        check_skills: bool = True,
    ):
        self.registries = registries
        self.reference_date = reference_date or date.today()
        self.strict = strict
        self.check_skills = check_skills

        # Precompute lookups from registries
        self.tax_by_id = {n.taxonomy_id: n for n in self.registries.taxonomy_registry.taxonomy}
        self.obj_types = self.registries.object_registry.object_types
        self.domains = set(self.registries.object_registry.domains)
        self.relations = self.registries.relation_registry.relations
        self.inverse_view_names = {
            r.inverse_view for r in self.relations.values() if not r.symmetric
        }
        self.gov_rules = self.registries.governance_policy.status_consensus_rules
        self.facet_defs = self.registries.facet_registry.facets

        # Outbound degree cap (threshold_policy.yaml / GRAPH-MAX-OUTBOUND-DEGREE)
        self.max_degree = 20
        for th in self.registries.threshold_policy.thresholds:
            if th.threshold_id == "GRAPH-MAX-OUTBOUND-DEGREE":
                self.max_degree = int(th.value)
                break

    def lint_corpus(self, corpus: Corpus, target_file: Optional[Path] = None) -> List[Finding]:
        """Execute Layers 1 to 5 across the loaded corpus.

        If target_file is specified, filters findings to that file (D25),
        while maintaining full corpus context for cross-object checks.
        """
        findings: List[Finding] = []

        # Layer 1: Schema / Pydantic validation
        for ko in corpus.objects:
            findings.extend(self._check_layer1_schema(ko))

        # Layer 2: Structural validation (ID, Path, Scope, Taxonomy)
        for ko in corpus.objects:
            findings.extend(self._check_layer2_structural(ko))

        # Layer 3: Semantic validation (Domain, Facets, Epistemology, Provenance)
        for ko in corpus.objects:
            findings.extend(self._check_layer3_semantic(ko))

        # Layer 4: Graph validation (Self-refs, Duplicates, Degrees, Cycles)
        findings.extend(self._check_layer4_graph(corpus))

        # Layer 5: Cross-object validation (Duplicate IDs, Broken links, Status dependencies)
        findings.extend(self._check_layer5_cross_object(corpus))

        # Section ownership check (OWN-001..003, W014, E051)
        for ko in corpus.objects:
            findings.extend(self._check_section_ownership(ko))

        # Agent skill drift check (AGENT-SKILLS.md, E050)
        if self.check_skills and target_file is None:
            from trashheap.skills import SKILL_RELATIVE_PATH, check_agent_skills

            repo_root = corpus.root.resolve()
            current = repo_root
            while current != current.parent:
                if (
                    (current / "pyproject.toml").exists()
                    or (current / ".git").exists()
                    or (current / ".agents" / "skills").exists()
                ):
                    break
                current = current.parent
            else:
                current = repo_root
            if not check_agent_skills(current):
                findings.append(
                    Finding(
                        code="E050",
                        field=str(SKILL_RELATIVE_PATH),
                        message="Emitted .agents/skills/trashheap/SKILL.md diverges from code and schemas/registry (AGENT-SKILLS.md §7)",
                        suggestion="Run 'trashheap generate-skills' to synchronize skill definition",
                        file=str(current / SKILL_RELATIVE_PATH),
                        level="ERROR",
                    )
                )

        # Filter by target_file if requested (D25)
        if target_file is not None:
            resolved_target = str(target_file.resolve())
            findings = [
                f
                for f in findings
                if f.file is not None and str(Path(f.file).resolve()) == resolved_target
            ]

        # In strict mode, elevate warnings
        if self.strict:
            for f in findings:
                if f.level == "WARNING":
                    f.level = "ERROR"

        return findings

    def _check_layer1_schema(self, ko: KnowledgeObject) -> List[Finding]:
        findings: List[Finding] = []
        rel_path = str(ko.path)

        if ko.load_error is not None:
            msg = str(ko.load_error)
            findings.append(
                Finding(
                    code="E000",
                    field="frontmatter",
                    message=f"Frontmatter schema validation failure: {msg}",
                    suggestion="Verify YAML syntax and mandatory fields.",
                    file=rel_path,
                    level="ERROR",
                )
            )

        # Check for unallocated fields (META-002)
        all_allocated = set().union(*METADATA_CATEGORIES.values())
        for key in ko.frontmatter_dict.keys():
            if key not in all_allocated:
                findings.append(
                    Finding(
                        code="E000",
                        field=key,
                        message=f"Unallocated frontmatter field '{key}' (META-002)",
                        suggestion="Field must belong to one of the 9 metadata categories.",
                        file=rel_path,
                        level="ERROR",
                    )
                )

        return findings

    def _check_layer2_structural(self, ko: KnowledgeObject) -> List[Finding]:
        findings: List[Finding] = []
        rel_path = str(ko.path)
        fm = ko.frontmatter_dict
        node_id = fm.get("id", "")
        scope = fm.get("scope", "")
        object_type = fm.get("object_type", "")
        tax_path = fm.get("taxonomy_path", "")
        tax_id = fm.get("taxonomy_id")

        # 1. ID pattern & Scope prefix (ID-001, E005)
        m = re.match(ID_PATTERN, node_id)
        if not m:
            findings.append(
                Finding(
                    code="E005",
                    field="id",
                    message=f"ID '{node_id}' does not match ID_PATTERN (ID-001)",
                    suggestion="Format: (PERS|ENG)-<TYPE>-<TAG>-<SEQ>",
                    file=rel_path,
                    level="ERROR",
                )
            )
        else:
            scope_prefix = m.group(1)
            seq_str = m.group(2)
            # Scope prefix match
            expected_prefix = (
                "PERS" if scope == "personal" else "ENG" if scope == "engineering" else ""
            )
            if scope_prefix != expected_prefix:
                findings.append(
                    Finding(
                        code="E005",
                        field="id",
                        message=f"ID prefix '{scope_prefix}' does not match scope '{scope}'",
                        suggestion=f"Use prefix '{expected_prefix}-'",
                        file=rel_path,
                        level="ERROR",
                    )
                )

            # Sequence cap (ID-004, E008)
            seq_num = int(seq_str)
            if seq_num > 9999:
                findings.append(
                    Finding(
                        code="E008",
                        field="id",
                        message=f"Sequence number {seq_num} exceeds 9999 (ID-004)",
                        suggestion="Sequence numbers must be between 0001 and 9999",
                        file=rel_path,
                        level="ERROR",
                    )
                )

        # 2. TYPE segment match (ID-002, E005)
        if object_type in self.obj_types:
            expected_code = self.obj_types[object_type].code
            parts = node_id.split("-")
            if len(parts) >= 2 and parts[1] != expected_code:
                findings.append(
                    Finding(
                        code="E005",
                        field="id",
                        message=f"ID type segment '{parts[1]}' does not match expected '{expected_code}' for {object_type}",
                        suggestion=f"Use code '{expected_code}'",
                        file=rel_path,
                        level="ERROR",
                    )
                )

            # Tag strategy (ID-003, E005)
            tag_strat = self.obj_types[object_type].tag_strategy
            if len(parts) >= 3:
                tag = parts[2]
                if tag_strat == "year" and not re.match(YEAR_TAG_PATTERN, tag):
                    findings.append(
                        Finding(
                            code="E005",
                            field="id",
                            message=f"Year object type '{object_type}' requires 4-digit year tag, got '{tag}'",
                            suggestion="Use YYYY format",
                            file=rel_path,
                            level="ERROR",
                        )
                    )
                elif tag_strat == "domain" and not re.match(DOMAIN_TAG_PATTERN, tag):
                    findings.append(
                        Finding(
                            code="E005",
                            field="id",
                            message=f"Domain object type '{object_type}' requires uppercase domain tag, got '{tag}'",
                            suggestion="Use uppercase domain tag, e.g. BAZEL",
                            file=rel_path,
                            level="ERROR",
                        )
                    )

        # 3. Scope vs Engineering-only types (ID-005, E006)
        if scope == "personal" and object_type in ENGINEERING_ONLY_TYPES:
            findings.append(
                Finding(
                    code="E006",
                    field="object_type",
                    message=f"Object type '{object_type}' is engineering-only and forbidden in scope 'personal' (ID-005)",
                    suggestion="Move to scope 'engineering' or use a personal object type.",
                    file=rel_path,
                    level="ERROR",
                )
            )

        # 4. Taxonomy validations (TAX-001, TAX-004, TAX-007, E016, E017, W001)
        if not tax_id:
            findings.append(
                Finding(
                    code="W001",
                    field="taxonomy_id",
                    message="Knowledge Object lacks recommended field taxonomy_id",
                    suggestion="Add taxonomy_id referencing taxonomy_registry.yaml",
                    file=rel_path,
                    level="WARNING",
                )
            )
        else:
            if tax_id not in self.tax_by_id:
                findings.append(
                    Finding(
                        code="E017",
                        field="taxonomy_id",
                        message=f"Unknown taxonomy_id '{tax_id}' (TAX-001)",
                        suggestion="Reference a valid taxonomy_id from taxonomy_registry.yaml",
                        file=rel_path,
                        level="ERROR",
                    )
                )
            else:
                reg_node = self.tax_by_id[tax_id]
                # Flat leaf-name match (TAX-007, TAX-004, E016)
                if tax_path != reg_node.name:
                    findings.append(
                        Finding(
                            code="E016",
                            field="taxonomy_path",
                            message=f"taxonomy_path '{tax_path}' does not match registry name '{reg_node.name}' (TAX-004)",
                            suggestion=f'Set taxonomy_path: "{reg_node.name}"',
                            file=rel_path,
                            level="ERROR",
                        )
                    )
                # Scope match (TAX-004, E016)
                if scope != reg_node.scope:
                    findings.append(
                        Finding(
                            code="E016",
                            field="scope",
                            message=f"Scope '{scope}' does not match taxonomy node scope '{reg_node.scope}' (TAX-004)",
                            suggestion=f"Set scope: {reg_node.scope}",
                            file=rel_path,
                            level="ERROR",
                        )
                    )

                # Disk path calculation vs actual path (TAX-002, E002)
                # Convert raw registry list to dict format for slug resolution
                raw_tax_dict = {
                    n.taxonomy_id: {"name": n.name, "parent_id": n.parent_id, "scope": n.scope}
                    for n in self.registries.taxonomy_registry.taxonomy
                }
                try:
                    expected_dir = taxonomy_id_to_directory(raw_tax_dict, reg_node.scope, tax_id)
                    expected_file_suffix = f"{expected_dir}{node_id}.md"
                    actual_posix = ko.path.as_posix()
                    if not actual_posix.endswith(expected_file_suffix):
                        findings.append(
                            Finding(
                                code="E002",
                                field="taxonomy_id",
                                message=f"Disk path '{actual_posix}' does not match expected slug path '{expected_file_suffix}' (TAX-002)",
                                suggestion=f"Move file to '{expected_file_suffix}'",
                                file=rel_path,
                                level="ERROR",
                            )
                        )
                except Exception as exc:
                    findings.append(
                        Finding(
                            code="E002",
                            field="taxonomy_id",
                            message=f"Failed to resolve expected slug path for node '{node_id}': {exc} (TAX-002)",
                            file=rel_path,
                            level="ERROR",
                        )
                    )

        return findings

    def _check_layer3_semantic(self, ko: KnowledgeObject) -> List[Finding]:
        findings: List[Finding] = []
        rel_path = str(ko.path)
        fm = ko.frontmatter_dict
        object_type = fm.get("object_type", "")
        domain = fm.get("domain", "")

        # 1. Domain in object_registry domains (CLS-001, E027)
        if domain not in self.domains:
            findings.append(
                Finding(
                    code="E027",
                    field="domain",
                    message=f"Unknown domain '{domain}' (CLS-001)",
                    suggestion=f"Must be one of: {sorted(list(self.domains))}",
                    file=rel_path,
                    level="ERROR",
                )
            )

        # 2. Mandatory facets for object_type (FAC-001, E020)
        if object_type in self.obj_types:
            req_facets = self.obj_types[object_type].required_facets
            for rf in req_facets:
                val = fm.get(rf)
                if val is None or (isinstance(val, list) and len(val) == 0):
                    findings.append(
                        Finding(
                            code="E020",
                            field=rf,
                            message=f"Missing mandatory facet '{rf}' for object_type '{object_type}' (FAC-001)",
                            suggestion=f"Provide non-empty value for facet '{rf}'",
                            file=rel_path,
                            level="ERROR",
                        )
                    )

        # 3. Facet value sets and list rules (FAC-002, FAC-003, E013, E014, E015, E026, W011)
        for facet_name, f_def in self.facet_defs.items():
            if facet_name in fm and fm[facet_name] is not None:
                raw_val = fm[facet_name]
                val_list = raw_val if isinstance(raw_val, list) else [raw_val]

                # Empty list (E013)
                if isinstance(raw_val, list) and len(raw_val) == 0:
                    findings.append(
                        Finding(
                            code="E013",
                            field=facet_name,
                            message=f"Specified facet list for '{facet_name}' is empty (FAC-002)",
                            suggestion="Omit field or specify at least one value",
                            file=rel_path,
                            level="ERROR",
                        )
                    )
                    continue

                # Duplicates (E014)
                if isinstance(raw_val, list) and len(val_list) != len(set(val_list)):
                    findings.append(
                        Finding(
                            code="E014",
                            field=facet_name,
                            message=f"Facet list '{facet_name}' contains duplicates (FAC-002)",
                            suggestion="Remove duplicate values",
                            file=rel_path,
                            level="ERROR",
                        )
                    )

                # Mixed none/unknown (E015)
                has_none = "none" in val_list
                has_unknown = "unknown" in val_list
                has_concrete = any(v not in ("none", "unknown") for v in val_list)

                if (
                    (has_none and has_concrete)
                    or (has_unknown and has_concrete)
                    or (has_none and has_unknown)
                ):
                    findings.append(
                        Finding(
                            code="E015",
                            field=facet_name,
                            message=f"Facet '{facet_name}' mixes none/unknown with concrete values (FAC-002)",
                            suggestion="Use either concrete values alone, or a single sentinel value",
                            file=rel_path,
                            level="ERROR",
                        )
                    )

                # Allowed values and none/unknown (FAC-003, E026, W011)
                for v in val_list:
                    if v == "none" and not f_def.allows_none:
                        findings.append(
                            Finding(
                                code="E026",
                                field=facet_name,
                                message=f"Facet '{facet_name}' does not allow 'none' (FAC-003)",
                                suggestion="Specify a valid concrete facet value",
                                file=rel_path,
                                level="ERROR",
                            )
                        )
                    elif v not in f_def.values:
                        findings.append(
                            Finding(
                                code="E026",
                                field=facet_name,
                                message=f"Unknown facet value '{v}' for '{facet_name}' (FAC-003)",
                                suggestion=f"Must be one of: {sorted(f_def.values)}",
                                file=rel_path,
                                level="ERROR",
                            )
                        )
                    elif v == "unknown":
                        findings.append(
                            Finding(
                                code="W011",
                                field=facet_name,
                                message=f"Facet '{facet_name}' specifies [unknown]; concrete classification recommended",
                                suggestion="Replace [unknown] with concrete classification when known",
                                file=rel_path,
                                level="WARNING",
                            )
                        )

        # 4. Governance status/consensus rules (GOV-002, E004)
        status = fm.get("status")
        consensus = fm.get("consensus")
        if status in self.gov_rules:
            allowed_c = self.gov_rules[status].allowed_consensus
            if consensus not in allowed_c:
                findings.append(
                    Finding(
                        code="E004",
                        field="consensus",
                        message=f"Invalid consensus '{consensus}' for status '{status}' (GOV-002)",
                        suggestion=f"Allowed consensus for '{status}': {allowed_c}",
                        file=rel_path,
                        level="ERROR",
                    )
                )

        # 5. Provenance checks (PROV-001, PROV-006, PROV-007, E028, E029, E030)
        author = fm.get("author")
        if author and not re.match(ACTOR_PATTERN, str(author)):
            findings.append(
                Finding(
                    code="E028",
                    field="author",
                    message=f"Author '{author}' does not match ACTOR_PATTERN (PROV-001)",
                    suggestion="Use human:<id>, process:<id>, or <producer>/<version>",
                    file=rel_path,
                    level="ERROR",
                )
            )

        reviewer = fm.get("reviewer")
        last_verified = fm.get("last_verified")
        if reviewer and not re.match(ACTOR_PATTERN, str(reviewer)):
            findings.append(
                Finding(
                    code="E028",
                    field="reviewer",
                    message=f"Reviewer '{reviewer}' does not match ACTOR_PATTERN (PROV-001)",
                    suggestion="Use human:<id>, process:<id>, or <producer>/<version>",
                    file=rel_path,
                    level="ERROR",
                )
            )

        # Reviewer and last_verified binding (PROV-006, E029)
        if (reviewer is None) != (last_verified is None):
            findings.append(
                Finding(
                    code="E029",
                    field="reviewer",
                    message="Exactly one of reviewer and last_verified is null (PROV-006)",
                    suggestion="Both reviewer and last_verified must be provided together, or both null",
                    file=rel_path,
                    level="ERROR",
                )
            )

        # Source_refs non-empty, no duplicates (PROV-007, E030)
        source_refs = fm.get("source_refs")
        if not source_refs or not isinstance(source_refs, list) or len(source_refs) == 0:
            findings.append(
                Finding(
                    code="E030",
                    field="source_refs",
                    message="source_refs is empty or omitted (PROV-007)",
                    suggestion="Provide at least one non-empty source reference string",
                    file=rel_path,
                    level="ERROR",
                )
            )
        elif len(source_refs) != len(set(source_refs)):
            findings.append(
                Finding(
                    code="E030",
                    field="source_refs",
                    message="source_refs contains duplicates (PROV-007)",
                    suggestion="Remove duplicate source references",
                    file=rel_path,
                    level="ERROR",
                )
            )

        # 6. Validity & Temporal chronology (VAL-001, E007, W002, W003, W012, W013)
        validity = fm.get("validity")
        if isinstance(validity, dict):
            v_from = validity.get("valid_from")
            v_until = validity.get("valid_until")
            if v_from and v_until:
                try:
                    df = date.fromisoformat(str(v_from))
                    du = date.fromisoformat(str(v_until))
                    if du < df:
                        findings.append(
                            Finding(
                                code="E007",
                                field="validity.valid_until",
                                message=f"valid_until ({du}) is earlier than valid_from ({df}) (VAL-001)",
                                suggestion="Ensure valid_until >= valid_from",
                                file=rel_path,
                                level="ERROR",
                            )
                        )
                except Exception:
                    pass

        # Temporal clock-injected checks
        next_review = fm.get("next_review")
        if next_review:
            try:
                dn = date.fromisoformat(str(next_review))
                if dn < self.reference_date:
                    findings.append(
                        Finding(
                            code="W002",
                            field="next_review",
                            message=f"next_review date ({dn}) is in the past relative to {self.reference_date}",
                            suggestion="Schedule an updated review date",
                            file=rel_path,
                            level="WARNING",
                        )
                    )
            except Exception:
                pass

        if last_verified:
            try:
                dlv = date.fromisoformat(str(last_verified))
                if dlv > self.reference_date:
                    findings.append(
                        Finding(
                            code="W003",
                            field="last_verified",
                            message=f"last_verified date ({dlv}) lies in the future",
                            suggestion="Fix last_verified date",
                            file=rel_path,
                            level="WARNING",
                        )
                    )
            except Exception:
                pass

        last_modified = fm.get("last_modified")
        if last_modified:
            try:
                dlm = date.fromisoformat(str(last_modified))
                if dlm > self.reference_date:
                    findings.append(
                        Finding(
                            code="W012",
                            field="last_modified",
                            message=f"last_modified date ({dlm}) lies in the future",
                            suggestion="Fix last_modified date",
                            file=rel_path,
                            level="WARNING",
                        )
                    )
                if last_verified:
                    dlv = date.fromisoformat(str(last_verified))
                    if dlm > dlv:
                        findings.append(
                            Finding(
                                code="W013",
                                field="last_modified",
                                message=f"last_modified ({dlm}) is later than last_verified ({dlv}); unverified changes present",
                                suggestion="Re-verify content and update last_verified",
                                file=rel_path,
                                level="WARNING",
                            )
                        )
            except Exception:
                pass

        return findings

    def _check_layer4_graph(self, corpus: Corpus) -> List[Finding]:
        """Validate ontology relations, degree caps, self-refs, duplicates, and DAG cycles."""
        findings: List[Finding] = []

        # Graph representations for cycle checks
        dag_edges_by_type: Dict[str, Dict[str, Set[str]]] = {}
        hierarchical_edges: Dict[str, Set[str]] = {}  # PART_OF, INSTANCE_OF, TYPE_OF

        for ko in corpus.objects:
            rel_path = str(ko.path)
            node_id = ko.id or ""
            relations = ko.frontmatter_dict.get("relations", [])
            if not isinstance(relations, list):
                continue

            # Check outbound degree cap (GRAPH-004, W015)
            if len(relations) > self.max_degree:
                findings.append(
                    Finding(
                        code="W015",
                        field="relations",
                        message=f"Outbound link count ({len(relations)}) exceeds degree cap {self.max_degree} (GRAPH-004)",
                        suggestion=f"Prune or consolidate relations to <= {self.max_degree}",
                        file=rel_path,
                        level="WARNING",
                    )
                )

            seen_relations: Set[tuple[str, str]] = set()

            for r in relations:
                if not isinstance(r, dict):
                    continue
                rtype = r.get("type", "")
                target = r.get("target", "")

                # 1. Self-reference (GRAPH-002, E011)
                if target == node_id:
                    findings.append(
                        Finding(
                            code="E011",
                            field="relations",
                            message=f"Object links to its own id '{node_id}' (GRAPH-002)",
                            suggestion="Remove self-referencing relation",
                            file=rel_path,
                            level="ERROR",
                        )
                    )

                # 2. Duplicate relation (GRAPH-002, E012)
                pair = (rtype, target)
                if pair in seen_relations:
                    findings.append(
                        Finding(
                            code="E012",
                            field="relations",
                            message=f"Duplicate relation '{rtype}' -> '{target}' (GRAPH-002)",
                            suggestion="Specify identical relations at most once",
                            file=rel_path,
                            level="ERROR",
                        )
                    )
                seen_relations.add(pair)

                # 3. Virtual inverse check (REL-004, E019)
                if rtype in self.inverse_view_names:
                    findings.append(
                        Finding(
                            code="E019",
                            field="relations.type",
                            message=f"Virtual inverse relation '{rtype}' persisted in YAML (REL-004)",
                            suggestion="Use canonical persisted relation name instead",
                            file=rel_path,
                            level="ERROR",
                        )
                    )

                # 4. Canonical relation exists in registry
                if rtype not in self.relations:
                    continue

                r_def = self.relations[rtype]

                # 5. Source / Target type constraints (REL-005, E021)
                src_type = ko.object_type
                if src_type and src_type not in r_def.source_types:
                    findings.append(
                        Finding(
                            code="E021",
                            field="relations.type",
                            message=f"Relation '{rtype}' cannot originate from source_type '{src_type}' (REL-005)",
                            suggestion=f"Allowed source_types: {r_def.source_types}",
                            file=rel_path,
                            level="ERROR",
                        )
                    )

                target_obj = corpus.get_by_id(target)
                if target_obj and target_obj.object_type:
                    if target_obj.object_type not in r_def.target_types:
                        findings.append(
                            Finding(
                                code="E021",
                                field="relations.target",
                                message=f"Relation '{rtype}' cannot point to target_type '{target_obj.object_type}' (REL-005)",
                                suggestion=f"Allowed target_types: {r_def.target_types}",
                                file=rel_path,
                                level="ERROR",
                            )
                        )

                # 6. Direction check for opposed relations (REL-009, E031)
                # E.g. DESCRIBES vs DOCUMENTED_BY: documented object must declare DOCUMENTED_BY
                if r_def.opposed_to:
                    # If A declares DESCRIBES B and B is in corpus, it's non-canonical direction
                    if rtype == "DESCRIBES" and target_obj is not None:
                        findings.append(
                            Finding(
                                code="E031",
                                field="relations.type",
                                message=f"Relation 'DESCRIBES' declared in non-canonical direction against target '{target}' (REL-009)",
                                suggestion=f"Documented object '{target}' should declare 'DOCUMENTED_BY' pointing to '{node_id}'",
                                file=rel_path,
                                level="ERROR",
                            )
                        )

                # Collect DAG edges for cycle checking
                if r_def.dag:
                    if rtype not in dag_edges_by_type:
                        dag_edges_by_type[rtype] = {}
                    if node_id not in dag_edges_by_type[rtype]:
                        dag_edges_by_type[rtype][node_id] = set()
                    dag_edges_by_type[rtype][node_id].add(target)

                # Composite hierarchical edges (PART_OF, INSTANCE_OF, TYPE_OF) (GRAPH-001, D96)
                if rtype in ("PART_OF", "INSTANCE_OF", "TYPE_OF"):
                    if node_id not in hierarchical_edges:
                        hierarchical_edges[node_id] = set()
                    hierarchical_edges[node_id].add(target)

        # 7. Cycle detection per dag relation (GRAPH-001, E010)
        for rtype, adj in dag_edges_by_type.items():
            cycle = self._detect_cycle(adj)
            if cycle:
                findings.append(
                    Finding(
                        code="E010",
                        field="relations",
                        message=f"DAG cycle detected in relation '{rtype}': {' -> '.join(cycle)} (GRAPH-001)",
                        suggestion="Break relation cycle to maintain DAG property",
                        level="ERROR",
                    )
                )

        # 8. Cycle detection across composite hierarchical edges (GRAPH-001, D96)
        comp_cycle = self._detect_cycle(hierarchical_edges)
        if comp_cycle:
            findings.append(
                Finding(
                    code="E010",
                    field="relations",
                    message=f"DAG cycle detected in composite hierarchical closure: {' -> '.join(comp_cycle)} (GRAPH-001)",
                    suggestion="Remove circular hierarchical references across PART_OF, INSTANCE_OF, TYPE_OF",
                    level="ERROR",
                )
            )

        return findings

    def _check_layer5_cross_object(self, corpus: Corpus) -> List[Finding]:
        """Validate cross-object integrity: duplicates, broken links, status dependencies."""
        findings: List[Finding] = []

        # 1. Duplicate IDs across files (ID-004, E001)
        seen_ids: Dict[str, Path] = {}
        for ko in corpus.objects:
            nid = ko.id
            if not nid:
                continue
            if nid in seen_ids:
                findings.append(
                    Finding(
                        code="E001",
                        field="id",
                        message=f"Duplicate node id '{nid}' occurs in '{seen_ids[nid]}' and '{ko.path}' (ID-004)",
                        suggestion="Node IDs must be globally unique across all source files",
                        file=str(ko.path),
                        level="ERROR",
                    )
                )
            else:
                seen_ids[nid] = ko.path

        # 2. Target existence and broken links (GRAPH-003, E009, W004, W005)
        for ko in corpus.objects:
            rel_path = str(ko.path)
            node_scope = ko.scope
            node_status = ko.frontmatter_dict.get("status", "")
            relations = ko.frontmatter_dict.get("relations", [])
            if not isinstance(relations, list):
                continue

            for r in relations:
                if not isinstance(r, dict):
                    continue
                rtype = r.get("type", "")
                target = r.get("target", "")
                soft_link = r.get("soft_link", False)
                target_obj = corpus.get_by_id(target)

                if target_obj is None:
                    if not soft_link:
                        findings.append(
                            Finding(
                                code="E009",
                                field="relations.target",
                                message=f"Broken link: target '{target}' does not exist and soft_link is False (GRAPH-003)",
                                suggestion="Ensure target exists or mark with soft_link: true",
                                file=rel_path,
                                level="ERROR",
                            )
                        )
                    else:
                        # Soft link unresolved
                        pass
                else:
                    # Target exists
                    if soft_link:
                        findings.append(
                            Finding(
                                code="W005",
                                field="relations.soft_link",
                                message=f"Target '{target}' exists, but soft_link: true has not been cleaned up",
                                suggestion="Remove soft_link: true",
                                file=rel_path,
                                level="WARNING",
                            )
                        )

                    target_status = target_obj.frontmatter_dict.get("status", "")
                    # Status dependencies (W006, W007, W008)
                    if node_status == "established":
                        if target_status == "deprecated":
                            findings.append(
                                Finding(
                                    code="W006",
                                    field="relations.target",
                                    message=f"Active node '{ko.id}' depends on deprecated node '{target}'",
                                    suggestion="Update dependency or review node status",
                                    file=rel_path,
                                    level="WARNING",
                                )
                            )
                        elif target_status == "archived":
                            findings.append(
                                Finding(
                                    code="W007",
                                    field="relations.target",
                                    message=f"Active node '{ko.id}' points to archived node '{target}'",
                                    suggestion="Remove reference to archived node or modernize target",
                                    file=rel_path,
                                    level="WARNING",
                                )
                            )

                    if rtype == "SUPERSEDES" and target_status not in ("deprecated", "archived"):
                        findings.append(
                            Finding(
                                code="W008",
                                field="relations.target",
                                message=f"SUPERSEDES points to node '{target}' with status '{target_status}' (neither deprecated nor archived)",
                                suggestion="Update superseded node's status to deprecated or archived",
                                file=rel_path,
                                level="WARNING",
                            )
                        )

                    # Cross-scope link warning (W009)
                    if target_obj.scope and node_scope and target_obj.scope != node_scope:
                        findings.append(
                            Finding(
                                code="W009",
                                field="relations.target",
                                message=f"Relation '{rtype}' crosses scope from '{node_scope}' to '{target_obj.scope}'",
                                suggestion="Ensure cross-scope dependency is intentional",
                                file=rel_path,
                                level="WARNING",
                            )
                        )

        return findings

    def _check_section_ownership(self, ko: KnowledgeObject) -> List[Finding]:
        """Validate Section Ownership (OWN-001..003, W014, E051)."""
        findings: List[Finding] = []
        rel_path = str(ko.path)
        sections = ko.parse_sections()

        notes_count = sum(1 for h in sections.keys() if h == "Notes")
        if notes_count > 1:
            findings.append(
                Finding(
                    code="E051",
                    field="sections",
                    message=f"Multiple '## Notes' sections ({notes_count}) detected (OWN-002, E051)",
                    suggestion="At most one '## Notes' section is permitted per page",
                    file=rel_path,
                    level="ERROR",
                )
            )

        for heading in sections.keys():
            if heading not in KNOWN_TEMPLATE_HEADINGS:
                findings.append(
                    Finding(
                        code="W014",
                        field=f"sections.{heading}",
                        message=f"Unrecognized heading '## {heading}' outside template standard (OWN-001)",
                        suggestion="Place custom insights under '## Notes' or align with standard template",
                        file=rel_path,
                        level="WARNING",
                    )
                )

        return findings

    @staticmethod
    def _detect_cycle(adj: Dict[str, Set[str]]) -> Optional[List[str]]:
        """DFS cycle detection returning the cycle path if found."""
        visited: Dict[str, int] = {}  # 0 = unvisited, 1 = visiting, 2 = visited
        parent_map: Dict[str, str] = {}

        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            visited[node] = 1
            for nxt in adj.get(node, ()):
                if visited.get(nxt, 0) == 1:
                    # Found cycle
                    idx = path.index(nxt) if nxt in path else 0
                    return path[idx:] + [nxt]
                if visited.get(nxt, 0) == 0:
                    parent_map[nxt] = node
                    res = dfs(nxt, path + [nxt])
                    if res:
                        return res
            visited[node] = 2
            return None

        all_nodes = set(adj.keys()).union(*adj.values())
        for n in sorted(list(all_nodes)):
            if visited.get(n, 0) == 0:
                cycle = dfs(n, [n])
                if cycle:
                    return cycle
        return None
