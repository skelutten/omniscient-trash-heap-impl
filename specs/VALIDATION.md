# LLM Wiki Validation & Linter Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-VALIDATION-001`
> **Version**: `3.8.10`
> **Updated**: `2026-09-08`
> **Source**: Extracted from `spec.md` §10–11; extended by current registry and source contracts
> **Status**: `LOCKED`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Compatibility target**: Baseline linter/error contract plus additive extension allocations
> **Normative owner**: This document owns validation layers, error-code allocation and status vocabulary
> **Related documents**: `DATA_MODEL.md`, `ONTOLOGY.md`, `SPEC_STATUS.md`, all registry files

---

## 10. Validation, Multi-Layered Linter & Formal Error Code Table

The validation engine (invoked via CLI `/lint` or CI/CD test gates) executes the multi-layered validation rules deterministically. Exit code 0 is returned if no errors are detected. Exit code 1 is returned on one or more validation errors.

### 10.1 Linter Architecture

The linter is divided into several layers:

```
Layer 1: Pydantic Schema Validation
  │
  ▼
Layer 2: Structural Validation (ID, Path, Taxonomy)
  │
  ▼
Layer 3: Semantic Validation (Relations, Facets)
  │
  ▼
Layer 4: Graph Validation (DAG, Cycles, Links)
  │
  ▼
Layer 5: Cross-Object Validation (Duplicates, References)
```

**Finding contract (`Finding` dataclass):**
Every diagnostic emitted by the linter MUST be structured with exactly four fields (D24):
- `code: str` — e.g. `E001`, `W014`.
- `field: str` — the specific frontmatter field, header, or `None` if corpus-wide.
- `message: str` — concise explanation of the violation.
- `suggestion: str | None` — machine-actionable suggestion or remediation string (or `None`).

**Clock injection requirement:**
All temporal and date-dependent checks (such as `W002`, `W003`, `W012`, `W013`) SHALL accept an injected `reference_date` parameter (defaulting to the CLI `--now` option). The framework MUST NOT call `datetime.date.today()` directly during validation execution (D29).

**Corpus load requirement:**
Running `lint <file>` SHALL filter the reported diagnostics to the specified file, but MUST always load the full corpus in memory so graph and referential integrity checks (`E001`, `E009`, `E010`, `E031`) are evaluated accurately across all relationships (D25).

**Implementation requirement — one read per file.** The five layers are a logical
ordering, not five passes over disk. A file SHALL be read and parsed **once** and the
parsed representation shared across all layers. Measured prior art: in a comparable
four-stage pipeline the lint stage consumed 56% of total runtime at 5,000 files and
the bottleneck was disk I/O, not validation logic
(`research/critiques-and-community-feedback.md` L2). Five naive passes multiply that
cost by five.

### 10.2 Formal Error and Warning Codes

#### ERROR Codes (E000-E031, E050-E052)

