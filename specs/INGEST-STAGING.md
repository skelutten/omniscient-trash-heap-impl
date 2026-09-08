# LLM Wiki Ingestion Discovery Staging & Promotion Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-INGEST-STAGING-001`
> **Document family ID**: `LLM-WIKI-INGEST-SPEC-001`
> **Version**: `v0.5.2-RC` (Production-Hardening Candidate)
> **Updated**: `2026-08-17`
> **Source**: Extracted from `LLM-WIKI-INGEST-SPEC-001` §7, §9–§10
> **Status**: `DRAFT`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Compatibility target**: Additive, non-invasive, opt-in
> **System documents**: `INGEST.md` (core) · `INGEST-ADAPTERS.md` (§3) · `INGEST-PIPELINE.md` (§4–§6) · `INGEST-STAGING.md` (§7, §9–§10) · `INGEST-DATA-MODEL.md` (§11, §13)
> **Normative owner**: This document owns Source Storage/Capture Layer, staging, CSCC, DSCP/DPCP promotion and retention semantics
> **Related documents**: `UNIVERSAL-SOURCE-EXTENSION.md`, `INGEST-ADAPTERS.md`, `INGEST-PIPELINE.md`, `INGEST-DATA-MODEL.md`

---

## 7. Discovery Staging & Declarative Schema Evolution

### 7.0 Migration and import boundary

Migration/import is a governed Source-to-candidate operation, not a claim that
every file in a source tree is a canonical Knowledge Object. A migration record
MUST distinguish at least:

- `source_file_count`: every file included in the audited source snapshot;
- `eligible_object_count`: source files eligible for Knowledge Object analysis;
- `migrated_object_count`: eligible files actually emitted as candidates or
  canonical objects by the migration mode;
- `excluded_file_count`: deliberately excluded files, such as navigation or
  index files, with exclusion reason;
- `quarantined_file_count`: ambiguous, malformed, unsupported or otherwise
  blocked files, with a machine-readable reason per file.

Counts MUST NOT be collapsed into a single “migrated files” value. A successful
analysis MUST NOT report zero errors when fallback classification, lossy
mapping, unresolved scope, malformed metadata or another ambiguity occurred.
Fallback MAY produce a provisional candidate for analysis, but the record MUST
remain marked `ambiguous` or `quarantined` and MUST retain the original error,
mapping decision and source-relative path. Such a record MUST NOT be promoted
without the required review. The migration's summary MUST expose ambiguity and
quarantine counts separately from parser/analysis error counts; `error_count: 0`
MUST NOT imply that every object was safely classified.

Scope inference follows `DATA_MODEL.md` §8.1 and `INGEST.md` scope rules. A
verified personal source MAY use `personal` as an explicit migration target;
uncertain scope MUST remain `ambiguous` and MUST NOT silently fall back to
`personal`.

Legacy taxonomy mapping MUST distinguish exact from provisional/lossy mapping.
A top-level placement that discards legacy descendants or topics is
`lossy`; it MUST retain the original taxonomy path and mapping rationale and
MUST NOT silently refile or rewrite an existing canonical object. Subject
taxonomy, object type, domain and facets remain separate axes.

Migration enrichment is read-only. Subject keywords MUST NOT be promoted to
registry facets, and matched or unresolved wikilinks MUST NOT become canonical
relations automatically. Matched links MAY yield relation proposals; unresolved
links remain unresolved proposals. Any relation proposal MUST validate its type
and endpoints against `relation_registry.yaml` before review.

Legacy `source_ref` MAY be accepted as a compatibility input only. The normalized
provenance representation is `source_refs`; the original relative source path
MUST be preserved in the provenance/audit record. `source_ref` is not a new
normative canonical field.

Migration manifests MUST use a portable source identity and repository-relative
POSIX paths where possible. A resolved local path MAY be recorded as diagnostic
metadata, but an absolute machine-local path MUST NOT be the normative source
identity.

Migration defaults such as `draft`, `unverified`, `general` or a numeric
confidence placeholder describe processing state or an unclassified fallback;
they MUST NOT be interpreted as an epistemic assessment of source quality.

The migration executor MUST support a manifest-bound, fail-closed protocol:
exact-byte hashes over sorted relative POSIX paths, source preservation before
target creation, fresh-target-only execution, matching-manifest no-op, rejection
of changed source or unmanaged target, and no target execution when analysis
errors or quarantine obligations remain unresolved. The manifest MUST record
the mode, source snapshot identity/hash, counts above, target identity,
preservation result and analysis/quarantine summary.

The manifest MUST also record the mapping class for each emitted object or
proposal (`exact`, `provisional`, `lossy`, `ambiguous`, or `quarantined`) and
the source-relative path. `provisional` and `lossy` mappings MUST remain
review-gated and MUST NOT be represented as exact taxonomy or epistemic
classification.

### 7.1 Storage Structure, Source Capture & Retention Rules

