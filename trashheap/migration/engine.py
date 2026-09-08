"""Legacy corpus migration executor (plans/60-OLD-WIKI-MIGRATION.md).

Implements:
- Rule 1: Normative migration manifest with source hash, counts, source_mutated flag.
- Rule 2: Fresh-target-only executor with idempotent reruns and fail-closed behavior for unmanaged targets.
- Rule 3: Exact-byte SHA-256 over sorted repository-relative POSIX paths and bytes.
- Rule 4: Read-only proposal emission (link_proposals.json, facet_proposals.json).
- Rule 7: Source preservation verification (source_mutated: false).
- Rule 8: Anti-contamination audit log (legacy_tag_audit.json).
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from trashheap.migration.models import (
    FacetProposal,
    LinkProposal,
    MigrationManifest,
    MigrationMap,
    QuarantineRecord,
)
from trashheap.migration.parser import LegacyParser
from trashheap.models import KnowledgeObject
from trashheap.registry.loader import LoadedRegistries, load_registries
from trashheap.slug import taxonomy_id_to_directory


class MigrationError(Exception):
    """Base exception for migration errors."""

    pass


class UnmanagedTargetError(MigrationError):
    """Raised when target directory exists and contains unmanaged non-migration files (Rule 2)."""

    pass


class ChangedSourceError(MigrationError):
    """Raised when source corpus hash changed without a fresh target directory (Rule 2)."""

    pass


def compute_corpus_hash(source_dir: Path) -> Tuple[str, List[Tuple[str, bytes]]]:
    """Compute exact-byte SHA-256 hash over sorted relative POSIX paths and bytes (Rule 3)."""
    source_dir = Path(source_dir)
    file_records: List[Tuple[str, bytes]] = []

    for p in sorted(source_dir.glob("**/*")):
        if p.is_file():
            rel = p.relative_to(source_dir).as_posix()
            content = p.read_bytes()
            file_records.append((rel, content))

    hasher = hashlib.sha256()
    for rel_path, content in file_records:
        hasher.update(rel_path.encode("utf-8"))
        hasher.update(content)

    return f"sha256:{hasher.hexdigest()}", file_records


class MigrationEngine:
    """Deterministic, idempotent migration engine for legacy knowledge corpora."""

    def __init__(
        self,
        migration_map: MigrationMap,
        registries: Optional[LoadedRegistries] = None,
    ):
        self.migration_map = migration_map
        self.registries = registries or load_registries()
        self.parser = LegacyParser(self.registries)

    def plan(self, source_dir: Path, target_dir: Path) -> MigrationManifest:
        """Run dry-run migration analysis without writing canonical target objects."""
        return self._run(source_dir=source_dir, target_dir=target_dir, dry_run=True)

    def execute(self, source_dir: Path, target_dir: Path, force: bool = False) -> MigrationManifest:
        """Execute migration to target directory with idempotency and target safety (Rule 2)."""
        return self._run(source_dir=source_dir, target_dir=target_dir, dry_run=False, force=force)

    def _run(
        self,
        source_dir: Path,
        target_dir: Path,
        dry_run: bool,
        force: bool = False,
    ) -> MigrationManifest:
        source_dir = Path(source_dir)
        target_dir = Path(target_dir)

        if not source_dir.is_dir():
            raise FileNotFoundError(f"Source corpus directory not found: {source_dir}")

        # Compute source corpus hash (Rule 3)
        source_hash, file_records = compute_corpus_hash(source_dir)

        # Fresh-target and idempotency checks (Rule 2)
        manifest_file = target_dir / "migration_manifest.json"
        if not dry_run and target_dir.exists():
            existing_files = list(target_dir.iterdir())
            if existing_files:
                if not manifest_file.exists():
                    raise UnmanagedTargetError(
                        f"Target directory '{target_dir}' contains unmanaged files. Migration requires a fresh target (Rule 2)."
                    )

                # Target has existing migration manifest
                with open(manifest_file, "r", encoding="utf-8") as f:
                    prior_manifest = json.load(f)

                prior_source_hash = prior_manifest.get("source_corpus_hash")
                if prior_source_hash == source_hash and not force:
                    # Idempotent no-op!
                    return MigrationManifest.model_validate(prior_manifest)

                if prior_source_hash != source_hash and not force:
                    raise ChangedSourceError(
                        f"Source corpus changed ({prior_source_hash} -> {source_hash}). Rerun requires clean target or force flag (Rule 2)."
                    )

        # Process source files
        eligible_objects: List[Tuple[KnowledgeObject, str]] = []  # (ko, rel_src)
        all_link_proposals: List[LinkProposal] = []
        all_facet_proposals: List[FacetProposal] = []
        legacy_tag_audit: Dict[str, List[str]] = {}
        quarantined: List[QuarantineRecord] = []
        excluded_count = 0

        for rel_posix, content in file_records:
            # Check if file is markdown
            if not rel_posix.endswith(".md"):
                excluded_count += 1
                continue

            # Check if navigation / index file
            if Path(rel_posix).name in ("index.md", "README.md", "SUMMARY.md"):
                excluded_count += 1
                continue

            res = self.parser.parse_file(
                rel_path=rel_posix,
                content_bytes=content,
                migration_map=self.migration_map,
            )

            if isinstance(res, QuarantineRecord):
                quarantined.append(res)
            else:
                ko, link_props, facet_props, tags = res
                eligible_objects.append((ko, rel_posix))
                all_link_proposals.extend(link_props)
                all_facet_proposals.extend(facet_props)
                if tags:
                    legacy_tag_audit[rel_posix] = tags

        # Re-verify source directory has not been mutated (Rule 1, Rule 7)
        post_source_hash, _ = compute_corpus_hash(source_dir)
        source_mutated = post_source_hash != source_hash

        counts = {
            "total_source_files": len(file_records),
            "eligible_files": len(eligible_objects),
            "emitted_files": len(eligible_objects) if not dry_run else 0,
            "excluded_files": excluded_count,
            "quarantined_files": len(quarantined),
            "ambiguity_count": len(quarantined),
        }

        manifest = MigrationManifest(
            schema_version="1.0.0",
            source_corpus_hash=source_hash,
            target_corpus_hash=None,
            source_location=str(source_dir),
            target_location=str(target_dir),
            source_mutated=source_mutated,
            mode="dry-run" if dry_run else "execute",
            frontmatter_mode=self.migration_map.frontmatter_mode.value,
            counts=counts,
            quarantined=quarantined,
        )

        if dry_run:
            return manifest

        # Materialize files to target directory atomically
        tax_by_id = {node.taxonomy_id: node.model_dump() for node in self.registries.taxonomy}
        target_dir.mkdir(parents=True, exist_ok=True)

        target_hasher = hashlib.sha256()

        for ko, _ in eligible_objects:
            scope = ko.scope or "engineering"
            tax_id = getattr(ko.frontmatter, "taxonomy_id", None) or "TX-ENG-01"

            tax_dir_rel = taxonomy_id_to_directory(tax_by_id, scope, tax_id)
            dest_dir = target_dir / tax_dir_rel
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / f"{ko.id}.md"

            # Serialize canonical markdown note
            fm_yaml = yaml.dump(
                ko.frontmatter_dict,
                sort_keys=False,
                allow_unicode=True,
            )
            serialized = f"---\n{fm_yaml}---\n\n{ko.raw_body}\n"
            dest_file.write_text(serialized, encoding="utf-8")

            rel_dest = dest_file.relative_to(target_dir).as_posix()
            target_hasher.update(rel_dest.encode("utf-8"))
            target_hasher.update(serialized.encode("utf-8"))

        manifest.target_corpus_hash = f"sha256:{target_hasher.hexdigest()}"

        # Write migration artifacts
        with open(target_dir / "migration_manifest.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(manifest.model_dump(), indent=2, sort_keys=True))

        with open(target_dir / "link_proposals.json", "w", encoding="utf-8") as f:
            f.write(
                json.dumps([p.model_dump() for p in all_link_proposals], indent=2, sort_keys=True)
            )

        with open(target_dir / "facet_proposals.json", "w", encoding="utf-8") as f:
            f.write(
                json.dumps([p.model_dump() for p in all_facet_proposals], indent=2, sort_keys=True)
            )

        with open(target_dir / "legacy_tag_audit.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(legacy_tag_audit, indent=2, sort_keys=True))

        return manifest
