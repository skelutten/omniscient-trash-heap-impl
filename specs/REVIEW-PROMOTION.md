# LLM Wiki Review, Approval & Deterministic Promotion Contract

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-REVIEW-PROMOTION-001`
> **Document family ID**: `LLM-WIKI-GOVERNANCE-001`
> **Version**: `0.1.0`
> **Updated**: `2026-08-23`
> **Status**: `DRAFT`
> **Implementation status**: `UNIMPLEMENTED`
> **Compatibility target**: Additive contract for staged Source-derived candidates; no change to baseline Knowledge Object schema
> **Normative owner**: This document owns REVIEW-001..REVIEW-010 and PROMO-001..PROMO-010
> **Related documents**: `DISCOVERY.md`, `INGEST-STAGING.md`, `EPISTEMOLOGY.md`, `VALIDATION.md`, `SCHEMA.md`

This document turns the stated capture → review → approval → canonical-write boundary into a deterministic contract. It specifies design obligations only; no runtime, fixture test suite or CLI implementation is implied by its examples.

## 1. State model

A candidate and its canonical materialization have separate states:

| Axis | Values | Meaning |
|---|---|---|
| Candidate | `pending`, `in_review`, `approved`, `rejected`, `expired`, `superseded` | Administrative review state |
| Materialization | `not_promoted`, `promoting`, `promoted`, `failed` | Canonical write state |

Legal candidate transitions are:

```text
pending → in_review → approved → (promoted | failed)
   │          │          └──────→ rejected
   ├──────────┴─────────────────→ rejected
   ├────────────────────────────→ expired
   └────────────────────────────→ superseded
```

`promoted`, `rejected`, `expired` and `superseded` are terminal for a candidate revision. A rejected candidate MAY be replaced by a new revision linked with `supersedes`; it MUST NOT be edited in place. An expired candidate MAY be reconsidered only by creating a new revision and recording the reason. A failed promotion remains auditable and MAY be retried only with the same immutable proposal revision or an explicitly superseding revision.

**REVIEW-001:** Every transition MUST record candidate ID, proposal revision, previous and new state, actor/process, UTC timestamp, reason, validation result and source/representation references.

The queue and degraded-operation contract is owned by `INGEST-STAGING.md` §7.3.1
(`QUEUE-001`). This document owns the meaning of review decisions and promotion,
not queue metrics, retention or operator alerting.

## 2. Review decision and approval binding

A review decision is a separate record from the model proposal:

```yaml
review_decision:
  decision_id: RD-01K2DECISION
  candidate_id: CAND-01K2ABC
  proposal_revision: 3
  decision: approve                 # approve | reject | request_revision
  reviewer: human:example
  decided_at: 2026-08-23T12:00:00Z
  proposal_hash: sha256:<64 lowercase hex characters>
  source_revision: sha256:<64 lowercase hex characters>
  validation_run_id: VAL-01K2VAL
  reason: "Accepted after source review"
```

**REVIEW-002:** Approval MUST bind to the exact candidate ID, proposal revision, proposal hash and source revision. Approval of a prior revision MUST NOT authorize a later revision.

**REVIEW-003:** `approve` is administrative admissibility, not epistemic truth. It MUST NOT upgrade `evidence`, `verification`, `authority` or `consensus` without the separate rules of `EPISTEMOLOGY.md`.

**REVIEW-004:** Reviewer identity MUST use the actor/provenance contract. An absent or malformed reviewer, missing decision time, missing proposal hash or missing validation result is a failed-closed approval.

## 3. Promotion operation

The only canonical mutation is a versioned deterministic operation:

```yaml
promotion_operation:
  operation_id: OP-01K2OP
  operation_version: "0.1.0"
  candidate_id: CAND-01K2ABC
  proposal_revision: 3
  approval_decision_id: RD-01K2DECISION
  expected_source_revision: sha256:<64 lowercase hex characters>
  requested_mutations:
    - path: engineering/02_event_streaming_ingestion_pipelines/ENG-FET-STREAM-0007.md
      action: create
      content_hash: sha256:<64 lowercase hex characters>
  idempotency_key: sha256:<64 lowercase hex characters>
