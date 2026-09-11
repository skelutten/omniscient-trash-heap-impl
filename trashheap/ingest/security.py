"""Security sandboxing, prompt injection defense, and resource limit enforcement (FR-12, FR-13, NFR-6, AC-5, AC-6)."""

import os
import re
from pathlib import Path
from typing import List, Union

from trashheap.ingest.exceptions import AccessDeniedError, QuarantineError

DEFAULT_MAX_SOURCE_BYTES = 25 * 1024 * 1024  # 25 MB

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+prompt\s*:", re.IGNORECASE),
    re.compile(r"<script[\s>]", re.IGNORECASE),
    re.compile(r"rm\s+-rf\s+[/~]", re.IGNORECASE),
    re.compile(r"exec\s*\(\s*['\"]", re.IGNORECASE),
    re.compile(r"os\.system\s*\(", re.IGNORECASE),
    re.compile(r"shutil\.rmtree\s*\(", re.IGNORECASE),
]


def sandbox_path(target_path: Union[str, Path], root: Path) -> Path:
    """Normalize path via os.path.realpath and enforce confinement within root (FR-13, AC-6).

    Raises AccessDeniedError if target_path resolves outside root.
    """
    root_resolved = Path(os.path.realpath(root))
    target_resolved = Path(os.path.realpath(target_path))

    try:
        # relative_to will raise ValueError if target_resolved is not relative to root_resolved
        target_resolved.relative_to(root_resolved)
    except ValueError:
        raise AccessDeniedError(
            f"Path traversal detected: '{target_path}' resolves to '{target_resolved}' outside root '{root_resolved}'",
            path=str(target_path),
        )

    return target_resolved


_FENCE_TAG_PATTERN = re.compile(r"<\s*/?\s*untrusted_source\s*/?\s*>", re.IGNORECASE)


def fence_untrusted_content(raw_text: str) -> str:
    """Wrap untrusted source content in immutable fences (FR-12, NFR-6, AC-5).

    Neutralizes every fence-tag lookalike in the payload — opening or closing,
    any case, optional interior whitespace — so untrusted content cannot forge
    or escape the fence boundary seen by downstream LLM consumers.
    """
    sanitized = _FENCE_TAG_PATTERN.sub(
        lambda m: m.group(0).replace("<", "&lt;").replace(">", "&gt;"), raw_text
    )
    return f"<untrusted_source>\n{sanitized}\n</untrusted_source>"


def check_resource_limits(
    content_bytes: bytes,
    max_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> None:
    """Ensure raw content size does not exceed resource limits."""
    size = len(content_bytes)
    if size > max_bytes:
        raise QuarantineError(
            f"Content size {size} bytes exceeds maximum limit of {max_bytes} bytes",
            reason="size_limit_exceeded",
        )


def detect_prompt_injection_indicators(text: str) -> List[str]:
    """Inspect untrusted text for known prompt injection payloads."""
    detected = []
    for pattern in INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            detected.append(match.group(0))
    return detected
