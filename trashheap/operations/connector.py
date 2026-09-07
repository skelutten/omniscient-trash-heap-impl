"""Connector and Adapter abstractions (specs/INGEST-ADAPTERS.md §3.1)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generator, Optional

from trashheap.ingest.models import compute_sha256
from trashheap.ingest.pipeline import IngestionResult, intake_source
from trashheap.operations.cursor import CursorStore


@dataclass
class RawPayload:
    """Raw payload captured by a connector."""

    source_path: str
    content_bytes: bytes
    content_hash: str
    media_type: str = "text/plain"
    metadata: Optional[Dict[str, Any]] = None


class BaseConnector(ABC):
    """Abstract Connector acquiring representations from external or local resources."""

    @abstractmethod
    def acquire(self) -> Generator[RawPayload, None, None]:
        """Yield raw payloads from target resource."""
        pass


class FileConnector(BaseConnector):
    """Connector for local files using inode-safe cursors."""

    def __init__(self, file_path: Path, cursor_store: Optional[CursorStore] = None):
        self.file_path = file_path
        self.cursor_store = cursor_store

    def acquire(self) -> Generator[RawPayload, None, None]:
        if not self.file_path.exists():
            return

        if self.cursor_store:
            content, cursor = self.cursor_store.check_and_read_new_bytes(self.file_path)
            if not content:
                return
            h = compute_sha256(content)
            yield RawPayload(
                source_path=str(self.file_path),
                content_bytes=content,
                content_hash=h,
                metadata={"byte_offset": cursor.byte_offset, "inode": cursor.inode},
            )
        else:
            data = self.file_path.read_bytes()
            yield RawPayload(
                source_path=str(self.file_path),
                content_bytes=data,
                content_hash=compute_sha256(data),
            )


class DirectoryConnector(BaseConnector):
    """Connector for scanning directories with glob patterns."""

    def __init__(
        self,
        directory_path: Path,
        pattern: str = "*.md",
        cursor_store: Optional[CursorStore] = None,
    ):
        self.directory_path = directory_path
        self.pattern = pattern
        self.cursor_store = cursor_store

    def acquire(self) -> Generator[RawPayload, None, None]:
        if not self.directory_path.exists() or not self.directory_path.is_dir():
            return

        for p in sorted(self.directory_path.glob(self.pattern)):
            if p.is_file() and not p.name.startswith("."):
                conn = FileConnector(p, self.cursor_store)
                yield from conn.acquire()


class BaseAdapter(ABC):
    """Abstract Adapter normalizing connector outputs into governed IngestionResults."""

    @abstractmethod
    def normalize_and_ingest(
        self,
        payload: RawPayload,
        workspace_root: Path,
    ) -> IngestionResult:
        """Normalize raw payload and stage through intake_source."""
        pass


class DocumentAdapter(BaseAdapter):
    """Standard adapter for document artifacts."""

    def normalize_and_ingest(
        self,
        payload: RawPayload,
        workspace_root: Path,
    ) -> IngestionResult:
        return intake_source(
            source_input=payload.content_bytes,
            source_type="document",
            workspace_root=workspace_root,
            identity={"resource": payload.source_path, "representation_hash": payload.content_hash},
            provenance={"resource": payload.source_path, "representation_hash": payload.content_hash},
        )


class TrajectoryAdapter(BaseAdapter):
    """Adapter for agent trajectory event sources (specs/INGEST-ADAPTERS.md §3.1)."""

    def __init__(self, agent_runtime: str = "generic"):
        self.agent_runtime = agent_runtime

    def normalize_and_ingest(
        self,
        payload: RawPayload,
        workspace_root: Path,
    ) -> IngestionResult:
        return intake_source(
            source_input=payload.content_bytes,
            source_type="agent_trajectory",
            workspace_root=workspace_root,
            identity={
                "source_system": self.agent_runtime,
                "external_id": Path(payload.source_path).name,
                "representation_hash": payload.content_hash,
            },
            provenance={
                "source_system": self.agent_runtime,
                "external_id": Path(payload.source_path).name,
                "representation_hash": payload.content_hash,
                "occurred_at": "2026-09-07T10:00:00Z",
            },
        )