The ingestion storage model has four logically separate layers. `raw/` is the
immutable Source Storage / Capture Layer; it is not a Knowledge Object workspace
and it is not mutable staging.

```text
wiki/
├── raw/                         # Immutable Source Store / Capture Layer
│   ├── sources/
│   │   └── <source_id>/
│   │       ├── source.yaml       # Stable Source identity and policy-neutral metadata
│   │       └── representations/
│   │           └── <representation_id>/
│   │               ├── metadata.yaml
│   │               └── content.*  # Lossless capture, or pointer to content store
│   ├── objects/sha256/           # Optional content-addressable byte store
│   │   └── <prefix>/<sha256>     # Immutable Content Object
│   └── manifests/                # Capture/import/export manifests
├── staging/                     # Derived and mutable proposals/audit state
│   ├── discovery/
│   │   ├── trajectories/sanitized/
│   │   ├── concept_proposals.parquet
│   │   ├── ambiguous_scope.parquet
│   │   └── rejected_low_quality.parquet
│   ├── transactions/             # DSCP/DPCP journals and temporary files
│   └── state/schema_version.json
├── knowledge/                   # Logical canonical Knowledge Object layer
│   └── ...
└── schemas/registry/
    └── ...
```

The physical location of `knowledge/` MAY remain the existing canonical
`personal/` and `engineering/` trees. The logical name is used here to distinguish
canonical Knowledge from Source Storage and staging; it does not authorize a
second canonical directory tree.

The minimal identity chain is:

```text
Source
  └── Representation
        └── Content Object (sha256)
```

`Source`, `Representation` and `Content Object` MUST remain distinct. A Source
MAY have many immutable representations; multiple Sources MAY reference the
same Content Object. The same bytes MUST NOT be copied merely because they are
associated with different Sources.

The Source directory is the addressable provenance view. The content store is
an optional deduplicating byte backend. An implementation MUST be able to
reconstruct the Source → Representation → Content Object relationship from
`source.yaml`, representation `metadata.yaml` and manifests without inspecting
Knowledge Objects.

Example representation metadata:

```yaml
source_id: SRC-01K2ABC
representation_id: REP-01K2XYZ
representation_hash: sha256:abcdef...
content_object_ref: sha256:abcdef...
media_type: text/html
captured_at: 2026-08-17T18:31:22Z
raw_status: immutable
supersedes: null
content_store:
  backend: repository | filesystem | lfs | external_blob
  object_id: sha256:abcdef...
```

The following transitions are forbidden:

```text
raw → edit → knowledge
raw → mutable normalization → knowledge
```

The permitted conceptual path is:

```text
raw → derive → candidate → review/governance → canonical Knowledge
```

Raw capture MUST be lossless and append-only. A changed URL, document,
conversation export or repository state creates a new Representation linked by
`supersedes`; an existing representation and its Content Object MUST NOT be
overwritten. Normalized or sanitized derivatives belong in staging or derived
artifacts and MUST retain `raw_ref`, `source_refs` and `representation_refs`.

Small text sources MAY be stored directly in Git. Large binaries MUST be
pluggable between repository, filesystem, Git LFS and external blob storage;
metadata, hashes and manifests remain diffable and traceable in the repository.
The storage backend MUST NOT change Source, Representation or Content Object
identity semantics.

Capture manifests MUST record, as applicable, source/representation IDs,
content hashes, media type, byte size, capture time, backend, schema/policy
version and integrity status. A manifest is an audit/index artifact, not a
replacement for the per-source metadata.

The Universal Source Extension's `raw_storage` block in
`source_registry.yaml` defines the registry-level minimum. This section owns
the ingestion storage layout, staging separation, retention behavior and
crash-safety consequences.

The existing trajectory discovery tables are retained as a compatibility view:

```text
discovery/
├── trajectories/
│   └── sanitized/               # Sanitized trajectories (Audit Trail: 365 d retention)
├── concept_proposals.parquet    # Pending proposals (TTL: 90 d, Invariant E108)
├── ambiguous_scope.parquet      # Ambiguous scope (TTL: 180 d)
├── rejected_low_quality.parquet # Terminal audit log (TTL: 90 d)
└── state/
    └── schema_version.json
```

New implementations SHOULD place this compatibility view under
`staging/discovery/`. Existing trajectory consumers MAY continue using
`discovery/` until migration.

TTL compliance is enforced by a deterministic reaper (§7.3, INGEST-CORE-022).
Retention MUST be layer-specific: staging TTLs MUST NOT delete raw Source
representations, and the ingestion reaper MUST NOT delete canonical Knowledge
Objects. Raw retention and deletion are governed by `governance_policy.yaml`
and, when deletion is required, the audit manifest MUST preserve the deletion
event without silently rewriting historical provenance.

### 7.1.1 Storage invariants

