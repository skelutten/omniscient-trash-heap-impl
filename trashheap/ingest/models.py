"""Data models for Universal Source Envelope, Representations, and Evidence Units (UNIVERSAL-SOURCE-EXTENSION.md)."""

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


def current_iso_timestamp() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def compute_sha256(data: bytes) -> str:
    """Compute sha256 hex digest prefixed with 'sha256:'."""
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


class RepresentationRecord(BaseModel):
    """Immutable representation metadata (INGEST-STAGING.md §7.1)."""

    model_config = ConfigDict(extra="ignore")

    representation_id: str
    representation_hash: str
    media_type: str = "text/plain"
    captured_at: str = Field(default_factory=current_iso_timestamp)
    raw_status: Literal["immutable"] = "immutable"
    supersedes: Optional[str] = None
    content_object_ref: Optional[str] = None
    byte_size: int = 0


class UniversalSourceEnvelope(BaseModel):
    """Universal Source Record envelope (UNIVERSAL-SOURCE-EXTENSION.md §3)."""

    model_config = ConfigDict(extra="ignore")

    source_id: str
    source_type: str
    category: Literal["Artifact", "Event", "Experience"]
    medium: str
    semantic_kind: str
    captured_at: str = Field(default_factory=current_iso_timestamp)
    lifecycle: str = "captured"
    identity: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    representation: RepresentationRecord
    payload: Dict[str, Any] = Field(default_factory=dict)


class EvidenceUnit(BaseModel):
    """Staging Evidence Unit projection (UNIVERSAL-SOURCE-EXTENSION.md §5)."""

    model_config = ConfigDict(extra="ignore")

    evidence_unit_ref: str
    observation_ref: Optional[str] = None
    source_refs: List[str]
    representation_refs: List[str]
    span_or_location: str
    target_ref: Optional[str] = None
    method: str = "direct_observation"
    verification_state: str = "unverified"
    fenced_content: Optional[str] = None
