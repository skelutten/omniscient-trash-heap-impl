# LLM Wiki Trajectory Ingestion Engine Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-INGEST-001`
> **Document family ID**: `LLM-WIKI-INGEST-SPEC-001`
> **Version**: `v0.5.2-RC` (Production-Hardening Candidate)
> **Updated**: `2026-08-17`
> **Source**: Extracted from `LLM-WIKI-INGEST-SPEC-001` §1–§2, §8, §12
> **Status**: `DRAFT`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Compatibility target**: Additive, non-invasive, opt-in

> **Universal Source extension:** The generic input abstraction is a normalized
> Source Record. The current trajectory engine remains an opt-in specialization;
> see `UNIVERSAL-SOURCE-EXTENSION.md`. This does not alter the DSCP contract.
> **Normative owner**: This document owns the trajectory ingestion specialization, sanitizer, Evidence Bundle and ingestion invariants
> **Related documents**: `UNIVERSAL-SOURCE-EXTENSION.md`, `INGEST-ADAPTERS.md`, `INGEST-PIPELINE.md`, `INGEST-STAGING.md`
> **System documents**: `INGEST.md` (core) · `INGEST-ADAPTERS.md` (§3) · `INGEST-PIPELINE.md` (§4–§6) · `INGEST-STAGING.md` (§7, §9–§10) · `INGEST-DATA-MODEL.md` (§11, §13)

> **Document revision v0.5.2-RC (2026-08-16) — Review-Hardening.** Addresses review findings: (1) scope-conditioned ontological triad so that `personal` trajectories never require the ENGINEERING_ONLY-typed `Incident` object (C1), (2) normative promotion contract for staging→canonical frontmatter mapping (C2), (3) parameterized SQL in DSCP/recovery (C3), (4) clarified E120 firewall (C4), (5) deterministic identity hardening against naive datetimes and NFC key collisions (C5), plus watermark/commit split, singleton TTL, TTL reaper and CLI contract.

---

## 1. Purpose, Scope & Epistemic Pipeline

This document constitutes the complete, self-contained specification for the **Multi-Agent Trajectory Ingestion & Extraction Engine (`wiki-ingest`) v0.5.2-RC**.

The engine functions as an asynchronous, non-invasive harvesting layer (*harvesting layer*) on top of external LLM agent runtimes (Kiro CLI, Mistral Vibe, OpenCode CLI, Google Antigravity `agy`, Claude Code, SWE-agent, and others). It captures completed agent trajectories, sanitizes sensitive data and PII via a fail-closed redaction pipeline, strips private reasoning data via field allowlists, derives an immutable **Evidence Bundle** deterministically *before* the LLM call, classifies scope via

This trajectory engine is a specialized Event ingestion path under the
Universal Source Model. It MUST NOT be interpreted as the general source
abstraction. Non-trajectory inputs use the same normalized Source Record
boundary and the same deterministic validation/staging principles, while this
 document retains the trajectory-specific sanitizer and DSCP/DPCP contracts.
The trajectory path then uses a version-bound cascade and extracts knowledge
candidates into the **scope-conditioned ontological triad** (engineering: **Incident $\rightarrow$ Lesson $\rightarrow$ Workflow**; personal: **Observation $\rightarrow$ Lesson $\rightarrow$ Workflow**, because `Incident` is ENGINEERING_ONLY per ID-005 in `object_registry.yaml`), and stages and promotes Knowledge Objects under strict transaction protocols (**DSCP** and **DPCP**).

```text
                    OBSERVATION (External Agents)
                                 │
                                 ▼
                  SANITIZED TRAJECTORY (Fail-Closed)
                                 │
                                 │ Deterministic NFC UTF-8 Hashing (E109)
                                 ▼
                    EVIDENCE BUNDLE (Pre-LLM)
                                 │
                                 │ Deterministic Scope + Isolated LLM Extraction (E120)
                                 ▼
                   DISCOVERY PROPOSAL (Staging)
                                 │
                                 │ Human Governance & DPCP Protocol (E117)
                                 ▼
                    CANONICAL KNOWLEDGE GRAPH

```