| Error code | Linter class | Triggering condition |
|---|---|---|
| **E000** | FileReadError | File cannot be read from disk or frontmatter YAML is malformed |
| **E001** | DuplicateNodeIdError | The same id occurs in more than one source file (ID-004) |
| **E002** | PathScopeMismatchError | The disk path does not match the computed slug (TAX-002) |
| **E003** | TaxonomySlugCollisionError | Two different taxonomy_path strings normalize to the same disk path (TAX-003) |
| **E004** | InvalidStatusConsensusCombinationError | Invalid state combination against governance_policy.yaml (GOV-002) |
| **E005** | InvalidTagConventionError | TAG does not match the object type's requirement (ID-003) |
| **E006** | ObjectScopeNotAllowedError | The object type is not allowed in the given scope (ID-005) |
| **E007** | ValidityChronologyError | valid_until is earlier than valid_from (VAL-001) |
| **E008** | SequenceOverflowError | The sequence number exceeds 9999 in the allocation registry (ID-004) |
| **E009** | BrokenLinkError | Ontology relation points to a missing target ID (soft_link: false, GRAPH-003) |
| **E010** | DAGCycleError | Cycle detected in a relation where dag: true is specified (GRAPH-001) |
| **E011** | SelfReferenceError | Object link to its own id (GRAPH-002) |
| **E012** | DuplicateRelationError | Identical relation type and target ID specified more than once (GRAPH-002) |
| **E013** | EmptyFacetListError | A specified facet list is empty ([], FAC-002) |
| **E014** | DuplicateFacetValueError | A facet list contains duplicates (FAC-002) |
| **E015** | MixedNoneFacetError | Facet list mixes none with concrete enums, unknown with concrete enums, or none with unknown (FAC-002) |
| **E016** | TaxonomyIdMismatchError | Specified taxonomy_id deviates from taxonomy_path or scope in the registry (TAX-004) |
| **E017** | UnknownTaxonomyIdError | Specified taxonomy_id does not exist in taxonomy_registry.yaml (TAX-001) |
| **E018** | TaxonomyParentNotFoundError | A parent_id in taxonomy_registry.yaml points to an unknown node (TAX-005) |
| **E019** | PersistedVirtualInverseError | A virtual inverse relation has been persisted in a YAML source file (REL-004) |
| **E020** | MissingRequiredFacetError | A mandatory facet according to §3.1 is entirely missing (None, FAC-001) |
| **E021** | InvalidRelationSourceTargetTypeError | The ontology relation violates source_types / target_types in relation_registry.yaml (REL-005) |
| **E022** | MissingRelationTypeConstraintError | A relation in relation_registry.yaml lacks source_types or target_types (REL-006) |
| **E023** | UnknownRelationObjectTypeError | A relation in relation_registry.yaml references an unknown object type (REL-007) |
| **E024** | TaxonomyCycleError | Cycle detected in taxonomy_registry.yaml via parent_id links (TAX-006) |
| **E025** | DuplicateInverseViewNameError | Two different **non-symmetric** relations in relation_registry.yaml declare the same inverse_view name. Symmetric relations are exempt — they MUST set inverse_view to their own name (REL-008) |
| **E026** | UnknownFacetValueError | A facet value does not exist in the facet's `values` list in facet_registry.yaml, or `none` is used on a facet declaring `allows_none: false` (FAC-003) |
| **E027** | UnknownDomainValueError | `domain` is not a value listed in the `domains` block of object_registry.yaml (CLS-001) |
| **E028** | InvalidActorFormatError | `provenance.author` or `provenance.reviewer` does not match ACTOR_PATTERN (PROV-001) |
| **E029** | IncompleteReviewError | Exactly one of `provenance.reviewer` or `provenance.last_verified` is `null` (PROV-006) |
| **E030** | EmptyOrDuplicateSourceRefsError | `provenance.source_refs` is empty, contains duplicate entries, or is omitted (PROV-007) |
| **E031** | OpposedRelationDirectionError | Relation declared in non-canonical direction (e.g. `A --DESCRIBES--> B` where B is in corpus; should be `B --DOCUMENTED_BY--> A`) (REL-009) |
| **E050** | GeneratedSkillDriftError | Emitted `.agents/skills/trashheap/SKILL.md` diverges from code and schemas/registry (AGENT-SKILLS.md §7) |
| **E051** | SectionOwnershipError | Regeneration or compiler pass encountered an unrecognized non-Notes section or multiple `## Notes` sections; compilation aborted to prevent data loss (BODY-003, OWN-002) |
| **E052** | RunawayLoopError | Agent or tool execution harness detected repeated identical tool call signatures >= 5 times without state mutation (The 40% Rule circuit breaker) (VAL-014) |

#### Registry ERROR Codes (E080-E086)

| Error code | Linter class | Triggering condition |
|---|---|---|
| **E080** | DuplicateFamilyOwnerError | Duplicate invariant family owner in `spec_ownership.yaml` |
| **E081** | UnknownOwnerPathError | Owner file specified in `spec_ownership.yaml` does not exist |
| **E082** | DuplicateThresholdIdError | Duplicate threshold ID in `threshold_policy.yaml` |
| **E083** | UnknownThresholdOwnerPathError | Owner file specified in `threshold_policy.yaml` does not exist |
| **E084** | EmptySourceTaxonomyError | `source_taxonomy` path is empty in `source_registry.yaml` |
| **E085** | UnknownSourceTaxonomyRootError | Root element of `source_taxonomy` not found in `source_registry.yaml` |
| **E086** | UnknownSourceTaxonomyChildError | Child element of `source_taxonomy` not found under its root in `source_registry.yaml` |

#### WARNING Codes (W001-W017)

