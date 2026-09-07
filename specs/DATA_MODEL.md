# LLM Wiki Data Model Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-DATA-MODEL-001`
> **Version**: `3.8.10`
> **Updated**: `2026-08-17`
> **Source**: Extracted from `spec.md` §3, §6, §8; extended by current modular specs
> **Status**: `LOCKED`
> **Implementation status**: `UNIMPLEMENTED`
> **Compatibility target**: Baseline Knowledge Object schema; additive source model remains opt-in
> **Normative owner**: This document owns Knowledge Object types, IDs, facets, scope and domain
> **Related documents**: `ARCHITECTURE.md`, `ONTOLOGY.md`, `EPISTEMOLOGY.md`, `VALIDATION.md`

---

## 3. Information Model: Object Types & Facets

Knowledge is divided into two primary domain layers — **Knowledge World** and
**Engineering World** — connected via semantic ontology links
(`ONTOLOGY.md` §4). The object type answers **WHAT KIND** of Knowledge Object it is
(`ARCHITECTURE.md` §1.1), while the facets answer **WHICH PROPERTIES** it has.

`object_registry.yaml` constitutes the canonical source of truth for object types,
TYPE_CODES, allowed scopes, mandatory facets and tag strategy.

`Source` is not a Knowledge Object and is not owned by this registry. Source
classification is owned by `schemas/registry/source_registry.yaml`; the two
namespaces MUST NOT be collapsed. Source scope is input context and does not
replace the derived Knowledge Object's scope (see `UNIVERSAL-SOURCE-EXTENSION.md`).

Source, Representation and Content Object are distinct concepts: a Source is
the stable external/internal identity, a Representation is the immutable
capture at a point in time, and a Content Object is the immutable bytes/content
addressed by hash. A normalized Source Record is the validated envelope plus
typed payload used by ingestion; it is not a canonical Knowledge Object.

### 3.1 Object Types, Allowed Scopes & Mandatory Facets

| `object_type` | Category | TYPE_CODE | Allowed scopes | Mandatory classification | Mandatory facets | Tag strategy |
|---|---|---|---|---|---|---|
| **Article** | information | `ART` | personal, engineering | `domain` (1..1) | `language` (1..N), `audience` (1..1) | domain |
| **Document** | information | `DOC` | personal, engineering | `domain` (1..1) | `language` (1..N) | domain |
| **Specification** | information | `SPC` | engineering | `domain` (1..1) | `toolchain` (1..N), `lifecycle` (1..1), `architecture` (1..N) | domain |
| **Report** | information | `RPT` | personal, engineering | `domain` (1..1) | — | year |
| **Concept** | semantic | `CON` | personal, engineering | `domain` (1..1) | `language` (1..N) | domain |
| **Definition** | semantic | `DEF` | personal, engineering | `domain` (1..1) | `language` (1..N) | domain |
| **Principle** | semantic | `PRN` | personal, engineering | `domain` (1..1) | `language` (1..N) | domain |
| **Claim** | semantic | `CLM` | personal, engineering | `domain` (1..1) | — | year |
| **Product** | domain | `PRD` | engineering | `domain` (1..1) | `lifecycle` (1..1) | domain |
| **Feature** | domain | `FET` | engineering | `domain` (1..1) | `toolchain` (1..N), `prog_language` (1..N), `lifecycle` (1..1) | domain |
| **Requirement** | domain | `REQ` | engineering | `domain` (1..1) | `lifecycle` (1..1) | domain |
| **Component** | domain | `CMP` | engineering | `domain` (1..1) | `prog_language` (1..N), `toolchain` (1..N), `lifecycle` (1..1) | domain |
| **WorkPackage** | domain | `WPK` | engineering | `domain` (1..1) | `lifecycle` (1..1) | domain |
| **Interface** | domain | `IFC` | engineering | `domain` (1..1) | `architecture` (1..N) | domain |
| **Protocol** | domain | `PRT` | engineering | `domain` (1..1) | `architecture` (1..N) | domain |
| **Incident** | events | `INC` | engineering | `domain` (1..1) | `toolchain` (1..N), `lifecycle` (1..1) | year |
| **TroubleReport** | events | `TRB` | engineering | `domain` (1..1) | `toolchain` (1..N), `lifecycle` (1..1) | year |
| **Experiment** | events | `EXP` | personal, engineering | `domain` (1..1) | `toolchain` (1..N) | year |
| **Observation** | events | `OBS` | personal, engineering | `domain` (1..1) | `toolchain` (1..N) | year |
| **Lesson** | events | `LES` | personal, engineering | `domain` (1..1) | `toolchain` (1..N), `language` (1..N) | year |
| **Workflow** | procedural | `WFL` | personal, engineering | `domain` (1..1) | `toolchain` (1..N), `audience` (1..1) | domain |
| **Procedure** | procedural | `PRC` | personal, engineering | `domain` (1..1) | `audience` (1..1) | domain |
| **Checklist** | procedural | `CHK` | personal, engineering | `domain` (1..1) | `audience` (1..1) | domain |
| **Skill** | procedural | `SKL` | personal, engineering | `domain` (1..1) | `audience` (1..1) | domain |
| **Sequence** | procedural | `SEQ` | engineering | `domain` (1..1) | `architecture` (1..N) | domain |

