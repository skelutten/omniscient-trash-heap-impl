# LLM Wiki Ingestion Data Models & Production Configuration Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-INGEST-DATA-MODEL-001`
> **Document family ID**: `LLM-WIKI-INGEST-SPEC-001`
> **Version**: `v0.5.2-RC` (Production-Hardening Candidate)
> **Updated**: `2026-08-17`
> **Source**: Extracted from `LLM-WIKI-INGEST-SPEC-001` §11, §13
> **Status**: `DRAFT`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Universal Source addendum**: normative design extension; runtime unimplemented
> **Compatibility target**: Additive, non-invasive, opt-in
> **Normative owner**: This document owns ingestion data models, normalized Source Record envelope and production configuration schemas
> **Related documents**: `UNIVERSAL-SOURCE-EXTENSION.md`, `INGEST-ADAPTERS.md`, `INGEST-STAGING.md`, `VALIDATION.md`

---

## Universal Source Record addendum

The trajectory model is a typed specialization, not the universal input
abstraction. Every input MUST be representable as a normalized Source Record
with a common envelope and typed payload:

```yaml
source_id: SRC-...
source_type: web_resource
category: Artifact
medium: web
semantic_kind: article
captured_at: 2026-08-17T18:31:22Z
identity: {canonical_uri: https://example.test/article}
representation:
  representation_id: REP-...
  representation_hash: sha256:...
raw_ref: raw/sources/SRC-.../representations/REP-...
payload: {}
```

`Source identity`, `Representation`, `Content Object` and `Normalized Source
Record` MUST remain distinct. Raw content is immutable and append-only; a
changed representation creates a new representation. The typed payload MUST
retain source-specific richness and MUST NOT be flattened into trajectory
fields.

The generic envelope is not a permissive source validator. A registry-driven
validator MUST resolve `source_type` in `source_registry.yaml`, verify the
declared category and taxonomy path, reject identity keys not allowed by that
source profile, require at least one complete identity alternative, validate
category-required provenance fields, verify the representation hash against the
immutable raw bytes, and fail closed on ambiguity. Source identity and
representation identity MUST be validated separately. Source types without an
implemented profile remain declared-but-unsupported and MUST be reported as
such; they MUST NOT silently pass through the generic dictionary fields.

> **Compatibility target**: Additive, non-invasive, opt-in
> **System documents**: `INGEST.md` (core) · `INGEST-ADAPTERS.md` (§3) · `INGEST-PIPELINE.md` (§4–§6) · `INGEST-STAGING.md` (§7, §9–§10) · `INGEST-DATA-MODEL.md` (§11, §13)

---

## 11. Data Models & Pydantic v2 Schemas

> **Note on exception messages:** the **normative** contract in the code samples
> below is the bracketed error code (`[E104]`, `[E122]`, …) registered in
> `VALIDATION.md` §10.3 — not the human-readable message text, which
> implementations MAY reword or localize.