| Warning code | Linter class | Triggering condition |
|---|---|---|
| **W001** | TaxonomyIdMissingWarning | Knowledge Object lacks the recommended field taxonomy_id |
| **W002** | ReviewOverdueWarning | next_review has passed today's date (or --now) |
| **W003** | FutureLastVerifiedWarning | last_verified is in the future |
| **W004** | UnresolvedSoftLinkWarning | soft_link: true has been unresolved > 90 days |
| **W005** | SoftLinkResolvedButNotCleanedWarning | Target ID exists, but soft_link: true has not been removed |
| **W006** | DeprecatedDependencyWarning | Active node depends on a deprecated node |
| **W007** | ArchivedDependencyWarning | An active node points to an archived node |
| **W008** | SupersedesStatusWarning | SUPERSEDES points to a node that is neither deprecated nor archived |
| **W009** | CrossScopeLinkWarning | Informational warning: Ontology relation crosses scope |
| **W010** | DuplicateTaxonomyRegistryEntryWarning | The same taxonomy_id is defined multiple times in the registry |
| **W011** | ConcreteFacetValueRecommendedWarning | Domain object specifies [unknown] on a facet where a concrete enum is pending (D39) |
| **W012** | FutureLastModifiedWarning | `last_modified` lies in the future |
| **W013** | UnverifiedChangesWarning | `last_modified` is later than `last_verified`: content changed without re-confirmation |
| **W014** | SectionOwnershipViolationWarning | Static linter detected unrecognized template heading or multiple `## Notes` sections during read-only pass (OWN-001..003) |
| **W015** | HighDegreeWarning | Outbound link count exceeds threshold ($k > 20$) on a single node (GRAPH-004). Promotion-blocking: DPCP rejects candidates violating the cap |
| **W016** | LinkMirrorWarning | A frontmatter relation target is not mirrored as a Markdown/wikilink in body prose (VAL-011, the Redundancy Rule) |
| **W017** | MermaidSyntaxWarning | A ```mermaid block in body prose fails deterministic syntax validation (VAL-012); degrade in place to a ```text fence with the LINT_FAILURE marker |

---

### 10.3 Error Code Allocation (Normative Registry)

The base linter (`linter.py`) owns the range `E000`–`E052`, registry validation owns
`E080`–`E086`, and the base warning framework owns `W001`–`W017`. Every
additive pipeline SHALL implement its errors in its own validator/pipeline
namespace and SHALL NOT mix them into the base linter's error code contract.

| Range | Owner | Document | Allocated in this version |
|---|---|---|---|
| `E000`–`E031`, `E050`–`E052` | Base linter & Agent Skills | `VALIDATION.md` §10.2, `AGENT-SKILLS.md` | `E000`–`E031`, `E050`, `E051`, `E052` |
| `E053`–`E079`, `E087`–`E099` | Reserved for the base linter | `VALIDATION.md` | — |
| `E080`–`E086` | YAML Registry Validation | `VALIDATION.md` §10.2, `trashheap/registry/validator.py` | `E080`–`E086` |
| `E101`–`E129` | Ingestion Engine (trajectory specialization and raw capture) | `INGEST.md` §2, `INGEST-CORE.md` | `E101`–`E125`, `E102A` (`E106`–`E107` reserved) |
| `E130`–`E149` | Universal Source Extension | `UNIVERSAL-SOURCE-EXTENSION.md` §12 | `E130`–`E134`, `E141` |
| `E150`–`E169` | Relation Extraction & Entity Linking | `RELATION-EXTRACTION.md` §2 | `E150`–`E162` |
| `E201`–`E249` | Graph Intelligence Delta | `GRAPH-INTELLIGENCE.md` §3 | `E201`–`E207` |
| `E250`–`E269` | Interactive Graph Visualization | `VISUALIZE.md` §2 | `E250`–`E259` |
| `E301`–`E399` | Structural Knowledge Graph | `STRUCTURAL-GRAPH.md` §15.6 | — (none in v0.1.0) |
| `E401`–`E499` | OKF interoperability adapter | `OKF-INTEROP.md` §16.8 | — (none in v0.1.0) |
| `W001`–`W017` | Base linter | `VALIDATION.md` §10.2 | `W001`–`W017` (all) |
| `W018`–`W099` | Reserved for extensions | — | — |

**Allocation invariants:**

- **ERR-001**: An error code MAY belong to exactly one owner. Two documents MUST NOT
  declare the same code.
- **ERR-002**: An extension SHALL allocate codes from its own assigned
  range; it MUST NOT reuse or extend the base linter's range.
- **ERR-003**: Each new code SHALL be registered in the table above in the same change
  as it is introduced.
- **ERR-004**: Warning codes SHALL NOT be introduced by extensions before
  the base system's warning framework (`W001`–`W017`) is implemented
  (cf. `GRAPH-INTELLIGENCE.md` §14).

### 10.4 Specification status versus implementation status

`Production Locked` is not an implementation claim. Every specification and
extension SHALL report two independent statuses:

| Status axis | Values | Meaning |
|---|---|---|
| Specification status | `PROPOSED`, `DRAFT`, `RELEASE_CANDIDATE`, `LOCKED` | Design maturity and normative intent |
| Implementation status | `UNIMPLEMENTED`, `PARTIAL`, `IMPLEMENTED`, `CONFORMANCE_TESTED`, `PRODUCTION_VERIFIED` | Exercised runtime coverage |

`LOCKED / UNIMPLEMENTED` is valid. A document MUST NOT use `Production Locked`
as shorthand for runtime validation. A conformance claim requires the relevant
registry, implementation, tests and CI rows to be present and green.