- **RAW-001**: Captured Source representations MUST NOT be modified in place.
- **RAW-002**: Every raw representation MUST be addressable by `source_id` and
  `representation_id` and MUST retain its content hash.
- **RAW-003**: A changed representation MUST create a new representation linked
  by `supersedes`; historical representations MUST remain addressable.
- **RAW-004**: Raw capture MUST be lossless; normalization, sanitization and
  extraction MUST write derived artifacts outside the immutable capture bytes.
- **RAW-005**: A Content Object MAY be deduplicated by content hash, but hash
  identity MUST NOT replace Source or Representation identity.
- **RAW-006**: Content backend selection MUST be pluggable and MUST NOT alter
  provenance or identity semantics.
- **RAW-007**: Source Storage, mutable staging and canonical Knowledge Storage
  MUST have separate ownership and retention rules.
- **RAW-008**: Capture/import manifests MUST preserve integrity and backend
  metadata sufficient to audit and reconstruct the identity chain.
- **RAW-009**: Raw capture MUST use a crash-safe commit sequence and be
  recoverable independently of normalization and promotion.
- **RAW-010**: Same Source identity plus same representation hash is idempotent;
  same representation identity plus a different hash fails closed.

The storage contract is intentionally additive and opt-in. It does not require
moving existing canonical `personal/` or `engineering/` files, and it does not make
raw files part of the Knowledge Object schema.

### 7.1.2 Crash-safe Source Capture Commit (CSCC)

Writing a raw representation is a separate transaction from normalization,
staging and canonical promotion. The capture commit MUST use this sequence:

```text
1. Reserve/check Source identity and Representation identity
2. Write content bytes to a sibling temporary path
3. fsync content bytes and close the file
4. Write metadata.yaml and source.yaml to temporary paths
5. fsync metadata, directories and manifest
6. Atomically rename the complete representation directory into raw/
7. Atomically append/replace the capture manifest index entry
8. Mark the representation committed in the ingestion state store
```

A crash before step 6 MUST leave no visible committed representation. A crash
after step 6 MUST be recoverable by scanning the committed directory and
rebuilding the manifest index without changing content or identity. A manifest
entry MUST NOT point to a representation directory that has not passed the
integrity/hash check.

Capture is idempotent: the same Source identity plus the same representation
hash is a no-op after integrity verification. The same representation identity
with a different hash is an integrity conflict and MUST fail closed (E141); it
MUST NOT overwrite the existing representation. A changed source state MUST
receive a new Representation ID or an explicitly deterministic versioned ID.

CSCC completion and recovery MUST be recorded separately from DSCP/DPCP. Raw
capture may be committed even if normalization or promotion later fails; such
failure changes the derived lifecycle/audit state, never the captured bytes.

---

### 7.2 Safe-Guarded Schema Evolution & Null-Tolerant Reconciliation

