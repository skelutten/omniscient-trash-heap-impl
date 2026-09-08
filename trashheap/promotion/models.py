"""Data models for Proposal, Review Decisions, and Promotion Operations (specs/REVIEW-PROMOTION.md)."""

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from trashheap.constants import ACTOR_PATTERN

CandidateState = Literal[
    "pending", "in_review", "approved", "rejected", "expired", "superseded", "promoted"
]
MaterializationState = Literal["not_promoted", "promoting", "promoted", "failed"]
DecisionType = Literal["approve", "reject", "request_revision"]
MutationAction = Literal["create", "replace_owned_sections", "append_notes", "update_frontmatter"]

ACTOR_REGEX = re.compile(ACTOR_PATTERN)


def current_iso_timestamp() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def compute_content_sha256(content: str) -> str:
    """Return sha256:<hex> for a text string."""
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return f"sha256:{h}"


class StateTransitionRecord(BaseModel):
    """Immutable transition audit entry (REVIEW-001)."""

    model_config = ConfigDict(extra="forbid")

    transition_id: str
    candidate_id: str
    proposal_revision: int
    previous_state: str
    new_state: str
    actor: str
    transitioned_at: str = Field(default_factory=current_iso_timestamp)
    reason: str
    validation_result: Optional[str] = None
    source_refs: List[str] = Field(default_factory=list)
    representation_refs: List[str] = Field(default_factory=list)


class ReviewDecision(BaseModel):
    """Formal review decision record binding to exact proposal revision and hash (REVIEW-002..REVIEW-004)."""

    model_config = ConfigDict(extra="forbid")

    decision_id: str
    candidate_id: str
    proposal_revision: int
    decision: DecisionType
    reviewer: str
    decided_at: str = Field(default_factory=current_iso_timestamp)
    proposal_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    source_revision: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    validation_run_id: str
    reason: str

    @field_validator("reviewer")
    @classmethod
    def validate_reviewer_actor(cls, v: str) -> str:
        if not ACTOR_REGEX.match(v):
            raise ValueError(f"Reviewer '{v}' does not match actor contract (ACTOR_PATTERN)")
        return v


class MutationRecord(BaseModel):
    """Allowlisted mutation item (PROMO-001)."""

    model_config = ConfigDict(extra="forbid")

    path: str
    action: MutationAction
    content_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    rendered_content: Optional[str] = None


class PromotionOperation(BaseModel):
    """Deterministic promotion operation record (PROMO-001..PROMO-006)."""

    model_config = ConfigDict(extra="forbid")

    operation_id: str
    operation_version: str = "0.1.0"
    candidate_id: str
    proposal_revision: int
    approval_decision_id: str
    expected_source_revision: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    requested_mutations: List[MutationRecord]
    idempotency_key: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")


class SemanticResolutionRecord(BaseModel):
    """Explicit audit record of semantic duplicate/match resolution decisions (G-3)."""

    outcome: str = "NEW_CANDIDATE"  # EXISTING_MATCH, NEW_CANDIDATE, EVIDENCE_ONLY, CONTRADICTION, UNRESOLVED
    method: str = "hybrid_rrf"
    candidate_ids: List[str] = Field(default_factory=list)
    decision_confidence: float = 1.0
    evidence: Dict[str, Any] = Field(default_factory=dict)
    requires_review: bool = False


class CandidateProposal(BaseModel):
    """Full Candidate Proposal record staged for review and promotion."""

    model_config = ConfigDict(extra="ignore")

    candidate_id: str
    proposal_revision: int = 1
    created_at: str = Field(default_factory=current_iso_timestamp)
    state: CandidateState = "pending"
    materialization_state: MaterializationState = "not_promoted"
    evidence_unit_ref: Optional[str] = None
    source_refs: List[str] = Field(default_factory=list)
    representation_refs: List[str] = Field(default_factory=list)
    source_revision: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    target_path: str
    proposed_frontmatter: Dict[str, Any]
    proposed_body: str
    proposed_content: str
    proposal_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    history: List[StateTransitionRecord] = Field(default_factory=list)
    review_decision: Optional[ReviewDecision] = None
    supersedes: Optional[str] = None
    semantic_resolution: Optional[SemanticResolutionRecord] = None

