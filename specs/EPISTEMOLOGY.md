# LLM Wiki Epistemology & Governance Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-EPISTEMOLOGY-001`
> **Version**: `3.8.10`
> **Updated**: `2026-08-17`
> **Source**: Extracted from `spec.md` §5; extended by Universal Source provenance rules
> **Status**: `LOCKED`
> **Implementation status**: `UNIMPLEMENTED`
> **Compatibility target**: Baseline epistemic model and governance semantics
> **Normative owner**: This document owns epistemic dimensions, provenance and governance boundaries
> **Related documents**: `DATA_MODEL.md`, `VALIDATION.md`, `UNIVERSAL-SOURCE-EXTENSION.md`, `governance_policy.yaml`

---

## 5. Epistemic Modeling & Declarative Governance Policy

### 5.1 Epistemic Dimensions in Frontmatter

Epistemic dimensions are **orthogonal** and SHALL NOT be automatically derived from one another (**EPI-001**).

```yaml
# EPISTEMOLOGY (Category 5 per META-001)
evidence: observed         # observed | derived | inferred | postulated
verification: peer_verified # formal_proof | peer_verified | self_verified | unverified | falsified
authority: authoritative   # normative | authoritative | informative | advisory | deprecated
consensus: accepted        # accepted | proposed | contested
```

### 5.2 Epistemic Valuation Matrix (View of `epistemic_registry.yaml`)

> **Normative owner:** `schemas/registry/epistemic_registry.yaml` is the canonical source of truth for all epistemic dimensions, allowed values, and integer ranking weights (D19, S5). The table below is a normative view.

| Dimension | Value | Numeric Rank (used by $K(d)$) | Description |
|---|---|---:|---|
| **Evidence** | observed | 3 | Empirically observed |
| | derived | 2 | Mathematically or logically derived |
| | inferred | 1 | Synthesized or inducted by an agent or human |
| | postulated | 0 | Hypothesis, theoretical premise |
| **Verification** | formal_proof | 4 | Formally proved or machine-checked |
| | peer_verified | 3 | Independent peer review |
| | self_verified | 2 | Self-verified by author or test execution |
| | unverified | 1 | Unverified draft |
| | falsified | 0 | Disproven / invalidated |
| **Authority** | normative | 4 | Binding standard or hard invariant |
| | authoritative | 3 | Official architecture or handbook |
| | informative | 2 | Recommended practice or design note |
| | advisory | 1 | Informal suggestion or opinion |
| | deprecated | 0 | Historical / superseded |
| **Consensus** | accepted | 2 | Broadly accepted |
| | proposed | 1 | Working proposal |
| | contested | 0 | Active dispute present |

### 5.3 Epistemic Ranking (Conflict Resolution)

When two or more nodes (N ≥ 2) are part of a mutual `CONTRADICTS` cluster, each node is evaluated independently by maximizing the formal vector key:

$$K(d) = \bigl( V(d),\ A(d),\ C(d),\ E(d),\ \operatorname{Conf}(d),\ \operatorname{Date}(d),\ -\operatorname{ASCII}(\operatorname{ID}(d)) \bigr)$$

**Where:**
- $V(d)$ = verification value (4, 3, 2, 1, 0) from `epistemic_registry.yaml`
- $A(d)$ = authority value (4, 3, 2, 1, 0) from `epistemic_registry.yaml`
- $C(d)$ = consensus value (2, 1, 0) from `epistemic_registry.yaml`
- $E(d)$ = evidence value (3, 2, 1, 0) from `epistemic_registry.yaml`
- $\operatorname{Conf}(d)$ = confidence (float 0.0-1.0)
- $\operatorname{Date}(d)$ = last_verified (ISO format, latest date wins; `null` sorts lowest)
- $-\operatorname{ASCII}(\operatorname{ID}(d))$ = Lowest Node-ID wins the final tie-breaker

The winning node is defined as:
$$d^* = \arg\max_{d \in C} K(d)$$

where $C$ is the conflict cluster. $d^*$ is placed in `evidence_bundle` as the preferred
evidence candidate, not as proven truth. The other $(N-1)$ nodes are placed in
`suppressed_nodes` with the reason `conflict_lower_epistemic_rank`. Suppression
does not imply deletion, invalidity or that the node is false.

**Symmetric Contradiction & Epistemic Dispute Flagging:**
If two contradictory claims in $C$ share identical $(V, A, C, E)$ scores within $\Delta \text{Conf} \le 0.05$, the retrieval engine MUST set `epistemic_dispute: true` in the `EvidenceBundle` metadata and include the top opposing node in `disputed_counter_claims`. The generation prompt MUST instruct the synthesizing LLM to present both perspectives rather than fabricating synthetic consensus.

