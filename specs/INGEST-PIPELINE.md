# LLM Wiki Ingestion Scope Router, Extraction & Sanitization Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-INGEST-PIPELINE-001`
> **Document family ID**: `LLM-WIKI-INGEST-SPEC-001`
> **Version**: `v0.5.2-RC` (Production-Hardening Candidate)
> **Updated**: `2026-08-17`
> **Source**: Extracted from `LLM-WIKI-INGEST-SPEC-001` §4–§6
> **Status**: `DRAFT`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Compatibility target**: Additive, non-invasive, opt-in
> **System documents**: `INGEST.md` (core) · `INGEST-ADAPTERS.md` (§3) · `INGEST-PIPELINE.md` (§4–§6) · `INGEST-STAGING.md` (§7, §9–§10) · `INGEST-DATA-MODEL.md` (§11, §13)
> **Normative owner**: This document owns scope routing, extraction, sanitization and trajectory pipeline-stage semantics
> **Related documents**: `UNIVERSAL-SOURCE-EXTENSION.md`, `INGEST.md`, `INGEST-ADAPTERS.md`, `INGEST-STAGING.md`

---

## 4. Scope Router, Versioning & Epistemic Model

### 4.1 Version-Bound Decision Key

$$\text{ScopeDecisionKey} = (\text{input\_sha256}, \; \text{scope\_policy\_version}, \; \text{taxonomy\_version})$$

```text
                    SANITIZED TRAJECTORY
                             │
                             ▼
       ┌───────────────────────────────────────────┐
       │ Step 1: Version-Bound Decision Cache      │ (input_sha256, policy_v, tax_v)
       └─────────────────────┬─────────────────────┘
                             │ Match?
                     ┌───────┴───────┐
                Yes  ▼               ▼  No
               Cached          ┌───────────────────────────────────────────┐
               Decision        │ Step 2: Repository Anchor Heuristic       │ (Git remotes, working directory)
                               └─────────────────────┬─────────────────────┘
                                                     │ Match?
                                             ┌───────┴───────┐
                                        Yes  ▼               ▼  No
                                        Determined      ┌───────────────────────────────────────────┐
                                        Scope           │ Step 3: Keyword & Toolchain Rules         │ (Duckburg Vibe, Bazel, Kafka etc.)
                                                        └─────────────────────┬─────────────────────┘
                                                                             │ Match?
                                                                     ┌───────┴───────┐
                                                                Yes  ▼               ▼  No
                                                               Determined      ┌───────────────────────────────────────────┐
                                                               Scope           │ Step 4: Probabilistic LLM Fallback        │
                                                                               └─────────────────────┬─────────────────────┘
                                                                                                     │
                                                                                                     ▼
                                                                                       Confidence >= 0.85?
                                                                                       ├── Yes ─► Determined Scope (inferred)
                                                                                       └── No ──► "ambiguous" (Queued for review)

```

---

### 4.2 The 5-Dimensional Epistemic & Lifecycle Framework

| Category | Dimension | Semantic Question | Allowed Values | Definition & Guarantee |
| --- | --- | --- | --- | --- |
| **Lifecycle** | `status` | What is the object's Discovery state? | `pending`, `approved`, `rejected`, `expired` | Administrative lifecycle in the staging layer. |
| **Materialization** | `promotion_status` | Has the object been written to the canonical graph? | `staged`, `promoted`, `failed` | Physical materialization status via DPCP. |
| **Scope** | `scope_status` | How certain is the scope classification? | `inferred`, `reviewed`, `confirmed` | `inferred` = automatic router; `reviewed` = manually reviewed; `confirmed` = explicit governance lock. |
| **Epistemic** | `epistemic_status` | How strong is the knowledge claim? | `inferred`, `reviewed`, `confirmed` | Epistemic reliability of the factual content itself. |
| **Epistemic** | `evidence_level` | What kind of evidence supports the claim? | `trajectory_observed`, `reproduced_verified`, `formal_proof` | The degree of empirical observation. |
| **Epistemic** | `validation_status` | Has the procedure been operationally verified? | `unverified`, `tool_verified`, `peer_verified` | Receipt of error-free action execution. |