```python
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AgentSourceEnum(str, Enum):
  KIRO = "kiro"
  MISTRAL_VIBE = "mistral_vibe"
  OPENCODE = "opencode"
  ANTIGRAVITY = "antigravity"
  CLAUDE_CODE = "claude_code"
  SWE_AGENT = "swe_agent"
  GENERIC_OTEL = "generic_otel"


class SourceCategoryEnum(str, Enum):
  """Universal Source top-level category (SOURCE-001..014)."""
  ARTIFACT = "Artifact"
  EVENT = "Event"
  EXPERIENCE = "Experience"


class SourceEnvelope(BaseModel):
  """Common envelope; `payload` remains source-type-specific."""

  model_config = ConfigDict(extra="forbid")
  source_id: str
  source_type: str
  category: SourceCategoryEnum
  medium: str
  semantic_kind: Optional[str] = None
  captured_at: datetime
  lifecycle: Literal["captured", "normalized", "interpreted", "verified", "superseded", "retracted", "expired", "deleted"] = "captured"
  actor_ref: Optional[str] = None
  identity: Dict[str, str]
  representation_id: str
  representation_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
  payload: Dict[str, Any] = Field(default_factory=dict)

  @field_validator("captured_at")
  @classmethod
  def require_tz_aware(cls, v: datetime) -> datetime:
    if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
      raise ValueError("Naive datetime (missing tzinfo) is forbidden. [E137]")
    return v


class ActionTypeEnum(str, Enum):
  EXECUTE_BASH = "execute_bash"
  EDIT_FILE = "edit_file"
  READ_FILE = "read_file"
  SEARCH_CODE = "search_code"
  MCP_CALL = "mcp_call"


class TrajectoryStep(BaseModel):
  model_config = ConfigDict(extra="forbid")

  step_index: int = Field(ge=0)
  timestamp: datetime
  action_type: ActionTypeEnum
  tool_name: str
  tool_input: Dict[str, Any]
  tool_output: str
  exit_code: Optional[int] = None
  files_modified: List[str] = Field(default_factory=list)

  @field_validator("timestamp")
  @classmethod
  def require_tz_aware(cls, v: datetime) -> datetime:
    # E122: determinism across hosts requires explicit time zone (§6.1).
    if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
      raise ValueError("Naive datetime (missing tzinfo) is forbidden. [E122]")
    return v


class NormalizedTrajectoryDraft(BaseModel):
  """Draft trajectory before canonical hash computation."""

  model_config = ConfigDict(extra="forbid")

  schema_version: str = Field(default="0.5.2", pattern=r"^0\.5\.\d+$")
  trajectory_id: str = Field(pattern=r"^TRAJ-[A-Z0-9_-]+$")
  trajectory_revision: int = Field(default=1, ge=1)
  ingestion_id: str = Field(pattern=r"^INGEST-[a-f0-9]{8,16}$")
  agent_source: AgentSourceEnum
  session_id: str
  intent: str
  workspace_root: str
  git_repo: Optional[str] = None
  git_branch: Optional[str] = None
  inferred_scope: Literal["personal", "engineering", "ambiguous"]
  scope_inference_confidence: float = Field(ge=0.0, le=1.0)
  start_time: datetime
  end_time: datetime
  outcome: Literal["success", "failure", "partial"]
  steps: List[TrajectoryStep]

  @field_validator("start_time", "end_time")
  @classmethod
  def require_tz_aware(cls, v: datetime) -> datetime:
    # E122: determinism across hosts requires explicit time zone (§6.1).
    if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
      raise ValueError("Naive datetime (missing tzinfo) is forbidden. [E122]")
    return v


class NormalizedTrajectory(NormalizedTrajectoryDraft):
  """Immutable, canonically hashed trajectory."""

  input_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class EvidenceBundle(BaseModel):
  """Deterministically derived evidence before the LLM call (INGEST-CORE-016)."""

  model_config = ConfigDict(extra="forbid")

  trajectory_id: str
  trajectory_revision: int
  ingestion_id: str
  input_sha256: str
  # All trajectory steps are included (no implicit filtering);
  # the field is named accordingly (v0.5.2-RC, previously `relevant_steps`).
  step_indices: List[int]
  files_modified: List[str]
  commands_executed: List[str]
  # Only exit-0 commands that match `verification_command_patterns` (§13)
  # qualify as a verification receipt; arbitrary commands (e.g. `ls`)
  # give NO points in Q_det (v0.5.2-RC).
  verification_receipt: Optional[str] = None
  derived_at: datetime


class ProvenanceMetadata(BaseModel):
  """Complete revision and provenance chain."""

  model_config = ConfigDict(extra="forbid")

  ingestion_version: str = "0.5.2"
  adapter_id: str
  adapter_contract_version: str
  sanitizer_version: str
  scope_policy_version: str
  taxonomy_version: str
  extraction_model: str
  extraction_prompt_version: str
  ontology_version: str = "3.8.10"
  quality_formula_version: str = "2.1.0"


class ExtractedIncident(BaseModel):
  """Root object for the ENGINEERING triad. `Incident` is ENGINEERING_ONLY (ID-005)."""

  model_config = ConfigDict(extra="forbid")
  title: str = Field(min_length=5, max_length=140)
  symptoms: str
  error_logs_excerpt: str
  environment: Dict[str, str] = Field(default_factory=dict)


class ExtractedObservation(BaseModel):
  """Root object for the PERSONAL triad.

  `Observation` allows both scopes (object_registry.yaml) and is used as
  root when `Incident` would be an ID-005 violation. Mandatory facet: `toolchain`.
  """

  model_config = ConfigDict(extra="forbid")
  title: str = Field(min_length=5, max_length=140)
  observation_summary: str
  observed_change: str
  environment: Dict[str, str] = Field(default_factory=dict)


class ExtractedLesson(BaseModel):
  model_config = ConfigDict(extra="forbid")
  title: str = Field(min_length=5, max_length=140)
  root_cause: str
  insight: str


class ExtractedWorkflowStep(BaseModel):
  model_config = ConfigDict(extra="forbid")
  step_number: int = Field(ge=1)
  action: str
  command: Optional[str] = None
  explanation: str


class ExtractedWorkflow(BaseModel):
  model_config = ConfigDict(extra="forbid")
  title: str = Field(min_length=5, max_length=140)
  prerequisites: List[str] = Field(default_factory=list)
  steps: List[ExtractedWorkflowStep] = Field(min_length=1)
  verification_command: Optional[str] = None


def generate_deterministic_proposal_id(
    trajectory_id: str,
    trajectory_revision: int,
    input_sha256: str,
    schema_version: str,
    start_time: datetime,
) -> str:
  date_str = start_time.astimezone(timezone.utc).strftime("%Y%m%d")
  payload = f"{trajectory_id}|{trajectory_revision}|{input_sha256}|{schema_version}".encode(
      "utf-8"
  )
  digest_16 = hashlib.sha256(payload).hexdigest()[:16]
  return f"DISC-PROP-{date_str}-{digest_16}"


class SynthesizedKnowledgeBundle(BaseModel):
  """Discovery proposal with SCOPE-CONDITIONAL triad (INGEST-CORE-004, E104).

  engineering => root object `incident` (Incident is ENGINEERING_ONLY, ID-005)
  personal    => root object `observation` (Observation allows both scopes)
  """

  model_config = ConfigDict(extra="forbid")

  schema_version: str = Field(default="0.5.2", pattern=r"^0\.5\.\d+$")
  proposal_id: str = Field(pattern=r"^DISC-PROP-\d{8}-[a-f0-9]{16}$")
  trajectory_id: str
  trajectory_revision: int = Field(default=1, ge=1)
  ingestion_id: str
  inferred_scope: Literal["personal", "engineering", "ambiguous"]
  scope_confidence: float = Field(ge=0.0, le=1.0)
  # "decision_cache" = Version-Bound Decision Cache (§4.1 step 1).
  scope_method: Literal[
      "decision_cache",
      "repo_anchor",
      "keyword_rule",
      "llm_classifier",
      "historical_unknown",
  ]
  scope_status: Literal["inferred", "reviewed", "confirmed"] = "inferred"
  # Explicit scope bridging (E105): allows engineering trajectories to
  # propose links to personal objects under review (§9.4.6).
  cross_scope: bool = False
  inferred_domain: str
  # Taxonomy choice per §9.4.4: the extractor MUST choose a taxonomy_id from
  # the scope's tree; validated against taxonomy_registry.yaml on promotion.
  inferred_taxonomy_id: Optional[str] = None
  inferred_facets: Dict[str, Any]
  epistemic_status: Literal["inferred", "reviewed", "confirmed"] = "inferred"
  evidence_level: Literal[
      "trajectory_observed", "reproduced_verified", "formal_proof"
  ] = "trajectory_observed"
  validation_status: Literal["unverified", "tool_verified", "peer_verified"] = (
      "unverified"
  )
  promotion_status: Literal["staged", "promoted", "failed"] = "staged"
  provenance: ProvenanceMetadata
  evidence_bundle: EvidenceBundle
  incident: Optional[ExtractedIncident] = None
  observation: Optional[ExtractedObservation] = None
  lesson: Optional[ExtractedLesson] = None
  workflow: Optional[ExtractedWorkflow] = None
  model_confidence: float = Field(ge=0.0, le=1.0)
  quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
  status: Literal["pending", "approved", "rejected", "expired"] = "pending"
  created_at: datetime
  expires_at: datetime
  input_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")

  @field_validator("expires_at")
  @classmethod
  def validate_ttl(cls, v: datetime, info) -> datetime:
    created = info.data.get("created_at")
    scope = info.data.get("inferred_scope")
    if created:
      delta = v - created
      if delta.total_seconds() < 0:
        raise ValueError("expires_at must be greater than created_at.")
      max_days = 180 if scope == "ambiguous" else 90
      if delta > timedelta(days=max_days):
        raise ValueError(
            f"TTL exceeds {max_days} days for scope '{scope}'."
        )
    return v

  @model_validator(mode="after")
  def enforce_scope_conditional_triad(self) -> "SynthesizedKnowledgeBundle":
    """INGEST-CORE-004 / E104: the root object follows scope; Incident is
    ENGINEERING_ONLY (ID-005) and MUST NOT appear in personal proposals."""
    if self.inferred_scope == "engineering":
      if self.observation is not None:
        raise ValueError(
            "The engineering triad uses Incident as root, not Observation. [E104]"
        )
      if self.incident is None:
        raise ValueError("Engineering scope REQUIRES the root object Incident. [E104]")
    elif self.inferred_scope == "personal":
      if self.incident is not None:
        raise ValueError(
            "Incident MUST NOT be assigned personal scope (ENGINEERING_ONLY,"
            " ID-005). [E104]"
        )
      if self.observation is None:
        raise ValueError(
            "Personal scope REQUIRES the root object Observation. [E104]"
        )
    else:  # ambiguous: at least one root object required before review
      if self.incident is None and self.observation is None:
        raise ValueError(
            "At least one root object (Incident or Observation) is required. [E104]"
        )
    return self


class RejectedProposalBundle(BaseModel):
  """Terminal audit schema for rejected proposals."""

  model_config = ConfigDict(extra="forbid")

  schema_version: str = Field(default="0.5.2", pattern=r"^0\.5\.\d+$")
  proposal_id: str = Field(pattern=r"^DISC-PROP-\d{8}-[a-f0-9]{16}$")
  trajectory_id: str
  trajectory_revision: int = Field(default=1, ge=1)
  ingestion_id: str
  inferred_scope: Literal["personal", "engineering", "ambiguous"]
  inferred_domain: str
  rejection_reason: Literal[
      "LOW_QUALITY",
      "LOW_CONFIDENCE",
      "REPRODUCIBILITY_FAILED",
      "INVALID_ONTOLOGY",
      "SANITIZATION_UNCERTAIN",
  ]
  # Scope-conditional root object (E104): exactly one of incident/observation.
  incident: Optional[ExtractedIncident] = None
  observation: Optional[ExtractedObservation] = None
  model_confidence: float = Field(ge=0.0, le=1.0)
  quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
  created_at: datetime
  expires_at: datetime
  input_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")

  @model_validator(mode="after")
  def require_root_object(self) -> "RejectedProposalBundle":
    if self.incident is None and self.observation is None:
      raise ValueError(
          "RejectedProposalBundle requires at least one root object. [E104]"
      )
    if self.incident is not None and self.observation is not None:
      raise ValueError(
          "Exactly one root object is allowed per scope-conditional triad. [E104]"
      )
    return self

```

