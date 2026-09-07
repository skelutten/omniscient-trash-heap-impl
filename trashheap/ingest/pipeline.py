"""Universal Source intake pipeline, profile validation, and staging triage (Plan 03)."""

import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from trashheap.ingest.cscc import CaptureResult, commit_raw_capture
from trashheap.ingest.exceptions import SourceValidationError
from trashheap.ingest.models import (
    EvidenceUnit,
    RepresentationRecord,
    UniversalSourceEnvelope,
    compute_sha256,
    current_iso_timestamp,
)
from trashheap.ingest.security import (
    DEFAULT_MAX_SOURCE_BYTES,
    check_resource_limits,
    detect_prompt_injection_indicators,
    fence_untrusted_content,
    sandbox_path,
)
from trashheap.registry.loader import load_registries

SUPPORTED_PROFILES = {
    "document",
    "agent_trajectory",
    "thought",
    "meeting",
    "code_repository",
    "note",
}

WIKILINK_PATTERN = re.compile(r"\[\[([a-zA-Z0-9_\-\./]+)(?:\|[^\]]+)?\]\]")


@dataclass
class IngestionResult:
    """Result of source intake and staging."""

    source_id: str
    representation_id: str
    representation_hash: str
    envelope: UniversalSourceEnvelope
    capture_result: CaptureResult
    evidence_unit: EvidenceUnit
    evidence_unit_path: Path
    injections_detected: List[str] = field(default_factory=list)
    is_noop: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "representation_id": self.representation_id,
            "representation_hash": self.representation_hash,
            "is_noop": self.is_noop,
            "injections_detected": self.injections_detected,
            "evidence_unit_ref": self.evidence_unit.evidence_unit_ref,
            "evidence_unit_path": str(self.evidence_unit_path),
            "representation_dir": str(self.capture_result.representation_dir),
            "content_path": str(self.capture_result.content_path),
        }


@dataclass
class StageLintItem:
    """Triage report item for a staged Evidence Unit."""

    evidence_unit_ref: str
    source_refs: List[str]
    representation_refs: List[str]
    suggested_object_type: str
    candidate_relations: List[str]
    injections_detected: List[str]
    status: str = "staged"


@dataclass
class StageLintReport:
    """Aggregate triage report for staging/."""

    total_count: int
    items: List[StageLintItem]
    injections_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_count": self.total_count,
            "injections_count": self.injections_count,
            "items": [
                {
                    "evidence_unit_ref": item.evidence_unit_ref,
                    "source_refs": item.source_refs,
                    "representation_refs": item.representation_refs,
                    "suggested_object_type": item.suggested_object_type,
                    "candidate_relations": item.candidate_relations,
                    "injections_detected": item.injections_detected,
                    "status": item.status,
                }
                for item in self.items
            ],
        }


def _suggest_object_type(source_type: str) -> str:
    """Suggest canonical knowledge object type based on source type."""
    mapping = {
        "document": "concept",
        "code_repository": "specification",
        "agent_trajectory": "event",
        "meeting": "event",
        "thought": "note",
        "note": "note",
    }
    return mapping.get(source_type, "concept")