```python
import json
import logging
import os
from pathlib import Path
import time
import uuid
import duckdb

logger = logging.getLogger("wiki_ingest.schema")


class ParquetMigrationError(Exception):
  pass


TARGET_SCHEMAS = {
    "concept_proposals": [
        ("proposal_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_revision", "INTEGER", "1::INTEGER"),
        ("ingestion_id", "VARCHAR", "''::VARCHAR"),
        ("schema_version", "VARCHAR", "'0.5.2'::VARCHAR"),
        ("inferred_scope", "VARCHAR", "'ambiguous'::VARCHAR"),
        ("scope_confidence", "DOUBLE", "0.0::DOUBLE"),
        ("scope_method", "VARCHAR", "'historical_unknown'::VARCHAR"),
        ("scope_status", "VARCHAR", "'inferred'::VARCHAR"),
        ("cross_scope", "BOOLEAN", "FALSE::BOOLEAN"),
        ("inferred_domain", "VARCHAR", "''::VARCHAR"),
        ("inferred_taxonomy_id", "VARCHAR", "''::VARCHAR"),
        ("inferred_facets", "VARCHAR", "'{}'::VARCHAR"),
        ("epistemic_status", "VARCHAR", "'inferred'::VARCHAR"),
        ("evidence_level", "VARCHAR", "'trajectory_observed'::VARCHAR"),
        ("validation_status", "VARCHAR", "'unverified'::VARCHAR"),
        ("promotion_status", "VARCHAR", "'staged'::VARCHAR"),
        ("provenance", "VARCHAR", "'{}'::VARCHAR"),
        ("evidence_bundle", "VARCHAR", "'{}'::VARCHAR"),
        # Scope-conditional triad (E104): exactly one of incident/observation
        # is root object; both are serialized as JSON-VARCHAR.
        ("incident", "VARCHAR", "NULL::VARCHAR"),
        ("observation", "VARCHAR", "NULL::VARCHAR"),
        ("lesson", "VARCHAR", "NULL::VARCHAR"),
        ("workflow", "VARCHAR", "NULL::VARCHAR"),
        ("model_confidence", "DOUBLE", "0.0::DOUBLE"),
        ("quality_score", "DOUBLE", "NULL::DOUBLE"),
        ("status", "VARCHAR", "'pending'::VARCHAR"),
        ("created_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP"),
        ("expires_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP + INTERVAL '90 days'"),
        ("input_sha256", "VARCHAR", "''::VARCHAR"),
    ],
    "ambiguous_scope": [
        ("proposal_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_revision", "INTEGER", "1::INTEGER"),
        ("ingestion_id", "VARCHAR", "''::VARCHAR"),
        ("schema_version", "VARCHAR", "'0.5.2'::VARCHAR"),
        ("inferred_scope", "VARCHAR", "'ambiguous'::VARCHAR"),
        ("scope_confidence", "DOUBLE", "0.0::DOUBLE"),
        ("scope_method", "VARCHAR", "'historical_unknown'::VARCHAR"),
        ("scope_status", "VARCHAR", "'inferred'::VARCHAR"),
        ("cross_scope", "BOOLEAN", "FALSE::BOOLEAN"),
        ("inferred_domain", "VARCHAR", "''::VARCHAR"),
        ("inferred_taxonomy_id", "VARCHAR", "''::VARCHAR"),
        ("inferred_facets", "VARCHAR", "'{}'::VARCHAR"),
        ("epistemic_status", "VARCHAR", "'inferred'::VARCHAR"),
        ("evidence_level", "VARCHAR", "'trajectory_observed'::VARCHAR"),
        ("validation_status", "VARCHAR", "'unverified'::VARCHAR"),
        ("promotion_status", "VARCHAR", "'staged'::VARCHAR"),
        ("provenance", "VARCHAR", "'{}'::VARCHAR"),
        ("evidence_bundle", "VARCHAR", "'{}'::VARCHAR"),
        ("incident", "VARCHAR", "NULL::VARCHAR"),
        ("observation", "VARCHAR", "NULL::VARCHAR"),
        ("lesson", "VARCHAR", "NULL::VARCHAR"),
        ("workflow", "VARCHAR", "NULL::VARCHAR"),
        ("model_confidence", "DOUBLE", "0.0::DOUBLE"),
        ("quality_score", "DOUBLE", "NULL::DOUBLE"),
        ("status", "VARCHAR", "'pending'::VARCHAR"),
        ("created_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP"),
        (
            "expires_at",
            "TIMESTAMPTZ",
            "CURRENT_TIMESTAMP + INTERVAL '180 days'",
        ),
        ("input_sha256", "VARCHAR", "''::VARCHAR"),
    ],
    "rejected_low_quality": [
        ("proposal_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_id", "VARCHAR", "''::VARCHAR"),
        ("trajectory_revision", "INTEGER", "1::INTEGER"),
        ("ingestion_id", "VARCHAR", "''::VARCHAR"),
        ("schema_version", "VARCHAR", "'0.5.2'::VARCHAR"),
        ("inferred_scope", "VARCHAR", "'ambiguous'::VARCHAR"),
        ("inferred_domain", "VARCHAR", "''::VARCHAR"),
        ("rejection_reason", "VARCHAR", "'LOW_QUALITY'::VARCHAR"),
        # Scope-conditional root object (E104); exactly one is filled in.
        ("incident", "VARCHAR", "NULL::VARCHAR"),
        ("observation", "VARCHAR", "NULL::VARCHAR"),
        ("model_confidence", "DOUBLE", "0.0::DOUBLE"),
        ("quality_score", "DOUBLE", "NULL::DOUBLE"),
        ("created_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP"),
        ("expires_at", "TIMESTAMPTZ", "CURRENT_TIMESTAMP + INTERVAL '90 days'"),
        ("input_sha256", "VARCHAR", "''::VARCHAR"),
    ],
}


def run_schema_migrations(state_db_conn, discovery_root: Path):
  """Always runs in Step 1 before Sweeping and Recovery (INGEST-CORE-017)."""
  current_version = state_db_conn.execute("PRAGMA user_version").fetchone()[0]

  if current_version < 1:
    state_db_conn.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_watermarks (
                source_type VARCHAR NOT NULL,
                file_path VARCHAR NOT NULL PRIMARY KEY,
                inode BIGINT NOT NULL DEFAULT 0,
                last_processed_offset BIGINT NOT NULL DEFAULT 0,
                last_processed_mtime DOUBLE NOT NULL,
                file_sha256 VARCHAR NOT NULL,
                proposal_id VARCHAR NOT NULL DEFAULT '',
                target_table VARCHAR NOT NULL DEFAULT 'concept_proposals',
                status VARCHAR NOT NULL,
                staging_tx_id VARCHAR NOT NULL,
                staging_tmp_path VARCHAR NOT NULL DEFAULT '',
                processed_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
    state_db_conn.execute("""
            CREATE TABLE IF NOT EXISTS promotion_journal (
                journal_id VARCHAR PRIMARY KEY,
                proposal_id VARCHAR NOT NULL,
                state VARCHAR NOT NULL,
                staged_files TEXT NOT NULL,
                target_paths TEXT NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
    state_db_conn.execute("PRAGMA user_version = 1;")
    current_version = 1

  if current_version < 2:
    state_db_conn.execute("""
            CREATE TABLE IF NOT EXISTS used_replay_nonces (
                nonce VARCHAR PRIMARY KEY,
                used_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
    state_db_conn.execute("PRAGMA user_version = 2;")

  if current_version < 3:
    # v0.5.2-RC: watermark/commit-split (§3.3). Historical migrations
    # (v1/v2) are append-only and MUST NOT be rewritten (E111); the split
    # is therefore implemented as an add-on step.
    state_db_conn.execute("""
            -- MUST be byte-equivalent in constraints to the canonical DDL in
            -- INGEST-ADAPTERS.md §3.3: the migration is the only path that creates
            -- this table on a fresh install, so omitting the CHECK constraints would
            -- remove the storage-layer safety net behind E114.
            CREATE TABLE IF NOT EXISTS commit_transactions (
                staging_tx_id VARCHAR PRIMARY KEY,
                proposal_id VARCHAR NOT NULL,
                input_sha256 VARCHAR NOT NULL,
                target_table VARCHAR NOT NULL CHECK (target_table IN (
                    'concept_proposals', 'ambiguous_scope', 'rejected_low_quality')),
                staging_tmp_path VARCHAR NOT NULL,
                status VARCHAR NOT NULL DEFAULT 'PENDING_COMMIT' CHECK (status IN (
                    'PENDING_COMMIT', 'COMMITTED', 'FAILED')),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
    # Migrate unfinished transactions out of the legacy watermark table.
    # `file_sha256` was used in v0.5.1 as identity hash; the field is retained as
    # best available value on upgrade (E111: no data loss).
    state_db_conn.execute("""
            INSERT OR IGNORE INTO commit_transactions (
                staging_tx_id, proposal_id, input_sha256, target_table,
                staging_tmp_path, status, created_at, updated_at)
            SELECT staging_tx_id, proposal_id, file_sha256, target_table,
                   staging_tmp_path, status, processed_at, processed_at
            FROM ingestion_watermarks
            WHERE staging_tx_id <> '' AND status IN (
                'PENDING_COMMIT', 'FAILED');
        """)
    state_db_conn.execute("PRAGMA user_version = 3;")

  # Reconcile Parquet
  for table_name in [
      "concept_proposals",
      "ambiguous_scope",
      "rejected_low_quality",
  ]:
    reconcile_parquet_schema(
        discovery_root / f"{table_name}.parquet",
        target_version="0.5.2",
        table_type=table_name,
    )

  version_file = discovery_root / "state" / "schema_version.json"
  version_file.parent.mkdir(parents=True, exist_ok=True)
  with open(version_file, "w") as f:
    json.dump(
        {
            "schema_version": "0.5.2",
            "sqlite_user_version": 3,
            "migrated_at": time.time(),
        },
        f,
        indent=2,
    )

```

