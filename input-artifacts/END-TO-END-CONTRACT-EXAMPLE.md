# End-to-End Contract Example (Normative Input Artifact)

> **Status:** illustrative specification input; normative reference for field-shape contracts  
> **Purpose:** provide one complete capture → proposal → review → validation → promotion shape  
> **Normative owners:** `specs/REVIEW-PROMOTION.md`, `specs/INGEST-STAGING.md`, `specs/EPISTEMOLOGY.md`, `specs/VALIDATION.md`

This document defines the exact field-shapes and data contracts across all stages of the LLM Wiki lifecycle, ensuring full coherence across `input-artifacts/`, `PRD.md`, `specs/`, and `plans/`.

---

## 1. Raw Capture (`staging/`)

```yaml
source:
  source_id: SRC-EXAMPLE-001
  source_type: document
  category: Artifact
  captured_at: 2026-08-24T10:00:00Z
  lifecycle: captured
  identity:
    resource: example://review-contract/001
  representation:
    representation_id: REP-EXAMPLE-001
    representation_hash: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  payload:
    media_type: text/plain
    content: "A deterministic review gate must precede canonical promotion."
```

*The raw representation is immutable, cryptographically hashed, and strictly sandboxed (`<untrusted_source>`).*

---

## 2. Staged Proposal (`discovery/`)

```yaml
candidate_id: CAND-EXAMPLE-001
proposal_revision: 1
candidate_type: node_proposal
status: pending
materialization_status: not_promoted
created_at: 2026-08-24T10:01:00Z
expires_at: 2026-09-24T10:01:00Z
source_refs: [SRC-EXAMPLE-001]
representation_refs: [REP-EXAMPLE-001]
evidence_unit_refs: [EU-EXAMPLE-001]
derivation_ref: DR-EXAMPLE-001
proposed_object:
  id: PERS-CON-EXAMPLE-0001
  title: Deterministic Review Gate
  scope: personal
  taxonomy_id: TX-PERS-07-04
  object_type: Concept
  domain: software_engineering
  facets:
    language: [en]
  epistemology:
    verification_level: unverified
    evidence_quality: high
    consensus: provisional
```

*The proposal is emitted by `/stage-lint` as a candidate diff and is quarantined from production query retrieval.*

---

## 3. Human Review Decision

```yaml
review_decision:
  decision_id: RD-EXAMPLE-001
  candidate_id: CAND-EXAMPLE-001
  proposal_revision: 1
  decision: approve
  reviewer: human:example-reviewer
  decided_at: 2026-08-24T10:05:00Z
  proposal_hash: sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
  source_revision: sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
  validation_run_id: VAL-EXAMPLE-001
  reason: "The source and proposed concept were reviewed and verified."
```

*Approval authorizes admissibility of this exact revision. It grants admittance, not subjective truth.*

---

## 4. Multi-Layer Validation Result (`specs/VALIDATION.md`)

```yaml
validation_result:
  validation_run_id: VAL-EXAMPLE-001
  result: pass
  owner: specs/VALIDATION.md
  checked_invariants: [ID-001, TAX-001, TAX-002, FAC-001, PROV-001, PROV-006, PROV-007, E001-E099]
  errors: []
```

*A failed validation result prevents canonical mutation and retains the failed attempt in the audit path.*

---

## 5. Promotion Operation & Atomic File Materialization

```yaml
promotion_operation:
  operation_id: OP-EXAMPLE-001
  operation_version: "0.1.0"
  candidate_id: CAND-EXAMPLE-001
  proposal_revision: 1
  approval_decision_id: RD-EXAMPLE-001
  expected_source_revision: sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
  requested_mutations:
    - path: personal/07.04_ai-assisted_software_engineering/PERS-CON-EXAMPLE-0001.md
      action: create
      atomic_strategy: tempfile_rename
```

*Promoted via atomic write (`.tmp` + `os.replace`), followed by index cache recreation and backlink resolution.*
