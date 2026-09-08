# LLM Wiki Ingestion Source Adapters & Commit Protocol Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-INGEST-ADAPTERS-001`
> **Document family ID**: `LLM-WIKI-INGEST-SPEC-001`
> **Version**: `v0.5.2-RC` (Production-Hardening Candidate)
> **Updated**: `2026-08-17`
> **Source**: Extracted from `LLM-WIKI-INGEST-SPEC-001` §3
> **Status**: `DRAFT`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Compatibility target**: Additive, non-invasive, opt-in
> **System documents**: `INGEST.md` (core) · `INGEST-ADAPTERS.md` (§3) · `INGEST-PIPELINE.md` (§4–§6) · `INGEST-STAGING.md` (§7, §9–§10) · `INGEST-DATA-MODEL.md` (§11, §13)
> **Normative owner**: This document owns connector/adapter contracts, cursors, completion signals and DSCP source-commit semantics
> **Related documents**: `UNIVERSAL-SOURCE-EXTENSION.md`, `INGEST-PIPELINE.md`, `INGEST-STAGING.md`, `INGEST-DATA-MODEL.md`

---

## 3. Source Adapters, Filesystem Matrix & DSCP Protocol

### 3.1 Versioned Source Adapters & Inode-Safe Cursors

The adapter contract is universal at the boundary:

```text
External system → Connector → Adapter → Normalized Source Record
                                      → validation/hash/provenance/staging
```

Connectors acquire access; adapters normalize source-specific payloads; the
ingestion core validates, hashes and stages. Adapters MUST NOT write canonical
Knowledge Objects. The contract covers files, directories, globs, archives,
URLs, URL lists, stdin, batches, repositories, databases/API connectors,
mailboxes, calendars and chat workspaces. Connector-specific schemas remain
separate adapter specifications.

Each source adapter declares strict allowlists for fields as well as contracts for completion events. Cursor tracking in SQLite handles file rotation and truncation by binding the offset to the file's `inode`, `file_sha256` and `mtime`.

**Inode Recycling Defense (D107):** On Linux filesystems, inodes can be rapidly recycled upon unlinking and recreating files. A cursor implementation relying solely on `(st_dev, st_ino)` is vulnerable to false offset hits when a file is replaced by another with the same inode number. To eliminate false offset hits across recycled inodes, the cursor verification routine (`CursorStore.check_and_read_new_bytes`) MUST verify that the SHA-256 hash of the content prefix up to `byte_offset` matches the recorded `file_sha256`. If the prefix hash mismatches, or if `curr_size < cursor.byte_offset`, the file MUST be treated as rotated or truncated, resetting `start_offset` to 0.

The adapter boundary is source-agnostic: `Connector` acquires an external
representation, `Adapter` normalizes it into a Source Record, and the ingestion
core validates, hashes, records provenance and stages it. An adapter MUST NOT
write canonical Knowledge Objects directly. Trajectory adapters remain supported
specializations under `source_registry.yaml`, not the universal input model.

```yaml
# ~/.trashheap/adapters/claude_code.yaml
adapter_contract:
  adapter_id: "claude_code"
  contract_version: "1.2.0"
  supported_runtime_versions: ["0.2.x", "0.3.x", "0.4.x", "0.5.x"]
  source_format: "jsonl"
  completion_signal: {"field": "type", "value": "session_finish"}
  cursor_strategy: "inode_byte_offset"
  allowed_event_fields:
    - "type"
    - "timestamp"
    - "session_id"
    - "tool_name"
    - "tool_input"
    - "tool_output"
    - "exit_code"
    - "files_modified"
  forbidden_reasoning_fields:
    - "thought"
    - "internal_cot"
    - "extended_thinking"
    - "private_deliberation"
  fail_closed_on_unknown_field: true

```