def intake_source(
    source_input: Union[str, Path, bytes],
    source_type: str = "document",
    workspace_root: Optional[Union[str, Path]] = None,
    identity: Optional[Dict[str, Any]] = None,
    provenance: Optional[Dict[str, Any]] = None,
    payload: Optional[Dict[str, Any]] = None,
    source_id: Optional[str] = None,
    representation_id: Optional[str] = None,
    semantic_kind: Optional[str] = None,
    actor_ref: Optional[str] = None,
    media_type: str = "text/plain",
    max_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> IngestionResult:
    """Universal source intake pipeline enforcing sandboxing, CSCC, fencing, and staging.

    Steps:
    1. Path sandboxing check (AccessDeniedError on escape/traversal)
    2. Byte retrieval & resource limits enforcement (QuarantineError on limit exceed)
    3. SHA-256 computation
    4. Prompt injection detection and immutable untrusted fencing
    5. Registry profile validation (SourceValidationError on invalid envelope/profile)
    6. Crash-safe Source Capture Commit (CSCC)
    7. Staging Evidence Unit projection
    """
    ws_root = Path(workspace_root).resolve() if workspace_root else Path.cwd().resolve()

    # Step 1 & 2: Sandboxing and Content Extraction
    resource_name = "raw_stream"
    extension = ".txt"

    if isinstance(source_input, (str, Path)):
        candidate_path = Path(source_input)
        is_file_like = (
            candidate_path.is_file()
            or "/" in str(source_input)
            or "\\" in str(source_input)
            or str(source_input).startswith(".")
        )

        if is_file_like:
            # Enforce path sandboxing against workspace root (FR-13, AC-6)
            resolved_target = sandbox_path(candidate_path, ws_root)
            if not resolved_target.exists():
                raise FileNotFoundError(
                    f"Source file '{candidate_path}' not found at '{resolved_target}'"
                )
            raw_bytes = resolved_target.read_bytes()
            try:
                resource_name = str(resolved_target.relative_to(ws_root))
            except ValueError:
                resource_name = resolved_target.name
            if resolved_target.suffix:
                extension = resolved_target.suffix
        else:
            # Treat as string payload
            raw_bytes = str(source_input).encode("utf-8")
    elif isinstance(source_input, bytes):
        raw_bytes = source_input
        extension = ".bin"
    else:
        raise SourceValidationError(f"Unsupported source_input type: {type(source_input)}")

    # Enforce resource limits (QuarantineError)
    check_resource_limits(raw_bytes, max_bytes=max_bytes)

    # Step 3: SHA-256 Hash
    content_hash = compute_sha256(raw_bytes)

    # Step 4: Prompt injection detection & untrusted fencing (FR-12, NFR-6, AC-5)
    try:
        text_content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text_content = raw_bytes.decode("latin-1", errors="replace")

    injections_detected = detect_prompt_injection_indicators(text_content)
    fenced_text = fence_untrusted_content(text_content)

    # Step 5: Profile Validation against source_registry.yaml
    registries = load_registries()
    source_reg = registries.source_registry

    if source_type not in source_reg.source_types:
        raise SourceValidationError(f"Unknown source_type '{source_type}' [E130]")

    if source_type not in SUPPORTED_PROFILES:
        raise SourceValidationError(
            f"Source type '{source_type}' is registered but has no executable profile in current engine [E131]"
        )

    profile_def = source_reg.source_types[source_type]
    category = profile_def.category
    medium = profile_def.medium

    # Determine semantic kind
    if semantic_kind is None:
        semantic_kind = profile_def.semantic_kinds[0] if profile_def.semantic_kinds else "document"
    elif semantic_kind not in profile_def.semantic_kinds:
        raise SourceValidationError(
            f"Invalid semantic_kind '{semantic_kind}' for source_type '{source_type}'. Allowed: {profile_def.semantic_kinds} [E134]"
        )

    # Construct and validate identity
    id_data = dict(identity or {})
    prov_data = dict(provenance or {})

    now_iso = current_iso_timestamp()

    # Pre-fill standard identity & provenance fields if absent
    if source_type == "document":
        id_data.setdefault("resource", resource_name)
        id_data.setdefault("representation_hash", content_hash)
        prov_data.setdefault("resource", resource_name)
        prov_data.setdefault("representation_hash", content_hash)
    elif source_type == "code_repository":
        id_data.setdefault("resource", resource_name)
        id_data.setdefault("representation_hash", content_hash)
        prov_data.setdefault("representation_hash", content_hash)
        if "repository_uri" in id_data and "revision_or_commit" in id_data:
            prov_data.setdefault("repository_uri", id_data["repository_uri"])
            prov_data.setdefault("revision_or_commit", id_data["revision_or_commit"])
        else:
            prov_data.setdefault("repository_uri", "file://" + resource_name)
            prov_data.setdefault("revision_or_commit", "HEAD")
    elif source_type in {"thought", "note"}:
        id_data.setdefault("actor_ref", actor_ref or "human:user")
        id_data.setdefault("experienced_at", now_iso)
        id_data.setdefault("content_hash", content_hash)
        prov_data.setdefault("actor_ref", id_data["actor_ref"])
        prov_data.setdefault("experienced_at", id_data["experienced_at"])
        prov_data.setdefault("content_hash", content_hash)
    elif source_type == "agent_trajectory":
        id_data.setdefault("representation_hash", content_hash)
        prov_data.setdefault("representation_hash", content_hash)
        prov_data.setdefault("occurred_at", now_iso)
    elif source_type == "meeting":
        prov_data.setdefault("occurred_at", now_iso)

    # Validate identity_fields_any_of
    if profile_def.identity_fields_any_of:
        matched_identity = False
        for option_fields in profile_def.identity_fields_any_of:
            if all(f in id_data and id_data[f] for f in option_fields):
                matched_identity = True
                break
        if not matched_identity:
            raise SourceValidationError(
                f"Identity for source_type '{source_type}' does not satisfy any allowed set in {profile_def.identity_fields_any_of}. Given: {list(id_data.keys())} [E132]"
            )

    # Validate provenance_requirements
    for req in profile_def.provenance_requirements:
        if req not in prov_data or not prov_data[req]:
            raise SourceValidationError(
                f"Missing required provenance field '{req}' for source_type '{source_type}' [E133]"
            )

    # Generate IDs if not provided
    generated_source_id = source_id or f"SRC-{uuid.uuid4().hex[:12].upper()}"
    generated_rep_id = representation_id or f"REP-{uuid.uuid4().hex[:12].upper()}"

    rep_record = RepresentationRecord(
        representation_id=generated_rep_id,
        representation_hash=content_hash,
        media_type=media_type,
        captured_at=now_iso,
        raw_status="immutable",
        byte_size=len(raw_bytes),
    )

    envelope = UniversalSourceEnvelope(
        source_id=generated_source_id,
        source_type=source_type,
        category=category,
        medium=medium,
        semantic_kind=semantic_kind,
        captured_at=now_iso,
        lifecycle="captured",
        identity=id_data,
        provenance=prov_data,
        representation=rep_record,
        payload=payload or {},
    )

    # Step 6: CSCC Commit (raw capture)
    capture_result = commit_raw_capture(
        workspace_root=ws_root,
        envelope=envelope,
        raw_bytes=raw_bytes,
        extension=extension,
    )

    # Step 7: Staging Evidence Unit projection
    staging_eu_dir = ws_root / "staging" / "evidence_units"
    staging_eu_dir.mkdir(parents=True, exist_ok=True)

    eu_ref = f"EU-{uuid.uuid4().hex[:12].upper()}"
    evidence_unit = EvidenceUnit(
        evidence_unit_ref=eu_ref,
        source_refs=[envelope.source_id],
        representation_refs=[envelope.representation.representation_id],
        span_or_location=f"{envelope.source_type}://{envelope.source_id}#L1",
        target_ref=None,
        method="direct_observation",
        verification_state="unverified",
        fenced_content=fenced_text,
    )

    eu_path = staging_eu_dir / f"{eu_ref}.yaml"
    tmp_eu_path = staging_eu_dir / f".{eu_ref}.yaml.tmp"

    eu_dict = evidence_unit.model_dump()
    if injections_detected:
        eu_dict["injections_detected"] = injections_detected

    with open(tmp_eu_path, "w", encoding="utf-8") as f:
        yaml.dump(eu_dict, f, sort_keys=False, allow_unicode=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_eu_path, eu_path)

    return IngestionResult(
        source_id=envelope.source_id,
        representation_id=envelope.representation.representation_id,
        representation_hash=content_hash,
        envelope=envelope,
        capture_result=capture_result,
        evidence_unit=evidence_unit,
        evidence_unit_path=eu_path,
        injections_detected=injections_detected,
        is_noop=capture_result.is_noop,
    )


def stage_lint(staging_dir: Union[str, Path]) -> StageLintReport:
    """Scan staging directory, analyze Evidence Units, draft frontmatter, and extract candidate relations."""
    s_path = Path(staging_dir)
    items: List[StageLintItem] = []
    injections_count = 0

    eu_dir = s_path / "evidence_units"
    candidate_files = []
    if eu_dir.exists() and eu_dir.is_dir():
        candidate_files.extend(eu_dir.glob("*.yaml"))
        candidate_files.extend(eu_dir.glob("*.yml"))
    elif s_path.exists() and s_path.is_dir():
        candidate_files.extend(s_path.glob("*.yaml"))
        candidate_files.extend(s_path.glob("*.yml"))

    for f_path in sorted(candidate_files):
        if f_path.name.startswith("."):
            continue
        try:
            with open(f_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict) or "evidence_unit_ref" not in data:
                continue

            fenced_content = data.get("fenced_content") or ""
            injections = data.get("injections_detected") or detect_prompt_injection_indicators(
                fenced_content
            )
            if injections:
                injections_count += len(injections)

            # Detect candidate relations via [[wikilinks]]
            links = WIKILINK_PATTERN.findall(fenced_content)
            unique_links = sorted(list(set(links)))

            suggested_type = "concept"
            source_refs = data.get("source_refs", [])
            rep_refs = data.get("representation_refs", [])

            items.append(
                StageLintItem(
                    evidence_unit_ref=data["evidence_unit_ref"],
                    source_refs=source_refs,
                    representation_refs=rep_refs,
                    suggested_object_type=suggested_type,
                    candidate_relations=unique_links,
                    injections_detected=injections,
                    status="staged",
                )
            )
        except Exception:
            continue

    return StageLintReport(
        total_count=len(items),
        items=items,
        injections_count=injections_count,
    )