---

### 7.3 TTL-Reaper (Deterministic Retention)

Retention (§7.1, INGEST-CORE-022 / E125) is enforced by a deterministic, idempotent reaper that executes in every poll cycle — **after** schema migration and DSCP recovery have completed (INGEST-CORE-017):

1. **Status transition:** an `UPDATE` statement in SQLite/DuckDB marks expired proposals: `status = 'expired'` where `expires_at < CURRENT_TIMESTAMP` AND `status = 'pending'`. Proposals with `status = 'approved'` are NOT included (a human decision has been made; they await promotion or explicit rejection).
2. **Cleanup with grace period:** rows with `status = 'expired'` are purged from the staging tables only after `reaper_grace_days` (default 7 d, §13), so that audit traceability is preserved during the grace period.
3. **Protected targets:** the reaper MUST NEVER touch rows with `promotion_status = 'staged'` that await DSCP commit, and it MUST NEVER delete canonical files (`personal/`, `engineering/`) — retention in the canonical graph is governed by wiki governance, not by the ingest engine (E103).
4. **Sanitized trajectories:** files under `discovery/trajectories/sanitized/` are purged path-exactly after `sanitized_audit_retention_days` (365 d, §13).

The reaper MUST log every transition via the Prometheus metric `wiki_ingest_rejections_total{reason="expired"}` (§10.2).

### 7.3.1 Review queue and degraded operation

The pending staging tables constitute one logical review queue even when they
are stored in separate compatibility tables. A queue listing MUST expose, at
minimum, proposal ID, status, created time, expiry time, scope status, quality
signals, source/representation references, and the reason for any rejection or
quarantine. Listing order MUST be deterministic and MUST make age visible.

