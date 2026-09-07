"""Canonical manifest and immutability protection for Graph Delta.

Complies with specs/GRAPH-INTELLIGENCE.md §1, §2.1, §2.1.1, §12 (Phase 1).
Implements DELTA-CORE-001..DELTA-CORE-007 (E201..E207).
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

from trashheap.graph.models import GraphManifest, current_iso_timestamp


def compute_file_sha256(path: Path) -> str:
    """Compute exact-byte SHA-256 hash of a file with sha256: prefix."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return f"sha256:{h.hexdigest()}"


def scan_canonical_inputs(
    workspace_root: Path, corpus_dir: Path | None = None
) -> List[Tuple[str, Path, str]]:
    """Scan canonical knowledge objects and normative registries, returning sorted entries.

    Returns:
        List of (relative_posix_path, absolute_path, file_sha256) sorted by relative path.
    """
    entries: List[Tuple[str, Path, str]] = []

    # 1. Canonical Markdown objects
    canon_dir = corpus_dir if corpus_dir is not None else (workspace_root / "fixtures" / "canonical")
    if canon_dir.exists():
        for p in sorted(canon_dir.glob("**/*.md")):
            if p.is_file():
                try:
                    rel = str(p.relative_to(workspace_root)).replace("\\", "/")
                except ValueError:
                    rel = str(p.relative_to(canon_dir)).replace("\\", "/")
                entries.append((rel, p, compute_file_sha256(p)))

    # 2. Normative registries
    reg_dir = workspace_root / "schemas" / "registry"
    if reg_dir.exists():
        for p in sorted(reg_dir.glob("*.yaml")):
            if p.is_file():
                try:
                    rel = str(p.relative_to(workspace_root)).replace("\\", "/")
                except ValueError:
                    rel = str(p.name)
                entries.append((rel, p, compute_file_sha256(p)))

    # Sort strictly by Unicode code point
    entries.sort(key=lambda x: x[0])
    return entries


def compute_aggregate_corpus_hash(entries: List[Tuple[str, Path, str]]) -> str:
    """Compute aggregate corpus_hash per GRAPH-INTELLIGENCE.md §2.1.1.

    SHA-256 over the UTF-8 bytes of sorted entries, where each entry is:
    relative_posix_path + "\\0" + file_hash + "\\n"
    """
    h = hashlib.sha256()
    for rel_path, _, file_hash in entries:
        line = f"{rel_path}\0{file_hash}\n"
        h.update(line.encode("utf-8"))
    return f"sha256:{h.hexdigest()}"


def build_and_publish_manifest(
    workspace_root: Path,
    output_dir: Path,
    records_count: Dict[str, int] | None = None,
    observability: Dict[str, Any] | None = None,
    corpus_dir: Path | None = None,
) -> Tuple[GraphManifest, Path]:
    """Scan canonical inputs, compute hashes, verify immutability, and publish manifest atomically.

    Raises:
        RuntimeError: If canonical input hashes mutated during generation (DELTA-CORE-001 / E201).
    """
    # 1. Pre-scan
    pre_scan = scan_canonical_inputs(workspace_root, corpus_dir=corpus_dir)
    corpus_hash = compute_aggregate_corpus_hash(pre_scan)

    if records_count is None:
        records_count = {"canonical_objects": len(pre_scan)}
    if observability is None:
        observability = {
            "inputs_scanned": len(pre_scan),
            "canonical_inputs": [rel for rel, _, _ in pre_scan],
        }

    manifest = GraphManifest(
        schema_version="1.0.0",
        architecture_version="3.8.10",
        pipeline_version="1.0.0",
        corpus_hash=corpus_hash,
        generated_at=current_iso_timestamp(),
        backend="jsonl",
        determinism="bitwise",
        records_count=records_count,
        observability=observability,
    )

    # 2. Immutability verification pass (E201)
    post_scan = scan_canonical_inputs(workspace_root, corpus_dir=corpus_dir)
    post_corpus_hash = compute_aggregate_corpus_hash(post_scan)

    if corpus_hash != post_corpus_hash:
        raise RuntimeError(
            f"DELTA-CORE-001 (E201): Canonical inputs mutated during graph processing! "
            f"Pre-hash {corpus_hash} != Post-hash {post_corpus_hash}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.jsonl"

    # 3. Atomic publication via temporary file
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=output_dir,
        delete=False,
        prefix="manifest_",
        suffix=".tmp",
    )
    try:
        # Header record
        temp_file.write(json.dumps({"manifest_header": manifest.to_dict()}) + "\n")
        # Item records
        for rel_path, _, file_hash in pre_scan:
            rec = {
                "record_type": "canonical_input",
                "path": rel_path,
                "file_hash": file_hash,
                "corpus_hash": corpus_hash,
            }
            temp_file.write(json.dumps(rec) + "\n")
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_file.close()

        # Atomic rename
        os.replace(temp_file.name, manifest_path)
    except Exception:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise

    return manifest, manifest_path
