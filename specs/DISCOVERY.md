# LLM Wiki Discovery & Promotion Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-DISCOVERY-001`
> **Document family ID**: `LLM-WIKI-KG-DELTA-001`
> **Version**: `1.0.0`
> **Updated**: `2026-08-17`
> **Source**: Extracted from `LLM-WIKI-KG-DELTA-001` §5.2, §6, §10
> **Status**: `PROPOSED`
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status
> **Compatibility target**: Additive, isolated, opt-in (Phase 4–5)
> **Base specification**: `EPISTEMOLOGY.md` §5.4 (governance policy), `VALIDATION.md` §10
> **Companion documents**: `GRAPH-INTELLIGENCE.md` (delta core), `GRAPH-RETRIEVAL.md`
> **Normative owner**: This document owns discovery, candidate formation and promotion-boundary semantics
> **Related documents**: `UNIVERSAL-SOURCE-EXTENSION.md`, `INGEST-STAGING.md`, `ONTOLOGY.md`, `RETRIEVAL.md`

---

## 5. Versioned data contracts (discovery part)

Internal discovery cut-offs, including duplicate similarity and cooccurrence
boundaries, are owned by `schemas/registry/threshold_policy.yaml` (THRESH-002).

The general artifact contract for derived and discovery records is specified in
`GRAPH-INTELLIGENCE.md` §5. This document specifies only the discovery-record
part of that contract, together with its lifecycle (§6) and generation rules
(§10). Section numbering is preserved across the document family so that
cross-references remain stable.

### 5.2 Discovery candidate

Discovery candidates are a discriminated union. Relation candidates refer to existing canonical nodes; a `node_proposal` may intentionally have no canonical target yet. A node proposal is not a canonical relation and MUST NOT be serialized as one.

Discovery accepts normalized Sources from Artifact, Event and Experience
categories. Experience captures (thoughts, ideas, questions and hypotheses) may
produce candidates, but are not automatically evidence or canonical objects.

Discovery is category-aware but epistemically orthogonal: Artifact captures are
normally stronger extraction inputs, Event captures require temporal/actor
context, and Experience captures normally produce inferred or hypothesis
candidates. These are discovery signals, not replacements for evidence,
verification, authority or consensus.

```python
class DiscoveryBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: str
    candidate_type: Literal["relation_proposal", "duplicate", "knowledge_gap", "node_proposal"]
    confidence: float = Field(ge=0.0, le=1.0)
    status: Literal["pending", "reviewed", "approved", "promoted", "rejected", "expired", "superseded"] = "pending"
    created_at: datetime
    expires_at: datetime
    scope: str
    corpus_hash: str
    algorithm_version: str
    evidence_refs: list[str]
    source_refs: list[str]
    representation_refs: list[str]
    evidence_unit_refs: list[str]
    derivation_ref: str

class RelationDiscoveryCandidate(DiscoveryBaseModel):
    candidate_type: Literal["relation_proposal", "duplicate", "knowledge_gap"]
    source_id: str
    target_id: str
    suggested_relation: str | None = None

class NodeDiscoveryCandidate(DiscoveryBaseModel):
    candidate_type: Literal["node_proposal"]
    trigger_source_ids: list[str]
    suggested_title: str
    suggested_domain: str | None = None
    suggested_taxonomy_id: str | None = None
```

`source_refs`, `representation_refs`, `evidence_unit_refs` and `derivation_ref`
form the mandatory lineage envelope for every candidate (**DISC-001**). Candidate-specific source
fields remain convenience fields and MUST be consistent with the envelope. The
envelope is the discovery projection of the provenance contract in
`UNIVERSAL-SOURCE-EXTENSION.md`, not a second source of truth.

For `RelationDiscoveryCandidate`, `source_id` and `target_id` MUST refer to existing canonical objects at generation time. For `NodeDiscoveryCandidate`, `trigger_source_ids` MUST refer to existing canonical objects; the class has no `source_id` or `target_id` fields because it is not a relation candidate. `suggested_relation`, when present, MUST exist in the relation registry and satisfy source/target constraints before promotion. `expires_at` is mandatory for all discovery candidates and MUST be no later than 90 calendar days after `created_at` (**DISC-005**); the general artifact contract permits `expires_at: null` only for non-expiring derived artifacts.

## 6. Discovery lifecycle and promotion

Promotion is not currently a base-system workflow. The base `governance_policy.yaml` enforces status/consensus combinations, but it does not create approvals, patches, commits, or audit transitions. Phase 5 MUST therefore introduce an explicit Delta promotion command and approval record; it MUST NOT assume an existing ordinary workflow.

The lifecycle is:

```text
pending → reviewed → approved → promoted
       ↘ rejected
       ↘ expired
       ↘ superseded
```

Every transition MUST record:

- previous status;
- new status;
- actor or process identity;
- UTC timestamp;
- reason;
- validation result;
- optional canonical commit/reference.

Promotion MUST:

1. validate the candidate schema;
2. verify source and target still exist and hashes are current;
3. validate the proposed relation against `relation_registry.yaml`;
4. reject virtual inverse relations;
5. reject duplicates and self-references;
6. run the relevant base Layer 1–5 validation;
7. require explicit approval;
8. write canonical changes only through an explicit promotion command that creates a review artifact, validates the proposed patch, and requires a human approval record; the base governance policy validates status/consensus combinations but does not itself define a write workflow;
9. retain the discovery audit record.