The queue MUST support deterministic prioritisation by expiry urgency, then
creation time, then proposal ID; implementations MAY expose additional filters
but MUST NOT hide expired, rejected, quarantined, or failed items from the audit
view. Review capacity and queue state MUST be observable through counts by
status, oldest pending age, and transition/rejection counts. These are
observability signals, not conformance thresholds.

When review capacity is below incoming work, the implementation MUST enter an
explicit degraded mode rather than bypassing review: new proposals remain
staged, autonomous promotion is disabled, and capture remains non-invasive.
The mode and its reason MUST be recorded and surfaced to operators. Recovery
MUST drain the existing queue before normal promotion resumes; no proposal may
be silently discarded or auto-approved. Expiry, rejection, quarantine and
failed-promotion records remain auditable under the retention rules above.

**QUEUE-001**: Queue state, age and terminal/degraded outcomes MUST be
observable and reviewable; degraded mode MUST fail safe by stopping promotion,
not by weakening validation or approval. The review decision and promotion
semantics are owned by `REVIEW-PROMOTION.md`; this section owns only queue
operations and retention observability.

### 7.3.2 Passive Staleness & Knowledge Debt Metrics

The architecture is designed to operate in intermittent and session-based environments (e.g. local CLI, WSL2, developer laptops) as well as continuous environments. The system MUST NOT mandate a 24/7 background daemon or raise active liveness alarms simply due to elapsed wall-clock time between sessions.

Instead, the system enforces **passive staleness and backlog debt tracking**, surfaced to operators upon CLI invocation (`llm-wiki status`, `/query` banner):

1. **Passive Staleness Reporting:**
   ```yaml
   staleness:
     last_run:
       ingestion: "2026-09-01T10:00:00Z"
       extraction: "2026-09-04T22:00:00Z"
       promotion: null
     days_since_last_run: 2
   ```

2. **Knowledge Debt Metrics:**
   ```yaml
   knowledge_debt:
     pending_backlog_count: 42
     oldest_item_age_days: 5
     quarantined_count: 3
     extraction_failures: 2
   ```

3. **Staleness Expiry Warning:**
   When `oldest_item_age_days` approaches the configured staging TTL threshold ($\text{age} \ge \text{TTL} - 2\text{ days}$), the status report MUST issue a high-visibility warning to ensure human reviewers can triage high-value proposals before the automated reaper archives them as expired.

---

## 9. Durable Promotion Commit Protocol (DPCP)

