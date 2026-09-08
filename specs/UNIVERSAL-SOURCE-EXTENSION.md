# LLM Wiki Universal Source & Knowledge Compilation Extension

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-SOURCE-EXT-001`
> **Version**: `0.2.0`
> **Updated**: `2026-08-17`
> **Baseline**: v3.8.10
> **Source**: Architectural extension derived from the Universal Source review and current ingestion model
> **Status**: `PROPOSED`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Compatibility target**: Opt-in; no change to baseline canonical objects or retrieval
> **Normative owner**: This document owns SOURCE-001..SOURCE-020; storage invariants RAW-001..RAW-010 are owned by `INGEST-STAGING.md`
> **Related documents**: `INGEST.md`, `INGEST-ADAPTERS.md`, `INGEST-DATA-MODEL.md`, `INGEST-STAGING.md`, `VALIDATION.md`

---

## 1. Purpose and non-goals

LLM Wiki is extended from trajectory-centric ingestion to a source-agnostic governed knowledge compiler. Every external or internally captured input first becomes a traceable Source representation. It does not become canonical knowledge merely because it was captured.

This extension does not replace the Knowledge Object model, object/taxonomy/facet/relation registries, epistemology, governance gates, Markdown+YAML canonical representation, or the existing trajectory commit protocol. It defines the missing source boundary above them.

## 2. Normative architecture principles

- **SOURCE-001**: All external and internally captured information MUST enter through the Universal Source Model.
- **SOURCE-002**: Source types MUST remain orthogonal to Knowledge Object types, taxonomy, facets, relations, actors and epistemic status.
- **SOURCE-003**: Agent trajectories are one specialized Event source type and MUST NOT define the general ingestion abstraction.
- **SOURCE-004**: Capture MUST be possible without prior canonical classification.
- **SOURCE-005**: Discovery MAY derive candidates and Knowledge Objects from Sources but MUST NOT mutate a Source into a Knowledge Object.
- **SOURCE-006**: Every canonical Knowledge Object MUST retain traceable provenance to one or more Sources.
- **SOURCE-007**: Source identity and representation identity MUST be distinguishable.
- **SOURCE-008**: Source representations MUST be immutable; changed content creates a new representation linked by `supersedes`.
- **SOURCE-009**: Source type, Knowledge Object type, Actor identity and taxonomy are separate namespaces.
- **SOURCE-010**: Personal thoughts, ideas, questions and hypotheses MUST NOT automatically be treated as verified evidence.
- **SOURCE-011**: Connectors acquire external data; adapters normalize it; ingestion validates and stages it; governance determines canonical promotion.
- **SOURCE-012**: Source access and privacy constraints MUST propagate through derivation according to governance policy. The source registry does not own security policy.
- **SOURCE-013**: Re-ingestion of a canonical Knowledge Object is an ingest mode (`create`, `update`, `migrate`, `reingest`), not a source type.
- **SOURCE-014**: Universal ingestion MUST use a common envelope with a typed payload; it MUST NOT flatten away source-specific richness.
- **SOURCE-015**: Artifact identity MUST use a resource/external identity or content hash; Event identity MUST include occurrence context; Experience identity MUST include actor, time and content identity.
- **SOURCE-016**: A representation MAY carry event metadata or represent an Event; this MUST NOT change its intrinsic source category.
- **SOURCE-017**: Source classification MUST NOT replace Knowledge taxonomy or object classification.
- **SOURCE-018**: A source MAY contribute to multiple derived objects and a canonical object MAY cite multiple source representations.
- **SOURCE-019**: Source identity deduplication, representation deduplication, semantic duplicate detection and Knowledge duplicate detection are separate decisions.
- **SOURCE-020**: Raw representations MUST be lossless and append-only; normalization MUST retain a reference to the raw representation.

## 3. Universal Source Model

The model has three stable top-level categories:

- **Artifact**: a durable, addressable information-bearing representation (web resource, book, code, email message, chat capture, diagram, dataset, configuration).
- **Event**: an occurrence or interaction at a time (meeting, call, commit, CI run, incident, experiment run, agent trajectory).
- **Experience**: an actor-bound cognitive or subjective capture (thought, idea, question, observation, insight, hypothesis, doubt, assumption, reflection, learning, intention, memory, contradiction notice or affective note).

The categories are a stable top-level partition, not a claim that every external
representation has only one physical aspect. Email, chat and calendar entries
are normally Artifacts with event metadata; a Meeting, Deployment or Incident is
an Event. A transcript, recording or meeting note is an Artifact that references
the Event. A Decision is normally a Knowledge Object candidate, not a generic
Source Event. A ticket is an Artifact/record that may report an Incident.

A source record has a common envelope and typed payload:

```yaml
source:
  source_id: SRC-...
  source_type: web_resource
  category: Artifact
  medium: web
  semantic_kind: article
  captured_at: 2026-08-17T18:31:22Z
  lifecycle: captured
  identity:
    canonical_uri: https://example.test/article
  representation:
    representation_id: REP-...
    representation_hash: sha256:...
  payload: {}