> **Epistemic Founding Principle:** *Governance approval establishes admissibility into the canonical knowledge graph; it does not convert an inferred claim into objective truth.* Administrative approval and epistemic certainty are kept strictly separate in all data models and lifecycle transitions.

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 EXTERNAL AGENT RUNTIMES                                 │
│    [Kiro CLI]          [Mistral Vibe]          [OpenCode CLI]       [Google agy / Claude]│
│    (~/.kiro/)           (~/.vibe/)          (~/.config/opencode/)     (~/.claude/)      │
└─────────┬───────────────────┬────────────────────────┬─────────────────────────┬────────┘
          │                   │                        │                         │
          ▼                   ▼                        ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                       MULTI-AGENT INGESTION DAEMON (wiki-ingestd)                       │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 0. PROCESS-IDENTITY SINGLETON & CROSS-FS LOCK (§3.4, E116)                        │  │
│  │    O_CREAT|O_EXCL + Linux /proc start_time validering / Conservative Mode         │  │
│  ├───────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 1. DUAL DECLARATIVE SCHEMA RECONCILIATION & BACKFILL ENGINE (§7.2, E119)          │  │
│ │    PRAGMA user_version + Parameterized Backfill + NULL Audit before Sweeper        │  │
│  ├───────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 2. READ-ONLY ADAPTERS, INODE-AWARE CURSORS & PATH-EXACT SWEEPER (§3.1-§3.2, E101)  │  │
│  │    Fail-Closed Schema + Mode=RO + Inode/Mtime/Offset Tracking                     │  │
│  ├───────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 3. FAIL-CLOSED SANITIZATION & PRIVATE REASONING ALLOWLIST (§6, E102, E102A)       │  │
│  │    Field Allowlist + Linear Bounded DFA Regex + High-Entropy Quarantine           │  │
│  ├───────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 4. RECURSIVE NFC CANONICAL SERIALIZATION & INPUT HASH (§6.1, E109)                │  │
│  │    NormalizedTrajectoryDraft -> Canonical UTF-8 JSON -> input_sha256              │  │
│  ├───────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 5. DETERMINISTIC EVIDENCE BUNDLE BUILDER (PRE-LLM) (§5.1, E118)                   │  │
│  │    Deterministic extraction of files_modified, exit_codes, derived_at            │   │
│  ├───────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 6. VERSION-BOUND SCOPE ROUTER (§4, E105, E110)                                    │  │
│  │    ScopeKey(input_sha256, policy_v, tax_v) -> Repo Anchors -> Rules -> LLM        │  │
│  ├───────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 7. ZERO-SIDE-EFFECT EXTRACTION & COMPOSITE QUALITY GATE (§5.2, E108, E120)        │  │
│ │   Conf_model >= 0.75 & Q_composite >= 0.70 (where Q_det >= 0.45) -> Proposal     │  │
│  ├───────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 8. SERIALIZED MULTI-TARGET COMMITER & IDEMPOTENT DSCP (§3.3, E114, E115)          │  │
│  │    CommitIdentity(proposal_id, input_sha256, target_table) + Deduplication       │  │
│  ├───────────────────────────────────────────────────────────────────────────────────┤  │
│  │ 9. DURABLE PROMOTION COMMIT PROTOCOL (DPCP JOURNAL) (§9, E117, E124)              │  │
│  │    ID allocation + Promotion Contract (§9.4) + L1-5 Lint + Staged Write + Rollback│  │
│  └─────────────────────────────────────┬─────────────────────────────────────────────┘  │
└────────────────────────────────────────┼────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                       DISCOVERY GRAPH STAGING LAYER (§7)                                │
│    discovery/concept_proposals.parquet   (status: pending, TTL: 90 d, Invariant E108)   │
│    discovery/ambiguous_scope.parquet     (isolated review queue, TTL: 180 d)           │
│    discovery/rejected_low_quality.parquet(terminal audit logg, TTL: 90 d)               │
│  discovery/trajectories/sanitized/*.json(audit trail with canonical SHA-256)            │
└────────────────────────────────────────┬────────────────────────────────────────────────┘
                                         │  (CLI: wiki review promote <ID> — DPCP Engine, §9.3–§9.5)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                  CANONICAL KNOWLEDGE GRAPH (v3.8.10 CORE SPECIFICATION)                 │
│    personal/ | engineering/ (Validated by Layer 1–5 Linters: E001–E027)                 │
└─────────────────────────────────────────────────────────────────────────────────────────┘

```

---

## 2. Formal Invariants for the Capture Engine (INGEST-CORE)

| Invariant ID | Domain | Error code | Rule / Contract Condition |
| --- | --- | --- | --- |
| INGEST-CORE-001 | Observation | E101 | **Non-Invasive Observation:** The ingestion engine MUST NEVER block, delay, modify or abort the execution of the source agents. Capture happens asynchronously via filesystem watching or read-only database reading (`mode=ro`, `PRAGMA query_only=ON`, without `immutable=1`). |
| INGEST-CORE-002 | Sanitization | E102 | **Deterministic Redaction & Reasoning Strip:** All API keys, tokens, passwords, certificates, user-specific paths and PII MUST be scrubbed. Private reasoning data MUST NOT be persisted or sent to the LLM. |
| INGEST-CORE-002A | Security | E102A | **Sanitization Uncertainty Fail-Closed:** If the sanitization engine encounters undefined fields or unclassifiable high entropy ($H > 4.5$ bits/character, Shannon entropy with $\log_2$; $L \ge 20$ characters) that do not match allowed contexts, the field MUST NOT be processed and the Trajectory is set to `quarantined_sanitization_uncertain`. **Allowlist Exemption:** Verified non-secret technical literals (standard hexadecimal SHA-256/SHA-1 hashes `^[a-f0-9]{40,64}$`, canonical UUIDs `^[a-f0-9-]{36}$`, and MIME-prefixed Base64 data `^data:[a-zA-Z0-9/+.-]+;base64,`) matching strict structural patterns are exempted from entropy quarantine. |
| INGEST-CORE-003 | Boundary | E103 | **Discovery Boundary:** The ingestion engine MUST NEVER write directly to canonical folders (`personal/`, `engineering/`) or modify `relation_registry.yaml`. All initial output MUST be staged under `discovery/`. |
| INGEST-CORE-004 | Ontology | E104 | **Ontological Alignment (Scope-Conditioned Triad):** All extracted metadata MUST map strictly to defined object types and approved facets per `object_registry.yaml`. The triad is scope-conditioned: `engineering` ⇒ root object `Incident` (followed by `Lesson` $\rightarrow$ `Workflow`); `personal` ⇒ root object `Observation` (followed by `Lesson` $\rightarrow$ `Workflow`), because `Incident` is ENGINEERING_ONLY (ID-005) and MUST NEVER be assigned `personal` scope. `Skill` constitutes a secondary Canonical transformation of a verified `Workflow`, never a direct raw extraction. |
| INGEST-CORE-005 | Scope firewall | E105 | **Strict Scope Isolation:** A Trajectory classified as `engineering` MUST NOT propose connections to `personal` objects unless `cross_scope: true` has been set (field defined in §11 `SynthesizedKnowledgeBundle`). Engineering-specific object types (`Specification`, `Feature`, `Incident`, `TroubleReport`) MUST NOT be assigned `personal` scope. |
| INGEST-CORE-006 | Quality gate | E108 | **Minimum Evidence Quality:** Proposals with model confidence $\text{Conf}_{\text{model}} < 0.75$, deterministic evidence $Q_{\text{det}} < 0.45$ or composite quality $Q_{\text{composite}} < 0.70$ MUST NOT be saved to `concept_proposals.parquet` but are relegated to `discovery/rejected_low_quality.parquet`. |
| INGEST-CORE-007 | Content identity | E109 | **Canonical Content Identity:** `input_sha256` MUST be computed over the recursively NFC-normalized, sorted and compact UTF-8 JSON representation of the sanitized Trajectory. |
| INGEST-CORE-008 | Scope guard | E110 | **No Silent Fallback to Personal:** Trajectories where the scope inference has confidence $< 0.85$ MUST NOT be silently degraded to `personal`. The `ambiguous_scope.parquet` table and missing migration defaults MUST use `'ambiguous'::VARCHAR`. |
| INGEST-CORE-009 | Schema evolution | E111 | **Type-Safe Dual-Engine Evolution:** Schema migrations MUST declare version numbers (`schema_version`) and migrate Parquet and SQLite without data loss. Columns with identity data are strictly cast (`CAST`), metric values via `TRY_CAST` with a post-cast NULL audit, and missing historical migration values are set to `'historical_unknown'::VARCHAR`. |
| INGEST-CORE-010 | Replay protection | E112 | **Immutable Approved Proposals:** The replay engine MUST NEVER automatically overwrite or modify proposals with status `approved` or `promoted` unless the `--force-reextract-approved` flag is provided together with a cryptographic HMAC-SHA256 challenge token (§10.3). |
| INGEST-CORE-011 | Regex safety | E113 | **Bounded Linear Regex Execution:** All sanitization patterns MUST be executed under a linear regex engine (DFA/re2) with size limits per field (`MAX_SANITIZATION_FIELD_BYTES = 1 MB`) and per Trajectory (`MAX_TRAJECTORY_BYTES = 50 MB`). |
| INGEST-CORE-012 | DSCP idempotency | E114 | **Durable Staged Commit Idempotency:** A staged proposal is uniquely identified by the tuple $I = (\text{proposal\_id}, \text{input\_sha256}, \text{target\_table})$. The committer MUST deduplicate against existing rows and throw a fatal `E114` on an identity collision with divergent content. |
| INGEST-CORE-013 | Serialized commit | E115 | **Zero Lost Updates Across Staging Tables:** Writes to all staging tables are serialized via a single-threaded Committer queue. Parallel extraction workers MAY ONLY write to unique temporary files (`.tmp_proposals_<tx_id>.parquet`). |
| INGEST-CORE-014 | Singleton guarantee | E116 | **Process-Identity Singleton:** `wiki-ingestd` guarantees exactly one active instance via `O_CREAT \| O_EXCL` with `/proc` start-time validation (or `stale_lock_ttl_seconds` in conservative mode, §3.4). |
| INGEST-CORE-015 | Promotion atomicity | E117 | **Durable Promotion Commit Protocol (DPCP):** Promotion from staging to the canonical graph MUST be executed via a journaled state machine with automated compensation/rollback on errors in the linter or file writing. Retention in staging is maintained by the TTL reaper (§7.3). |
| INGEST-CORE-016 | Deterministic evidence | E118 | **Pre-LLM Evidence Derivation:** An `EvidenceBundle` MUST be constructed deterministically directly from Trajectory data *before* the LLM is called. The extraction model MUST NOT generate or modify the evidence fields. |
| INGEST-CORE-017 | Startup order | E119 | **Strict Migration-Before-Sweeping Order:** Schema reconciliation and SQLite backfill (`run_schema_migrations`) MUST be completed and verified before the path-exact sweeper or DSCP recovery is run. |
| INGEST-CORE-018 | Capability firewall | E120 | **Zero-Side-Effect Extraction:** The extraction LLM operates as a pure function without external tools, file-write permissions or network access **beyond the single inference call to the configured `model_endpoint`** (§13). Extracted commands are treated as pure text data and are never executed. |
| INGEST-CORE-019 | Epistemic separation | E121 | **Explicit Epistemic Staging:** Proposals are staged with `epistemic_status: "inferred"`, `evidence_level: "trajectory_observed"` and `validation_status: "unverified"`. Status `approved` in the Discovery Graph means administrative review, never autonomous absolute truth. |
| INGEST-CORE-020 | Deterministic identity | E122, E123 | **Canonical Identity Hardening:** Naive datetimes (without `tzinfo`) and NFC key collisions MUST be rejected fail-closed before canonical hash computation (§6.1), since they break E109 determinism across hosts. |
| INGEST-CORE-021 | Promotion contract | E124 | **Canonical Promotion Contract:** Promotion MUST follow the normative promotion contract (§9.4): epistemic value-space mapping, Provenance construction, taxonomy validation, mandatory facets (FAC-001), ID allocation and relations per `relation_registry.yaml`. Every deviation aborts DPCP before canonical writing. |
| INGEST-CORE-022 | Retention | E125 | **TTL Enforcement:** The staging TTL (§7.1) MUST be enforced by a deterministic, idempotent reaper (§7.3). Expired `pending` proposals are marked `expired`; canonical or DSCP-staged targets are never purged by the reaper. |

### 2.1 Resource limits and fail-closed processing

The limits in `INGEST-CORE-011` are the minimum bounds for sanitization. Every
other bounded operation over an external or semi-trusted Source Record MUST
also have an explicit, versioned limit for parser input, nesting/recursion,
expanded output, model input/output, wall-clock time and concurrent work. A
limit MUST be applied before the operation can consume the unbounded input;
operator configuration MUST NOT remove a required bound.

Exceeding any limit, cancellation, timeout, parser error, model transport
failure, worker-isolation failure, or inability to determine consumption MUST
fail closed: the record is not promoted or emitted as a successful proposal,
partial output is discarded or quarantined, and a structured failure with the
applicable limit and stage is retained in the audit path. The source capture
itself remains non-invasive and immutable. Cancellation MUST propagate to all
child work, and a timed-out or cancelled operation MUST NOT retain a write
capability or continue in the background.

Parsing and extraction MUST run in a resource-isolated worker boundary with no
canonical-write capability. Output caps MUST be checked before persistence;
implementations MUST NOT claim conformance by truncating data silently.

**RES-001**: External-input processing is bounded, cancellable, isolated and
fail-closed. Concrete numeric limits are deployment policy values and MUST be
recorded with the policy version; this specification deliberately makes no
performance claim or universal numeric choice.

**Error code register:** E106–E107 are reserved but not allocated in this version. E122–E124 are introduced in v0.5.2-RC (see §12.1). E125 is allocated to INGEST-CORE-022 (TTL enforcement), which previously shared E117 with INGEST-CORE-015 in violation of **ERR-001** in `VALIDATION.md` §10.3.

---

> **§3–§7 as well as §9–§11 and §13** are specified in the system documents listed in the header.
> The section numbering is preserved throughout the document family so that cross-references
> remain stable.

## 8. Threat Model & Security Guarantees

| Threat / Attack vector | Description | Mitigation & Invariant |
| --- | --- | --- |
| Prompt Injection via Tool Output | An error log or tool data contains instructions that attempt to manipulate the extraction. | **Capability Firewall & Data Barrier (§5.2, E120):** The extraction worker lacks tools and runs with zero side effects (INGEST-CORE-018). Extracted code is never executed. |
| Unclassified Sensitive Data / Secrets | Logs contain tokens or internal certificates that are missed by standard patterns. | **Fail-Closed Sanitization (INGEST-CORE-002A):** Unclassified high entropy (Shannon $H > 4.5$ bits/character, $\log_2$) is unconditionally quarantined. |
| Corruption of Watermark/Discovery Data | Malicious modification of SQLite or Parquet files to re-inject logs or inject SQL via state data. | **Canonical SHA-256 Hashing (INGEST-CORE-007):** Each record is bound to its canonically serialized `input_sha256`. **Parameterized SQL bindings + path validation (§3.3):** manipulated state rows cannot yield SQL injection in commit/recovery (v0.5.2-RC). |
| Denial-of-Service via Trajectory Flood | A broken agent creates millions of logs in a loop. | **Token Bucket & Bounded Regex (INGEST-CORE-011):** Maximum limits per field and Trajectory, plus a rate limit of 10 extractions/minute. |

---

## 12. Conformance & Adversarial Test Suite

### 12.1 Canonical Invariant Register & Test Coverage

> **Status (v0.5.2-RC):** The register is a *target structure* — the listed modules SHALL exist in `conformance/` before the specification is declared stable. Currently, `conformance/` covers the v3.8.10 core (identity, facets, epistemics, retrieval); the ingest modules below are planned.

| Invariant ID | Domain | Implementation | Failure Mode | Test file |
| --- | --- | --- | --- | --- |
| E101 | Observation | Read-only adapters | Agent is blocked | `test_non_invasive_adapters.py` |
| E102 | Sanitization | Tier 1–5 Sanitizer + Strip | Leaked keys/CoT | `test_sanitization_adversarial.py` |
| E102A | Security | Fail-Closed Quarantine | Undefined data leaks | `test_sanitization_fail_closed.py` |
| E103 | Boundary | Ingestion staging guard | Writes to canonical | `test_discovery_boundary.py` |
| E104 | Ontology | Scope-conditioned triad (engineering: INC→LES→WFL; personal: OBS→LES→WFL) | Disallowed Skill node / Incident in personal scope | `test_ontological_alignment.py` |
| E105 | Scope | Engineering type lock + `cross_scope` review | Leakage to personal | `test_scope_firewall.py` |
| E108 | Quality | $Q_{\text{composite}}$ and $Q_{\text{det}}$ | Low quality is staged | `test_quality_score_formula.py` |
| E109 | Hash | Recursive NFC UTF-8 hash | Hash mismatch on byte-rep | `test_canonical_content_hash.py` |
| E110 | Scope guard | Ambiguous routing | Silent personal fallback | `test_scope_ambiguous_routing.py` |
| E111 | Schema | DuckDB reconciliation + audit | NULL data loss | `test_schema_reconciliation_audit.py` |
| E112 | Replay | HMAC Nonce Token Verification | Overwrite of approved | `test_replay_protection_nonce.py` |
| E113 | Regex | DFA + max payload bounds | ReDoS / DoS memory hang | `test_bounded_regex_execution.py` |
| E114 | DSCP | CommitIdentity $(P, S, T)$ | Double commit / collision | `test_dscp_idempotent_commit.py` |
| E115 | Committer | Single-threaded commit queue | Parallel race conditions | `test_serialized_committer.py` |
| E116 | Singleton | PID starttime cross-FS | Double daemon start | `test_daemon_singleton.py` |
| E117 | Promotion | DPCP Journal Recovery | Partial files in canonical | `test_dpcp_promotion_journal.py` |
| E118 | Evidence | Pre-LLM EvidenceBuilder | LLM generates evidence | `test_deterministic_evidence.py` |
| E119 | Startup | Migration before sweeper | Data is deleted at startup | `test_startup_lifecycle_order.py` |
| E120 | Firewall | Zero-side-effect extraction | LLM executes code | `test_capability_firewall.py` |
| E121 | Epistemics | 5-D Lifecycle & Governance | Approved interpreted as truth | `test_epistemic_status_tagging.py` |
| E122 | Determinism | Naive-datetime fail-closed (§6.1) | Time-zone-dependent hash across hosts | `test_canonical_content_hash.py` |
| E123 | Determinism | NFC key-collision detection (§6.1) | Silent data loss in canonicalization | `test_canonical_content_hash.py` |
| E124 | Promotion | Promotion contract §9.4 (mapping, facets, ID, relations) | Partial/incorrect canonical write | `test_dpcp_promotion_journal.py` |

---

### 12.2 Crash-Point Fault Injection Matrix (`test_dscp_crash_matrix.py`)

Automated tests inject `SIGKILL` at 8 state points. From v0.5.2-RC the recovery tests verify against `commit_transactions` (§3.3) and the fault injection is extended with: corrupt/unknown `target_table` (fail-closed E114) plus SQL injection attempts via manipulated `proposal_id`/`input_sha256` values (parameterized bindings, §3.3).

* **Crash CP-1:** Crash after SQLite `PENDING_COMMIT`, before `.tmp_proposals_*.parquet` is created $\rightarrow$ Status is set to `FAILED`, Trajectory is re-queued.
* **Crash CP-2:** Crash in the middle of DuckDB `COPY` of the merge part $\rightarrow$ Transient `.tmp_commit_*.parquet` is cleaned at startup, `.tmp_proposals_*` is re-run.
* **Crash CP-3:** Crash after `COPY`, before `os.replace` $\rightarrow$ Target unchanged, the committer retries at startup.
* **Crash CP-4:** Crash after `os.replace`, before SQLite `COMMITTED` $\rightarrow$ The tuple $I$ is found in the target table at startup, SQLite is updated to `COMMITTED`, the tmp file is deleted.
* **Crash CP-5:** Crash after SQLite `COMMITTED`, before `.tmp_proposals_*` is deleted $\rightarrow$ The sweeper matches against SQLite `COMMITTED` and safely deletes the residual file.
* **Crash CP-6:** Crash in the middle of Parquet schema migration in `run_schema_migrations` $\rightarrow$ Transient `.tmp_migration_*.parquet` is deleted, the original Parquet remains intact.
* **Crash CP-7:** Crash after migration `os.replace`, before the version manifest is written $\rightarrow$ The next startup detects a manifest mismatch and completes registration deterministically.
* **Crash CP-8:** Crash in the middle of a sweeper run $\rightarrow$ No permanent states are corrupted; the sweeper resumes deterministically.

---

---

**End of LLM Wiki Trajectory Ingestion Engine Specification v0.5.2-RC**

See also: `INGEST-ADAPTERS.md`, `INGEST-PIPELINE.md`, `INGEST-STAGING.md`,
`INGEST-DATA-MODEL.md`, `DISCOVERY.md` (Delta discovery), `VALIDATION.md` §10.3 (error code register).