### 10.5 Conformance ownership and evidence

`spec_ownership.yaml` is the machine-readable ownership projection; the
normative rule text remains in the owner named there. Each invariant family
MUST have exactly one owner, and each owner MUST identify the invariant IDs it
defines, the relevant registry/policy inputs, and the conformance test target.
Companion documents MAY link to an invariant but MUST NOT redefine its
semantics. A conformance result MUST cite the owner, invariant ID, implementation
path (or `UNIMPLEMENTED`), test path (or `planned`) and verification command.

Missing implementation, test or CI evidence MUST remain `UNIMPLEMENTED`,
`PARTIAL` or `planned` as applicable; documentation or a registry entry alone
MUST NOT upgrade implementation status. The conformance owner is responsible
for resolving duplicate ownership and for keeping cross-document references
consistent before a claim is made.

**CONFORM-001**: Conformance vocabulary, ownership, evidence fields and status
semantics MUST be deterministic and centrally checkable through
`spec_ownership.yaml` and this section.

**Extension invariant families.** The base register above covers base-linter
invariants only. Extension families are owned by their own documents and are listed
here for navigation: `DELTA-CORE-001`–`007` (`GRAPH-INTELLIGENCE.md` §3),
`INGEST-CORE-001`–`022` (`INGEST.md` §2), `SG-001`–`020` (`STRUCTURAL-GRAPH.md` §15.3),
`OKF-001`–`012` and `BUNDLE-001`–`009` (`OKF-INTEROP.md` §16.3, §17.4).

> **Historical note:** `Graph Intelligence Delta` previously declared
> `E101`–`E107`, which collided with the ingestion engine's `E101`–`E124`.
> The delta codes are renumbered to `E201`–`E207` per **ERR-001**.

### 10.6 Verification Integrity, Link Mirroring and Rendering Degradation

To ensure resilient knowledge representation across diverse consumer runtimes and uncompromised epistemic promotion, the validation subsystem enforces three specific operational rules:

1. **Dual-Representation Link Mirroring (The Redundancy Rule / VAL-011)**:
   Every semantic relationship declared in frontmatter (`relations`) MUST also be mirrored as a valid Markdown link (`[Target Title](./path/to/TARGET-ID.md)`) in the document body prose. Conversely, all cross-article Markdown links in body prose should correspond to declared relationships. This dual-representation guarantees that readers and tools operating purely on prose (e.g. standard markdown readers, OKF-only parsers, web renderers) and graph-aware compilers retain 100% graph visibility without structural breakage.

2. **Graceful Mermaid Degradation & Auto-Heal (VAL-012)**:
   When a generated or ingested Mermaid diagram (` ```mermaid `) fails AST or syntax parsing, the compiler/linter MUST NOT crash the pipeline or break frontend visualization. Instead, the compiler MUST gracefully degrade the block in place to a standard code fence (` ```text `) prefixed with an explicit diagnostic marker:
   `<!-- LINT_FAILURE: mermaid syntax error: <details> -->`
   This preserves readability, prevents rendering explosions, and surfaces the failure in the diagnostic queue so an automated self-healing pass can attempt re-generation on the next compilation cycle.

3. **Uncheatable Non-Neural Verifier Mandate (VAL-013)**:
   Promotion of candidates to a governed canonical lifecycle status (`status: established`) and assignment of verification stamps (the flat `verification` field together with a `reviewer` actor, per `EPISTEMOLOGY.md` and `SCHEMA.md`) SHALL NEVER be granted solely by a generative LLM self-evaluation ("I have verified this and it is correct"). All promotion and verification transitions require passing the deterministic, non-neural 5-layer validation pipeline (`VALIDATION.md` Layers 1–5). Neural models propose; deterministic non-neural verifiers validate and commit.

4. **Anti-Runaway Loop Fence (The 40% Rule / VAL-014)**:
   Agent execution harnesses and tool orchestrators MUST maintain an in-memory sliding hash ring of recent tool calls (tool name + canonicalized arguments). If identical tool call signatures repeat $\ge 5$ times without state mutation, or if repeated identical failures consume $\ge 40\%$ of the agent's allocated token/turn budget, the execution harness MUST immediately trip the circuit breaker, abort execution, and emit `E052: RunawayLoopError` rather than burn compute in a degenerate loop.

---

## 11. Formal System Invariants

System invariants are immutable rules that must always be satisfied.

### 11.1 Architecture Invariants