**ENGINEERING_ONLY_OBJECT_TYPES** (MUST NOT be used under `scope: personal`,
**ID-005** / **E006**): `Specification`, `Product`, `Feature`, `Requirement`,
`Component`, `WorkPackage`, `Interface`, `Protocol`, `Incident`,
`TroubleReport`, `Sequence`.

### 3.1.1 Procedural vs. Evaluative Disambiguation (Workflow vs. Heuristic/Principle)

The classification of an object as procedural (`Workflow` or `Procedure`) MUST NOT be based on:
- The number of times a pattern has been observed or informally executed;
- The subjective confidence of an observer or extraction model;
- Informal recurrence in human or agent sessions.

A candidate MAY only be classified as `Workflow` (or `Procedure`) if it satisfies all of the following:
1. **W1 — Defined Step Sequence:** The object specifies an ordered, repeatable, and non-ambiguous sequence of concrete steps ($1, 2, \dots, n$), rather than merely a rule of thumb about how to weight, interpret, or judge information.
2. **W2 — Third-Party Executability:** A third party (human or agent) can execute the sequence without having to independently reconstruct the underlying judgment call at each step. (Bounded judgment may remain within individual steps, provided execution does not depend on rediscovering the procedure itself).
3. **W3 — Observable Completion:** The workflow defines an identifiable completion condition, state transition, or generated artifact (e.g. a recorded decision, modified configuration, completed build, or committed change). Vague sequences lacking an exit condition fail W3.

**Deterministic Validation & Downgrade Invariant:**
Classification as a procedural object SHALL be validator-enforceable:
$$\text{candidate.object\_type} \in \{\text{Workflow}, \text{Procedure}\} \implies \text{W1} \land \text{W2} \land \text{W3}$$
If a candidate proposed as a workflow fails any of W1–W3 during deterministic validation, it MUST be downgraded to an appropriate evaluative/semantic object (`Principle`, `Lesson`, or `Observation`), regardless of observation count or model confidence.

**Boundary Condition:**
A workflow MAY contain heuristics as internal decision rules within specific steps (e.g., *Step 2: apply heuristic H to weigh candidate architectures*). The presence of an internal heuristic MUST NOT downgrade the overall procedure, provided the enclosing procedure satisfies W1–W3.

### 3.2 Facet Cardinality

| Code | Pydantic type | Rule |
|---|---|---|
| `0..1` | `Optional[Enum] = None` | Optional scalar. At most one value. |
| `1..1` | `Enum` | Mandatory scalar. Exactly one value required. |
| `0..N` | `Optional[List[Enum]] = None` | Optional list. May be omitted. If specified, it MUST NOT be empty. |
| `1..N` | `List[Enum]` | Mandatory list. MUST contain at least 1 value. |