| Agent / Environment | Default resource | Format | Completion indicator | Private Reasoning field |
| --- | --- | --- | --- | --- |
| Kiro CLI | `~/.kiro/sessions/*.jsonl` | JSONL (v1) | `status: "completed"` / inactivity $> 15$ s | `thought`, `reasoning` |
| Mistral Vibe | `~/.vibe/logs/*.jsonl` | JSONL / OTLP | Completion event `session_end` / trace OK | `internal_reasoning` |
| OpenCode CLI | `~/.config/opencode/opencode.db` | SQLite (`mode=ro`) | `sessions.finished_at IS NOT NULL` | `reasoning_trace` |
| Google Antigravity (`agy`) | `~/.antigravity/sessions/*.json` | JSON (v1) | `task_state: "SUCCESS"` / file lock released | `thought` |
| Claude Code | `~/.claude/sessions/*.jsonl` | JSONL (v1) | Event type `type: "session_finish"` | `thought`, `extended_thinking` |
| SWE-agent | `trajectories/**/*.json` | JSON (v1) | File write in `trajectories/` complete | `internal_thought` |

**Precedence (v0.5.2-RC):** The adapter's `fail_closed_on_unknown_field` refers to unknown *event fields* in the raw file and quarantines the entire Trajectory (E102A). The sanitizer's fail-closed rules (§6, E102) thereafter apply to unknown *payload fields* in allowed events. A Trajectory rejected at the adapter level never reaches the sanitizer.

**`GENERIC_OTEL`:** The `generic_otel` source (`AgentSourceEnum`, §11) still lacks an adapter contract — path and field profile are undefined. The source IS DISABLED until a contract has been specified per the template above (fail-closed, E101/E102).

---

### 3.2 Filesystem Matrix: Visibility vs Durability

| Filesystem / Environment | `O_CREAT|O_EXCL` | Atomic Visibility (`os.replace`) | Crash Durability (`fsync` sequence) | Support status |
| --- | --- | --- | --- | --- |
| Linux Native (ext4 / XFS / Btrfs) | Full | Full | Full | Production (Tier 1) |
| WSL2 Native VHDX (`/home/...`) | Full | Full | Full | Production (Tier 1) |
| WSL2 DrvFs (`/mnt/c/...`) | Emulated | Not guaranteed atomic | Limited | Degraded (Tier 2) |
| NFS / SMB / CIFS / Cloud sync | Unreliable | Absent | Absent | Not Supported (Unsupported) |

**Filesystem sequence for Crash Durability:**


$$\text{write}(\text{temp}) \rightarrow \text{fsync}(\text{temp}) \rightarrow \text{close}(\text{temp}) \rightarrow \text{os.replace}(\text{temp}, \text{target}) \rightarrow \text{fsync}(\text{parent\_dir})$$

**Runtime Durability Tier Detection (D107):**
Implementations MUST inspect the host environment (`inspect_environment`) to determine the active durability tier before performing atomic publication or staging commits:
- **Tier 1 (Production):** Linux Native (ext4, XFS, Btrfs) or macOS (APFS) where `os.replace` guarantees atomic directory/file replacement and POSIX `fsync` ensures on-disk crash durability.
- **Tier 2 (Degraded):** WSL2 DrvFs cross-boundary mounts (e.g. `/mnt/c/`, `/mnt/d/`), where Windows NTFS semantics are translated through 9P/Plan9 or virtio-fs. Atomic replacement is not guaranteed across processes, and file locks are emulated. The system MUST report Degraded status in system diagnostics.
- **Unsupported:** Network filesystems (NFS, SMB, CIFS) or cloud synchronization folders lacking POSIX atomicity.
The runtime MUST report its durability tier truthfully and MUST NOT claim full Tier 1 production guarantees when operating on Tier 2 or unsupported mounts.

---

### 3.3 Durable Staged Commit Protocol (DSCP) & Deduplication

A staged proposal is deterministically identified by the identity tuple:


$$I = (\text{proposal\_id}, \text{input\_sha256}, \text{target\_table})$$