| Invariant-ID | Domain | Rule | Error code |
|---|---|---|---|
| **CANON-001** | Architecture | Canonical Knowledge Objects and the normative registries are the source of truth | - |
| **CANON-002** | Architecture | Every derived artifact MUST be fully rebuildable from the canonical objects; a graph database MUST NOT become the real database | - |
| **CANON-003** | Architecture | A derived artifact MUST carry `corpus_hash`, algorithm and policy version so it can be invalidated deterministically | - |
| **CANON-004** | Architecture | Derived data MUST NOT be written into a knowledge object's frontmatter | - |
| **CANON-005** | Architecture | The evidential source of truth (raw sources) and the architectural source of truth (canonical objects) MUST NOT be conflated; derived artifacts rebuild from canonical objects, never directly from raw sources | - |
| **CANON-006** | Architecture | The LLM reasons; deterministic code writes. Structural operations (file creation, slugging, ID allocation, relation and inverse-view maintenance, merging, indexing, hashing) SHALL be performed by deterministic code | - |
| **SOURCE-001** | Universal Source | All external and internally captured information MUST enter through the Universal Source Model | - |
| **SOURCE-002** | Universal Source | Source types MUST remain orthogonal to Knowledge Object types, taxonomy, facets, relations, actors and epistemic status | - |
| **SOURCE-007** | Universal Source | Source identity and representation identity MUST be distinguishable | - |
| **SOURCE-008** | Universal Source | Source representations MUST be immutable; changes create new representations | - |
| **SOURCE-010** | Universal Source | Personal thoughts, ideas, questions and hypotheses MUST NOT automatically become verified evidence | - |
| **SOURCE-015** | Universal Source | Identity contracts differ by Artifact, Event and Experience and MUST be deterministic | - |
| **SOURCE-016** | Universal Source | Representation event metadata MUST NOT alter intrinsic source category | - |
| **SOURCE-017** | Universal Source | Source classification MUST NOT replace Knowledge taxonomy or object classification | - |
| **SOURCE-018** | Universal Source | Sources and canonical objects have many-to-many traceability | - |
| **SOURCE-019** | Universal Source | Source, representation, semantic and Knowledge deduplication are separate decisions | - |
| **SOURCE-020** | Universal Source | Raw representations are lossless and append-only | - |
| **RAW-001** | Capture | Captured representations MUST NOT be modified in place | - |
| **RAW-002** | Capture | Every raw representation MUST be addressable by Source and Representation IDs and retain its content hash | - |
| **RAW-003** | Capture | Changed representations create new immutable representations linked by `supersedes` | - |
| **RAW-004** | Capture | Raw capture is lossless; normalization and extraction write derived artifacts separately | - |
| **RAW-005** | Capture | Content hash deduplication MUST NOT replace Source or Representation identity | - |
| **RAW-006** | Capture | Content backend selection MUST NOT alter provenance or identity semantics | - |
| **RAW-007** | Storage | Source Storage, staging and canonical Knowledge Storage have separate ownership and retention rules | - |
| **RAW-008** | Storage | Capture/import manifests MUST preserve integrity and backend metadata for audit/reconstruction | - |
| **RAW-009** | Storage | Raw capture MUST use a crash-safe commit sequence and be recoverable independently of normalization/promotion | - |
| **RAW-010** | Storage | Same Source identity plus same representation hash is idempotent; same representation identity plus different hash fails closed | E141 |
| **EPI-004** | Epistemology | Evidence MUST be contextualized with respect to a proposition, claim, observation or inference target | - |
| **EPI-005** | Epistemology | Source or Experience capture MUST NOT by itself promote evidence, verification, authority or consensus | - |
| **PROV-004** | Provenance | Canonical relations and derived inferences MUST retain provenance like Knowledge Objects | - |
| **LIB-001** | Architecture | A Knowledge Library is typed objects + indexes + relations + policies, not a directory tree | - |
| **LIB-002** | Architecture | The directory structure MUST NOT carry semantics absent from taxonomy_registry.yaml | - |

Owning document: `ARCHITECTURE.md` §2.2–§2.3.

### 11.2 Metadata Invariants

| Invariant ID | Domain | Rule |
|---|---|---|
| **META-001** | Metadata | Each frontmatter field SHALL belong to exactly one of the 9 metadata categories (§1.2) |
| **META-002** | Metadata | No frontmatter field may be unallocated or belong to multiple categories |

### 11.3 Ontology Invariants

