"""Tests for Candidate Proposals, Review Decisions, DPCP Promotion, and Crash Recovery (Plan 04)."""

import tempfile
from pathlib import Path

import pytest

from trashheap.cli import main as cli_main
from trashheap.constants import ExitCode
from trashheap.promotion import (
    ApprovalBindingError,
    ConflictError,
    StateTransitionError,
    ValidationRollbackError,
    approve_candidate,
    create_candidate_proposal,
    get_journal,
    list_candidates,
    load_candidate,
    promote_candidate,
    reject_candidate,
)


@pytest.fixture
def temp_workspace():
    """Create temporary workspace root with staging and canonical trees."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir).resolve()
        (ws / "staging" / "proposals").mkdir(parents=True)
        (ws / "staging" / "transactions" / "locks").mkdir(parents=True)
        (ws / "engineering" / "01_domain_system_architecture").mkdir(parents=True)
        (
            ws
            / "personal"
            / "07_computer_science_ai_it_security"
            / "07_04_ai_assisted_software_engineering"
        ).mkdir(parents=True)
        yield ws


def test_candidate_creation_and_lifecycle_transitions(temp_workspace):
    """REVIEW-001: Creation, transition auditing, and illegal transition rejection."""
    proposal = create_candidate_proposal(
        candidate_id="CAND-TEST-001",
        title="Test Proposal Architecture",
        scope="engineering",
        object_type="Concept",
        workspace_root=temp_workspace,
    )

    assert proposal.candidate_id == "CAND-TEST-001"
    assert proposal.state == "pending"
    assert proposal.materialization_state == "not_promoted"
    assert len(proposal.history) == 1
    assert proposal.history[0].new_state == "pending"

    # List candidates
    candidates = list_candidates(temp_workspace)
    assert len(candidates) == 1
    assert candidates[0].candidate_id == "CAND-TEST-001"

    # Reject proposal
    rejected = reject_candidate(
        candidate_id="CAND-TEST-001",
        reviewer="human:auditor",
        reason="Rejected during review",
        workspace_root=temp_workspace,
    )
    assert rejected.state == "rejected"
    assert len(rejected.history) == 2

    # Attempting to approve an already rejected candidate fails
    with pytest.raises(StateTransitionError):
        approve_candidate(
            candidate_id="CAND-TEST-001",
            reviewer="human:auditor",
            reason="Illegal attempt to approve rejected candidate",
            workspace_root=temp_workspace,
        )


def test_approval_binding_and_validation(temp_workspace):
    """REVIEW-002..REVIEW-004: Approval binding, reviewer contract, and unauthorized promotion rejection."""
    create_candidate_proposal(
        candidate_id="CAND-TEST-002",
        scope="engineering",
        workspace_root=temp_workspace,
    )

    # 1. Reject invalid reviewer actor (REVIEW-004)
    with pytest.raises(ApprovalBindingError) as exc_actor:
        approve_candidate(
            candidate_id="CAND-TEST-002",
            reviewer="bad_actor_without_namespace",
            reason="Invalid reviewer",
            workspace_root=temp_workspace,
        )
    assert "[REVIEW-004]" in str(exc_actor.value)

    # 2. Cannot promote unapproved candidate (PROMO-002)
    with pytest.raises(ApprovalBindingError) as exc_unapproved:
        promote_candidate("CAND-TEST-002", temp_workspace)
    assert "[PROMO-002]" in str(exc_unapproved.value)

    # 3. Valid approval
    approved = approve_candidate(
        candidate_id="CAND-TEST-002",
        reviewer="human:reviewer1",
        reason="Looks solid",
        workspace_root=temp_workspace,
    )
    assert approved.state == "approved"
    assert approved.review_decision is not None
    assert approved.review_decision.reviewer == "human:reviewer1"

    # 4. Tampering: alter proposal_hash to simulate divergence after approval (REVIEW-002)
    approved.proposal_hash = "sha256:" + "f" * 64
    from trashheap.promotion.engine import save_candidate

    save_candidate(approved, temp_workspace)

    with pytest.raises(ApprovalBindingError) as exc_tamper:
        promote_candidate("CAND-TEST-002", temp_workspace)
    assert "Proposal hash mismatch" in str(exc_tamper.value)


def test_dpcp_promotion_success_and_idempotency(temp_workspace):
    """PROMO-001..PROMO-005, INGEST-STAGING.md §9: 5-step DPCP promotion and idempotency."""
    create_candidate_proposal(
        candidate_id="CAND-TEST-003",
        title="Promoted Architecture Document",
        scope="engineering",
        object_type="Concept",
        workspace_root=temp_workspace,
    )

    approve_candidate(
        candidate_id="CAND-TEST-003",
        reviewer="human:lead_engineer",
        reason="Design verified",
        workspace_root=temp_workspace,
    )

    # First promotion: success
    res = promote_candidate("CAND-TEST-003", temp_workspace)
    assert not res.is_noop
    assert res.target_path.exists()
    assert res.target_path.is_file()

    # Verify candidate state updated
    loaded = load_candidate("CAND-TEST-003", temp_workspace)
    assert loaded.state == "promoted"
    assert loaded.materialization_state == "promoted"

    # Second promotion: verified no-op (PROMO-005)
    res_noop = promote_candidate("CAND-TEST-003", temp_workspace)
    assert res_noop.is_noop
    assert res_noop.content_hash == res.content_hash


def test_dpcp_validation_rollback_on_invalid_ontology(temp_workspace):
    """PROMO-004, §9: Invalid frontmatter causes DPCP Step 3 rollback with zero canonical mutation."""
    # Create a proposal with an invalid/unregistered domain
    proposal = create_candidate_proposal(
        candidate_id="CAND-INVALID-001",
        scope="engineering",
        object_type="Concept",
        frontmatter_overrides={"domain": "unregistered_bogus_domain_name"},
        workspace_root=temp_workspace,
    )

    approve_candidate(
        candidate_id="CAND-INVALID-001",
        reviewer="human:approver",
        reason="Approved by mistake",
        workspace_root=temp_workspace,
    )

    target_canonical_file = temp_workspace / proposal.target_path
    assert not target_canonical_file.exists()

    # Promotion should fail during Linter validation (Step 3) and rollback
    with pytest.raises(ValidationRollbackError) as exc_rollback:
        promote_candidate("CAND-INVALID-001", temp_workspace)
    assert "Linter validation rejected candidate" in str(exc_rollback.value)

    # Invariant PROMO-004: Target canonical file MUST NOT exist!
    assert not target_canonical_file.exists()

    # Candidate materialization marked failed
    loaded = load_candidate("CAND-INVALID-001", temp_workspace)
    assert loaded.materialization_state == "failed"


def test_dpcp_conflict_detection_on_existing_target(temp_workspace):
    """PROMO-006: Target file existing with differing content triggers conflict error."""
    proposal = create_candidate_proposal(
        candidate_id="CAND-CONFLICT-001",
        scope="engineering",
        workspace_root=temp_workspace,
    )

    approve_candidate(
        candidate_id="CAND-CONFLICT-001",
        reviewer="human:approver",
        reason="Approved",
        workspace_root=temp_workspace,
    )

    # Pre-create conflicting target file
    target_path = temp_workspace / proposal.target_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text("Conflicting preexisting content", encoding="utf-8")

    with pytest.raises(ConflictError) as exc_conflict:
        promote_candidate("CAND-CONFLICT-001", temp_workspace)
    assert "already exists with conflicting content" in str(exc_conflict.value)


def test_dpcp_crash_recovery_and_orphan_sweep(temp_workspace):
    """PROMO-008, §9.2: Crash recovery for interrupted transactions."""
    journal = get_journal(temp_workspace)

    # 1. Simulate pre-commit crash (state: TEMPORARY_OUTPUT_WRITTEN)
    fake_tmp_dir = temp_workspace / "staging" / "transactions" / ".tmp_promo_CAND-CRASH-001_1"
    fake_tmp_dir.mkdir(parents=True, exist_ok=True)
    fake_tmp_file = fake_tmp_dir / "draft.md"
    fake_tmp_file.write_text("incomplete output", encoding="utf-8")

    journal.record_prepared(
        operation_id="OP-CRASH-001",
        candidate_id="CAND-CRASH-001",
        proposal_revision=1,
        target_paths=["engineering/fake.md"],
        expected_hashes={"engineering/fake.md": "sha256:" + "0" * 64},
        temporary_paths=[str(fake_tmp_dir)],
        idempotency_key="sha256:" + "1" * 64,
    )
    journal.transition_state("OP-CRASH-001", "TEMPORARY_OUTPUT_WRITTEN")

    # Run recovery
    log = journal.recover_crash(temp_workspace)
    assert len(log) >= 1
    assert any(entry.get("action") == "rolled_back" for entry in log)

    # Ensure temporary directory was deleted
    assert not fake_tmp_dir.exists()

    # Journal state transitioned to FAILED
    entry = journal.get_journal_entry("OP-CRASH-001")
    assert entry.current_state == "FAILED"


def test_cli_review_and_promote(temp_workspace):
    """CLI review commands: list, show, approve, reject, promote, recover."""
    proposal = create_candidate_proposal(
        candidate_id="CAND-CLI-001",
        scope="engineering",
        workspace_root=temp_workspace,
    )

    # 1. review list
    code_list = cli_main(["review", "list", "--workspace-root", str(temp_workspace), "--json"])
    assert code_list == ExitCode.SUCCESS

    # 2. review show
    code_show = cli_main(
        ["review", "show", "CAND-CLI-001", "--workspace-root", str(temp_workspace), "--json"]
    )
    assert code_show == ExitCode.SUCCESS

    # 3. review approve
    code_approve = cli_main(
        [
            "review",
            "approve",
            "CAND-CLI-001",
            "--reviewer",
            "human:cli_admin",
            "--reason",
            "CLI verification approval",
            "--workspace-root",
            str(temp_workspace),
            "--json",
        ]
    )
    assert code_approve == ExitCode.SUCCESS

    # 4. review promote (or promote)
    code_promote = cli_main(
        [
            "promote",
            "CAND-CLI-001",
            "--workspace-root",
            str(temp_workspace),
            "--json",
        ]
    )
    assert code_promote == ExitCode.SUCCESS

    # Verify target file exists
    target_path = temp_workspace / proposal.target_path
    assert target_path.exists()

    # 5. review recover
    code_recover = cli_main(
        ["review", "recover", "--workspace-root", str(temp_workspace), "--json"]
    )
    assert code_recover == ExitCode.SUCCESS


def test_k3_promotion_path_traversal_rejection(temp_workspace):
    """K3: Path sandboxing rejects traversal ('..') and absolute paths in promotion."""
    from pydantic import ValidationError

    from trashheap.promotion.models import CandidateProposal

    with pytest.raises(ValidationError):
        CandidateProposal(
            candidate_id="CAND-ATTACK-001",
            source_revision="sha256:" + "a" * 64,
            target_path="../outside.md",
            proposed_frontmatter={"id": "ENG-TRV-0001", "object_type": "Concept"},
            proposed_body="Content",
            proposed_content="---\nid: ENG-TRV-0001\n---\nContent",
            proposal_hash="sha256:" + "b" * 64,
        )

    with pytest.raises(ValidationError):
        CandidateProposal(
            candidate_id="CAND-ATTACK-002",
            source_revision="sha256:" + "a" * 64,
            target_path="/etc/evil.md",
            proposed_frontmatter={"id": "ENG-TRV-0002", "object_type": "Concept"},
            proposed_body="Content",
            proposed_content="---\nid: ENG-TRV-0002\n---\nContent",
            proposal_hash="sha256:" + "b" * 64,
        )