### 3.3 Facet Dimensions & Sentinel Semantics (none vs unknown)

`facet_registry.yaml` is the canonical source of truth for facet **value sets**;
`object_registry.yaml` declares only **which** facets are mandatory per object
type (§3.1). The separation is deliberate: requiredness is a property of the
object type, legal values are a property of the facet.

**Sentinel value distinction (D39):**
* `none`: The facet axis genuinely **does not apply** to this object (e.g. `prog_language: [none]` on a `Principle`). This is a definitive, legitimate value and **does not fire W011**.
* `unknown`: The facet axis applies, but the specific value is **not yet determined / pending classification** (e.g. during bulk migration). This value **fires warning W011** as an actionable reminder to classify the object.

| Facet | Answers | Cardinality | Notes |
|---|---|---|---|
| `toolchain` | Which tooling does this concern? | `1..N` | Build, test, analysis, runtime and AI tooling |
| `prog_language` | Which implementation language? | `1..N` | Includes configuration languages |
| `language` | Which natural language is the content in? | `1..N` | `en`, `sv` |
| `audience` | Who is it written for? | `1..1` | Includes `customer` for released documentation |
| `architecture` | Which hardware/platform/deployment context? | `1..N` | — |
| `lifecycle` | Which lifecycle state is the **described system** in? | `1..1` | See §3.5 — never the wiki page's state |
| `test_level` | Which verification level? | `0..N` | `unit`, `smoke`, `integration`, `e2e`, `performance`, `chaos`, `security` |

`test_level` is orthogonal to `toolchain`: one framework can serve several levels
and one level can use several frameworks. It is optional (`0..N`) and appears in
no object type's `required_facets`.

### 3.4 Facet Invariants

- **FAC-001** / **E020**: Mandatory facets according to §3.1 MUST be specified for each
  object type. If multi-valued (`1..N`), at least one value MUST be specified.
- **FAC-002** / **E013**, **E014**, **E015**: Facet lists MUST NOT be empty
  (`[]`), contain duplicates, mix `none` with concrete enums, mix `unknown` with
  concrete enums, or mix `none` with `unknown`.
- **FAC-003** / **E026**: Every facet value MUST exist in the corresponding `values`
  list in `facet_registry.yaml`. A facet MUST NOT use `none` unless that facet declares
  `allows_none: true`. Sentinel `unknown` is permitted only where present in that facet's
  `values` list (and fires `W011`).
- **FAC-004**: `FacetEnum` types in source code MUST be generated deterministically
  from `facet_registry.yaml` (mirroring **REL-002**).
- **W011**: Knowledge Objects that specify `[unknown]` on a facet generate a warning
  recommending concrete classification. Legitimate `[none]` values do not trigger `W011`.
- **CLS-003**: `keywords` are descriptive free-text terms in the IDENTITY category. They
  SHALL NOT be a pre-filter axis, SHALL NOT gate retrieval, and SHALL NOT be generated.

### 3.5 `facets.lifecycle` vs `status` (GOV-001)

This is the most frequently conflated pair in the model, so it is stated
normatively here:

| | `facets.lifecycle` | `status` |
|---|---|---|
| Describes | the **system, feature or work item** | the **wiki page** about it |
| Metadata category | FACETS | GOVERNANCE |
| Values | `planned`, `ongoing`, `delivered`, `maintained`, `legacy`, `withdrawn`, `none` | `draft`, `established`, `deprecated`, `archived` |
| Owning registry | `facet_registry.yaml` | `governance_policy.yaml` |

**GOV-001** forbids conflating them. A page with `status: established` (reviewed,
current, trustworthy) may legitimately describe a feature with
`lifecycle: planned` (not yet built).

