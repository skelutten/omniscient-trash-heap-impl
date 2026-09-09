"""Candidate extraction, review decisions, and DPCP deterministic promotion engine (Plan 04)."""

import os
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from trashheap.corpus import load_corpus, load_single_file
from trashheap.ingest.exceptions import AccessDeniedError
from trashheap.ingest.models import EvidenceUnit
from trashheap.ingest.security import sandbox_path
from trashheap.linter import Linter
from trashheap.promotion.exceptions import (
    ApprovalBindingError,
    ConflictError,
    PromotionError,
    StateTransitionError,
    ValidationRollbackError,
)
from trashheap.promotion.journal import DPCPJournal
from trashheap.promotion.lock import canonical_promotion_lock
from trashheap.promotion.models import (
    ACTOR_REGEX,
    CandidateProposal,
    ReviewDecision,
    StateTransitionRecord,
    compute_content_sha256,
    current_iso_timestamp,
)
from trashheap.registry.loader import load_registries


@dataclass
class PromotionResult:
    """Result of DPCP candidate promotion."""

    candidate_id: str
    proposal_revision: int
    operation_id: str
    target_path: Path
    content_hash: str
    is_noop: bool = False
    audit_record: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "proposal_revision": self.proposal_revision,
            "operation_id": self.operation_id,
            "target_path": str(self.target_path),
            "content_hash": self.content_hash,
            "is_noop": self.is_noop,
            "audit_record": self.audit_record or {},
        }


def get_proposals_dir(workspace_root: Path) -> Path:
    p_dir = workspace_root / "staging" / "proposals"
    p_dir.mkdir(parents=True, exist_ok=True)
    return p_dir


def get_journal(workspace_root: Path) -> DPCPJournal:
    db_path = workspace_root / "staging" / "transactions" / "dpcp_journal.sqlite3"
    return DPCPJournal(db_path)


def save_candidate(proposal: CandidateProposal, workspace_root: Path) -> Path:
    """Save proposal atomically to staging/proposals/<candidate_id>.yaml."""
    p_dir = get_proposals_dir(workspace_root)
    dest = p_dir / f"{proposal.candidate_id}.yaml"
    tmp = p_dir / f".{proposal.candidate_id}.yaml.tmp"

    data = proposal.model_dump()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, dest)
    return dest