When a proposal is approved via the command `wiki review promote <proposal_id>`, promotion executes under a **journaled state machine** (`INGEST-CORE-015`) to prevent partial states, concurrency conflicts, and race conditions:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. PREPARED                                                 │
│    - Acquire POSIX Advisory Exclusive Lock (flock) (§9.4.5) │
│    - Allocate canonical ID via File-Lock                    │
│    - Create Journal in SQLite: state = 'PREPARED'           │
├─────────────────────────────────────────────────────────────┤
│ 2. STAGED_WRITTEN                                           │
│    - Write Markdown files to .tmp_promo_<id>/ per           │
│      the promotion contract (§9.4)                          │
│    - SQLite: state = 'STAGED_WRITTEN'                       │
├─────────────────────────────────────────────────────────────┤
│ 3. LINTER_VALIDATED                                         │
│    - Execute linter.py (Layer 1–5) in-memory against tmp    │
│    - If Linter fails -> ROLLBACK (remove tmp, FAILED)       │
├─────────────────────────────────────────────────────────────┤
│ 4. CANONICAL_COMMITTED                                      │
│    - Atomic POSIX rename of files to canonical tree         │
│      (personal/ or engineering/)                            │
│    - SQLite: state = 'CANONICAL_COMMITTED'                  │
├─────────────────────────────────────────────────────────────┤
│ 5. DISCOVERY_UPDATED                                        │
│    - Update Discovery Parquet:                              │
│      status = 'approved', promotion_status = 'promoted'     │
│    - SQLite: state = 'COMPLETED'                            │
│    - Release flock Lock                                     │
└─────────────────────────────────────────────────────────────┘
```

### 9.1 Multi-Process Concurrency & OS-Level File Locking
1. **Canonical Mutex:** Any process (CLI `trashheap review promote` or `trashheap-sort`) mutating canonical files MUST acquire an OS-level exclusive advisory lock (`fcntl.flock(fd, fcntl.LOCK_EX)` or cross-platform equivalent) on `~/.trashheap/locks/canonical_promotion.lock` with a mandatory 10-second acquisition timeout.
2. **DuckDB Concurrency:** All CLI tools inspecting `discovery/*.parquet` (e.g. `wiki review list`) MUST open DuckDB connections with `read_only=True` to prevent write-lock collisions with the active `wiki-ingestd` daemon.
3. **Single-Writer Guarantee:** Only the designated daemon or the interactive review CLI holding the `canonical_promotion.lock` MAY write to canonical directories (`personal/` and `engineering/`).

### 9.2 DPCP Crash Recovery & Cleanup
* **Startup Orphan Sweep:** On daemon startup (Step 1 of `INGEST-CORE-017`), the process scans staging directory for dangling `.tmp_promo_*` folders older than 15 minutes and unlinks them.
* **Crash in Steps 1–3 (`PREPARED` / `STAGED_WRITTEN`):** The startup recovery reads SQLite journal, purges `.tmp_promo_*`, marks journal as `FAILED`, and logs `E124`. Canonical knowledge remains completely unaffected.
* **Crash in Step 4 (`CANONICAL_COMMITTED`):** Files have already been moved atomically. The next daemon startup inspects the journal and deterministically executes Step 5 (`DISCOVERY_UPDATED`) to bring DuckDB Parquet tables into consistency.
* **Lint Failure in Step 3:** The proposal remains in staging with `promotion_status = 'failed'` and `rejection_reason = 'INVALID_ONTOLOGY'` (returned to review queue); no canonical file is touched.

---

### 9.4 Canonical Promotion Contract (Staging → v3.8.10 Frontmatter)

Promotion MUST reproduce a complete v3.8.10 Knowledge Object (9 metadata categories, META-001) from the staged proposal. The mapping in this section is **normative** (INGEST-CORE-021 / E124); every deviation aborts DPCP before canonical writing (step 3, `LINTER_VALIDATED`).

#### 9.4.1 Epistemic Value-Space Mapping

The staging fields have their own value spaces (§4.2) that differ from the canonical epistemology (`EPISTEMOLOGY.md`). The following translation is binding:

| Staging field | Staging value | Canonical field | Canonical value |
| --- | --- | --- | --- |
| `validation_status` | `unverified` | `epistemology.verification` | `unverified` |
| `validation_status` | `tool_verified` | `epistemology.verification` | `self_verified` |
| `validation_status` | `peer_verified` | `epistemology.verification` | `peer_verified` |
| `evidence_bundle.files_modified` | `len > 0` | `epistemology.evidence` | `observed` |
| `evidence_bundle.files_modified` | `len == 0` | `epistemology.evidence` | `inferred` |
| — (autonomous synthesis) | — | `epistemology.authority` | `informative` |
| `epistemic_status` | `inferred` / `reviewed` | `consensus` | `proposed` |
| `epistemic_status` | `confirmed` with remark | `consensus` | `contested` (only on explicit disagreement) |

`authority` MUST NOT be set to `authoritative` on autonomous promotion; this requires separate human establishment (E121). Both consensus values are permitted for `status: draft` according to `governance_policy.yaml` (GOV-002).

#### 9.4.2 Governance & Lifecycle Mapping

| Canonical field | Value on promotion | Rationale |
| --- | --- | --- |
| `status` | `draft` | Administrative approval is not epistemic truth (E121). Upgrade to `established` requires a separate human process. |
| `consensus` | `proposed` (or `contested`) | See §9.4.1. |
| `validity.valid_from` | The trajectory's `start_time` (UTC date) | Timestamp of the empirical data. |
| `validity.valid_until` | `null` | No automatic expiry date for canonical objects. |
| `aliases` | Includes `proposal_id` (`DISC-PROP-…`) | Traceability staging → canonical graph. |

#### 9.4.3 Provenance Mapping

Canonical provenance requires fields that are missing from the staging `ProvenanceMetadata`; these are constructed deterministically on promotion:

| Canonical field | Source / Construction |
| --- | --- |
| `source_type` | `post_mortem` for root object `Incident`; `observation` for `Observation`, `Lesson`, `Workflow` (values from `SourceTypeEnum`, `linter.py`). |
| `source_refs` | Ordered source and representation references retained from the sanitized trajectory and its lineage envelope. |
| `representation_refs` | Representation IDs for the captured inputs used by the proposal. |
| `confidence` | `model_confidence`, rounded to 2 decimals. |
| `last_verified` | Promotion date (UTC, `YYYY-MM-DD`). |
| `next_review` | Promotion date + 90 days. |
| `reviewer` | `wiki-ingestd` (autonomous promotion; human reviewer required for `established`). |

#### 9.4.4 Taxonomy, Facets & Scope

* **Taxonomy:** The extraction prompt MUST present the inferred scope's taxonomy tree (`taxonomy_registry.yaml`) and require exactly one `inferred_taxonomy_id` from the model. On promotion the value is validated against the registry (existence + scope match). If the value is missing or invalid, a deterministic fallback is used: `personal` ⇒ `TX-PERS-10`, `engineering` ⇒ `TX-ENG-06`. `taxonomy_path` is derived from the registry so that `taxonomy_path + scope` yields a deterministic disk path (TAX-002).
* **Facets:** On promotion `inferred_facets` MUST satisfy `object_registry.yaml` `required_facets` for the respective object type: `Incident` ⇒ `toolchain` + `lifecycle`; `Observation` ⇒ `toolchain`; `Lesson` ⇒ `toolchain` + `language`; `Workflow` ⇒ `toolchain` + `audience` (FAC-001). Linter E020/E021 is the final arbiter; rejection yields `INVALID_ONTOLOGY` per DPCP step 3.
* **Scope:** `inferred_scope` MUST be `personal` or `engineering`; ambiguous proposals cannot be promoted (§9.5). The root object type follows the scope-conditional triad (E104).

#### 9.4.5 Canonical ID Allocation

The ID format follows `DATA_MODEL.md` §6: `(PERS|ENG)-<KOD>-<TAGG>-<SEKVENS>` (e.g. `ENG-INC-2026-0042`, `PERS-OBS-2026-0007`, `PERS-WFL-AGY-0003`).

1. **Sequence space:** `(scope, object_type, tagg)` where tag = year (`YEAR_TAG`) for `Incident`/`Observation`/`Lesson` and domain for `Workflow` (per `object_registry.yaml` `tag_strategy`). The maximum sequence is 9999 per sequence space.
2. **Lock:** `~/.trashheap/locks/id_alloc.json` is created with `O_CREAT | O_EXCL` and the fsync sequence (§3.2). Contents: `{namespace, next_seq, pid, acquired_at}`. Unlocking happens via `os.replace` to an empty file followed by `unlink`.
3. **Allocation:** `next_seq = max(lock counter, scanned maximum among existing canonical objects in the sequence space) + 1`. The scan captures manually created objects and prevents collision (ID-004).
4. **Error:** exhausted sequence space, lock failure or invalid format ⇒ E124 and DPCP rollback. Linter E001 (global ID uniqueness) remains the last line of defense.

#### 9.4.6 Relations

Promoted objects MUST be linked according to `relation_registry.yaml` (REL-005):

| Triad | Relation | Registry support |
| --- | --- | --- |
| Engineering | `Lesson` → `Incident` | `DERIVED_FROM` |
| Engineering | `Lesson` → `Workflow` | `IMPLEMENTED_AS` |
| Personal | `Lesson` → `Observation` | `DERIVED_FROM` |
| Personal | `Lesson` → `Workflow` | `IMPLEMENTED_AS` |

Additional relations to existing canonical objects are only permitted within the same scope, or when `cross_scope: true` (E105) has been explicitly set and reviewed. Targets are resolved by canonical ID; dangling references are caught by linter E009 (BrokenLinkError). `APPLIES_TO` (`Workflow` → engineering domain objects) is only permitted within engineering scope.

---

### 9.5 CLI Contract (`wiki review`)

| Command | Semantics |
| --- | --- |
| `wiki review list [--scope <scope>] [--status <status>]` | Deterministic list (RET-001 order). |
| `wiki review show <proposal_id>` | Show bundle, evidence and provenance. |
| `wiki review approve <proposal_id>` | `status: pending → approved`. |
| `wiki review reject <proposal_id> --reason "<text>"` | `status: pending → rejected`; archived to `rejected_low_quality.parquet`. |
| `wiki review reclassify <proposal_id> --scope <personal\|engineering>` | Manual scope determination: `scope_status → reviewed`. |
| `wiki review promote <proposal_id>` | Executes DPCP (§9) under the contract §9.4. |

**Promotion preconditions (fail-closed):** `status = approved` AND `inferred_scope ∈ {personal, engineering}` AND `scope_status ∈ {confirmed, reviewed}`. Ambiguous proposals and proposals with only LLM-inferred scope (`scope_status = inferred`) MUST first be reclassified via `wiki review reclassify` (or confirmed via governance) before promotion is permitted.

---

## 10. Observability, Metrics & Replay Engine

### 10.1 Rate-Limiting (Token Bucket)

The daemon applies a Token Bucket algorithm configured via `rate_limit_per_minute` (default: 10 extractions/min, burst: 15).

### 10.2 Prometheus Metrics

* `wiki_ingest_processed_trajectories_total{source, status}`
* `wiki_ingest_quality_score_distribution` (Histogram over $Q_{\text{composite}}$)
* `wiki_ingest_rejections_total{reason}` (`low_confidence`, `low_quality`, `ambiguous_scope`, `sanitization_uncertain`, `expired`)
* `wiki_ingest_sanitization_redactions_total{tier}`

### 10.3 Secure Replay Engine with Nonce & HMAC (`INGEST-CORE-010`)

* **Key source:** `~/.trashheap/secrets/replay_hmac.key` (`0600`).
* **Payload:** $\text{HMAC-SHA256}(K, \; \text{repo\_path} \parallel \text{timestamp} \parallel \text{nonce})$.
* **Anti-Replay Nonce:** 128-bit random nonce with 15-minute TTL, stored in `used_replay_nonces`.

---

---

**End of LLM Wiki Ingestion Discovery Staging & Promotion Specification v0.5.2-RC**

See also: `INGEST.md` (core specification and INGEST-CORE invariants).