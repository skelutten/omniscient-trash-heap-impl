# Plan 06 — Specification remediation after input-artifact review

> **Status:** active spec-only work; runtime not started
> **Normative owners:** `specs/` and `schemas/registry/`
> **Input boundary:** `input-artifacts/` is immutable review input; examples added there are illustrative only

## Objective

Close the review-identified contract gaps without implementing runtime code,
fixtures as executable tests, loaders, linters, adapters or CI gates.

## Addressed contract areas

| Review area | Contract destination | Status |
|---|---|---|
| Capture/review/promotion lifecycle | `specs/REVIEW-PROMOTION.md` | Draft, unimplemented |
| Deterministic write, approval binding, idempotency and recovery | `specs/REVIEW-PROMOTION.md` | Draft, unimplemented |
| End-to-end field-shape ambiguity | `input-artifacts/END-TO-END-CONTRACT-EXAMPLE.md` | Illustrative input |
| Review queue and degraded mode | `specs/INGEST-STAGING.md` §7.3.1 | Specified; unimplemented |
| Resource limits and fail-closed processing | `specs/INGEST-PIPELINE.md` §6 | Specified; deployment values pending |
| Derived freshness and invalidation | `specs/ARCHITECTURE.md` §2.4 | Specified; unimplemented |
| Taxonomy evolution and migration | `specs/ARCHITECTURE.md` §7.4 | Specified; unimplemented |
| Conformance ownership and vocabulary | `specs/VALIDATION.md` §10.5 | Specified; executable projection pending |

## Remaining work before runtime

1. Reconcile terminology and identifiers across all normative owners.
2. Add the review/promotion contract to the ownership projection only if its
   invariant families are finalized and unique.
3. Define deployment-policy schema for resource limits and measured scale
   records without inventing universal performance thresholds.
4. Resolve review findings directly in the owning specs, registries or plans;
   do not create review reports under `plans/`.
5. Rerun the eight reviews after the spec-only change set; keep their output in
   `../review-outputs/`.
6. Verify each runtime plan against its owning spec: explicit prerequisites,
   complete scope, concrete acceptance evidence, failure/recovery behavior and
   conservative status. A review finding is not resolved merely because it is
   mentioned in a plan.

## Explicit non-goals

- No `pyproject.toml`, package, runtime module or CLI.
- No executable `tests/` or `conformance/` suite.
- No status upgrade to `IMPLEMENTED`, `CONFORMANCE_TESTED` or `PRODUCTION_VERIFIED`.
- No modification of vendored external specifications.

## Acceptance for this phase

All normative YAML parses; ownership paths resolve; no duplicate invariant
families or error-code owners are introduced; examples are labelled
non-executable; input artifacts remain unchanged except for explicitly added
illustrative examples; secrets are absent; and `git diff --check` passes.

The runtime readiness statement remains:

```text
Specifications improved; runtime implementation and conformance remain UNIMPLEMENTED.
```
