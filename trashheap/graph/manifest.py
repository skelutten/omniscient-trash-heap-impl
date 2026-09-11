"""Canonical manifest and immutability protection for Graph Delta.

Complies with specs/GRAPH-INTELLIGENCE.md §1, §2.1, §2.1.1, §12 (Phase 1).
Implements DELTA-CORE-001..DELTA-CORE-007 (E201..E207).
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from trashheap.constants import VERSION
from trashheap.fsutil import atomic_write_text
from trashheap.graph.models import GraphManifest
from trashheap.timeutil import current_iso_timestamp


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
    canon_dir = (
        corpus_dir if corpus_dir is not None else (workspace_root / "fixtures" / "canonical")
    )
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
    verify_immutability: bool = True,
) -> Tuple[GraphManifest, Path]:
    """Scan canonical inputs, publish the manifest atomically, and verify immutability.

    The E201 check brackets the real publication work: a pre-scan hashes all
    canonical inputs, the manifest is built and written, then a post-scan
    re-hashes and compares. If the inputs mutated in between, the freshly
    published (now invalid) manifest is removed and RuntimeError is raised.
    When ``verify_immutability`` is False, a single scan is performed and no
    post-scan comparison happens.

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
        architecture_version=VERSION,
        pipeline_version="1.0.0",
        corpus_hash=corpus_hash,
        generated_at=current_iso_timestamp(),
        backend="jsonl",
        determinism="bitwise",
        records_count=records_count,
        observability=observability,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.jsonl"

    # 2. Build JSONL payload (header record + item records) and publish atomically
    lines = [json.dumps({"manifest_header": manifest.to_dict()})]
    for rel_path, _, file_hash in pre_scan:
        rec = {
            "record_type": "canonical_input",
            "path": rel_path,
            "file_hash": file_hash,
            "corpus_hash": corpus_hash,
        }
        lines.append(json.dumps(rec))
    atomic_write_text(manifest_path, "\n".join(lines) + "\n")

    # 3. Immutability verification pass bracketing the publication work (E201)
    if verify_immutability:
        post_scan = scan_canonical_inputs(workspace_root, corpus_dir=corpus_dir)
        post_corpus_hash = compute_aggregate_corpus_hash(post_scan)

        if corpus_hash != post_corpus_hash:
            manifest_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"DELTA-CORE-001 (E201): Canonical inputs mutated during graph processing! "
                f"Pre-hash {corpus_hash} != Post-hash {post_corpus_hash}"
            )

    return manifest, manifest_path