### 5.4 Declarative Governance Policy

Management rules are read dynamically from `governance_policy.yaml` (**GOV-002**).

The canonical policy is `schemas/registry/governance_policy.yaml` (currently
`schema_version: "1.1.0"`). Implementations MUST read that registry dynamically;
the registry, not an inline copy in this specification, owns the status/consensus
mapping. The following is illustrative pseudocode, not a second policy source:

```text
allowed_consensus = governance_policy.status_consensus_rules[status]
```

### 5.5 Governance Principles

- **GOV-001**: `status` describes repository management status; `facets.lifecycle` describes the domain system's lifecycle. They MUST NOT be conflated.
- **GOV-002**: Disallowed status/consensus combinations MUST be rejected with E004 according to governance_policy.yaml.

**Status enum (StatusEnum):**
- `draft` - Working draft
- `established` - Established and active
- `deprecated` - Deprecated but still valid
- `archived` - Archived, historical interest

---

## Provenance Model

Provenance (lineage) describes **who produced** the Knowledge Object, **who
confirmed** it, **what it derives from**, and **how reliable** it is.

For the Universal Source Extension, `source_type` is a registry reference to
`schemas/registry/source_registry.yaml`; it identifies the captured source and
never the Knowledge Object's type or epistemic status. `source_refs` (PROV-007)
identifies the citations or stable Source identities used for derivation. Capturing a
Source or Experience does not by itself make it evidence (**SOURCE-010**).

Capture is not evidence. Evidence is contextual: an observation or source span
is evidence only in relation to a proposition, claim or inference target. A
thought, idea, reflection, hypothesis, doubt or question MAY produce a
discovery candidate, but MUST NOT receive `evidence: observed` or verified
status merely because it was captured.

### Provenance Fields

| Field | Type | Description | Requirement |
|---|---|---|---|
| `source_type` | SourceTypeEnum | Type of source | Mandatory |
| `source_refs` | list[str] | Non-empty list of source references (DOI, URL, filepath, Source ID) | Mandatory (PROV-007 / E030) |
| `author` | Actor | Who or what **produced** the current content | Mandatory |
| `last_modified` | date | When the content last changed **meaningfully** | Mandatory |
| `reviewer` | Optional[Actor] | Who or what **confirmed** the content against its sources | Nullable (PROV-006 / E029) |
| `last_verified` | Optional[date] | Date of the latest confirmation | Nullable (PROV-006 / E029) |
| `next_review` | date | Next planned review | Mandatory |
| `confidence` | float | Reliability (0.0-1.0) | Mandatory |

### Unreviewed Content & Review Nullability (PROV-006, E029)

For freshly authored drafts (`status: draft`), `reviewer` and `last_verified` MAY be `null`. However, they are **bound together**:
- **PROV-006** / **E029**: `reviewer` and `last_verified` MUST be set together. Exactly one being `null` is rejected with **E029** (`IncompleteReviewError`). An unreviewed draft carries `reviewer: null` and `last_verified: null`.
- Inventing a placeholder reviewer on unreviewed drafts is strictly forbidden, as it falsely inflates verification rank in the $K(d)$ conflict algorithm.

### Authorship vs. Verification (PROV-002)

`author` and `reviewer` are **separate roles and MUST NOT be collapsed**: whoever
wrote a Knowledge Object need not be whoever confirmed it. Likewise
`last_modified` and `last_verified` are independent:

- content can change without being re-confirmed (`last_modified` > `last_verified`
  ⇒ the object carries unverified changes);
- content can be re-confirmed without changing (`last_verified` > `last_modified`
  ⇒ the object is checked and current).

Without this split, an LLM-maintained wiki cannot distinguish agent-generated text
from human-written text, nor a recent edit from a stale fact that was merely
recently checked. That distinction is the system's most important trust signal.

### Actor Convention & Namespace Separation (PROV-001, PROV-005)

`author` and `reviewer` are **Actor** strings using one of three forms:

| Form | Meaning | Example |
|---|---|---|
| `human:<id>` | A person | `human:eperson` |
| `<producer>/<version>` | An automated agent or model | `kiro/claude-opus-4`, `wiki-ingest/0.5.2` |
| `process:<id>` | A non-agent automated process | `process:nightly-uplift` |

