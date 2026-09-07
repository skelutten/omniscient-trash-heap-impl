"""Exceptions for Source Ingestion and Security Sandboxing."""


class AccessDeniedError(PermissionError):
    """Raised when an I/O operation attempts path traversal or escapes repository root (FR-13, AC-6)."""

    def __init__(self, message: str, path: str = ""):
        super().__init__(f"[ACCESS_DENIED] {message}")
        self.path = path


class IntegrityConflictError(ValueError):
    """Raised when an existing representation ID is presented with divergent content hash (E141, RAW-010)."""

    def __init__(self, representation_id: str, existing_hash: str, new_hash: str):
        msg = f"[E141] Integrity conflict for representation '{representation_id}': existing hash {existing_hash} != new hash {new_hash}"
        super().__init__(msg)
        self.representation_id = representation_id
        self.existing_hash = existing_hash
        self.new_hash = new_hash


class QuarantineError(Exception):
    """Raised when untrusted input contains severe anomalies or exceeds resource limits."""

    def __init__(self, message: str, reason: str = ""):
        super().__init__(f"[QUARANTINE] {message}")
        self.reason = reason


class SourceValidationError(ValueError):
    """Raised when a source fails envelope or registry profile requirements."""

    def __init__(self, message: str, field: str = ""):
        super().__init__(f"[SOURCE_VALIDATION] {message}")
        self.field = field