---

## 13. Appendix: Production Configuration (`wiki_ingest_config.yaml`)

```yaml
version: "0.5.2"

daemon:
  poll_interval_seconds: 5
  write_quiescence_seconds: 5.0
  # Used by acquire_daemon_singleton (§3.4): the only protection against false
  # positives in conservative mode (v0.5.2-RC).
  stale_lock_ttl_seconds: 300
  pid_lock_path: "~/.trashheap/locks/wiki-ingestd.pid"
  # File-Lock for canonical ID allocation (§9.4.5, v0.5.2-RC).
  id_allocation_lock_path: "~/.trashheap/locks/id_alloc.json"
  max_concurrent_extractions: 3
  rate_limit_per_minute: 10
  token_bucket_burst: 15
  model_endpoint: "anthropic/claude-3-5-sonnet"
  extraction_confidence_threshold: 0.75
  deterministic_evidence_threshold: 0.45
  quality_composite_threshold: 0.70
  scope_confidence_threshold: 0.85

extraction:
  # Only exit-0 commands that match these patterns qualify as a
  # verification receipt in EvidenceBundle (§5.1, v0.5.2-RC).
  verification_command_patterns:
    - ".*pytest.*"
    - ".*\\btest(s)?\\b.*"
    - ".*ruff.*"
    - ".*\\blint\\b.*"
    - ".*\\bbuild\\b.*"
    - ".*make\\b.*"
  # Deterministic taxonomy fallbacks (§9.4.4, v0.5.2-RC).
  taxonomy_fallback_personal: "TX-PERS-10"
  taxonomy_fallback_engineering: "TX-ENG-06"

retention:
  # Grace period for expired rows before cleanup (§7.3, v0.5.2-RC).
  reaper_grace_days: 7

sanitization:
  max_field_bytes: 1048576       # 1 MB
  max_trajectory_bytes: 52428800 # 50 MB
  custom_allowlist_patterns:
    - "\\b[A-Za-z0-9_-]+\\.(proto|asn1|c|cpp|rs|py|json|parquet)\\b"
    - "\\b[A-Z0-9_]{4,10}_VERSION\\b"
  custom_pii_entities:
    - "KundX"
    - "ProjektY"

storage:
  discovery_parquet_path: "discovery/concept_proposals.parquet"
  ambiguous_parquet_path: "discovery/ambiguous_scope.parquet"
  rejected_parquet_path: "discovery/rejected_low_quality.parquet"
  sanitized_trajectories_path: "discovery/trajectories/sanitized"
  watermark_db_path: "~/.trashheap/ingest_state.db"
  discovery_ttl_days: 90
  ambiguous_ttl_days: 180
  sanitized_audit_retention_days: 365
```

---

**End of LLM Wiki Ingestion Data Models & Production Configuration Specification v0.5.2-RC**

See also: `INGEST.md` (core specification and INGEST-CORE invariants).