---

## 5. Extraction Pipeline, Deterministic Evidence & Quality Metric

### 5.1 Deterministic Evidence Bundle Builder (Pre-LLM)

An `EvidenceBundle` is derived **deterministically before the LLM call** (INGEST-CORE-016). The `derived_at` timestamp is set strictly to `trajectory.end_time` to guarantee reproducibility.

**Verification receipt (v0.5.2-RC):** `verification_receipt` is assigned ONLY to the last `execute_bash` step with `exit_code == 0` whose command matches at least one pattern in `verification_command_patterns` (§13). Arbitrary exit-0 commands (e.g. `ls` or `pwd`) do not constitute a verification receipt and do not score in $Q_{\text{det}}$.

```python
import re


def build_deterministic_evidence_bundle(
    trajectory: "NormalizedTrajectory",
    verification_patterns: list[re.Pattern],
) -> "EvidenceBundle":
  """Deterministic evidence construction (INGEST-CORE-016).

  verification_patterns: compiled regex from §13
  `verification_command_patterns` — defines which exit-0 commands
  qualify as a verification receipt.
  """
  step_indices = []
  files_modified = set()
  commands_executed = []
  verification_receipt = None

  for step in trajectory.steps:
    # All steps are indexed (no filtering; renamed from
    # `relevant_steps` in v0.5.2-RC for semantic correctness).
    step_indices.append(step.step_index)
    if step.files_modified:
      files_modified.update(step.files_modified)
    if step.action_type == "execute_bash":
      cmd = step.tool_input.get("command", "")
      if cmd:
        commands_executed.append(cmd)
        if step.exit_code == 0 and any(
            p.search(cmd) for p in verification_patterns
        ):
          # The latest qualifying command wins (deterministic
          # order: the trajectory's step order).
          verification_receipt = cmd

  return EvidenceBundle(
      trajectory_id=trajectory.trajectory_id,
      trajectory_revision=trajectory.trajectory_revision,
      ingestion_id=trajectory.ingestion_id,
      input_sha256=trajectory.input_sha256,
      step_indices=step_indices,
      files_modified=sorted(list(files_modified)),
      commands_executed=commands_executed,
      verification_receipt=verification_receipt,
      derived_at=trajectory.end_time,
  )

```

---

### 5.2 Deterministically Computed Quality Metric ($Q_{\text{composite}}$)

The Quality metric is split into a purely deterministic sub-metric ($Q_{\text{det}}$) and a composite score ($Q_{\text{composite}}$):

$$Q_{\text{det}} = 0.25 \cdot \mathbb{I}_{\text{has\_verified\_execution}} + 0.20 \cdot \mathbb{I}_{\text{has\_observable\_change}} + 0.15 \cdot S_{\text{step}} + 0.10 \cdot S_{\text{spec}}$$

$$Q_{\text{composite}} = 0.30 \cdot \text{Conf}_{\text{model}} + Q_{\text{det}}$$

| Term | Weight | Formal Definition |
| --- | --- | --- |
| $\text{Conf}_{\text{model}}$ | $0.30$ | The LLM extractor's self-reported model confidence $\in [0.0, 1.0]$. |
| $\mathbb{I}_{\text{has\_verified\_execution}}$ | $0.25$ | $1.0$ if `verification_receipt` exists with a verified `exit_code == 0`, otherwise $0.0$. |
| $\mathbb{I}_{\text{has\_observable\_change}}$ | $0.20$ | $1.0$ if `len(evidence_bundle.files_modified) > 0`, otherwise $0.0$. |
| $S_{\text{step}}$ | $0.15$ | $S_{\text{step}} = \min\left(1.0, \; \frac{N_{\text{steps}}}{4}\right)$ where $N_{\text{steps}} = \text{len}(\text{workflow.steps})$. |
| $S_{\text{spec}}$ | $0.10$ | Proportion of mandatory facets filled in per `object_registry.yaml` `required_facets` (FAC-001, cf. `DATA_MODEL.md` §3; $1.0$ if none are required). |

