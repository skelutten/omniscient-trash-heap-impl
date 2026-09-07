"""Registry validation engine enforcing invariants and cross-registry consistency."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

from trashheap.registry.loader import LoadedRegistries
from trashheap.registry.models import (
    SourceRegistryModel,
    SpecOwnershipModel,
    ThresholdPolicyModel,
)


@dataclass
class RegistryFinding:
    """Diagnostic finding emitted during registry validation."""

    code: str
    registry: str
    field: Optional[str]
    message: str
    suggestion: Optional[str] = None
    level: str = "ERROR"  # "ERROR" or "WARNING"


def validate_spec_ownership(
    spec_ownership: SpecOwnershipModel, repo_root: Path
) -> List[RegistryFinding]:
    """Validate spec_ownership.yaml: unique family owners and existing owner paths."""
    findings: List[RegistryFinding] = []
    seen_families: Set[str] = set()

    for entry in spec_ownership.invariant_families:
        # Check duplicate_family_owners
        if entry.family_id in seen_families:
            findings.append(
                RegistryFinding(
                    code="E080",
                    registry="spec_ownership.yaml",
                    field=f"invariant_families.{entry.family_id}",
                    message=f"Duplicate invariant family owner for '{entry.family_id}'",
                    suggestion=f"Ensure family_id '{entry.family_id}' is defined exactly once.",
                )
            )
        seen_families.add(entry.family_id)

        # Check unknown_owner_paths
        owner_path = repo_root / entry.owner
        if not owner_path.exists():
            findings.append(
                RegistryFinding(
                    code="E081",
                    registry="spec_ownership.yaml",
                    field=f"invariant_families.{entry.family_id}.owner",
                    message=f"Owner file does not exist: '{entry.owner}'",
                    suggestion=f"Update owner path '{entry.owner}' to an existing specification file.",
                )
            )

    return findings


def validate_threshold_policy(
    threshold_policy: ThresholdPolicyModel, repo_root: Path
) -> List[RegistryFinding]:
    """Validate threshold_policy.yaml: unique threshold IDs and resolving spec owners."""
    findings: List[RegistryFinding] = []
    seen_ids: Set[str] = set()

    for entry in threshold_policy.thresholds:
        # Check duplicate threshold IDs
        if entry.threshold_id in seen_ids:
            findings.append(
                RegistryFinding(
                    code="E082",
                    registry="threshold_policy.yaml",
                    field=f"thresholds.{entry.threshold_id}",
                    message=f"Duplicate threshold_id '{entry.threshold_id}'",
                    suggestion=f"Ensure threshold_id '{entry.threshold_id}' is unique.",
                )
            )
        seen_ids.add(entry.threshold_id)

        # Check owner path exists
        owner_path = repo_root / entry.owner
        if not owner_path.exists():
            findings.append(
                RegistryFinding(
                    code="E083",
                    registry="threshold_policy.yaml",
                    field=f"thresholds.{entry.threshold_id}.owner",
                    message=f"Threshold owner file does not exist: '{entry.owner}'",
                    suggestion=f"Update owner path '{entry.owner}' to an existing specification file.",
                )
            )

    return findings


def validate_source_registry(
    source_reg: SourceRegistryModel,
) -> List[RegistryFinding]:
    """Validate source_registry.yaml: hierarchy and source_taxonomy paths."""
    findings: List[RegistryFinding] = []
    stax = source_reg.source_taxonomy

    for st_name, st_def in source_reg.source_types.items():
        tax_path = st_def.source_taxonomy
        if not tax_path:
            findings.append(
                RegistryFinding(
                    code="E084",
                    registry="source_registry.yaml",
                    field=f"source_types.{st_name}.source_taxonomy",
                    message=f"Empty source_taxonomy for source_type '{st_name}'",
                    suggestion="Specify a valid path in source_taxonomy, e.g. [Digital, Web]",
                )
            )
            continue

        # Validate top-level category in source_taxonomy
        root = tax_path[0]
        if root not in stax:
            findings.append(
                RegistryFinding(
                    code="E085",
                    registry="source_registry.yaml",
                    field=f"source_types.{st_name}.source_taxonomy",
                    message=f"Unknown source_taxonomy root '{root}' for '{st_name}'",
                    suggestion=f"Root must be one of: {sorted(list(stax.keys()))}",
                )
            )
        elif len(tax_path) > 1:
            child = tax_path[1]
            children = stax[root].get("children", [])
            if child not in children:
                findings.append(
                    RegistryFinding(
                        code="E086",
                        registry="source_registry.yaml",
                        field=f"source_types.{st_name}.source_taxonomy",
                        message=f"Unknown child '{child}' under '{root}' for '{st_name}'",
                        suggestion=f"Child must be in {children}",
                    )
                )

    return findings


def validate_cross_registries(loaded: LoadedRegistries, repo_root: Path) -> List[RegistryFinding]:
    """Validate cross-registry consistency across all 10 registries."""
    findings: List[RegistryFinding] = []

    # 1. Spec ownership & thresholds
    findings.extend(validate_spec_ownership(loaded.spec_ownership, repo_root))
    findings.extend(validate_threshold_policy(loaded.threshold_policy, repo_root))
    findings.extend(validate_source_registry(loaded.source_registry))

    # 2. Relation registry source/target types in object_registry
    obj_types = set(loaded.object_registry.object_types.keys())
    for rel_name, rel_def in loaded.relation_registry.relations.items():
        for st in rel_def.source_types:
            if st not in obj_types:
                findings.append(
                    RegistryFinding(
                        code="E023",
                        registry="relation_registry.yaml",
                        field=f"relations.{rel_name}.source_types",
                        message=f"Relation '{rel_name}' references unknown source_type '{st}' (REL-007)",
                        suggestion=f"source_type '{st}' must exist in object_registry.yaml",
                    )
                )
        for tt in rel_def.target_types:
            if tt not in obj_types:
                findings.append(
                    RegistryFinding(
                        code="E023",
                        registry="relation_registry.yaml",
                        field=f"relations.{rel_name}.target_types",
                        message=f"Relation '{rel_name}' references unknown target_type '{tt}' (REL-007)",
                        suggestion=f"target_type '{tt}' must exist in object_registry.yaml",
                    )
                )

        # Non-symmetric relations must have unique inverse_view (REL-008, E025)
        # Symmetric relations must set inverse_view to relation name
        if rel_def.symmetric:
            if rel_def.inverse_view != rel_name:
                findings.append(
                    RegistryFinding(
                        code="E025",
                        registry="relation_registry.yaml",
                        field=f"relations.{rel_name}.inverse_view",
                        message=f"Symmetric relation '{rel_name}' must set inverse_view to its own name",
                        suggestion=f"Set inverse_view: {rel_name}",
                    )
                )

    # Check non-symmetric inverse_view uniqueness (REL-008 / E025)
    inverse_views: dict[str, str] = {}
    for rel_name, rel_def in loaded.relation_registry.relations.items():
        if not rel_def.symmetric:
            iv = rel_def.inverse_view
            if iv in inverse_views:
                findings.append(
                    RegistryFinding(
                        code="E025",
                        registry="relation_registry.yaml",
                        field=f"relations.{rel_name}.inverse_view",
                        message=f"Duplicate non-symmetric inverse_view '{iv}' shared by '{rel_name}' and '{inverse_views[iv]}'",
                        suggestion="Each non-symmetric relation must declare a unique inverse_view name.",
                    )
                )
            else:
                inverse_views[iv] = rel_name

    # 3. Object registry required_facets in facet_registry
    registered_facets = set(loaded.facet_registry.facets.keys())
    for ot_name, ot_def in loaded.object_registry.object_types.items():
        for rf in ot_def.required_facets:
            if rf not in registered_facets:
                findings.append(
                    RegistryFinding(
                        code="E020",
                        registry="object_registry.yaml",
                        field=f"object_types.{ot_name}.required_facets",
                        message=f"Object type '{ot_name}' requires unknown facet '{rf}'",
                        suggestion=f"Facet '{rf}' must be defined in facet_registry.yaml",
                    )
                )

    # 4. Taxonomy tree acyclicity and valid parents (TAX-005, TAX-006 / E018, E024)
    nodes_by_id = {n.taxonomy_id: n for n in loaded.taxonomy_registry.taxonomy}
    for node in loaded.taxonomy_registry.taxonomy:
        if node.parent_id is not None:
            if node.parent_id not in nodes_by_id:
                findings.append(
                    RegistryFinding(
                        code="E018",
                        registry="taxonomy_registry.yaml",
                        field=f"taxonomy.{node.taxonomy_id}.parent_id",
                        message=f"Taxonomy node '{node.taxonomy_id}' references unknown parent_id '{node.parent_id}'",
                        suggestion="parent_id must reference an existing taxonomy_id in the same scope",
                    )
                )
            else:
                parent = nodes_by_id[node.parent_id]
                if parent.scope != node.scope:
                    findings.append(
                        RegistryFinding(
                            code="E018",
                            registry="taxonomy_registry.yaml",
                            field=f"taxonomy.{node.taxonomy_id}.parent_id",
                            message=f"Taxonomy node '{node.taxonomy_id}' scope '{node.scope}' differs from parent '{node.parent_id}' scope '{parent.scope}'",
                            suggestion="Taxonomy nodes and parents must belong to the same scope",
                        )
                    )

    # Cycle detection in taxonomy per scope (TAX-006 / E024)
    for node in loaded.taxonomy_registry.taxonomy:
        seen: Set[str] = set()
        curr: Optional[str] = node.taxonomy_id
        while curr is not None:
            if curr in seen:
                findings.append(
                    RegistryFinding(
                        code="E024",
                        registry="taxonomy_registry.yaml",
                        field=f"taxonomy.{curr}",
                        message=f"Cycle detected in taxonomy parent chain starting at '{node.taxonomy_id}'",
                        suggestion="Ensure taxonomy forest is strictly acyclic",
                    )
                )
                break
            seen.add(curr)
            curr_node = nodes_by_id.get(curr)
            curr = curr_node.parent_id if curr_node else None

    # 5. Facet values: none permitted only if allows_none is true
    for facet_name, facet_def in loaded.facet_registry.facets.items():
        if not facet_def.allows_none and "none" in facet_def.values:
            findings.append(
                RegistryFinding(
                    code="E026",
                    registry="facet_registry.yaml",
                    field=f"facets.{facet_name}",
                    message=f"Facet '{facet_name}' defines 'none' in values but allows_none is False",
                    suggestion="Set allows_none: true or remove 'none' from values",
                )
            )

    return findings
