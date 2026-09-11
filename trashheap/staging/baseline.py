"""Baseline filesystem and SQLite staging backend (plans/93-OPT-IN-PARQUET-STAGING.md)."""

import hashlib
import json
import os
from typing import Any, Dict, List, Optional

import yaml

from trashheap.promotion.engine import get_journal, get_proposals_dir
from trashheap.promotion.models import CandidateProposal
from trashheap.staging.backend import StagingBackend
from trashheap.staging.models import (
    BackendAvailability,
    BackendType,
    CommitResult,
    DSCPIntegrityError,
    ParquetProposalRecord,
    StagingBackendStatus,
    StagingManifest,
    StagingTableInfo,
)
from trashheap.timeutil import current_iso_timestamp


class BaselineStagingBackend(StagingBackend):
    """Baseline Staging Backend using YAML proposals and SQLite transactions."""

    @property
    def backend_type(self) -> BackendType:
        return BackendType.BASELINE

    def is_available(self) -> bool:
        return True

    def get_status(self) -> BackendAvailability:
        return BackendAvailability(
            available=True,
            backend=BackendType.BASELINE,
            status=StagingBackendStatus.READY,
            duckdb_version=None,
            pyarrow_version=None,
            error_detail=None,
        )

    def commit_proposal(
        self,
        record: ParquetProposalRecord,
        target_table: str = "concept_proposals",
    ) -> CommitResult:
        p_dir = get_proposals_dir(self.workspace_root)
        dest = p_dir / f"{record.proposal_id}.yaml"
        tmp = p_dir / f".{record.proposal_id}.yaml.tmp"

        # Check existing for idempotency and integrity collision (fail closed)
        if dest.exists():
            try:
                with open(dest, "r", encoding="utf-8") as fp:
                    data = yaml.safe_load(fp)
                existing = CandidateProposal.model_validate(data)
            except Exception as e:
                raise DSCPIntegrityError(
                    f"Existing proposal at {dest} is corrupt or unparseable; refusing "
                    f"to overwrite it (fail closed): {e} [E114]"
                ) from e
            if existing.proposal_hash == record.input_sha256:
                # Idempotent no-op
                return CommitResult(
                    proposal_id=record.proposal_id,
                    input_sha256=record.input_sha256,
                    target_table=target_table,
                    is_noop=True,
                )
            raise DSCPIntegrityError(
                f"Identity collision for proposal_id '{record.proposal_id}' "
                f"with divergent hash: existing={existing.proposal_hash}, "
                f"new={record.input_sha256}. [E114]"
            )

        # Build candidate proposal
        body = ""
        if record.incident:
            try:
                body = json.loads(record.incident).get("body", "")
            except Exception:
                body = record.incident
        elif record.observation:
            try:
                body = json.loads(record.observation).get("body", "")
            except Exception:
                body = record.observation

        fm = {
            "scope": record.inferred_scope,
            "domain": record.inferred_domain or "software_engineering",
            "taxonomy_id": record.inferred_taxonomy_id or "TX-ENG-01",
            "confidence": record.model_confidence or 0.5,
            "status": record.status,
            "evidence": record.epistemic_status,
            "verification": record.validation_status,
        }

        candidate = CandidateProposal(
            candidate_id=record.proposal_id,
            proposal_revision=record.trajectory_revision,
            created_at=record.created_at,
            state=record.status
            if record.status in ("pending", "approved", "rejected")
            else "pending",
            evidence_unit_ref=record.trajectory_id,
            source_revision=f"sha256:{hashlib.sha256(record.proposal_id.encode('utf-8')).hexdigest()}",
            target_path=f"{record.inferred_scope}/01_domain_system_architecture/{record.proposal_id}.md",
            proposed_frontmatter=fm,
            proposed_body=body,
            proposed_content=f"---\n{yaml.dump(fm, sort_keys=False)}---\n\n{body}\n",
            proposal_hash=record.input_sha256,
        )

        with open(tmp, "w", encoding="utf-8") as f:
            yaml.dump(candidate.model_dump(), f, sort_keys=False, allow_unicode=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, dest)

        return CommitResult(
            proposal_id=record.proposal_id,
            input_sha256=record.input_sha256,
            target_table=target_table,
            is_noop=False,
        )

    def get_proposal(
        self,
        proposal_id: str,
        target_table: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        _ = target_table
        p_dir = get_proposals_dir(self.workspace_root)
        f_path = p_dir / f"{proposal_id}.yaml"
        if not f_path.exists():
            return None
        with open(f_path, "r", encoding="utf-8") as fp:
            data = yaml.safe_load(fp)
        return data

    def list_proposals(
        self,
        target_table: str = "concept_proposals",
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        _ = target_table
        p_dir = get_proposals_dir(self.workspace_root)
        results = []
        for f in sorted(p_dir.glob("*.yaml")):
            if f.name.startswith("."):
                continue
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = yaml.safe_load(fp)
                if status_filter is None or data.get("state") == status_filter:
                    results.append(data)
            except Exception as e:
                print(f"WARNING: skipping unparseable proposal {f}: {e}")
                continue
        return results

    def count_proposals(self, target_table: Optional[str] = None) -> int:
        _ = target_table
        return len(self.list_proposals(status_filter=None))

    def emit_manifest(self) -> StagingManifest:
        p_dir = get_proposals_dir(self.workspace_root)
        proposals = self.list_proposals()
        counts_by_status: Dict[str, int] = {}
        counts_by_scope: Dict[str, int] = {}

        for p in proposals:
            st = p.get("state", "pending")
            counts_by_status[st] = counts_by_status.get(st, 0) + 1
            fm = p.get("proposed_frontmatter", {})
            sc = fm.get("scope", "ambiguous")
            counts_by_scope[sc] = counts_by_scope.get(sc, 0) + 1

        tables = {
            "proposals": StagingTableInfo(
                table_name="proposals",
                relative_path="staging/proposals/",
                row_count=len(proposals),
                file_sha256=None,
                size_bytes=sum(
                    f.stat().st_size for f in p_dir.glob("*.yaml") if not f.name.startswith(".")
                ),
                columns=["candidate_id", "state", "proposal_hash", "target_path"],
            )
        }

        manifest = StagingManifest(
            schema_version="0.5.2",
            backend="baseline",
            tables=tables,
            total_proposals=len(proposals),
            counts_by_status=counts_by_status,
            counts_by_scope=counts_by_scope,
            generated_at=current_iso_timestamp(),
        )

        manifest_path = self.workspace_root / "staging" / "staging_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_manifest = self.workspace_root / "staging" / ".staging_manifest.json.tmp"
        with open(tmp_manifest, "w", encoding="utf-8") as f:
            f.write(json.dumps(manifest.model_dump(), indent=2, sort_keys=True))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_manifest, manifest_path)

        return manifest

    def run_migrations(self) -> None:
        # Baseline uses SQLite journal
        get_journal(self.workspace_root)

    def recover_transactions(self) -> Dict[str, int]:
        journal = get_journal(self.workspace_root)
        recovered = journal.recover_pending_transactions(self.workspace_root)
        return {"recovered_operations": len(recovered)}