Progress state therefore belongs on the **facet** axis, not in the taxonomy: a
feature does not change subject when it ships, and refiling it would break
`TAX-002` path determinism for no gain. Programme membership — which work package
or increment delivers it — belongs on the **relation** axis (`PART_OF`,
`INTRODUCED_IN`; see `ONTOLOGY.md` §4.3).

---

## 6. Identity Model & ID Convention

### 6.1 ID_PATTERN

```text
(PERS|ENG)-[A-Z]{2,5}-[A-Z0-9][A-Z0-9_]*-[0-9]{4}
```

| Segment | Content | Rule |
|---|---|---|
| SCOPE | `PERS` or `ENG` | `PERS` for `scope: personal`, `ENG` for `scope: engineering` (**ID-001**) |
| TYPE | TYPE_CODE | MUST be equal to `TYPE_CODES[object_type]` in `object_registry.yaml` (**ID-002**) |
| TAG | Domain or year tag | According to the object type's `tag_strategy` (**ID-003**) |
| SEQ | Four-digit sequence number | Namespace `(scope, object_type, tag)`, cap `9999` (**ID-004**) |

**Tag strategies:**

```text
YEAR_TAG_PATTERN   = ^[0-9]{4}$          # tag_strategy: year
DOMAIN_TAG_PATTERN = ^[A-Z0-9][A-Z0-9_]*$ # tag_strategy: domain
```

Example: `PERS-CON-AI-0002`, `ENG-CMP-BAZEL-0101`, `ENG-CLM-2026-0039`.

### 6.2 Identity Invariants

| Invariant | Rule | Error code |
|---|---|---|
| **ID-001** | Every ID MUST match `ID_PATTERN` and start with `PERS-` for personal scope or `ENG-` for engineering | E005 |
| **ID-002** | The TYPE segment MUST be equal to `TYPE_CODES[object_type]` | E005 |
| **ID-003** | Year object types MUST use `YEAR_TAG_PATTERN`; domain object types MUST use `DOMAIN_TAG_PATTERN` | E005 |
| **ID-004** | Object IDs MUST be globally unique. The sequence namespace is `(scope, object_type, tag)` with cap `9999` | E001 / E008 |
| **ID-005** | Object types in `ENGINEERING_ONLY_OBJECT_TYPES` MUST NOT be used under `scope: personal` | E006 |

### 6.3 Filename & Placement

The filename is the object's ID, not its slug:

```text
<scope>/<taxonomy_slug>/<ID>.md
```

The directory part is computed deterministically by the slug algorithm in `ARCHITECTURE.md`
§1.3 (**TAX-002** / **E002**).

---

## 8. Scope & Domain Classification

### 8.1 ScopeEnum

| Value | Meaning |
|---|---|
| `personal` | Broad personal knowledge base |
| `engineering` | Deep software and platform engineering domain for Duckburg Vibe Inc |

A future `global` scope is **not** included in v3.8.10. Introducing such a scope
requires changes to the object, taxonomy and governance registries and MUST NOT
be derived by a derived pipeline (`GRAPH-INTELLIGENCE.md` §4).

#### Scope Decision Rule (SCOPE-001)

Scope is decided by **portability**, not by subject matter:

> If the knowledge survives leaving this organisation, it is `personal`.
> If it depends on Duckburg Vibe Inc systems, toolchains or organisation, it is `engineering`.

For migration/import, an explicitly verified personal source MAY be assigned
`personal` as a declared target scope. A migration MUST NOT infer `personal`
merely because the source is local, lacks organization metadata, or has an
uncertain mapping. Uncertain scope is `ambiguous` until resolved by the
applicable review/governance step; it is not a canonical scope value.

This is the only rule needed to resolve the recurring ambiguity where the same
subject exists in both trees. Two worked pairs:

