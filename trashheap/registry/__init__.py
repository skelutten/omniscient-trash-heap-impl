"""Registry package for loading and validating declarative schemas."""

from trashheap.registry.loader import LoadedRegistries, RegistryLoadError, load_registries
from trashheap.registry.validator import (
    RegistryFinding,
    validate_cross_registries,
    validate_source_registry,
    validate_spec_ownership,
    validate_threshold_policy,
)

__all__ = [
    "LoadedRegistries",
    "RegistryFinding",
    "RegistryLoadError",
    "load_registries",
    "validate_cross_registries",
    "validate_source_registry",
    "validate_spec_ownership",
    "validate_threshold_policy",
]