**Quality gate (INGEST-CORE-006):**


$$\text{Admitted to staging iff } \text{Conf}_{\text{model}} \ge 0.75 \quad \text{AND} \quad Q_{\text{det}} \ge 0.45 \quad \text{AND} \quad Q_{\text{composite}} \ge 0.70$$

**Effective interplay of the thresholds (v0.5.2-RC):** Since $Q_{\text{composite}} = 0.30 \cdot \text{Conf}_{\text{model}} + Q_{\text{det}}$ and $\max Q_{\text{det}} = 0.70$, the three thresholds form a *joint* allowed region rather than three independent conditions:

* At the $Q_{\text{det}}$ floor of $0.45$, $\text{Conf}_{\text{model}} \ge \frac{0.70 - 0.45}{0.30} \approx 0.833$ is required. The advertised confidence limit of $0.75$ is thus only reachable with $Q_{\text{det}} \ge 0.475$.
* At the $\text{Conf}_{\text{model}}$ floor of $0.75$, $Q_{\text{det}} \ge 0.475$ is required (since $0.30 \cdot 0.75 + Q_{\text{det}} \ge 0.70$).

**Example (approved proposal):** verified execution ($0.25$) + observable change ($0.20$) + $N_{\text{steps}} = 3$ ($S_{\text{step}} = 0.15 \cdot \tfrac{3}{4} = 0.1125$) gives $Q_{\text{det}} = 0.5625$. With $\text{Conf}_{\text{model}} = 0.75$, $Q_{\text{composite}} = 0.225 + 0.5625 = 0.7875 \ge 0.70$ ✓. Implementing tests MUST cover the edge cases in this corner of the threshold space (`test_quality_score_formula.py`).

---

### 5.3 Two-Pass Knowledge Extraction & Granularity Invariants (First Principles)

When extracting knowledge from unstructured, multi-claim sources (articles, specifications, documentation, books, or agent trajectories), extraction MUST follow a two-pass architecture to establish consistent knowledge granularity and prevent graph fragmentation:

#### 5.3.1 Pass 1 — First Principles Decomposition (Atomization)
The extractor MUST decompose the source into typed, atomic, independently verifiable claims:
- `premise`: underlying assumptions taken as given by the source.
- `method`: mechanisms, procedures, or reasoning used to derive the result.
- `finding`: factual conclusions, empirical observations, or verified outcomes.
- `example`: contextual illustrations or specific instances demonstrating the finding.

**Eligibility Boundary:**
- Only core **findings** and primary **premises** are eligible to become candidate Knowledge Object nodes.
- **Methods** and **examples** MUST default to `evidence_refs` supporting the finding node rather than becoming standalone Knowledge Objects, preventing graph bloat with low-value contextual nodes.

#### 5.3.2 Pass 2 — Conceptual Aggregation & Synthesis
The extractor synthesizes atomic claims into a higher-level canonical object type (`Lesson`, `Concept`, `Component`, etc.), with underlying atoms forming the lineage/evidence chain (`Claim → Evidence Unit → Source`).

#### 5.3.3 Granularity Eligibility Invariants (The 3-Point Filter)
A candidate Knowledge Object node MUST satisfy all three criteria before admission to staging as an independent node:
1. **G-1 (Independent Reusability):** The knowledge can be cited, applied, or referenced meaningfully in an entirely different context.
2. **G-2 (Independent Falsifiability):** The claim can be independently refuted, updated, or superseded without invalidating the remainder of the source document.
3. **G-3 (Non-Redundancy / Existing Object Preference):** An extraction MUST execute a deduplication lookup against the existing knowledge graph before minting a new node ID. If an equivalent or broader concept already exists, new observations MUST attach as evidence or refinement relations rather than creating a duplicate node.

