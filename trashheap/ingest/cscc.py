"""Crash-safe Source Capture Commit (CSCC) sequence (INGEST-STAGING.md §7.1.2, RAW-001..RAW-010)."""

import json
import os
from pathlib import Path
from typing import Any, Dict

import yaml

from trashheap.ingest.exceptions import IntegrityConflictError
from trashheap.ingest.models import UniversalSourceEnvelope


class CaptureResult:
    """Result of a CSCC capture operation."""

    def __init__(
        self,
        source_id: str,
        representation_id: str,
        representation_dir: Path,
        content_path: Path,
        content_hash: str,
        is_noop: bool = False,
    ):
        self.source_id = source_id
        self.representation_id = representation_id
        self.representation_dir = representation_dir
        self.content_path = content_path
        self.content_hash = content_hash
        self.is_noop = is_noop

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "representation_id": self.representation_id,
            "representation_dir": str(self.representation_dir),
            "content_path": str(self.content_path),
            "content_hash": self.content_hash,
            "is_noop": self.is_noop,
        }


def commit_raw_capture(
    workspace_root: Path,
    envelope: UniversalSourceEnvelope,
    raw_bytes: bytes,
    extension: str = ".txt",
) -> CaptureResult:
    """Execute Crash-safe Source Capture Commit (CSCC §7.1.2).

    Guarantees:
    - RAW-001: Captured Source representations MUST NOT be modified in place.
    - RAW-002: Addressable by source_id and representation_id and retains content hash.
    - RAW-004: Raw capture is lossless.
    - RAW-010: Same identity + same hash is verified no-op; divergent hash fails closed (E141).
    """
    raw_root = workspace_root / "raw"
    sources_root = raw_root / "sources"
    manifests_root = raw_root / "manifests"

    source_dir = sources_root / envelope.source_id
    rep_dir = source_dir / "representations" / envelope.representation.representation_id
    content_file = rep_dir / f"content{extension}"

    # 1. Idempotency and Conflict Check (RAW-010, E141)
    if rep_dir.exists():
        meta_file = rep_dir / "metadata.yaml"
        existing_hash = ""
        if meta_file.exists():
            with open(meta_file, "r", encoding="utf-8") as f:
                existing_meta = yaml.safe_load(f)
                existing_hash = existing_meta.get("representation_hash", "")

        new_hash = envelope.representation.representation_hash
        if existing_hash and existing_hash == new_hash:
            # Verified no-op
            return CaptureResult(
                source_id=envelope.source_id,
                representation_id=envelope.representation.representation_id,
                representation_dir=rep_dir,
                content_path=content_file,
                content_hash=new_hash,
                is_noop=True,
            )
        else:
            # Divergent hash on same representation ID: fail closed (E141)
            raise IntegrityConflictError(
                representation_id=envelope.representation.representation_id,
                existing_hash=existing_hash,
                new_hash=new_hash,
            )

    # 2. Prepare atomic staging area under sibling tmp directory
    source_dir.mkdir(parents=True, exist_ok=True)
    tmp_rep_dir = source_dir / f".tmp_rep_{envelope.representation.representation_id}"
    tmp_rep_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Step 2 & 3: Write content bytes to temporary path and fsync
        tmp_content_file = tmp_rep_dir / f"content{extension}"
        with open(tmp_content_file, "wb") as f:
            f.write(raw_bytes)
            f.flush()
            os.fsync(f.fileno())

        # Step 4 & 5: Write metadata.yaml and source.yaml to temporary paths and fsync
        tmp_meta_file = tmp_rep_dir / "metadata.yaml"
        meta_data = envelope.representation.model_dump()
        meta_data["byte_size"] = len(raw_bytes)
        with open(tmp_meta_file, "w", encoding="utf-8") as f:
            yaml.dump(meta_data, f, sort_keys=False, allow_unicode=True)
            f.flush()
            os.fsync(f.fileno())

        source_yaml_path = source_dir / "source.yaml"
        if not source_yaml_path.exists():
            source_data = envelope.model_dump(exclude={"representation"})
            tmp_source_file = source_dir / ".source.yaml.tmp"
            with open(tmp_source_file, "w", encoding="utf-8") as f:
                yaml.dump(source_data, f, sort_keys=False, allow_unicode=True)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_source_file, source_yaml_path)

        # Step 6: Atomically rename temporary representation directory into raw/
        rep_parent = source_dir / "representations"
        rep_parent.mkdir(parents=True, exist_ok=True)
        os.replace(tmp_rep_dir, rep_dir)

        # Step 7: Atomically update capture manifest index entry
        manifests_root.mkdir(parents=True, exist_ok=True)
        manifest_file = manifests_root / "capture_manifest.json"
        manifest_data: Dict[str, Any] = {"schema_version": "1.0.0", "representations": {}}
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)
            except Exception:
                pass

        rep_key = f"{envelope.source_id}/{envelope.representation.representation_id}"
        manifest_data["representations"][rep_key] = {
            "source_id": envelope.source_id,
            "representation_id": envelope.representation.representation_id,
            "representation_hash": envelope.representation.representation_hash,
            "media_type": envelope.representation.media_type,
            "byte_size": len(raw_bytes),
            "captured_at": envelope.representation.captured_at,
        }

        tmp_manifest = manifests_root / ".capture_manifest.json.tmp"
        with open(tmp_manifest, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_manifest, manifest_file)

        return CaptureResult(
            source_id=envelope.source_id,
            representation_id=envelope.representation.representation_id,
            representation_dir=rep_dir,
            content_path=content_file,
            content_hash=envelope.representation.representation_hash,
            is_noop=False,
        )

    finally:
        # Cleanup temporary directory if still exists
        if tmp_rep_dir.exists():
            try:
                import shutil
                shutil.rmtree(tmp_rep_dir)
            except Exception:
                pass