| Invariant ID | Domain | Rule | Error code |
|---|---|---|---|
| **REL-001** | Ontology | relation_registry.yaml is the only source of truth for canonical relations | - |
| **REL-002** | Ontology | RelationTypeEnum in code MUST be deterministically generated from relation_registry.yaml | - |
| **REL-003** | Ontology | Each canonical non-symmetric relation MUST declare an inverse_view name; uniqueness is enforced by REL-008 / E025 | - |
| **REL-004** | Ontology | Virtual inverse relations MUST NOT be persisted in YAML source files | E019 |
| **REL-004a** | Ontology | Graph metrics (degree, orphan status, connectivity) SHALL be computed over persisted canonical edges only, never over inverse views | - |
| **REL-005** | Ontology | Links in the ontology MUST satisfy source_types and target_types in relation_registry.yaml | E021 |
| **REL-006** | Ontology | All relations in relation_registry.yaml MUST declare source_types and target_types | E022 |
| **REL-007** | Ontology | All types in source_types and target_types MUST exist in ObjectTypeEnum | E023 |
| **REL-008** | Ontology | Each canonical **non-symmetric** relation MUST have a unique inverse_view name. A symmetric relation MUST set inverse_view to its own name and is exempt from the uniqueness check | E025 |
| **REL-009** | Ontology | Where two canonical relations express the same fact in opposite directions, the documented object SHALL declare the relation (`DOCUMENTED_BY`), not the documenting object | E031 |

### 11.4 Taxonomy Invariants

| Invariant ID | Domain | Rule | Error code |
|---|---|---|---|
| **TAX-001** | Taxonomy | Each specified taxonomy_id MUST correspond to a node in taxonomy_registry.yaml | E017 |
| **TAX-002** | Taxonomy | taxonomy_path + scope SHALL deterministically compute the disk path (§1.3) | E002 |
| **TAX-003** | Taxonomy | Two different taxonomy_path strings within the same scope MUST NOT normalize to the same disk path | E003 |
| **TAX-004** | Taxonomy | If taxonomy_id is specified, taxonomy_path and scope MUST exactly match the canonical data in taxonomy_registry.yaml | E016 |
| **TAX-005** | Taxonomy | parent_id in taxonomy_registry.yaml MUST point to an existing node within the same scope | E018 |
| **TAX-006** | Taxonomy | taxonomy_registry.yaml SHALL form an acyclic forest structure (forest) per scope | E024 |
| **TAX-007** | Taxonomy | taxonomy_path MUST be a flat leaf-name identical to the registry node's `name`; breadcrumbs MUST NOT be used | E016 |
| **TAX-008** | Taxonomy | A node's optional `description` is documentation and a boundary guard only; it MUST NOT affect path computation or validation | - |
| **TAX-009** | Taxonomy | The taxonomy SHALL classify subject only; it MUST NOT encode object_type, lifecycle, audience or relations | - |

### 11.5 Identity Invariants

| Invariant ID | Domain | Rule | Error code |
|---|---|---|---|
| **ID-001** | Identity | Each ID MUST match ID_PATTERN and start with PERS- for personal scope or ENG- for engineering | E005 |
| **ID-002** | Identity | The TYPE segment in an ID MUST equal TYPE_CODES[object_type] | E005 |
| **ID-003** | Identity | Year object types MUST use YEAR_TAG_PATTERN. Domain object types MUST use DOMAIN_TAG_PATTERN | E005 |
| **ID-004** | Identity | Object IDs MUST be globally unique. The sequence namespace is (scope, object_type, tag) with a ceiling of 9999 | E001/E008 |
| **ID-005** | Identity | Engineering-only object types specified in ENGINEERING_ONLY_OBJECT_TYPES MUST NOT be used under scope: personal | E006 |

### 11.6 Facet Invariants

| Invariant ID | Domain | Rule | Error code |
|---|---|---|---|
| **FAC-001** | Facets | Mandatory facets according to §3.1 MUST be specified for each object type. If multi-valued (1..N) at least one value MUST be specified | E020 |
| **FAC-002** | Facets | Facet lists MUST NOT be empty (E013), contain duplicates (E014) or mix none with concrete enums (E015) | E013/E014/E015 |
| **FAC-003** | Facets | Every facet value MUST exist in facet_registry.yaml; `none` only where the facet declares `allows_none: true` | E026 |
| **FAC-004** | Facets | FacetEnum types in code MUST be generated deterministically from facet_registry.yaml | - |

### 11.7 Other Invariants