| Subject | `personal` | `engineering` |
|---|---|---|
| AI-assisted engineering | `07.04` — prompting, context engineering, LLM coding discipline | `13` — Duckburg Vibe's agent inventory, skill placement, model routing |
| Security | `07.02` — cryptography, attack classes, secure design theory | `16` — Duckburg Vibe platform secure coding rules, threat models, hardening |

Note that `ENGINEERING_ONLY_OBJECT_TYPES` (§3.1) constrains this independently: a
`Component`, `Interface` or `Specification` is always `engineering` regardless of the
portability rule.

### 8.2 Domain vs. Taxonomy vs. Facet

`domain` is an **orthogonal** classification at the object level and answers
**WHICH AREA OF EXPERTISE** the knowledge belongs to. It MUST NOT be used as:

- hierarchical placement (that is `taxonomy_path` / `taxonomy_id`), or
- property filter (that is facets).

This separation is axiom 3 of the five central axioms in `ARCHITECTURE.md` §1.1.
`domain` is mandatory (`1..1`) for all object types according to §3.1.

The `domains` block in `object_registry.yaml` is the canonical value set. Domain
lives with `object_type` because both belong to the CLASSIFICATION metadata
category (`ARCHITECTURE.md` §1.2), whereas facet values live in
`facet_registry.yaml`.

- **CLS-001** / **E027**: `domain` MUST be a value listed in the `domains` block
  of `object_registry.yaml`.
- **CLS-002**: The `domains` list MUST remain **coarser** than the taxonomy and MUST
  NOT be a one-to-one image of it. Two measurable conditions:
  1. `len(domains) < len(taxonomy nodes)`.
  2. The `domains` list MUST NOT enumerate a complete level of the tree: for any
     scope, fewer than half of that scope's root-node names may coincide with a
     domain value.

  Incidental single coincidences are permitted and expected — a subject and the
  expertise needed to judge it are sometimes named the same thing (`observability`,
  `natural_science`). What is forbidden is maintaining `domains` as a projection of
  the tree. A domain names the expertise required to *judge* an object; a taxonomy
  node names *where the object sits*. If adding a taxonomy node forces a new domain
  value, the two axes are being conflated.

---

## Data Model Invariants (summary)

| Invariant | Domain | Rule | Error code |
|---|---|---|---|
| **FAC-001** | Facets | Mandatory facets according to §3.1 MUST be specified | E020 |
| **FAC-002** | Facets | Facet lists MUST NOT be empty, contain duplicates or mix `none` with concrete enums | E013 / E014 / E015 |
| **FAC-003** | Facets | Every facet value MUST exist in `facet_registry.yaml`; `none` only where `allows_none: true` | E026 |
| **FAC-004** | Facets | `FacetEnum` types MUST be generated deterministically from `facet_registry.yaml` | - |
| **CLS-001** | Classification | `domain` MUST be a value listed in the `domains` block of `object_registry.yaml` | E027 |
| **CLS-002** | Classification | `len(domains) < len(nodes)`, and `domains` MUST NOT enumerate a complete level of the tree | - |
| **SCOPE-001** | Organization | Scope is decided by portability: organisation-independent → `personal`, product/org-bound → `engineering` | - |
| **ID-001** | Identity | ID MUST match `ID_PATTERN` with correct scope prefix | E005 |
| **ID-002** | Identity | The TYPE segment MUST correspond to `TYPE_CODES[object_type]` | E005 |
| **ID-003** | Identity | TAG MUST follow the object type's `tag_strategy` | E005 |
| **ID-004** | Identity | ID MUST be globally unique; sequence cap `9999` | E001 / E008 |
| **ID-005** | Identity | ENGINEERING_ONLY object types MUST NOT have `scope: personal` | E006 |

---

**End of LLM Wiki Data Model Specification v3.8.10**

See also: `ARCHITECTURE.md` (§1–§2, §7), `ONTOLOGY.md` (§4),
`EPISTEMOLOGY.md` (§5), `SCHEMA.md` (article templates), `VALIDATION.md` (§10–§12).