```text
ACTOR_PATTERN = ^(human:[a-z0-9._-]+|process:[a-z0-9._-]+|[a-z0-9._-]+/[A-Za-z0-9._-]+)$
```

An Actor that violates the pattern MUST be rejected with **E028** (`InvalidActorFormatError`).
- **PROV-005**: The provenance Actor reference namespace (`human:...`, `<producer>/<version>`) and the Actor Record registry (`schemas/registry/actor_registry.yaml`) are distinct.
- **PROV-007** / **E030**: `source_refs` SHALL be a non-empty list, ordered as authored, and free of duplicate entries. An empty list or duplicates triggers **E030** (`EmptyOrDuplicateSourceRefsError`).

**Derived trust tier (informative).** A consumer MAY derive a coarse tier from
`reviewer`, exactly as OKF v0.2 §5.3 does: no reviewer ⇒ *unverified*; a
non-`human:` reviewer ⇒ *machine-confirmed*; a `human:` reviewer ⇒ *human-reviewed*.
This is an advisory reading of existing fields, not a stored value, and it MUST NOT
be written into frontmatter or substituted for `epistemology.verification`
(**EPI-001**).

### SourceTypeEnum (legacy compatibility)

The canonical source type namespace is now owned by `source_registry.yaml`.
The values below remain accepted only as legacy mappings during migration; new
canonical provenance MUST use a registry value.

| Value | Description |
|---|---|
| `api_spec` | Public/internal API specification (e.g. OpenAPI, AsyncAPI, gRPC) |
| `internal_spec` | Internal architecture specification |
| `developer_doc` | Released developer documentation & user guides — own-platform documentation |
| `system_doc` | Internal system documentation (design docs, architecture decisions, RFCs) |
| `post_mortem` | Post-mortem analysis |
| `academic_paper` | Academic publication |
| `observation` | Direct observation |
| `vendor_doc` | **Third-party** vendor documentation. MUST NOT be used for own-platform documentation — use `developer_doc` or `system_doc` |
| `book` | Book |
| `web_page` | Web page |
| `rfc` | RFC document |
| `standard` | Standard |
| `conversation` | Conversation |
| `meeting` | Meeting notes |

> **CPI is provenance, not taxonomy.** A CPI page is `object_type: Document` (or
> `Specification`) with `source_type: cpi` and `facets.audience: customer`, filed
> under the **subject it documents** — not under a "customer documentation" node.
> Knowledge about *how CPI is authored and released* is a different object and
> belongs under `15.01 Customer Documentation & CPI`. Link the two with
> `DOCUMENTED_BY` from the documented Product/Feature/Interface.

### Provenance Validation Rules

- **EPI-002**: `provenance.source_type` SHALL describe the provenance source, never the claim's epistemic state.
- **PROV-001** / **E028**: `author` and `reviewer` SHALL match `ACTOR_PATTERN`.
- **PROV-002**: `author` and `reviewer` are separate roles and MUST NOT be collapsed;
  `last_modified` and `last_verified` are independent dates.
- **PROV-003**: `confidence` is a **provenance** field, not an epistemic dimension. It
  MUST NOT be derived from, or collapsed into, `evidence`/`verification`/`authority`/
  `consensus` (**EPI-001**).
- **EPI-004**: Evidence MUST be contextualized with respect to a proposition,
  claim, observation or inference target.
- **EPI-005**: Source or Experience capture MUST NOT by itself promote evidence,
  verification, authority or consensus.
- **PROV-004**: Canonical relations and derived inferences are claims and MUST
  retain provenance with the same lineage discipline as Knowledge Objects.
- **W012**: `last_modified` lying in the future generates a warning.
- **W013**: `last_modified` later than `last_verified` generates an informational
  warning: the object carries content changes that have not been re-confirmed.
- **VAL-001**: `validity.valid_until` MUST NOT be earlier than `validity.valid_from`.
- **W002**: `next_review` that has passed today's date generates a warning.
- **W003**: `last_verified` that lies in the future generates a warning.

### Validity Model

```yaml
validity:
  valid_from: "2026-01-01"  # Start date of validity
  valid_until: null         # End date (null = unbounded)
```

---

## Epistemic Invariants

| Invariant | Domain | Description |
|---|---|---|
| **EPI-001** | Epistemology | Epistemic dimensions (evidence, verification, authority, consensus) are orthogonal and SHALL NOT be automatically derived from one another |
| **EPI-002** | Epistemology | provenance.source_type SHALL describe the provenance source, never the claim's epistemic state |
| **EPI-003** | Epistemology | Epistemic ranking SHALL follow the formal algorithm in §5.3 |