| Invariant ID | Domain | Rule | Error code |
|---|---|---|---|
| **CLS-001** | Classification | `domain` MUST be a value listed in the `domains` block of object_registry.yaml | E027 |
| **CLS-002** | Classification | `len(domains) < len(nodes)`, and `domains` MUST NOT enumerate a complete level of the tree | - |
| **SCOPE-001** | Organization | Scope is decided by portability: organisation-independent → `personal`, product/org-bound → `engineering` | - |
| **PROV-001** | Provenance | `author` and `reviewer` SHALL match ACTOR_PATTERN | E028 |
| **PROV-002** | Provenance | `author`/`reviewer` are separate roles; `last_modified`/`last_verified` are independent | - |
| **PROV-003** | Provenance | `confidence` is provenance, not an epistemic dimension; it MUST NOT be collapsed into the four dimensions | - |
| **VAL-001** | Validity | validity.valid_until MUST NOT be earlier than validity.valid_from | E007 |
| **VAL-011** | Links | Every semantic relationship in frontmatter MUST also be mirrored as a valid Markdown link in body prose (Redundancy Rule) | - |
| **VAL-012** | Rendering | Generated Mermaid diagrams failing AST/syntax validation MUST degrade in place to text blocks with error comment markers and trigger auto-heal | - |
| **VAL-013** | Verification | Canonical promotion and verification stamps SHALL NEVER be granted by generative LLM self-evaluation; requires deterministic 5-layer non-neural verifiers | - |
| **VAL-014** | Agent Harness | Repetition of identical tool call signatures >= 5 times without state mutation MUST trip the circuit breaker with E052 (The 40% Rule) | E052 |
| **EPI-001** | Epistemology | Epistemic dimensions (evidence, verification, authority, consensus) are orthogonal and SHALL NOT be automatically derived from one another | - |
| **EPI-002** | Epistemology | provenance.source_type SHALL describe the provenance source, never the claim's epistemic state | - |
| **EPI-003** | Epistemology | Epistemic ranking SHALL follow the formal algorithm in `EPISTEMOLOGY.md` §5.3 | - |
| **GOV-001** | Governance | status describes repository management status; facets.lifecycle describes the domain system's lifecycle. They MUST NOT be conflated | - |
| **GOV-002** | Governance | Disallowed status/consensus combinations MUST be rejected with E004 according to governance_policy.yaml | E004 |
| **GRAPH-001** | Graph | Cycle detection SHALL be executed separately per relation type where dag: true is specified in relation_registry.yaml, and across the composite transitive closure of the hierarchical edges (`PART_OF`, `INSTANCE_OF`, `TYPE_OF`). Restated from the owning document `ONTOLOGY.md` §Graph Invariants (D96) | E010 |
| **GRAPH-002** | Graph | Self-references (target == id) and identical duplicate relations (type, target) SHALL be rejected | E011/E012 |
| **GRAPH-003** | Graph | Ontology links without soft_link: true MUST point to an existing object ID in the repository | E009 |
| **GRAPH-004** | Graph | Outbound relations from a single node SHALL NOT exceed the policy threshold `GRAPH-MAX-OUTBOUND-DEGREE` in threshold_policy.yaml. The cap is promotion-blocking: canonical promotion (DPCP) MUST reject candidates violating it | W015 |
| **RET-001** | Retrieval | Search results SHALL be deterministic. Fusion and conflict ranking SHALL execute the formal algorithms in §9.1–§9.3 | - |
| **RET-002** | Retrieval | The same query with the same parameters SHALL produce identical results | - |
| **RET-003** | Retrieval | An evidence bundle SHALL contain all fields necessary for LLM grounding | - |
| **RET-004** | Retrieval | Query execution SHALL be stateless and MUST NOT accumulate persistent contexts or search caches on disk | - |
| **RET-005** | Retrieval | Baseline retrieval (lexical + graph) SHALL operate 100% offline and air-gapped without external network calls | - |

> **Ownership note (D79–D95 reconciliation; corrected by D98).** The `RET`
> family is **owned by `specs/RETRIEVAL.md`** per
> `schemas/registry/spec_ownership.yaml`. This table is the consolidated
> *invariant register* that `specs/README.md` §3 assigns to `VALIDATION.md`
> (§10–§12, "system invariants"), and it MUST be kept in sync with the owner.
> `RET-004` and `RET-005` were introduced in `RETRIEVAL.md` by `5d33d1e` without
> being registered here, which left them outside the §12 conformance envelope
> (`META-001–RET-001`); they are registered so the suite has a complete list. On
> any divergence in semantics, `RETRIEVAL.md` wins per `specs/README.md` §1.

### 11.7 Section Ownership Invariants

| Invariant ID | Domain | Rule | Code |
|---|---|---|---|
| **OWN-001** | Authoring | Headings matching the normative Type A–D templates are machine-owned and regenerated on update | - |
| **OWN-002** | Authoring | At most ONE `## Notes` section is permitted per page. It is human-owned, append-only, and MUST be preserved byte-for-byte during regeneration | E051 |
| **OWN-003** | Authoring | Regenerating an unmodified page with an existing `## Notes` section MUST produce byte-identical file contents | - |
| **BODY-003** | Authoring | Unknown non-Notes sections MUST fail closed with E051 rather than be silently overwritten | E051 |
| **BODY-004** | Authoring | A manually changed machine-owned section MUST produce a reviewable conflict and MUST NOT be overwritten automatically | - |

### 11.8 Retrieval Threshold Invariants

