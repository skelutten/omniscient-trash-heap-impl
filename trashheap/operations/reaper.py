"""Deterministic TTL-Reaper, Passive Staleness & Knowledge Debt Metrics (INGEST-STAGING.md §7.3)."""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from trashheap.promotion.engine import list_candidates, save_candidate
from trashheap.promotion.models import StateTransitionRecord, current_iso_timestamp
from trashheap.timeutil import parse_iso_timestamp


@dataclass
class KnowledgeDebtReport:
    """Knowledge debt and passive staleness metrics (§7.3.2)."""

    pending_backlog_count: int
    oldest_item_age_days: float
    quarantined_count: int
    days_since_last_run: float
    expiry_warning: bool
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pending_backlog_count": self.pending_backlog_count,
            "oldest_item_age_days": round(self.oldest_item_age_days, 2),
            "quarantined_count": self.quarantined_count,
            "days_since_last_run": round(self.days_since_last_run, 2),
            "expiry_warning": self.expiry_warning,
            "details": self.details,
        }


class TTLReaper:
    """Deterministic, idempotent staging retention reaper (INGEST-CORE-022, INGEST-STAGING.md §7.3)."""

    def __init__(
        self,
        workspace_root: Path,
        ttl_days: int = 180,
        grace_days: int = 7,
    ):
        self.workspace_root = workspace_root
        self.ttl_days = ttl_days
        self.grace_days = grace_days
        self.audit_log_path = (
            self.workspace_root / "staging" / "transactions" / "reaper_audit.jsonl"
        )
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def _log_audit(self, entry: Dict[str, Any]) -> None:
        entry["logged_at"] = current_iso_timestamp()
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def _expiry_anchor(self, candidate: Any, created_dt: datetime) -> datetime:
        """Return the instant from which the grace period is measured.

        Prefers the timestamp of the most recent ``expired`` state transition in
        the proposal's history (the actual expiry event). When no parseable
        expiry transition exists, falls back to the theoretical expiry instant
        ``created_at + ttl_days`` — never to creation time itself (INGEST-STAGING.md §7.3).
        """
        for record in reversed(candidate.history):
            if record.new_state == "expired":
                transitioned = parse_iso_timestamp(record.transitioned_at)
                if transitioned is not None:
                    return transitioned
        return created_dt + timedelta(days=self.ttl_days)

    def run_reap_cycle(self, now: Optional[datetime] = None) -> Dict[str, Any]:
        """Execute deterministic retention reaper pass.

        Rules:
        1. Proposals with state == 'pending' whose age >= ttl_days are transitioned to 'expired'.
        2. Proposals with state == 'approved' or 'promoted' are NEVER expired.
        3. Expired proposals are purged only once ``now >= expiry_anchor + grace_days``,
           where the anchor is the recorded expiry transition (or the theoretical
           expiry ``created_at + ttl_days`` when no transition is present).
        4. Proposals with a corrupt/unparseable ``created_at`` are NEVER expired or
           purged; they are quarantined (fail-visible) and reported for manual review.
        5. Canonical files (personal/, engineering/) are NEVER touched.
        """
        current_time = now or datetime.now(timezone.utc)
        candidates = list_candidates(self.workspace_root)

        expired_count = 0
        purged_count = 0
        quarantined: List[str] = []

        for c in candidates:
            created_dt = parse_iso_timestamp(c.created_at)
            if created_dt is None:
                # Fail-visible: a corrupt creation timestamp must never trigger a
                # silent purge or a blind expiry. Quarantine and surface it.
                quarantined.append(c.candidate_id)
                self._log_audit(
                    {
                        "action": "quarantine_corrupt_timestamp",
                        "candidate_id": c.candidate_id,
                        "created_at": c.created_at,
                        "reason": "unparseable created_at; excluded from expiry and purge",
                    }
                )
                continue

            age_days = (current_time - created_dt).total_seconds() / 86400.0

            # Step 1: Transition pending proposals to expired if age >= ttl_days
            if c.state == "pending" and age_days >= self.ttl_days:
                trans = StateTransitionRecord(
                    transition_id=f"TR-EXPIRE-{c.candidate_id}",
                    candidate_id=c.candidate_id,
                    proposal_revision=c.proposal_revision,
                    previous_state="pending",
                    new_state="expired",
                    actor="process:ttl-reaper",
                    transitioned_at=current_iso_timestamp(),
                    reason=f"Exceeded TTL of {self.ttl_days} days (age: {age_days:.1f} d)",
                    source_refs=c.source_refs,
                    representation_refs=c.representation_refs,
                )
                c.state = "expired"
                c.history.append(trans)
                save_candidate(c, self.workspace_root)
                self._log_audit(
                    {
                        "action": "status_transition",
                        "candidate_id": c.candidate_id,
                        "new_state": "expired",
                        "age_days": age_days,
                    }
                )
                expired_count += 1

            # Step 2: Purge proposals whose grace period (measured from expiry) has elapsed
            elif c.state == "expired":
                expiry_anchor = self._expiry_anchor(c, created_dt)
                if current_time >= expiry_anchor + timedelta(days=self.grace_days):
                    p_file = (
                        self.workspace_root / "staging" / "proposals" / f"{c.candidate_id}.yaml"
                    )
                    p_file.unlink(missing_ok=True)
                    self._log_audit(
                        {
                            "action": "tombstone_purge",
                            "candidate_id": c.candidate_id,
                            "proposal_revision": c.proposal_revision,
                            "source_refs": c.source_refs,
                            "age_days": age_days,
                            "expiry_anchor": expiry_anchor.isoformat(),
                        }
                    )
                    purged_count += 1

        return {
            "expired_count": expired_count,
            "purged_count": purged_count,
            "quarantined_count": len(quarantined),
            "quarantined": quarantined,
        }


def calculate_knowledge_debt(
    workspace_root: Path,
    ttl_days: int = 180,
    now: Optional[datetime] = None,
) -> KnowledgeDebtReport:
    """Calculate passive staleness and knowledge debt metrics (§7.3.2)."""
    current_time = now or datetime.now(timezone.utc)
    candidates = list_candidates(workspace_root)

    pending_items = [c for c in candidates if c.state == "pending"]
    oldest_age = 0.0
    corrupt_timestamps = 0

    for p in pending_items:
        c_time = parse_iso_timestamp(p.created_at)
        if c_time is None:
            # Fail-visible: count corrupt timestamps instead of silently ignoring them.
            corrupt_timestamps += 1
            continue
        age = (current_time - c_time).total_seconds() / 86400.0
        if age > oldest_age:
            oldest_age = age

    # Count quarantined files
    quarantine_dir = workspace_root / "staging" / "quarantine"
    quarantined_count = len(list(quarantine_dir.glob("*"))) if quarantine_dir.exists() else 0

    # Expiry warning if oldest item age >= ttl - 2 days
    expiry_warning = oldest_age >= max(0.0, float(ttl_days - 2))

    return KnowledgeDebtReport(
        pending_backlog_count=len(pending_items),
        oldest_item_age_days=oldest_age,
        quarantined_count=quarantined_count,
        days_since_last_run=oldest_age,
        expiry_warning=expiry_warning,
        details={
            "total_candidates": len(candidates),
            "approved_count": len([c for c in candidates if c.state == "approved"]),
            "promoted_count": len([c for c in candidates if c.state == "promoted"]),
            "rejected_count": len([c for c in candidates if c.state == "rejected"]),
            "corrupt_timestamps": corrupt_timestamps,
        },
    )