```

`source_registry.yaml` is normative for source categories, source types, identity fields, provenance requirements, lifecycle and legacy mappings. It does not own object types, actors, taxonomy or policy.

The registry also defines a separate source-classification projection
(`source_taxonomy`). It is usable for adapter routing and discovery only and
MUST NOT be confused with `taxonomy_registry.yaml`, which classifies Knowledge
Object subject matter.

## 4. Source identity, representation and raw boundary

The system MUST distinguish:

```text
Source identity        = the external/internal thing
Representation         = what was captured at a particular time
Content object         = immutable bytes/content addressed by hash
Normalized Source Record = validated internal envelope + typed payload
```

A changed URL, document, conversation export or repository state creates a new representation; historical evidence MUST NOT be mutated. The raw capture layer is append-only and is the lossless boundary:

```text
capture → raw immutable representation → normalized source record
        → evidence/experience → discovery → staging → governance → knowledge
```

`deleted` in the source lifecycle is a logical availability state, not a raw
overwrite or untracked physical deletion. Raw bytes and audit manifests remain
subject to the retention policy owned by `INGEST-STAGING.md`; any permitted
physical deletion MUST leave an auditable tombstone with the source ID,
representation ID, hash and deletion decision.

The physical storage strategy (per-source directories, content-addressable objects, Git/LFS or external blob storage) is an implementation decision. It MUST preserve source, representation and content identity separately.

## 5. Evidence and epistemic boundary

The following concepts MUST remain distinct:

```text
Source       captured origin
Observation  normalized/extracted observation from a source
Evidence     an observation or source span used in relation to a proposition
Claim        a candidate or canonical proposition
Experience   actor-bound thought, idea, question or hypothesis
```

A Source or Experience MUST NOT acquire evidential status merely by capture or ingestion. Evidence is contextual: it is evidence *for* a proposition. Until a final Evidence storage shape is promoted, every adapter and discovery path SHALL use the following non-canonical Evidence Unit projection:

```yaml
evidence_unit_ref: EU-...
observation_ref: OBS-...
source_refs: [SRC-...]
representation_refs: [REP-...]
span_or_location: "document://...#L10-L18"
target_ref: CLAIM-...   # proposition or candidate target
method: direct_observation | extracted_span | derived_measurement
verification_state: unverified | corroborated | verified | contradicted
```

An Evidence Unit is immutable, provenance-bearing staging data; it is not a
Knowledge Object and does not itself establish consensus or authority. The final
canonical Evidence shape remains a separate governed decision.

The normative conceptual flow is:

```text
raw Source representation → normalized Observation → Evidence-for-proposition
Experience → candidate interpretation → evaluation → optional Knowledge Object
```

`Observation` as a source/derived observation MUST NOT be treated as verified
evidence without a proposition, source span or observation context, method and
verification state. An Evidence record is therefore not necessarily a separate
Knowledge Object; its final storage shape remains a governed epistemic/edge
decision.

## 6. Actor model boundary

Actors are not source types and are not owned by `source_registry.yaml`.
`actor_registry.yaml` owns the minimal Actor namespace (Person, Organization,
Team, Group) and its `ACTOR-*` IDs. Provenance producer references use the
separate stable string namespace `human:<id>`, `process:<id>` or
`<producer>/<version>` and are validated by `ACTOR_PATTERN`/E028. A source
`actor_ref` or `actor_refs` MAY point to an `ACTOR-*` record, but actor identity
MUST remain separate from knowledge about an actor. Privacy and access rules
remain governed by the governance/security subsystem.

## 7. Normalized ingestion and adapter contract

```text
External system → Connector → Adapter → Normalized Source Record
                                      → validation/hash/provenance/staging
