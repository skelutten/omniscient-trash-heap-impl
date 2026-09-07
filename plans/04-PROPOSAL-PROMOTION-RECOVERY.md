# Plan 04 — Proposal, promotion and recovery

> **Status:** complete
> **Prerequisite:** `03-SOURCE-INGESTION-SAFETY.md` green
> **Next:** `05-CONNECTORS-OPERATIONS-CI.md`
> **Normative contract:** `../specs/REVIEW-PROMOTION.md`

## Goal

Build the governed state transition from staged source material to canonical Knowledge Objects.

## Scope

1. Candidate lifecycle and retention states.
2. Source spans, Evidence Units, provenance and derivation records.
3. Actor/reviewer identity and approval binding.
4. Pending, reviewed, approved, rejected, expired, promoted and failed fixtures.
5. Deterministic write boundary and no-mutation-on-invalid/unauthorized promotion.
6. DPCP journal, crash recovery, replay and rebuild equivalence.
7. Idempotent promotion and audit reconstruction.

The state machine, approval binding, mutation allowlist, no-mutation-on-failure
rule, journal states, recovery behavior and provenance requirements are owned by
`specs/REVIEW-PROMOTION.md`. This plan sequences implementation only and does not
introduce a second contract.

The plan MUST implement the queue/review boundary without silently changing
the queue metrics, retention or degraded-mode semantics owned by
`../specs/INGEST-STAGING.md`. Approval is admissibility, not epistemic truth;
promotion MUST preserve the provenance and decision records required by the
normative contract.

## Stop point

```text
candidate → review → approval → deterministic promotion → audit/rebuild
```

## Acceptance

Invalid, stale or unauthorized proposals cannot mutate canonical storage. Interrupted transactions recover deterministically. Provenance, reviewer decisions and source references survive promotion and rebuild.

## Non-goals

No broad connector surface, recurrence implementation, structural graph or advanced retrieval.

## Source material

- `../specs/DISCOVERY.md`
- `../specs/INGEST-PIPELINE.md`, `INGEST-STAGING.md`, `EPISTEMOLOGY.md`