If a candidate fails G-1, G-2, or G-3, it MUST remain an evidence record under an existing or parent node.

#### 5.3.4 Semantic Resolution Outcomes
Every synthesized concept candidate evaluated against existing knowledge MUST resolve to exactly one primary outcome:
- **`EXISTING_MATCH`:** The knowledge is already represented adequately in the canonical graph. The candidate's new claims and sources are attached as evidence to the existing object, as required by **G-3** (§5.3.3).
- **`NEW_CANDIDATE`:** The knowledge represents a novel, validated reusable concept satisfying G-1–G-3. It enters the Discovery Graph as a new promotion candidate.
- **`EVIDENCE_ONLY`:** The information does not warrant an independent node but provides useful supporting or contextual evidence. It attaches to related parent nodes.
- **`CONTRADICTION`:** The candidate conflicts with existing knowledge. It enters the contradiction/epistemic resolution workflow rather than overwriting canonical nodes.
- **`UNRESOLVED`:** Semantic relationship is ambiguous. Fails safe: MUST NOT mutate the canonical graph.

#### 5.3.5 Context & Qualifier Preservation (G-4)
**G-4 (Qualifier Preservation):** Synthesis and claim decomposition MUST preserve materially relevant qualifiers, conditions, scope, and uncertainty. An extractor MUST NOT drop conditions to manufacture false generic claims (e.g. *"X improves performance"* MUST NOT replace *"X improved performance under workload Y when cache size was Z"*).

> **Granularity invariant series.** `G-1`–`G-3` are the admission filter defined
> in §5.3.3; `G-4` is defined here. This document owns the whole `G-N` series.
> Identifiers outside it (a former `G104`/`G107` pair) referenced no registry in
> this repository and have been folded into `G-4` and `G-3` respectively.

#### 5.3.6 Multi-Dimensional Confidence Model
The extraction pipeline MUST maintain separate confidence dimensions:
- `confidence.extraction`: model confidence in faithfully extracting the source claim.
- `confidence.synthesis`: confidence that grouped claims represent one coherent concept.
- `confidence.resolution`: confidence in the graph resolution decision (equivalence vs distinct).
- `confidence.provenance`: unbroken hash and span verification back to source.
These dimensions MUST NOT be collapsed into a single scalar during extraction. High extraction confidence does not imply canonical promotion eligibility.

#### 5.3.7 Core Invariant: Knowledge Resolution ≠ Chunking
The unit of extraction is the atomic claim; the unit of canonical representation is the reusable concept; evidence provides the traceable bridge between them. Document chunk boundaries are processing details and MUST NOT dictate canonical knowledge-object boundaries.

---

## 6. Fail-Closed Sanitization & Canonical Hashing

### 6.0 Prompt Injection Defense & Untrusted Source Fencing (FR-12, NFR-6, D105)

All untrusted source text passed to extraction routines or LLM workers MUST be wrapped in immutable boundary delimiters:

```text
<untrusted_source>
{sanitized_content}
</untrusted_source>
```

**Closing-Tag Escaping Invariant:** To prevent delimiter breakout attacks where adversarial input includes literal closing tags (e.g. `</untrusted_source>\nSystem instruction override:`), any occurrences of `</untrusted_source>` within the raw content MUST be sanitized by replacing them with `&lt;/untrusted_source&gt;` prior to wrapping.

The extraction LLM operates under the zero-side-effect capability firewall (`INGEST-CORE-018` / `E120`) with no tool execution or file modification privileges. Extracted commands or code snippets are treated as pure data and are never executed.

The Sanitization runs sequentially in memory under strict resource limits (`INGEST-CORE-002`, `INGEST-CORE-002A`, `INGEST-CORE-011`):


$$\text{MAX\_SANITIZATION\_FIELD\_BYTES} = 1\,048\,576 \quad (1\text{ MB}), \quad \text{MAX\_TRAJECTORY\_BYTES} = 52\,428\,800 \quad (50\text{ MB})$$