```python
from dataclasses import dataclass
from pathlib import Path
import duckdb


@dataclass(frozen=True)
class CommitIdentity:
  proposal_id: str
  input_sha256: str
  target_table: str


class DSCPIntegrityError(Exception):
  """Raised if the same identity has different data content (E114)."""

  pass

```

```text
               ┌──────────────────────────────┐
               │        PREPARE PHASE         │
               │ Write .tmp_proposals_<tx_id> │
               │ SQLite: PENDING_COMMIT       │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │       COMMITTER QUEUE        │
               │ Multi-Target Serial Commits  │
               └──────────────┬───────────────┘
                              │
                    ┌─────────┴─────────┐
          Success   ▼                   ▼   Crash / Power Loss
┌──────────────────────────────┐ ┌──────────────────────────────┐
│        COMMITTED             │ │        RECOVERY PHASE        │
│ Deduplicate -> os.replace    │ │ Scan SQLite: PENDING_COMMIT  │
│ SQLite: COMMITTED            │ │ Check Target via Tuple (I)   │
│ Unlink tmp file              │ └──────────────┬───────────────┘
└──────────────────────────────┘                │
                                       ┌────────┴────────┐
                        Found in Target│                 │ Missing in Target
                                       ▼                 ▼
                               ┌───────────────┐ ┌───────────────┐
                               │ Mark COMMITTED│ │ Check tmp_path│
                               │ Unlink orphan │ └───┬───────┬───┘
                               └───────────────┘     │       │
                                        File Exists  ▼       ▼ File Missing
                                        ┌───────────────┐ ┌───────────────┐
                                        │ Execute Merge │ │ Mark FAILED   │
                                        │ Mark COMMITTED│ │ Re-queue Traj │
                                        └───────────────┘ └───────────────┘

```

#### SQLite State Database (`~/.trashheap/ingest_state.db`)

**Watermark/Commit split (v0.5.2-RC):** In v0.5.1, *cursor state* (one row per source file) and *commit transactions* (one row per staged proposal) were mixed in the same table, with `file_path` as the primary key. A single source file can give rise to multiple proposals (e.g. a JSONL file with multiple sessions), whereby the second proposal's transaction state overwrote the first — a DSCP recovery corruption. The tables are therefore separated:

```sql
-- Cursor state: one row per source file (no proposal-bound state).
CREATE TABLE IF NOT EXISTS ingestion_watermarks (
    source_type VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL PRIMARY KEY,
    inode BIGINT NOT NULL DEFAULT 0,
    last_processed_offset BIGINT NOT NULL DEFAULT 0,
    last_processed_mtime DOUBLE NOT NULL,
    file_sha256 VARCHAR NOT NULL,          -- the source file's hash (cursor integrity)
    processed_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Commit transactions: one row per staged proposal (DSCP state machine).
-- NOTE: `input_sha256` is the CANONICAL trajectory hash (E109), NOT
-- the source file's hash — recovery must match against committed rows in the target.
CREATE TABLE IF NOT EXISTS commit_transactions (
    staging_tx_id VARCHAR PRIMARY KEY,
    proposal_id VARCHAR NOT NULL,
    input_sha256 VARCHAR NOT NULL,         -- canonical E109 hash
    target_table VARCHAR NOT NULL CHECK (target_table IN (
        'concept_proposals', 'ambiguous_scope', 'rejected_low_quality')),
    staging_tmp_path VARCHAR NOT NULL,
    status VARCHAR NOT NULL CHECK (status IN (
        'PENDING_COMMIT', 'COMMITTED', 'FAILED')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

```

#### Idempotent Committer with Deduplication

**SQL safety (v0.5.2-RC, C3):** All query bindings for *values* (`proposal_id`, `input_sha256`) are parameterized. File paths cannot be bound as parameters in DuckDB's table functions and are therefore validated fail-closed against a strict character allowlist before they are interpolated (the threat model §8 includes corrupt/manipulated state data).