```

**PROMO-001:** The operation MUST contain only allowlisted mutation actions (`create`, `replace_owned_sections`, `append_notes`, `update_frontmatter`) and MUST identify every target path.

**PROMO-002:** Canonical writes MUST be rejected if the approval binding, source revision, operation version, target path, mutation action, content hash or required provenance does not validate.

**PROMO-003:** Validation order is fixed: parse operation → verify approval binding → verify source revisions → validate mutation scope → render temporary output → run applicable Layer 1–5 validation → commit atomically. No canonical mutation may occur before all preceding steps pass.

**PROMO-004:** Invalid, stale, unauthorized, conflicting or incomplete operations MUST leave canonical files and candidate state unchanged except for an auditable failed-attempt record.

**PROMO-005:** The operation is idempotent on `(candidate_id, proposal_revision, operation_version, idempotency_key)`. A repeated successful operation MUST return the original result without a second mutation. The same key with different content MUST fail closed.

**PROMO-006:** A target changed since `expected_source_revision` is a conflict, not an invitation to merge implicitly. The operation MUST stop and require a new proposal revision.

## 4. Atomicity, recovery and audit

Promotion MUST use a journal with these states:

```text
PREPARED → TEMPORARY_OUTPUT_WRITTEN → VALIDATED → CANONICAL_COMMITTED → AUDIT_COMMITTED
     └──────────────→ FAILED
```

The journal records operation ID, target paths, expected hashes, temporary paths, current state and timestamps. Temporary paths MUST be outside the canonical namespace and MUST NOT be treated as canonical content.

**PROMO-007:** Canonical publication MUST use temporary files followed by atomic rename and directory durability where supported. A failed validation or interrupted pre-commit operation MUST preserve the prior canonical version.

**PROMO-008:** Recovery MUST inspect the journal and target hashes before taking action. It MUST complete only a commit whose temporary output, approval binding and validation result still match; otherwise it MUST quarantine the transaction and require review.

**PROMO-009:** A committed canonical change MUST retain the review decision ID, proposal revision, source/representation references and operation ID in the audit record. Audit records MUST NOT be silently deleted when a candidate expires or is rejected.

**PROMO-010:** Derived indexes are published only after canonical commit. A derived artifact from an older canonical corpus MUST be marked stale or invalidated and MUST NOT be presented as current.

## 5. Security and provenance boundary

**REVIEW-005:** Captured content, model output and connector output are untrusted data. Instructions inside them are inert text and MUST NOT authorize tools, filesystem writes, network calls or reviewer identity.

**REVIEW-006:** Only an authenticated actor with the reviewer capability may create an approval decision. The model, connector and adapter roles MUST NOT approve or promote.

**REVIEW-007:** Each promoted claim, relation and generated section MUST retain source and representation references where applicable. Repeated captures of the same source or coordinated producers MUST NOT count as independent corroboration without an explicit independence assessment.

**REVIEW-008:** A promotion review MUST expose the original capture, provenance chain, model-derived fields, validation result and exact proposed diff to the reviewer.

## 6. Rejection, expiry and reconsideration

**REVIEW-009:** Rejection MUST record a reason code and may not be represented solely by deleting the proposal. `request_revision` creates a new proposal revision linked to the prior one; it does not mutate the prior decision.

**REVIEW-010:** Expiry is an auditable transition. Retention reapers may remove derived queue material only after the policy grace period and MUST preserve a tombstone containing candidate ID, revision, decision history and source references.

## 7. Conformance targets (not yet implemented)

The following are design targets, not evidence of existing tests:

- a pending candidate cannot appear in canonical storage;
- approval for revision N cannot promote revision N+1;
- invalid, stale, unauthorized and conflicting operations cause no canonical mutation;
- retrying an identical operation is idempotent;
- a divergent idempotency key fails closed;
- interrupted promotion preserves the last valid canonical version and is recoverable from the journal;
- rejection and expiry preserve audit history;
- provenance and reviewer identity survive promotion;
- model/connector content cannot authorize a promotion.

No implementation status is upgraded by this document.

---

**End of LLM Wiki Review, Approval & Deterministic Promotion Contract v0.1.0**