```

Connectors handle access and external API concerns. Adapters handle source-specific normalization. The ingestion core handles validation, representation hashing, provenance, idempotency and staging. Adapters MUST NOT write canonical Knowledge Objects directly.

The abstract contract covers URLs, files/directories/globs, archives, stdin, batches, repositories, database/API connectors, mailboxes, calendars and chat workspaces. Connector-specific schemas (Web, Email, Slack, Teams, Calendar, Git) are deferred to separate adapter specifications.

The input surface is normative at the boundary and includes: single files,
directories, globs, URL and URL-list inputs, stdin, archives, batches,
repositories, databases, API connectors, mailboxes, calendars and chat
workspaces. A connector MAY expose additional input forms only through the same
Connector → Adapter → Normalized Source Record contract.

## 8. Provenance and temporal traceability

Canonical objects MAY derive from multiple sources and MUST preserve:

```yaml
provenance:
  source_refs: [SRC-001, SRC-017]
  representation_refs: [REP-001, REP-017]
  derivation_ref: DR-173
  derived_at: 2026-08-17T20:00:00Z
```

Object provenance, relation provenance and derived-artifact provenance are all claims about lineage and SHOULD be equally traceable. The system SHOULD support “what did we know then?” through captured/observed timestamps, validity intervals, representation hashes and derivation timestamps. `derivation_ref` is a deferred extension until a derivation-event registry exists.

Every asserted object, canonical relation, discovery inference and derived
community report MUST have a provenance contract containing, as applicable:
`source_refs`, `representation_refs`, evidence-unit/source-span references,
derivation method, actor/process, confidence, and timestamps. A relation is a
claim and MUST NOT be treated as provenance-free merely because its endpoints
have provenance.

Negative provenance MAY record `considered`, `excluded`, `supporting` and
`contradicting` source roles in staging/audit records. These roles do not become
canonical ontology relations unless separately registered.

## 9. Discovery generalization

The generalized pipeline is:

```text
Source → extraction → candidate discovery → classification → deduplication
       → contradiction detection → staging → governance → canonical knowledge