```python
import os
import re

_SAFE_PATH_RE = re.compile(r"^[A-Za-z0-9_./~-]+$")


def _validated_sql_path(path: Path) -> str:
  """Fail-closed path validation before interpolation into DuckDB SQL (E114)."""
  s = str(path)
  if not _SAFE_PATH_RE.match(s) or ".." in Path(s).parts:
    raise DSCPIntegrityError(
        f"Disallowed path in DSCP operation: {s!r} [E114]"
    )
  return s


def commit_staged_parquet(
    target_path: Path, tmp_path: Path, identity: CommitIdentity
):
  """Deduplicates and merges temporary Parquet data into the target table under DSCP."""
  target_sql = _validated_sql_path(target_path)
  tmp_sql = _validated_sql_path(tmp_path)
  temp_target = (
      target_path.parent
      / f".tmp_commit_{target_path.stem}_{identity.proposal_id}.parquet"
  )
  temp_target_sql = _validated_sql_path(temp_target)

  # 1. Check whether the identity already exists in the target table
  #    (parameterized binding; deterministic LIMIT 1).
  existing_check = []
  if target_path.exists():
    existing_check = duckdb.sql(
        f"""
        SELECT proposal_id, input_sha256
        FROM parquet_scan('{target_sql}')
        WHERE proposal_id = ?
        ORDER BY proposal_id
        LIMIT 1
        """,
        params=[identity.proposal_id],
    ).fetchall()

  if existing_check:
    existing_sha = existing_check[0][1]
    if existing_sha == identity.input_sha256:
      # Exact same identity and content -> No-op idempotency
      _safe_delete(tmp_path)
      return
    else:
      raise DSCPIntegrityError(
          f"Identity collision for proposal_id '{identity.proposal_id}' "
          f"with divergent hash: existing={existing_sha}, new={identity.input_sha256}. [E114]"
      )

  # 2. Bootstrap: if the target file is missing (first commit) it is created empty with
  #    the tmp file's schema, so that parquet_scan below never lacks a file.
  if not target_path.exists():
    duckdb.sql(f"""
        COPY (
            SELECT * FROM parquet_scan('{tmp_sql}') WHERE FALSE
        ) TO '{target_sql}' (FORMAT PARQUET)
    """)

  # 3. Perform atomic merge via DuckDB. Deduplication is guaranteed by
  #    the existence check in step 1 — UNION ALL does NOT deduplicate by itself.
  duckdb.sql(f"""
        COPY (
            SELECT * FROM parquet_scan('{target_sql}')
            UNION ALL BY NAME
            SELECT * FROM parquet_scan('{tmp_sql}')
        ) TO '{temp_target_sql}' (FORMAT PARQUET)
    """)

  # 4. Crash-durable commit (fsync sequence per §3.2)
  with open(temp_target, "rb") as f:
    os.fsync(f.fileno())
  os.replace(temp_target, target_path)

  parent_fd = os.open(str(target_path.parent), os.O_RDONLY)
  try:
    os.fsync(parent_fd)
  finally:
    os.close(parent_fd)

  _safe_delete(tmp_path)

```

#### Deterministic DSCP Recovery

