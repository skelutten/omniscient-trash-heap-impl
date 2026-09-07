"""Exceptions for Candidate Review, Approval Binding, and DPCP Promotion (Plan 04)."""


class PromotionError(Exception):
    """Base exception for proposal review and promotion failures."""


class ApprovalBindingError(PromotionError):
    """Raised when an approval decision does not bind to the exact candidate revision or hash (REVIEW-002, REVIEW-004)."""


class StateTransitionError(PromotionError):
    """Raised when an invalid state transition is attempted on a candidate proposal (REVIEW-001)."""


class ConflictError(PromotionError):
    """Raised when the target canonical path has changed since expected_source_revision (PROMO-006)."""


class LockTimeoutError(PromotionError):
    """Raised when acquiring the canonical promotion mutex times out (§9.1)."""


class ValidationRollbackError(PromotionError):
    """Raised when in-memory/temporary Layer 1–5 validation fails during DPCP step 3 (§9)."""