Discovery expiry MUST archive the candidate as `expired`; it MUST NOT physically delete the audit record.

## 10. Discovery rules

### 10.1 Potential duplicates (DISC-002)

A duplicate candidate requires cosine similarity at or above the configured threshold within the same scope (**DISC-002**). Pair identity MUST be canonicalized as:

```text
(min(node_id_a, node_id_b), max(node_id_a, node_id_b))
```

The pipeline MUST deduplicate repeated observations and preserve prior rejected/superseded decisions.

### 10.2 Knowledge gaps & opportunities

Knowledge gaps represent areas where the graph is missing relationships, evidence, or syntheses. Discovery distinguishes **Topological Gaps** (textual/semantic proximity without canonical edges) and **Ontological Gaps** (structural incompleteness against expected relation patterns).

#### 10.2.1 Topological Knowledge Gaps (DISC-003)
A topological gap candidate is generated only when at least two of these three predicates are true (**DISC-003**):

```text
A = same_scope_and_community
B = contextual_cooccurrence >= 3 chunks
C = semantic_similarity >= 0.80
gap_candidate = (A and B) or (A and C) or (B and C)
```

The candidate MUST not already have a canonical relation, MUST not be self-referential, and MUST pass scope and object-type policy. The exact predicate results MUST be stored as evidence.

#### 10.2.2 Ontological & Structural Gaps (Opportunities / DISC-004)
Discovery scans canonical and staged graphs for structural incompleteness patterns (**DISC-004**):
1. **`unresolved_event`:** An `Incident` or `TroubleReport` with no outgoing `RESOLVED_BY` or `SATISFIES` relation to a `Lesson`, `Component`, or `Fix`.
2. **`unimplemented_lesson`:** A `Lesson` or `Principle` that defines an empirical finding or recommendation but has no incoming `SATISFIES`, `INTRODUCED_IN`, or `IMPLEMENTS` relation from any canonical `Workflow`, `Procedure`, or `Specification`.
3. **`unreconciled_conflict`:** Two or more canonical `Claim` or `Fact` objects participating in a `CONTRADICTS` cluster with equal epistemic rank and no resolving synthesis node.

Ontological gap candidates are flagged with `candidate_type: "knowledge_gap"` and carry the structural pattern name in their metadata to guide operator and agent curation.

### 10.3 LLM-generated candidates

LLM extraction is optional and MUST require:

- model and prompt version;
- structured schema output;
- source document/chunk references;
- source spans or excerpts;
- temperature and seed metadata where supported;
- prompt-injection-safe handling of corpus text;
- explicit `best-effort` determinism classification.

An LLM output without source evidence MUST NOT become a promotion candidate.

Discovery MAY cluster sources by shared event, conversation, document, topic,
claim, idea or question and MAY synthesize across books, articles, messages,
experiments and personal captures. Every candidate MUST retain source and
representation references (that is, source and representation references are
mandatory lineage for every candidate). Contradiction detection is a discovery function;
it MUST propose conflicts for review and MUST NOT silently rewrite canonical
objects.

### 10.4 Automated Instruction Ingestion & Delimited Fence (DISC-009)

When the autonomous discovery or ingestion pipeline updates repository root instruction files (such as `AGENTS.md`, `CLAUDE.md`, or `.cursorrules`), it MUST strictly confine its automated updates within explicit delimiters:

```markdown
<!-- TRASHHEAP:START -->
... automated knowledge index, ontology summaries, and pointers ...
<!-- TRASHHEAP:END -->
```

- **DISC-009**: Automated injection of knowledge references into repository root instruction files (`AGENTS.md`, `CLAUDE.md`, etc.) MUST be enclosed strictly between `<!-- TRASHHEAP:START -->` and `<!-- TRASHHEAP:END -->`. Any content outside this delimited instruction fence is human-owned or operator-defined and MUST NOT be modified, reordered, or overwritten by automated tooling. If the delimiter comments are absent, tooling MUST append the delimited block at the end of the file rather than replacing existing content.

### 10.5 Swanson ABC Literature-Based Discovery (DISC-010)

Over large compiled citation/MeSH graph artifacts (CSR projections of the
PubMed-scale corpus), the system exposes Swanson-style A->B->C literature-based
discovery (`trashheap discover literature`):

- **DISC-010**: Literature-based discovery MUST be deterministic and
  artifact-driven: intermediate bridges B are ranked by the degree-normalized
  co-occurrence score `(co_A(B) * co_C(B)) / sqrt(deg(B))` with a total-order
  tie-break on the bridge node index; the MeSH/article partition MUST be derived
  from the compiled `node_mapping.parquet` at query time (no hardcoded index
  boundaries); all SQL over compiled artifacts MUST be parameterized; and the
  Swanson disjointness precondition MUST be measured and reported
  (`articles_discussing_both`), never assumed. Results are discovery candidates
  in the sense of DISC-001: they propose, and governed review decides.

---

**End of LLM Wiki Discovery & Promotion Specification v1.0.0**

See also: `GRAPH-INTELLIGENCE.md` (delta core), `EPISTEMOLOGY.md` §5.4 (governance policy).