```python
def recover_pending_dscp_transactions(state_db_conn, discovery_root: Path):
  """Executed in Step 2 after schema migration has been verified (INGEST-CORE-017).

  v0.5.2-RC: reads from `commit_transactions` (not the watermark table),
  uses the CANONICAL `input_sha256` for identity matching, is
  fail-closed on unknown `target_table`, and binds values parameterized.
  """
  target_map = {
      "concept_proposals": discovery_root / "concept_proposals.parquet",
      "ambiguous_scope": discovery_root / "ambiguous_scope.parquet",
      "rejected_low_quality": discovery_root / "rejected_low_quality.parquet",
  }

  cursor = state_db_conn.execute("""
        SELECT staging_tx_id, staging_tmp_path, target_table,
               input_sha256, proposal_id
        FROM commit_transactions
        WHERE status = 'PENDING_COMMIT'
        ORDER BY created_at
    """)
  pending_rows = cursor.fetchall()

  for tx_id, tmp_path_str, target_table, input_sha256, proposal_id in pending_rows:
    # FAIL-CLOSED: a silent fallback to concept_proposals on an unknown table
    # could route corrupt data to the wrong target. This is an
    # integrity violation (E114), not a recoverable state.
    target_path = target_map.get(target_table)
    if target_path is None:
      raise DSCPIntegrityError(
          f"Unknown target_table '{target_table}' in commit_transactions"
          f" (staging_tx_id={tx_id}). [E114]"
      )
    tmp_path = Path(tmp_path_str)
    identity = CommitIdentity(
        proposal_id=proposal_id,
        input_sha256=input_sha256,  # canonical E109 hash, not the source file's
        target_table=target_table,
    )

    already_committed = False
    if target_path.exists():
      target_sql = _validated_sql_path(target_path)
      res = duckdb.sql(
          f"""
                SELECT COUNT(*) FROM parquet_scan('{target_sql}')
                WHERE proposal_id = ? AND input_sha256 = ?
            """,
          params=[identity.proposal_id, identity.input_sha256],
      ).fetchone()
      if res and res[0] > 0:
        already_committed = True

    if already_committed:
      # CP-4 / CP-5 Recovery
      if tmp_path.exists():
        tmp_path.unlink(missing_ok=True)
      state_db_conn.execute(
          "UPDATE commit_transactions SET status='COMMITTED',"
          " updated_at=CURRENT_TIMESTAMP WHERE staging_tx_id=?",
          (tx_id,),
      )
    elif tmp_path.exists():
      # CP-2 / CP-3 Recovery
      commit_staged_parquet(target_path, tmp_path, identity)
      state_db_conn.execute(
          "UPDATE commit_transactions SET status='COMMITTED',"
          " updated_at=CURRENT_TIMESTAMP WHERE staging_tx_id=?",
          (tx_id,),
      )
    else:
      # CP-1 Recovery
      state_db_conn.execute(
          "UPDATE commit_transactions SET status='FAILED',"
          " updated_at=CURRENT_TIMESTAMP WHERE staging_tx_id=?",
          (tx_id,),
      )

```

---

### 3.4 Cross-FS Daemon Singleton & Start-Time Validation

