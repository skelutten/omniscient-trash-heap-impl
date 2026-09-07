"""Candidate proposal review, approval binding, and DPCP deterministic promotion package (Plan 04)."""

from trashheap.promotion.engine import (
    PromotionResult,
    approve_candidate,
    create_candidate_proposal,
    get_journal,
    list_candidates,
    load_candidate,
    promote_candidate,
    reject_candidate,
    save_candidate,
)
from trashheap.promotion.exceptions import (
    ApprovalBindingError,
    ConflictError,
    LockTimeoutError,
    PromotionError,
    StateTransitionError,
    ValidationRollbackError,
)
from trashheap.promotion.journal import DPCPJournal, JournalRecord
from trashheap.promotion.lock import canonical_promotion_lock
from trashheap.promotion.models import (
    CandidateProposal,
    CandidateState,
    MaterializationState,
    MutationRecord,
    PromotionOperation,
    ReviewDecision,
    StateTransitionRecord,
)

__all__ = [
    "PromotionResult",
    "CandidateProposal",
    "CandidateState",
    "MaterializationState",
    "MutationRecord",
    "PromotionOperation",
    "ReviewDecision",
    "StateTransitionRecord",
    "DPCPJournal",
    "JournalRecord",
    "canonical_promotion_lock",
    "create_candidate_proposal",
    "approve_candidate",
    "reject_candidate",
    "promote_candidate",
    "load_candidate",
    "save_candidate",
    "list_candidates",
    "get_journal",
    "PromotionError",
    "ApprovalBindingError",
    "ConflictError",
    "LockTimeoutError",
    "StateTransitionError",
    "ValidationRollbackError",
]