def load_candidate(candidate_id: str, workspace_root: Path) -> CandidateProposal:
    """Load proposal from staging/proposals/<candidate_id>.yaml."""
    p_dir = get_proposals_dir(workspace_root)
    f_path = p_dir / f"{candidate_id}.yaml"
    if not f_path.exists():
        raise FileNotFoundError(f"Candidate proposal '{candidate_id}' not found at {f_path}")
    with open(f_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return CandidateProposal.model_validate(data)


def list_candidates(
    workspace_root: Path, state_filter: Optional[str] = None
) -> List[CandidateProposal]:
    """List all candidate proposals in staging/proposals/."""
    p_dir = get_proposals_dir(workspace_root)
    candidates = []
    for f in sorted(p_dir.glob("*.yaml")):
        if f.name.startswith("."):
            continue
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = yaml.safe_load(fp)
            c = CandidateProposal.model_validate(data)
            if state_filter is None or c.state == state_filter:
                candidates.append(c)
        except Exception:
            continue
    return candidates


def create_candidate_proposal(
    candidate_id: Optional[str] = None,
    evidence_unit: Optional[EvidenceUnit] = None,
    source_revision: Optional[str] = None,
    source_refs: Optional[List[str]] = None,
    representation_refs: Optional[List[str]] = None,
    target_path: Optional[str] = None,
    scope: str = "engineering",
    object_type: str = "Concept",
    domain: Optional[str] = None,
    taxonomy_path: Optional[str] = None,
    taxonomy_id: Optional[str] = None,
    title: Optional[str] = None,
    body: Optional[str] = None,
    frontmatter_overrides: Optional[Dict[str, Any]] = None,
    workspace_root: Optional[Path] = None,
) -> CandidateProposal:
    """Synthesize a compliant CandidateProposal from an EvidenceUnit or manual inputs."""
    ws = workspace_root or Path.cwd().resolve()
    registries = load_registries()

    cid = candidate_id or f"CAND-{uuid.uuid4().hex[:12].upper()}"
    src_refs = source_refs or (evidence_unit.source_refs if evidence_unit else ["SRC-DIRECT"])
    rep_refs = representation_refs or (
        evidence_unit.representation_refs if evidence_unit else ["REP-DIRECT"]
    )
    src_rev = source_revision or (
        evidence_unit.representation_refs[0]
        if evidence_unit and evidence_unit.representation_refs
        else "sha256:" + "0" * 64
    )
    if not src_rev.startswith("sha256:"):
        src_rev = "sha256:" + "0" * 64

    # Resolve defaults from registry
    if scope == "engineering":
        chosen_domain = domain or "software_engineering"
        chosen_tax_path = taxonomy_path or "01. Domain & System Architecture"
        chosen_tax_id = taxonomy_id or "TX-ENG-01"
        chosen_type = object_type if object_type in registries.object_types else "Concept"
        canonical_id = f"ENG-CON-{uuid.uuid4().hex[:4].upper()}-0001"
        rel_dir = "engineering/01_domain_system_architecture"
    else:
        chosen_domain = domain or "computer_science"
        chosen_tax_path = (
            taxonomy_path
            or "07. Computer Science, AI & Information Technology / 07.04. AI-Assisted Software Engineering"
        )
        chosen_tax_id = taxonomy_id or "TX-PERS-07-04"
        chosen_type = object_type if object_type in registries.object_types else "Observation"
        canonical_id = f"PERS-OBS-{uuid.uuid4().hex[:4].upper()}-0001"
        rel_dir = (
            "personal/07_computer_science_ai_it_security/07_04_ai_assisted_software_engineering"
        )

    t_path = target_path or f"{rel_dir}/{canonical_id}.md"
    doc_title = title or f"Candidate Knowledge for {cid}"

    today_str = date.today().isoformat()
    review_date = (date.today() + timedelta(days=90)).isoformat()

    # Base compliant 9-category frontmatter
    fm: Dict[str, Any] = {
        "id": canonical_id,
        "title": doc_title,
        "schema_version": "3.8.10",
        "aliases": [cid],
        "keywords": ["candidate", "ingestion"],
        "scope": scope,
        "taxonomy_path": chosen_tax_path,
        "taxonomy_id": chosen_tax_id,
        "object_type": chosen_type,
        "domain": chosen_domain,
        "toolchain": ["pytest"],
        "language": ["en"],
        "audience": "engineer",
        "evidence": "inferred",
        "verification": "unverified",
        "authority": "informative",
        "consensus": "proposed",
        "source_type": "document",
        "source_refs": src_refs,
        "author": "process:wiki-ingestd",
        "last_modified": today_str,
        "confidence": 0.85,
        "last_verified": today_str,
        "next_review": review_date,
        "reviewer": "process:wiki-ingestd",
        "validity": {"valid_from": today_str, "valid_until": None},
        "status": "draft",
        "relations": [],
    }

    if frontmatter_overrides:
        fm.update(frontmatter_overrides)

    # Standard body with known template heading & Notes
    if body is None:
        body_content = (
            "## Introduction & Definition\n\n"
            f"Autonomous proposal derived from staged evidence {src_refs}.\n\n"
            "## Notes\n\n"
            "Initial candidate staging extraction."
        )
    else:
        body_content = body

    # Render full markdown with YAML frontmatter fence
    fm_yaml = yaml.dump(fm, sort_keys=False, allow_unicode=True)
    full_content = f"---\n{fm_yaml}---\n\n{body_content}\n"
    p_hash = compute_content_sha256(full_content)

    initial_trans = StateTransitionRecord(
        transition_id=f"TR-{uuid.uuid4().hex[:12].upper()}",
        candidate_id=cid,
        proposal_revision=1,
        previous_state="none",
        new_state="pending",
        actor="process:ingest-pipeline",
        transitioned_at=current_iso_timestamp(),
        reason="Staged from Evidence Unit",
        validation_result="staged",
        source_refs=src_refs,
        representation_refs=rep_refs,
    )

    proposal = CandidateProposal(
        candidate_id=cid,
        proposal_revision=1,
        created_at=current_iso_timestamp(),
        state="pending",
        materialization_state="not_promoted",
        evidence_unit_ref=evidence_unit.evidence_unit_ref if evidence_unit else None,
        source_refs=src_refs,
        representation_refs=rep_refs,
        source_revision=src_rev,
        target_path=t_path,
        proposed_frontmatter=fm,
        proposed_body=body_content,
        proposed_content=full_content,
        proposal_hash=p_hash,
        history=[initial_trans],
    )

    save_candidate(proposal, ws)
    return proposal


def approve_candidate(
    candidate_id: str,
    reviewer: str,
    reason: str,
    workspace_root: Path,
    validation_run_id: Optional[str] = None,
) -> CandidateProposal:
    """Approve a candidate proposal, binding decision to exact revision and hashes (REVIEW-002..REVIEW-004)."""
    if not ACTOR_REGEX.match(reviewer):
        raise ApprovalBindingError(
            f"Reviewer actor '{reviewer}' is invalid per ACTOR_PATTERN [REVIEW-004]"
        )

    proposal = load_candidate(candidate_id, workspace_root)

    if proposal.state not in {"pending", "in_review"}:
        raise StateTransitionError(
            f"Cannot approve candidate '{candidate_id}' in state '{proposal.state}'. Legal states: pending, in_review [REVIEW-001]"
        )

    decision = ReviewDecision(
        decision_id=f"RD-{uuid.uuid4().hex[:12].upper()}",
        candidate_id=proposal.candidate_id,
        proposal_revision=proposal.proposal_revision,
        decision="approve",
        reviewer=reviewer,
        decided_at=current_iso_timestamp(),
        proposal_hash=proposal.proposal_hash,
        source_revision=proposal.source_revision,
        validation_run_id=validation_run_id or f"VAL-{uuid.uuid4().hex[:12].upper()}",
        reason=reason,
    )

    trans = StateTransitionRecord(
        transition_id=f"TR-{uuid.uuid4().hex[:12].upper()}",
        candidate_id=proposal.candidate_id,
        proposal_revision=proposal.proposal_revision,
        previous_state=proposal.state,
        new_state="approved",
        actor=reviewer,
        transitioned_at=current_iso_timestamp(),
        reason=reason,
        validation_result="approved",
        source_refs=proposal.source_refs,
        representation_refs=proposal.representation_refs,
    )

    proposal.review_decision = decision
    proposal.state = "approved"
    proposal.history.append(trans)

    save_candidate(proposal, workspace_root)
    return proposal


def reject_candidate(
    candidate_id: str,
    reviewer: str,
    reason: str,
    workspace_root: Path,
) -> CandidateProposal:
    """Reject a candidate proposal (REVIEW-009)."""
    if not ACTOR_REGEX.match(reviewer):
        raise ApprovalBindingError(f"Reviewer actor '{reviewer}' is invalid per ACTOR_PATTERN")

    proposal = load_candidate(candidate_id, workspace_root)

    if proposal.state in {"promoted", "rejected", "expired", "superseded"}:
        raise StateTransitionError(
            f"Cannot reject candidate '{candidate_id}' already in terminal state '{proposal.state}'"
        )

    decision = ReviewDecision(
        decision_id=f"RD-{uuid.uuid4().hex[:12].upper()}",
        candidate_id=proposal.candidate_id,
        proposal_revision=proposal.proposal_revision,
        decision="reject",
        reviewer=reviewer,
        decided_at=current_iso_timestamp(),
        proposal_hash=proposal.proposal_hash,
        source_revision=proposal.source_revision,
        validation_run_id=f"VAL-{uuid.uuid4().hex[:12].upper()}",
        reason=reason,
    )

    trans = StateTransitionRecord(
        transition_id=f"TR-{uuid.uuid4().hex[:12].upper()}",
        candidate_id=proposal.candidate_id,
        proposal_revision=proposal.proposal_revision,
        previous_state=proposal.state,
        new_state="rejected",
        actor=reviewer,
        transitioned_at=current_iso_timestamp(),
        reason=reason,
        validation_result="rejected",
        source_refs=proposal.source_refs,
        representation_refs=proposal.representation_refs,
    )

    proposal.review_decision = decision
    proposal.state = "rejected"
    proposal.history.append(trans)

    save_candidate(proposal, workspace_root)
    return proposal


def promote_candidate(
    candidate_id: str,
    workspace_root: Path,
    idempotency_key: Optional[str] = None,
) -> PromotionResult:
    """Execute Durable Promotion Commit Protocol (DPCP, PROMO-001..PROMO-010, INGEST-STAGING.md §9).

    Protocol:
    1. Verify pre-conditions (status == approved, exact hash binding)
    2. Acquire POSIX advisory lock on canonical promotion mutex (§9.1)
    3. DPCP Step 1: PREPARED in SQLite journal
    4. DPCP Step 2: STAGED_WRITTEN to temporary directory outside canonical tree
    5. DPCP Step 3: LINTER_VALIDATED via Layer 1–5 validation
    6. DPCP Step 4: CANONICAL_COMMITTED via atomic POSIX rename (os.replace)
    7. DPCP Step 5: COMPLETED in SQLite journal, update candidate state
    """
    ws = workspace_root.resolve()
    proposal = load_candidate(candidate_id, ws)
    try:
        target_file = sandbox_path(ws / proposal.target_path, ws)
    except AccessDeniedError as exc:
        raise PromotionError(
            f"Path traversal detected in proposal target_path '{proposal.target_path}': {exc}"
        ) from exc
    operation_id = f"OP-{uuid.uuid4().hex[:12].upper()}"
    idem_key = idempotency_key or compute_content_sha256(
        f"{proposal.candidate_id}:{proposal.proposal_revision}:{proposal.proposal_hash}"
    )

    journal = get_journal(ws)
    locks_dir = ws / "staging" / "transactions" / "locks"
    lock_file = locks_dir / "canonical_promotion.lock"

    # 1. Idempotency check before pre-condition check (PROMO-005)
    existing_idem = journal.get_idempotency_entry(idem_key)
    if existing_idem:
        if existing_idem["content_hash"] == proposal.proposal_hash:
            return PromotionResult(
                candidate_id=proposal.candidate_id,
                proposal_revision=proposal.proposal_revision,
                operation_id=existing_idem["operation_id"],
                target_path=target_file,
                content_hash=proposal.proposal_hash,
                is_noop=True,
                audit_record=existing_idem["result"],
            )
        else:
            raise PromotionError(
                f"Integrity conflict: same idempotency key '{idem_key}' with divergent hash [PROMO-005]"
            )

    # 2. Pre-condition checks (fail-closed, PROMO-002, REVIEW-002, REVIEW-004)
    if proposal.state != "approved":
        raise ApprovalBindingError(
            f"Cannot promote candidate '{candidate_id}' with state '{proposal.state}'. Candidate MUST be approved first [PROMO-002]"
        )

    if proposal.review_decision is None or proposal.review_decision.decision != "approve":
        raise ApprovalBindingError(
            f"Candidate '{candidate_id}' lacks a valid approval decision record [REVIEW-002]"
        )

    # Approval binding verification (REVIEW-002)
    rd = proposal.review_decision
    if rd.candidate_id != proposal.candidate_id:
        raise ApprovalBindingError(
            "Candidate ID mismatch between approval and proposal [REVIEW-002]"
        )
    if rd.proposal_revision != proposal.proposal_revision:
        raise ApprovalBindingError(
            "Proposal revision mismatch between approval and proposal [REVIEW-002]"
        )
    if rd.proposal_hash != proposal.proposal_hash:
        raise ApprovalBindingError(
            "Proposal hash mismatch between approval and proposal [REVIEW-002]"
        )
    if rd.source_revision != proposal.source_revision:
        raise ApprovalBindingError(
            "Source revision mismatch between approval and proposal [REVIEW-002]"
        )

    # Bind approval to the actual content bytes (REVIEW-002, PROMO-002). A staged
    # payload whose recomputed hash no longer matches the approved hash is rejected.
    actual_content_hash = compute_content_sha256(proposal.proposed_content)
    if actual_content_hash != proposal.proposal_hash:
        raise ApprovalBindingError(
            f"Proposal hash mismatch: approved {proposal.proposal_hash} does not match "
            f"recomputed content hash {actual_content_hash} [REVIEW-002]"
        )

    # Verify scope admissibility (§9.5)
    scope = proposal.proposed_frontmatter.get("scope")
    if scope not in {"personal", "engineering"}:
        raise PromotionError(
            f"Inadmissible candidate scope '{scope}'. Must be personal or engineering [E104]"
        )

    # 3. Acquire lock & run DPCP
    with canonical_promotion_lock(lock_file, timeout_seconds=10.0):
        # Conflict check (PROMO-006)
        if target_file.exists():
            current_target_hash = compute_content_sha256(target_file.read_text(encoding="utf-8"))
            if current_target_hash != proposal.proposal_hash:
                raise ConflictError(
                    f"Target path '{proposal.target_path}' already exists with conflicting content [PROMO-006]"
                )

        # Step 1: PREPARED
        tmp_promo_dir = (
            ws
            / "staging"
            / "transactions"
            / f".tmp_promo_{proposal.candidate_id}_{proposal.proposal_revision}"
        )
        tmp_promo_dir.mkdir(parents=True, exist_ok=True)
        tmp_target_file = tmp_promo_dir / target_file.name

        journal.record_prepared(
            operation_id=operation_id,
            candidate_id=proposal.candidate_id,
            proposal_revision=proposal.proposal_revision,
            target_paths=[proposal.target_path],
            expected_hashes={proposal.target_path: proposal.proposal_hash},
            temporary_paths=[str(tmp_promo_dir)],
            idempotency_key=idem_key,
        )

        try:
            # Step 2: TEMPORARY_OUTPUT_WRITTEN
            with open(tmp_target_file, "w", encoding="utf-8") as f:
                f.write(proposal.proposed_content)
                f.flush()
                os.fsync(f.fileno())

            journal.transition_state(operation_id, "TEMPORARY_OUTPUT_WRITTEN")

            # Step 3: LINTER_VALIDATED (Layer 1–5 in-memory validation)
            ko = load_single_file(tmp_target_file)
            if ko.load_error:
                raise ValidationRollbackError(f"Frontmatter parsing error: {ko.load_error}")

            # Validate against intended canonical target location (TAX-002, E002)
            ko.path = target_file

            reg_dir = (
                ws / "schemas" / "registry" if (ws / "schemas" / "registry").exists() else None
            )
            registries = load_registries(reg_dir)
            linter = Linter(registries)
            findings = []
            findings.extend(linter._check_layer1_schema(ko))
            findings.extend(linter._check_layer2_structural(ko))
            findings.extend(linter._check_layer3_semantic(ko))
            findings.extend(linter._check_section_ownership(ko))

            # Layers 4 & 5 are cross-object (PROMO-003): validate the candidate
            # against the existing canonical corpus plus itself.
            corpus = load_corpus(ws)
            # Reflect exactly what will be committed: drop any already-materialized
            # copy of the target, then add the candidate.
            corpus.objects = [
                o for o in corpus.objects if o.path.resolve() != target_file.resolve()
            ]
            corpus.objects_by_path = {o.path: o for o in corpus.objects}
            corpus.objects_by_id = {}
            for o in corpus.objects:
                if o.id and o.id not in corpus.objects_by_id:
                    corpus.objects_by_id[o.id] = o
            corpus.objects.append(ko)
            corpus.objects_by_path[target_file] = ko
            if ko.id and ko.id not in corpus.objects_by_id:
                corpus.objects_by_id[ko.id] = ko
            findings.extend(linter._check_layer4_graph(corpus))
            findings.extend(linter._check_layer5_cross_object(corpus))

            errors = [f for f in findings if f.level == "ERROR"]
            if errors:
                raise ValidationRollbackError(
                    f"Linter validation rejected candidate: [{errors[0].code}] {errors[0].message}"
                )

            journal.transition_state(operation_id, "VALIDATED")

            # Step 4: CANONICAL_COMMITTED (Atomic rename)
            target_file.parent.mkdir(parents=True, exist_ok=True)
            os.replace(tmp_target_file, target_file)

            journal.transition_state(operation_id, "CANONICAL_COMMITTED")

            # Step 5: COMPLETED / AUDIT_COMMITTED
            trans = StateTransitionRecord(
                transition_id=f"TR-{uuid.uuid4().hex[:12].upper()}",
                candidate_id=proposal.candidate_id,
                proposal_revision=proposal.proposal_revision,
                previous_state="approved",
                new_state="promoted",
                actor=rd.reviewer,
                transitioned_at=current_iso_timestamp(),
                reason=f"Successfully promoted via DPCP {operation_id}",
                validation_result="passed",
                source_refs=proposal.source_refs,
                representation_refs=proposal.representation_refs,
            )
            proposal.state = "promoted"
            proposal.materialization_state = "promoted"
            proposal.history.append(trans)
            save_candidate(proposal, ws)

            audit_entry = {
                "operation_id": operation_id,
                "candidate_id": proposal.candidate_id,
                "proposal_revision": proposal.proposal_revision,
                "decision_id": rd.decision_id,
                "reviewer": rd.reviewer,
                "target_path": proposal.target_path,
                "content_hash": proposal.proposal_hash,
                "source_refs": proposal.source_refs,
                "promoted_at": current_iso_timestamp(),
            }

            journal.record_idempotency_success(
                idempotency_key=idem_key,
                operation_id=operation_id,
                candidate_id=proposal.candidate_id,
                proposal_revision=proposal.proposal_revision,
                content_hash=proposal.proposal_hash,
                result_dict=audit_entry,
            )

            journal.transition_state(operation_id, "COMPLETED")

            return PromotionResult(
                candidate_id=proposal.candidate_id,
                proposal_revision=proposal.proposal_revision,
                operation_id=operation_id,
                target_path=target_file,
                content_hash=proposal.proposal_hash,
                is_noop=False,
                audit_record=audit_entry,
            )

        except Exception as e:
            # Step 3 rollback & fail state (PROMO-007, §9.2)
            if not target_file.exists():
                journal.transition_state(operation_id, "FAILED", error_message=str(e))
                proposal.materialization_state = "failed"
                save_candidate(proposal, ws)
            raise e

        finally:
            # Clean temporary promotion folder
            if tmp_promo_dir.exists():
                import shutil

                shutil.rmtree(tmp_promo_dir, ignore_errors=True)
