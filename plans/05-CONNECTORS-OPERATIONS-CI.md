# Plan 05 — Connectors, operations and CI

> **Status:** completed, verified (2026-09-07, D107)
> **Prerequisite:** `04-PROPOSAL-PROMOTION-RECOVERY.md` green
> **Next:** optional plans `90–93`

## Goal

Complete the core operational boundary and make conformance reproducible in a clean checkout.

## Scope

1. Connector, adapter and cursor contracts.
2. Retention/reaper behavior and operational audit.
3. Local gate and CI-equivalent commands.
4. Generated conformance projection and status dashboard drift detector (D90) validating `SPEC_STATUS.md` against specs, registries, runtime, tests and CI markers.
5. Performance measurements and evidence-based scale transition criteria.
6. Explicit degraded/blocked reporting for unavailable dependencies.

The conformance projection is generated evidence, not a normative specification
and not a replacement for the owning specs or registries. Performance values
must be reported as measured baselines or explicitly uncalibrated proposed
targets; they must not be promoted to production claims by this plan alone.

## Stop point

```text
clean clone → local gate → CI-equivalent result → conformance projection
```

## Acceptance

A clean checkout reproduces the gate. Status dashboard changes are backed by observed output. `conformance_matrix.yaml` is generated output, never normative input.

## Non-goals

Vector retrieval, graph intelligence, structural graph and Parquet remain separate opt-in tracks.

## Source material

- `../specs/INGEST-ADAPTERS.md`, `VALIDATION.md`, `SPEC_STATUS.md`