```

Discovery candidates are never canonical by default. Personal capture may follow:

```text
Thought/Question → Idea/Hypothesis/Observation → candidate → optional Knowledge Object
```

Books/media may follow an explicit consumption event:

```text
Artifact → Reading/Viewing Event → Notes/Thoughts → discovery → knowledge
```

Question sources represent explicit knowledge gaps and MAY link to related concepts, motivating sources, answers and resolving experiments through the existing relation registry after those types are introduced.

Discovery weighting SHALL remain category-aware without collapsing epistemic
dimensions: Artifact-derived extracted spans are normally stronger extraction
signals; Event-derived observations require event context; Experience-derived
material is normally candidate/inference material and MUST retain its lower
epistemic boundary. A weighting is a discovery policy, not evidence,
verification, authority or consensus.

Discovery MAY perform source clustering (same event, conversation, document,
claim, topic, idea or question), cross-source synthesis and contradiction/gap
detection. These outputs remain derived candidates and MUST retain all source
and representation references.

## 10. Graph and retrieval implications

The architecture has a logical Source Graph and Knowledge Graph, but does not require two physical stores. A unified graph MAY use distinct namespaces and edge semantics. `DERIVED_FROM` connects canonical knowledge to source/representation lineage without making Sources Knowledge Objects.

Source-aware retrieval SHOULD support source, actor, event, experience, provenance and temporal queries in addition to Knowledge retrieval. Existing baseline retrieval remains unchanged until this extension is implemented and opted in.

Logical Source Graph and Knowledge Graph semantics MUST remain distinct even if
one physical graph is used. Source-aware traversal MAY answer “what did I think,
what happened, which source supported this, and what did actor X write?” but a
retrieved source path is not itself a canonical explanation. Temporal retrieval
MUST distinguish `captured_at`, `observed_at`, `occurred_at`, `published_at`,
`modified_at`, `experienced_at`, validity intervals and `derived_at`.

## 11. Governance and scope propagation

Source scope is input context, not a replacement for Knowledge Object scope. Derivation MUST apply governance policy explicitly; derived knowledge MUST NOT become more accessible than its source by default. Capture is cheap; canonicalization is expensive. Approval grants admissibility, not epistemic truth.

Source scope and derived-object scope are separate fields. The propagation and
access decision is owned by `governance_policy.yaml`; `source_registry.yaml`
MUST NOT define privacy, retention, PII or sharing policy. Personal journal and
affective captures MAY be restricted by policy, but that restriction is not a
new source category.

## 12. Error allocation and conformance

Source validation errors are owned by the ingestion subsystem and MUST NOT collide with the base linter's `E001`–`E050` or trajectory ingestion's already allocated `E101`–`E125`. The source extension therefore reserves `E130`–`E149` for future implementation. The range is owned by the ingestion subsystem as a whole; this extension does not create a competing error namespace:

| Code | Meaning |
|---|---|
| E130 | Missing source type |
| E131 | Unknown source type |
| E132 | Category mismatch |
| E133 | Missing required source field |
| E134 | Invalid source identity |
| E135 | Missing provenance requirement |
| E136 | Invalid representation hash |
| E137 | Invalid source timestamp |
| E138 | Invalid actor reference |
| E139 | Invalid source lifecycle transition |
| E140 | Invalid external identity |
| E141 | Duplicate source identity/representation |
| E142 | Mutable raw representation |
| E143 | Invalid ingest mode |
| E144 | Source access propagation violation |
| E145 | Invalid normalized source envelope |

Required future conformance tests include registry existence, unique types/aliases, category and field contracts, lifecycle transitions, unknown-type rejection, source/Object separation, identity idempotency, immutable representation handling and provenance round-trip.

### 12.1 Universal source coverage matrix

| Input family | Category/source types | Required identity | Primary derived signals | Canonical by capture? |
|---|---|---|---|---|
| Web and external documents | Artifact: `web_resource`, `document`, `specification`, `forum_post` | URI or external identity + representation hash | extracted spans, claims, concepts | No |
| Internal documentation | Artifact: `internal_document`, `meeting_notes`, `meeting_transcript` | system/external identity + representation hash + access context | extracted claims, decisions, requirements | No |
| Code and engineering data | Artifact: `code_repository`, `configuration`, `schema_definition`, `notebook`, `log_trace`, `dataset` | repository/resource identity + revision/hash | structural entities, relations, observations | No |
| Media | Artifact: `book`, `video_recording`, `audio_recording`, `presentation` | catalog/provider/resource identity + representation hash | notes, spans, concepts, claims | No |
| Communication | Artifact: `email_message`, `conversation_capture` | provider/system + message/thread/conversation identity | messages, topics, decisions, actions, questions | No |
| Calendar and work tracking | Artifact: `calendar_representation`, `ticket_record`; Event: `meeting`, `deadline`, `incident`, `deployment` | external identity plus occurrence context | events, observations, action/decision candidates | No |
| Agent runtime | Event: `agent_trajectory`, `ci_run`, `test_run`, `experiment_run` | runtime/external identity + occurrence/hash | deterministic evidence bundle, observations | No |
| Personal capture | Experience: `thought`, `idea`, `question`, `observation`, `hypothesis`, `reflection`, `learning`, `intention`, `memory`, `affective_note` | actor + time + content hash | candidate ideas, hypotheses, questions, lessons | No |

This matrix is a design/conformance target, not a claim that the adapters or
runtime validators already exist.

## 13. Normative delta map

| Existing owner | Required delta | Status |
|---|---|---|
| `ARCHITECTURE.md` | Add Universal Source boundary, Source≠Representation≠Content Object, raw append-only boundary; retain canonical/derived and CANON-006 | Proposed |
| `DATA_MODEL.md` | State Source ≠ Knowledge Object and source scope ≠ object scope | Proposed |
| `EPISTEMOLOGY.md` | Add capture ≠ evidence, contextual Evidence, source/representation lineage and relation provenance | Proposed |
| `INGEST.md` / `INGEST-PIPELINE.md` | Generalize normalized input from trajectory to Source Record; retain trajectory path | Proposed |
| `INGEST-ADAPTERS.md` | Make connector/adapter/core boundary normative | Proposed |
| `INGEST-DATA-MODEL.md` | Add common envelope + typed payload, Source Identity, Representation, Content Object and normalized record | Proposed |
| `INGEST-STAGING.md` | Define Source Storage/Capture Layer, content-addressable backend, staging separation, manifests and layer-specific retention | Proposed |
| `DISCOVERY.md` | Accept all source categories and retain candidate-only boundary | Proposed |
| `ONTOLOGY.md` | Add object/relation provenance and logical Source Graph separation without adding source types to object registry | Proposed |
| `RETRIEVAL.md` / `GRAPH-RETRIEVAL.md` | Define source-aware and temporal retrieval as opt-in | Proposed |
| `VALIDATION.md` | Reserve E130–E149, add source conformance matrix row, separate spec/implementation status | Proposed |
| `SCHEMA.md` / `README.md` | Document source registry as a separate namespace and this extension | Proposed |

### 13.1 Implementation-status matrix

| Contract | Specification status | Implementation status |
|---|---|---|
| Three-category Source Model | LOCKED within this extension | UNIMPLEMENTED |
| Source registry and source taxonomy | LOCKED within this extension | Declarative only |
| Actor namespace and policy ownership | LOCKED within this extension | Declarative only |
| Normalized Source Record | LOCKED within this extension | UNIMPLEMENTED |
| Raw append-only storage boundary | LOCKED within this extension | UNIMPLEMENTED |
| Source-aware graph/retrieval | PROPOSED/opt-in | UNIMPLEMENTED |
| Connector-specific adapters | DEFERRED | UNIMPLEMENTED |

## 14. Deliberate non-changes and deferred decisions

This extension does not change the canonical Knowledge Object unit, Markdown+YAML, object/taxonomy/facet/relation registries, existing epistemic dimensions, governance approval semantics, baseline retrieval, or the trajectory DSCP contract.

Deferred implementation decisions: physical graph split, final Evidence storage shape,
automated source credibility scoring, semantic source identity, connector-specific
schemas, multimodal decomposition and derivation-event registry. The architecture
does define source clustering, cross-source synthesis, negative provenance and
temporal retrieval contracts, but their runtime implementation remains deferred.

Thresholds MUST be classified by decision domain rather than silently merged:

| Class | Examples | Must not be confused with |
|---|---|---|
| quality | extraction confidence, deterministic evidence quality | relevance |
| relevance | semantic similarity, retrieval score | authority |
| graph | edge strength, path score | epistemic confidence |
| discovery | candidate acceptance, gap predicates | canonical approval |
| security | scope/access confidence | evidence strength |

Threshold values are policy-versioned and MUST carry rationale or calibration
status. No threshold may be presented as empirically validated before runtime
evaluation exists.

## 15. Implementation order

1. Freeze this additive specification and registry contract; no further ontology expansion is required for MVP.
2. Registry loader and source conformance tests.
3. Normalized Source Record with identity/versioning/idempotency.
4. Minimal Actor namespace and provenance integration.
5. Evidence/Experience boundary.
6. Generalized discovery and staging.
7. Source graph projections and source-aware retrieval.
8. Media/communication/calendar connectors.

Until these gates pass, this document MUST remain `Implementation status: UNIMPLEMENTED` even if the design status is `Proposed`.

---

See also: `ARCHITECTURE.md`, `DATA_MODEL.md`, `EPISTEMOLOGY.md`, `INGEST.md`, `INGEST-ADAPTERS.md`, `DISCOVERY.md`, `RETRIEVAL.md`, `VALIDATION.md`, and `schemas/registry/source_registry.yaml`.

**End of Universal Source & Knowledge Compilation Extension v0.2.0**
