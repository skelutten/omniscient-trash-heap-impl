"""Dual-backend equivalence checks and synchronization (plans/93-OPT-IN-PARQUET-STAGING.md)."""

import json
from typing import Optional

from trashheap.promotion.models import CandidateProposal
from trashheap.staging.baseline import BaselineStagingBackend
from trashheap.staging.models import (
    EquivalenceDiff,
    EquivalenceReport,
    ParquetProposalRecord,
    current_iso_timestamp,
)
from trashheap.staging.parquet import ParquetStagingBackend


def sync_baseline_to_parquet(
    baseline: BaselineStagingBackend,
    parquet: ParquetStagingBackend,
) -> int:
    """Synchronize all proposals from baseline staging to Parquet staging."""
    parquet.run_migrations()
    proposals = baseline.list_proposals()
    synced = 0

    for p_dict in proposals:
        candidate = CandidateProposal.model_validate(p_dict)
        fm = candidate.proposed_frontmatter or {}
        scope = fm.get("scope", "ambiguous")

        # Scope-conditioned root object (E104)
        incident_json: Optional[str] = None
        observation_json: Optional[str] = None

        if scope == "engineering":
            incident_json = json.dumps({"body": candidate.proposed_body})
        else:
            observation_json = json.dumps({"body": candidate.proposed_body})

        record = ParquetProposalRecord(
            proposal_id=candidate.candidate_id,
            trajectory_id=candidate.evidence_unit_ref or "default",
            trajectory_revision=candidate.proposal_revision,
            ingestion_id=f"ING-{candidate.candidate_id}",
            schema_version="0.5.2",
            inferred_scope=scope,
            scope_confidence=float(fm.get("confidence", 0.9)),
            scope_method="trajectory_observed",
            scope_status="inferred",
            cross_scope=False,
            inferred_domain=fm.get("domain", "software_engineering"),
            inferred_taxonomy_id=fm.get("taxonomy_id", "TX-ENG-01"),
            inferred_facets=json.dumps(
                {
                    k: v
                    for k, v in fm.items()
                    if k in ("language", "audience", "toolchain", "lifecycle")
                }
            ),
            epistemic_status=fm.get("evidence", "inferred"),
            evidence_level="trajectory_observed",
            validation_status=fm.get("verification", "unverified"),
            promotion_status="promoted" if candidate.state == "promoted" else "staged",
            provenance=json.dumps({"source_refs": candidate.source_refs}),
            evidence_bundle="{}",
            incident=incident_json,
            observation=observation_json,
            model_confidence=float(fm.get("confidence", 0.9)),
            quality_score=float(fm.get("confidence", 0.9)),
            status=candidate.state,
            created_at=candidate.created_at,
            input_sha256=candidate.proposal_hash,
            rejection_reason="LOW_QUALITY" if candidate.state == "rejected" else None,
        )

        # Route target table
        if candidate.state == "rejected":
            target_table = "rejected_low_quality"
        elif scope == "ambiguous":
            target_table = "ambiguous_scope"
        else:
            target_table = "concept_proposals"

        parquet.commit_proposal(record, target_table=target_table)
        synced += 1

    return synced


def verify_backend_equivalence(
    baseline: BaselineStagingBackend,
    parquet: ParquetStagingBackend,
) -> EquivalenceReport:
    """Verify state equivalence across baseline and Parquet staging backends."""
    baseline_proposals = baseline.list_proposals()
    baseline_map = {p["candidate_id"]: p for p in baseline_proposals}

    parquet_proposals = []
    for t_name in ["concept_proposals", "ambiguous_scope", "rejected_low_quality"]:
        parquet_proposals.extend(parquet.list_proposals(t_name))
    parquet_map = {p["proposal_id"]: p for p in parquet_proposals}

    matched_ids = []
    missing_in_parquet = []
    missing_in_baseline = []
    diffs = []

    for cand_id, b_data in baseline_map.items():
        if cand_id not in parquet_map:
            missing_in_parquet.append(cand_id)
        else:
            p_data = parquet_map[cand_id]
            has_diff = False

            # Compare status / state
            b_state = b_data.get("state")
            p_status = p_data.get("status")
            if b_state != p_status:
                diffs.append(
                    EquivalenceDiff(
                        proposal_id=cand_id,
                        field_name="status",
                        baseline_value=b_state,
                        parquet_value=p_status,
                    )
                )
                has_diff = True

            # Compare proposal hash / input_sha256
            b_hash = b_data.get("proposal_hash")
            p_hash = p_data.get("input_sha256")
            if b_hash != p_hash:
                diffs.append(
                    EquivalenceDiff(
                        proposal_id=cand_id,
                        field_name="input_sha256",
                        baseline_value=b_hash,
                        parquet_value=p_hash,
                    )
                )
                has_diff = True

            # Compare scope
            b_scope = (b_data.get("proposed_frontmatter") or {}).get("scope")
            p_scope = p_data.get("inferred_scope")
            if b_scope and p_scope and b_scope != p_scope:
                diffs.append(
                    EquivalenceDiff(
                        proposal_id=cand_id,
                        field_name="inferred_scope",
                        baseline_value=b_scope,
                        parquet_value=p_scope,
                    )
                )
                has_diff = True

            if not has_diff:
                matched_ids.append(cand_id)

    for p_id in parquet_map:
        if p_id not in baseline_map:
            missing_in_baseline.append(p_id)

    is_equiv = len(missing_in_parquet) == 0 and len(missing_in_baseline) == 0 and len(diffs) == 0

    return EquivalenceReport(
        is_equivalent=is_equiv,
        baseline_count=len(baseline_map),
        parquet_count=len(parquet_map),
        matched_ids=matched_ids,
        missing_in_parquet=missing_in_parquet,
        missing_in_baseline=missing_in_baseline,
        diffs=diffs,
        checked_at=current_iso_timestamp(),
    )