| Invariant ID | Domain | Rule | Code |
|---|---|---|---|
| **THRESH-001** | Retrieval | All relevance and quality signals SHALL be normalised to `[0,1]` before fusion | - |
| **THRESH-002** | Retrieval | Internal cut-offs (e.g. edge strength, min cooccurrence chunks) are versioned policy defaults | - |
| **THRESH-003** | Retrieval | The operator-facing knob budget is capped at two: `min_confidence` and `min_relevance` | - |

### 11.9 Filesystem Tiers & Degraded Mode Invariants

| Invariant ID | Domain | Rule | Code |
|---|---|---|---|
| **FS-001** | Filesystem | Filesystem tiers SHALL be detected and reported: Tier 1 (local POSIX), Tier 2 (unknown/safe fallback), Tier 3 (NFS/network) | - |
| **FS-002** | Filesystem | On Tier-3 filesystems, single-writer semantics are assumed and documented | - |
| **FS-003** | Filesystem | Ingest and promotion operations SHALL validate `corpus_hash` to catch remote modifications | - |
| **FS-004** | Filesystem | A Tier-3 network filesystem run MUST NOT be reported as clean Tier-1 `pass` | - |

---

## 12. Conformance Test Suite

To guarantee complete machine verifiability for all formal system invariants (META-001–RET-005), automated tests are executed in CI:

### 12.1 Test structure

```
conformance/
├── test_metadata_categories.py           (Verifies META-001, META-002)
├── test_registry_sync.py                 (Verifies REL-001–REL-008, TAX-001–TAX-009, epistemic_registry)
├── test_identity_and_paths.py            (Verifies ID-001–ID-005, TAX-002, TAX-003)
├── test_graph_integrity.py               (Verifies GRAPH-001–GRAPH-004)
├── test_facet_cardinality.py             (Verifies FAC-001–FAC-004, CLS-001, CLS-003)
├── test_epistemology_governance.py       (Verifies EPI-001, PROV-005–007, GOV-002 and validity)
├── test_taxonomy_validation.py            (Verifies taxonomy identity and registry integrity)
├── test_relation_validation.py            (Verifies relation-registry-integritet)
├── test_retrieval_models.py              (Verifies retrieval-parametrar och THRESH-001..003)
├── test_retrieval_index.py               (Verifies deterministiskt objektindex)
├── test_retrieval_lexical.py             (Verifies deterministic lexical search)
├── test_retrieval_graph.py               (Verifies bounded BFS graph expansion)
├── test_retrieval_fusion.py              (Verifies RRF-fusion)
├── test_retrieval_conflicts.py            (Verifies epistemisk konfliktranking)
├── test_evidence_bundle.py                (Verifies evidence bundle-schema)
└── test_retrieval_end_to_end.py           (Verifies end-to-end retrieval flow)
```

### 12.2 Test requirements

- All tests SHALL run in the CI/CD pipeline
- All tests SHALL return exit code 0 on successful validation
- The tests SHALL be deterministic
- Where a metric is computed by two components (for example orphan/degree counts by
  both the graph validator and the linter), the suite SHALL assert the two
  **independent code paths agree**. Asserting one implementation against itself cannot
  detect a shared wrong assumption (`research/critiques-and-community-feedback.md` L4)
- The tests SHALL cover all invariants

### 12.3 CI/CD Integration

```yaml
# .github/workflows/conformance.yml
name: Conformance Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run all conformance tests
        run: python -m pytest conformance/
```

---

## Linter CLI Interface

### Usage

```bash
# Run all validations
python linter.py

# Run with an injected clock (VALID-CLOCK-001)
python linter.py --now 2026-08-19

# Run on a specific file
python linter.py personal/11_datavetenskap/PERS-ART-AI-0001.md

# Run on a specific scope
python linter.py --scope personal

# Show help
python linter.py --help
```

### Exit Codes

| Exit code | Meaning |
|---|---|
| 0 | All validations succeeded (no ERRORs) |
| 1 | One or more ERRORs were detected |
| 2 | Warning detected under `--strict` mode |
| 3 | Invalid CLI argument or configuration error |
| 4 | Target file or directory not found |

### Output Format

```json
{
  "files_checked": 42,
  "errors": [
    {
      "code": "E002",
      "message": "Disk path does not match computed slug",
      "file": "personal/11_data/ART-0001.md",
      "line": 1,
      "suggestion": "Move file to: personal/11_computer_science_it_security_ai/11.01_artificial_intelligence/PERS-ART-AI-0001.md"
    }
  ],
  "warnings": [
    {
      "code": "W002",
      "message": "next_review has passed",
      "file": "personal/11_data/ART-0002.md",
      "line": 430
    }
  ],
  "summary": {
    "errors": 1,
    "warnings": 1,
    "passed": 40
  }
}
```