```python
import json
import os
from pathlib import Path
import time


class DaemonAlreadyRunningError(Exception):
  pass


def get_process_start_time(pid: int) -> float:
  """Reads the process start time from Linux /proc. Returns 0.0 on macOS/BSD/Windows."""
  stat_path = Path(f"/proc/{pid}/stat")
  if stat_path.exists():
    try:
      with open(stat_path, "r") as f:
        fields = f.read().split()
        return float(fields[21])
    except Exception:
      pass
  return 0.0


def acquire_daemon_singleton(
    pid_file_path: Path,
    stale_lock_ttl_seconds: float = 300.0,
) -> dict:
  """Acquires the daemon singleton via O_CREAT|O_EXCL (INGEST-CORE-014).

  v0.5.2-RC: `stale_lock_ttl_seconds` (§13) is now implemented — it is
  the ONLY protection against false positives in conservative mode, where
  PID reuse cannot be detected via /proc. The pidfile is fsynced
  per §3.2 before visibility.
  """
  pid_file_path.parent.mkdir(parents=True, exist_ok=True)
  current_pid = os.getpid()
  current_start_time = get_process_start_time(current_pid)
  capability_mode = (
      "linux_proc_verified" if current_start_time > 0.0 else "conservative_pid"
  )

  lock_payload = {
      "pid": current_pid,
      "start_time": current_start_time,
      "capability_mode": capability_mode,
      "created_at": time.time(),
      "daemon_name": "wiki-ingestd",
  }

  try:
    fd = os.open(pid_file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, "w") as f:
      json.dump(lock_payload, f)
      f.flush()
      os.fsync(f.fileno())  # Crash durability (§3.2) before visibility
    return lock_payload

  except FileExistsError:
    try:
      with open(pid_file_path, "r") as f:
        data = json.load(f)
      existing_pid = int(data.get("pid", 0))
      expected_start_time = float(data.get("start_time", 0.0))
      lock_created_at = float(data.get("created_at", 0.0))
    except (ValueError, OSError, json.JSONDecodeError):
      # Corrupt or unreadable pidfile -> fail-closed retry
      pid_file_path.unlink(missing_ok=True)
      return acquire_daemon_singleton(pid_file_path, stale_lock_ttl_seconds)

    try:
      os.kill(existing_pid, 0)
    except ProcessLookupError:
      # The process does not exist -> stale lock
      pid_file_path.unlink(missing_ok=True)
      return acquire_daemon_singleton(pid_file_path, stale_lock_ttl_seconds)
    except PermissionError:
      raise DaemonAlreadyRunningError(
          f"PID {existing_pid} is running under a different user. Daemon locked. [E116]"
      )

    actual_start_time = get_process_start_time(existing_pid)
    if expected_start_time > 0.0 and actual_start_time > 0.0:
      if actual_start_time != expected_start_time:
        # The OS has reused the same PID after a previous crash -> stale lock
        pid_file_path.unlink(missing_ok=True)
        return acquire_daemon_singleton(pid_file_path, stale_lock_ttl_seconds)
    else:
      # Conservative mode (WSL2/DrvFs, macOS, Windows): start time cannot
      # be verified and PID reuse cannot be ruled out.
      # stale_lock_ttl_seconds is the only protection against false positives.
      lock_age = time.time() - lock_created_at
      if lock_created_at > 0.0 and lock_age > stale_lock_ttl_seconds:
        pid_file_path.unlink(missing_ok=True)
        return acquire_daemon_singleton(pid_file_path, stale_lock_ttl_seconds)

    raise DaemonAlreadyRunningError(
        f"wiki-ingestd is already actively running (PID {existing_pid}, mode:"
        f" {capability_mode}). [E116]"
    )

```

```

---

### 3.8 Streaming XML Adapter & Ingestion Memory Invariance (ADA-008)

Large structured corpus ingestion (such as multi-gigabyte XML baselines e.g. PubMed/MeSH) poses severe out-of-memory risks if parsed into monolithic in-memory DOM trees.

1. **Streaming Iterator & Sibling Clearing (ADA-008):**
   - High-throughput XML adapters MUST utilize incremental streaming parsers (e.g. `lxml.etree.iterparse` or SAX) rather than monolithic DOM loaders (`lxml.etree.parse`).
   - After processing each atomic record element (e.g. `<PubmedArticle>`), the adapter MUST explicitly clear the element (`elem.clear()`) and remove previous siblings from its parent (`while elem.getprevious() is not None: del elem.getparent()[0]`).
   - Memory footprint across multi-gigabyte ingestion SHALL remain $O(1)$ flat RSS ($< 250$ MB).
2. **Deterministic Metadata Ingestion (Zero-LLM Pipeline):**
   - Structured identifiers (PMID, DOI), human-curated classifications (MeSH tree numbers, descriptors), author lists, and explicit citations (`<ReferenceList>`) MUST be mapped directly to canonical or candidate records without invoking LLM inference.
   - Retraction and errata notices (`<CommentsCorrectionsList>`) SHALL be deterministically mapped to `SUPERSEDES` or `INVALIDATED_BY` epistemic relations.
3. **Conclusion & Findings Section Preservation:**
   - Text extractors for structured abstracts MUST preserve section labels (`BACKGROUND`, `METHODS`, `RESULTS`, `CONCLUSIONS`) and guarantee that concluding paragraphs and epistemic hedges are preserved intact without naive character truncations.

---

**End of LLM Wiki Ingestion Source Adapters & Commit Protocol Specification v0.5.2-RC**

See also: `INGEST.md` (core specification and INGEST-CORE invariants).