```text
RAW TRAJECTORY ► [Step 1: Field Allowlist Check (Unknown fields rejected immediately)]
                         │
                         ▼
                  [Step 2: Bounded Regex Secrets & Keys (AWS, GitHub, Bearer)]
                         │
                         ▼
                  [Step 3: PII, Paths & Environment ($HOME, $WORKSPACE_ROOT, $USER)]
                         │
                         ▼
                  [Step 4: Stripping of Private Reasoning Fields (thought, cot)]
                         │
                         ▼
                  [Step 5: Entropy analysis (H > 4.5, L >= 20)]
                         │
                 ┌───────┴───────┐
   Deterministic │               │ Unclassified Entropy
         Safe    ▼               ▼
          SANITIZED TRAJECTORY  QUARANTINE (quarantined_sanitization_uncertain) [E102A]

```

### 6.1 Recursive NFC Normalization & Canonical JSON Hash (`INGEST-CORE-007`)

**Identity hardening (v0.5.2-RC, INGEST-CORE-020):** Naive datetimes are rejected fail-closed (`E122`), because `astimezone()` on a naive datetime assumes the *host's* local time zone and thereby breaks E109 determinism across hosts. NFC-normalized key collisions are rejected fail-closed (`E123`), because they otherwise cause silent data loss in the canonicalized dict comprehension. The float normalization is a *deliberate* precision limitation to 8 decimals for determinism; values $|v| < 10^{-8}$ collapse to `0.0`.

```python
from datetime import datetime
import hashlib
import json
from typing import Any
import unicodedata


def normalize_value_nfc(val: Any) -> Any:
  """Normalizes strings recursively to Unicode NFC and validates data types."""
  if isinstance(val, str):
    return unicodedata.normalize("NFC", val)
  if isinstance(val, dict):
    normalized = {}
    for k, v in sorted(val.items()):
      nk = normalize_value_nfc(k)
      # E123: NFC normalization may merge distinct keys -> silent
      # data loss in the dict comprehension. Fail-closed.
      if nk in normalized:
        raise ValueError(
            f"NFC key collision after normalization: {k!r} [E123]"
        )
      normalized[nk] = normalize_value_nfc(v)
    return normalized
  if isinstance(val, list):
    return [normalize_value_nfc(elem) for elem in val]
  if isinstance(val, datetime):
    # E122: naive datetimes are forbidden. Without tzinfo, astimezone()
    # would assume the host's local time zone and produce a host-dependent
    # (non-deterministic) canonical hash. Fail-closed.
    if val.tzinfo is None or val.tzinfo.utcoffset(val) is None:
      raise ValueError(
          f"Naive datetime (missing tzinfo) is forbidden in canonical hash:"
          f" {val.isoformat()} [E122]"
      )
    # ISO-8601 UTC with strict Z suffix
    return (
        val.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
  if isinstance(val, float):
    if val != val or val == float("inf") or val == float("-inf"):
      raise ValueError("NaN and Infinity are strictly forbidden in canonical JSON.")
    if val == 0.0 and str(val).startswith("-"):
      return 0.0  # Normalize -0.0 to 0.0
    # Deliberate precision limitation to 8 decimals (determinism);
    # |v| < 1e-8 collapses to 0.0. The rstrip chain preserves "1.0" as "1.0".
    return float(f"{val:.8f}".rstrip("0").rstrip("."))
  return val


def compute_canonical_input_sha256(raw_dict: dict) -> str:
  """Computes canonical SHA-256 over a recursively normalized data structure."""
  normalized_data = normalize_value_nfc(raw_dict)
  canonical_bytes = json.dumps(
      normalized_data,
      sort_keys=True,
      ensure_ascii=False,
      separators=(",", ":"),
      allow_nan=False,
  ).encode("utf-8")
  return hashlib.sha256(canonical_bytes).hexdigest()

```

---

---

**End of LLM Wiki Ingestion Scope Router, Extraction & Sanitization Specification v0.5.2-RC**

See also: `INGEST.md` (core specification and INGEST-CORE invariants).