"""Registry loader for The Omniscient Trash Heap."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from trashheap.constants import REGISTRY_FILES
from trashheap.registry.models import (
    ActorRegistryModel,
    EpistemicRegistryModel,
    FacetRegistryModel,
    GovernancePolicyModel,
    ObjectRegistryModel,
    RelationRegistryModel,
    SourceRegistryModel,
    SpecOwnershipModel,
    TaxonomyRegistryModel,
    ThresholdPolicyModel,
)


@dataclass
class LoadedRegistries:
    """Container for loaded and validated registry models."""

    object_registry: ObjectRegistryModel
    relation_registry: RelationRegistryModel
    taxonomy_registry: TaxonomyRegistryModel
    epistemic_registry: EpistemicRegistryModel
    governance_policy: GovernancePolicyModel
    facet_registry: FacetRegistryModel
    source_registry: SourceRegistryModel
    actor_registry: ActorRegistryModel
    threshold_policy: ThresholdPolicyModel
    spec_ownership: SpecOwnershipModel

    # Raw dictionaries for quick lookups if needed
    raw: Dict[str, Dict[str, Any]]

    @property
    def object_types(self) -> Dict[str, Any]:
        return self.object_registry.object_types

    @property
    def domains(self) -> list[str]:
        return self.object_registry.domains

    @property
    def relations(self) -> Dict[str, Any]:
        return self.relation_registry.relations

    @property
    def taxonomy(self) -> list[Any]:
        return self.taxonomy_registry.taxonomy

    @property
    def facets(self) -> Dict[str, Any]:
        return self.facet_registry.facets


class RegistryLoadError(Exception):
    """Raised when one or more registries fail to load or parse."""

    def __init__(self, filename: str, message: str):
        super().__init__(f"Failed to load registry {filename}: {message}")
        self.filename = filename
        self.message = message


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load a single YAML file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise RegistryLoadError(file_path.name, "Content must be a YAML dictionary")
        return data
    except Exception as e:
        if isinstance(e, RegistryLoadError):
            raise
        raise RegistryLoadError(file_path.name, str(e)) from e


def load_registries(registry_dir: Optional[Union[str, Path]] = None) -> LoadedRegistries:
    """Load all 10 canonical registries from directory."""
    if registry_dir is None:
        # Default to schemas/registry relative to repository root or cwd
        candidates = [
            Path("schemas/registry"),
            Path(__file__).resolve().parent.parent.parent / "schemas" / "registry",
        ]
        chosen = None
        for c in candidates:
            if c.is_dir():
                chosen = c
                break
        if chosen is None:
            raise FileNotFoundError("Could not find registry directory 'schemas/registry'")
        registry_path = chosen
    else:
        registry_path = Path(registry_dir)

    if not registry_path.is_dir():
        raise FileNotFoundError(f"Registry directory not found: {registry_path}")

    raw_data: Dict[str, Dict[str, Any]] = {}
    for filename in REGISTRY_FILES:
        fp = registry_path / filename
        if not fp.exists():
            raise FileNotFoundError(f"Required registry file missing: {fp}")
        raw_data[filename] = load_yaml(fp)

    try:
        loaded = LoadedRegistries(
            object_registry=ObjectRegistryModel.model_validate(raw_data["object_registry.yaml"]),
            relation_registry=RelationRegistryModel.model_validate(
                raw_data["relation_registry.yaml"]
            ),
            taxonomy_registry=TaxonomyRegistryModel.model_validate(
                raw_data["taxonomy_registry.yaml"]
            ),
            epistemic_registry=EpistemicRegistryModel.model_validate(
                raw_data["epistemic_registry.yaml"]
            ),
            governance_policy=GovernancePolicyModel.model_validate(
                raw_data["governance_policy.yaml"]
            ),
            facet_registry=FacetRegistryModel.model_validate(raw_data["facet_registry.yaml"]),
            source_registry=SourceRegistryModel.model_validate(raw_data["source_registry.yaml"]),
            actor_registry=ActorRegistryModel.model_validate(raw_data["actor_registry.yaml"]),
            threshold_policy=ThresholdPolicyModel.model_validate(raw_data["threshold_policy.yaml"]),
            spec_ownership=SpecOwnershipModel.model_validate(raw_data["spec_ownership.yaml"]),
            raw=raw_data,
        )
        return loaded
    except Exception as e:
        raise RegistryLoadError("PydanticValidation", str(e)) from e
