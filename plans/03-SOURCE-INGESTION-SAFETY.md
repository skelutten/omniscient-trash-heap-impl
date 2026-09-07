# Plan 03 — Source ingestion safety & Sandboxing

> **Status:** complete
> **Prerequisite:** `02-DETERMINISTIC-CORE.md` green
> **Next:** `04-PROPOSAL-PROMOTION-RECOVERY.md`

## Goal

Implement the smallest safe ingestion slice without coupling it to the full connector family or canonical promotion, enforcing prompt injection fences and path sandboxing.

## Scope

1. Universal Source envelope and registry-driven profile validation.
2. First executable profiles: `document`, `agent_trajectory`, `thought`, `meeting`, `code_repository`.
3. Source identity, representation identity, content hash and provenance validation.
4. Input sanitization, path traversal/size/timeout/resource-limit checks and fail-closed quarantine.
5. Canonical path normalization (`os.path.realpath`) enforcing workspace root confinement (`FR-13`).
6. Prompt injection defense wrapping raw untrusted inputs with immutable `<untrusted_source>` delimiters (`FR-12`, `NFR-6`).
7. Immutable raw capture and CSCC.
8. Evidence Unit staging projection only.
9. Same identity/hash as verified no-op; divergent hash as closed failure.
10. Adversarial fixtures, including secrets, traversal attacks, and prompt injection strings.

Raw capture MUST remain lossless and append-only. Normalized, sanitized and
trajectory-derived material belongs outside raw storage and MUST retain the
source/representation provenance required by `INGEST-STAGING.md`.

## Stop point

```text
safe input → sandbox & sanitize → source profile → immutable raw representation → normalized record
```

## Acceptance

- Unsafe input cannot partially persist.
- Path traversal payloads (e.g. `../../etc/passwd`) are rejected with `AccessDeniedError`.
- Untrusted text is fenced and cannot execute agent commands.
- Raw bytes are never overwritten.
- Capture is idempotent, divergent representations are distinguishable, provenance survives normalization and filesystem degradation is reported rather than passed.

## Non-goals

No connector family, canonical promotion, vector retrieval, graph intelligence or Parquet backend.

## Source material

- `../specs/UNIVERSAL-SOURCE-EXTENSION.md`
- `../specs/INGEST-DATA-MODEL.md`, `INGEST-STAGING.md`, `INGEST-ADAPTERS.md`
- `../schemas/registry/source_registry.yaml`
