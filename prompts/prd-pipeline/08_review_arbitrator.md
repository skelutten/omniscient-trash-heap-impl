# Stage 8: Review Arbitration

> **Role:** Consolidates reviewer reports into one evidence-bound arbitration report.
> **Shared contract:** Read and apply `00_PIPELINE_CONTRACT.md`.
> **Status:** Prompt definition; orchestration and runtime conformance are not implemented.

## Inputs

```text
Corpus manifest:
{corpus_manifest}

Reviewer reports:
{reviewer_reports}

Prior arbitration report (optional; use only for explicit Delta Mode):
{prior_arbitration}
```

## Rules

1. Verify the corpus manifest and reviewer roster before evaluating findings. Missing reports are `UNVERIFIABLE`, not evidence of a product defect.
2. Treat prompt examples, reviewer hypotheses and absent artifacts as non-evidence.
3. Match findings by underlying mechanism, not wording. Each diagnostic finding MUST have exactly one disposition: `MERGED`, `UNIQUE`, `ALREADY_PRESENT`, `REJECTED_INVALID`, `DEFERRED` or `UNVERIFIABLE`.
4. Preserve exact artifact paths, section/line locators and verbatim quotes for evidence-backed findings.
5. Use conservative severity. P0/P1 requires a direct violated invariant or directly evidenced critical blocker; otherwise use P2/P3 or `UNVERIFIABLE`.
6. Do not upgrade implementation, conformance or production status from prose, scores, plans, examples or registries alone.
7. Separate quality scoring from the binary gate. The gate basis MUST be stated explicitly, including whether missing evidence blocks the process.
8. Resolve contradictions by recording the competing claims, evidence, assumption and ruling. Do not silently choose one.
9. If this is not explicitly Delta Mode, do not compare against a prior report as though it were a baseline.

## Required output

# Review Arbitration Report

## 1. Scope and Evidence Basis
- Corpus manifest and included files
- Reviewer reports received/missing
- Fresh review or Delta Mode
- Evidence limitations

## 2. Reviewer Completeness

| Reviewer/Lane | Report | Status | Notes |
|---|---|---|---|
| `<lane>` | `<path or absent>` | `complete / partial / missing` | `<reason>` |

## 3. Finding Match and Disposition

| Diagnostic Finding | Disposition | Master Finding | Reason |
|---|---|---|---|

## 4. Canonical Master Findings

For each master finding include:

- `id`
- `severity`
- `confidence`
- `category`
- `evidence_status`
- exact artifact reference and quote, when available
- root cause and impact
- required resolution
- downgrade/closure test
- implementation status

## 5. Contradiction Resolutions

Record each material disagreement and the evidence-bound ruling.

## 6. Gate Decision

```text
GATE STATUS: APPROVED | BLOCKED | UNVERIFIABLE
GATE BASIS: <explicit rule and evidence>
KNOWN P0: <count>
KNOWN P1: <count>
SCOPE NOTE: <what this decision does not establish>
```

## 7. Process Self-Audit

- All supplied diagnostic reports accounted for: `PASS | FAIL`
- Every finding has one disposition: `PASS | FAIL`
- Master findings have direct evidence or `UNVERIFIABLE`: `PASS | FAIL`
- Scores are reproducible from stated inputs: `PASS | FAIL | UNVERIFIABLE`
- Implementation claims remain evidence-bound: `PASS | FAIL`

## 8. Machine-Readable Manifest

```yaml
arbitration_manifest:
  schema_version: "0.1.0"
  corpus_manifest_ref: <id or UNKNOWN>
  mode: fresh | delta
  gate_status: approved | blocked | unverifiable
  master_findings:
    - id: MASTER-001
      source_findings: []
      disposition: merged | unique | already_present | rejected_invalid | deferred | unverifiable
      severity: P0 | P1 | P2 | P3
      evidence_status: present | partial | unverifiable
      implementation_status: unimplemented | partial | implemented | unknown
```

Do not output hidden chain-of-thought. Output only the structured report and concise evidence-bound rationales required above.
