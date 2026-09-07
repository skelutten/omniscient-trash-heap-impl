"""Pydantic v2 models for registry schemas."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class StrictRegistryModel(BaseModel):
    """Base model for core registry models."""

    model_config = ConfigDict(extra="ignore")


# --- Object Registry ---
class ObjectTypeDefinition(StrictRegistryModel):
    code: str
    category: str
    allowed_scopes: List[str]
    required_facets: List[str]
    tag_strategy: str


class ObjectRegistryModel(StrictRegistryModel):
    schema_version: str
    object_types: Dict[str, ObjectTypeDefinition]
    domains: List[str]


# --- Relation Registry ---
class RelationDefinition(StrictRegistryModel):
    category: str
    inverse_view: str
    dag: bool
    symmetric: bool
    source_types: List[str]
    target_types: List[str]
    opposed_to: Optional[str] = None


class RelationRegistryModel(StrictRegistryModel):
    schema_version: str
    relations: Dict[str, RelationDefinition]


# --- Taxonomy Registry ---
class TaxonomyNode(StrictRegistryModel):
    taxonomy_id: str
    name: str
    scope: str
    parent_id: Optional[str] = None
    description: Optional[str] = None


class TaxonomyRegistryModel(StrictRegistryModel):
    schema_version: str
    taxonomy: List[TaxonomyNode]


# --- Epistemic Registry ---
class EpistemicDimensionValue(StrictRegistryModel):
    rank: int
    description: Optional[str] = None


class EpistemicDimensionDefinition(StrictRegistryModel):
    description: Optional[str] = None
    values: Dict[str, EpistemicDimensionValue]


class EpistemicRegistryModel(StrictRegistryModel):
    schema_version: str
    dimensions: Dict[str, EpistemicDimensionDefinition]


# --- Governance Policy ---
class StatusConsensusRule(StrictRegistryModel):
    allowed_consensus: List[str]


class GovernancePolicyModel(StrictRegistryModel):
    schema_version: str
    status_consensus_rules: Dict[str, StatusConsensusRule]
    source_scope_propagation: Optional[Dict[str, Any]] = None
    privacy_and_retention: Optional[Dict[str, Any]] = None
    review_grace_period_days: Optional[int] = None
    allowed_actions: Optional[Dict[str, List[str]]] = None


# --- Facet Registry ---
class FacetDefinition(StrictRegistryModel):
    cardinality: Optional[str] = None
    description: Optional[str] = None
    allows_none: bool = False
    values: List[str]


class FacetRegistryModel(StrictRegistryModel):
    schema_version: str
    facets: Dict[str, FacetDefinition]


# --- Source Registry ---
class SourceCategoryDefinition(StrictRegistryModel):
    description: Optional[str] = None
    required_fields: List[str] = Field(default_factory=list)
    identity_requirement: Optional[str] = None
    recommended_fields: List[str] = Field(default_factory=list)
    actor_rule: Optional[str] = None


class SourceTypeDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    category: str
    source_taxonomy: List[str]
    medium: str
    semantic_kinds: List[str]
    identity_fields_any_of: Optional[List[List[str]]] = None
    provenance_requirements: List[str] = Field(default_factory=list)
    recommended_fields: List[str] = Field(default_factory=list)


class SourceRegistryModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    schema_version: str
    registry_id: Optional[str] = None
    description: Optional[str] = None
    categories: Dict[str, SourceCategoryDefinition]
    source_taxonomy: Dict[str, Any]
    source_types: Dict[str, SourceTypeDefinition]
    lifecycle: Optional[Dict[str, Any]] = None
    ingest_modes: Optional[List[str]] = None
    legacy_source_type_map: Optional[Dict[str, Any]] = None
    invariants: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    raw_storage: Optional[Dict[str, Any]] = None
    rules: Optional[List[Dict[str, Any]]] = None


# --- Actor Registry ---
class ActorTypeDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    description: Optional[str] = None
    identity_fields: List[str] = Field(default_factory=list)
    required_fields: List[str] = Field(default_factory=list)


class ActorRegistryModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    schema_version: str
    registry_id: Optional[str] = None
    description: Optional[str] = None
    actor_types: Dict[str, ActorTypeDefinition]
    role_assignments: Optional[Dict[str, Any]] = None
    actor_id_pattern: Optional[str] = None
    invariants: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    actors: Optional[List[Dict[str, Any]]] = None
    rules: Optional[List[Dict[str, Any]]] = None


# --- Threshold Policy ---
class ThresholdEntry(StrictRegistryModel):
    threshold_id: str
    decision_domain: str
    value: Any
    unit: str
    owner: str
    rationale: Optional[str] = None


class ThresholdRule(StrictRegistryModel):
    threshold_id: str
    statement: str


class ThresholdPolicyModel(StrictRegistryModel):
    schema_version: str
    policy_id: str
    calibration_status: Optional[str] = None
    thresholds: List[ThresholdEntry]
    rules: Optional[List[ThresholdRule]] = None


# --- Spec Ownership ---
class InvariantFamilyOwnership(StrictRegistryModel):
    family_id: str
    owner: str


class SpecOwnershipValidationConfig(StrictRegistryModel):
    duplicate_family_owners: str
    unknown_owner_paths: str
    invariant_ids_require_owner: str
    conformance_evidence_fields: List[str]
    runtime_and_tests: str


class SpecOwnershipModel(StrictRegistryModel):
    schema_version: str
    registry_id: str
    status: str
    invariant_families: List[InvariantFamilyOwnership]
    validation: SpecOwnershipValidationConfig
