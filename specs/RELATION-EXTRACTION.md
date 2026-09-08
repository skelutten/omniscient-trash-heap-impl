# LLM Wiki Relation Extraction & Entity Linking Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10  
> **Document ID**: `LLM-WIKI-REL-EXTRACTION-001`  
> **Document family ID**: `LLM-WIKI-INGEST-001`  
> **Version**: `1.0.0`  
> **Updated**: `2026-09-08`  
> **Status**: `PROPOSED`  
> **Implementation status**: See [`SPEC_STATUS.md`](./SPEC_STATUS.md) for canonical runtime & conformance status  
> **Compatibility target**: Additive, isolated, opt-in (Phase 3 & Phase 5)  
> **Base specification**: `ONTOLOGY.md`, `DISCOVERY.md`, `INGEST-PIPELINE.md`, `REVIEW-PROMOTION.md`  
> **Normative owner**: This document owns automated relation extraction, entity linking, co-reference resolution, and error family `E150–E169`  
> **Related documents**: `DATA_MODEL.md`, `SCHEMA.md`, `VALIDATION.md`, `GRAPH-INTELLIGENCE.md`  

---

## 1. Purpose & Core Philosophy

The Relation Extraction (RE) and Entity Linking (EL) engine automates the discovery of typed, verifiable semantic edges between Knowledge Objects from unstructured text, ingested raw documents, or high-confidence discovery pairs.

In accordance with core system axioms (*"A Compiler, Not An Agent"* and *"Fail-Closed Everything"*):
1. **Closed-World Ontology Enforcement:** An LLM or extractor MUST NOT invent free-form relation names (e.g. `is_related_to`, `talks_about`). Extracted relations MUST strictly select from the normative types declared in [`relation_registry.yaml`](../schemas/registry/relation_registry.yaml) (`REX-001`).
2. **Type-Safe Endpoint Compatibility:** Proposed relations MUST conform to declared `source_types` and `target_types`. For example, a `Concept` may `EXTEND` another `Concept`, but cannot `IMPLEMENT` an `Incident` (`REX-002`).
3. **Quarantine Firewall:** Extracted relations MUST NEVER be written directly to canonical Markdown files by an agent or LLM. They are emitted as pending `RelationDiscoveryCandidate` objects in `staging/discovery/` and require explicit human review and DPCP promotion (`REX-005`).

```text
Raw Text / High-Confidence Discovery Pair
                      │
                      ▼  (Deterministic Alias & Token Matching)
             Entity Linking (EL) ──► Maps mentions to Canonical Node IDs
                      │
                      ▼  (Prompt Injection Fencing & Delimiter Escaping)
       Zero-Tool Relation Extraction Prompt (Bounded to relation_registry.yaml)
                      │
                      ▼  (Schema & Endpoint Type Validation: Layers 1–2)
        RelationDiscoveryCandidate (staging/discovery/candidates.jsonl)
                      │
                      ▼  (Human Review & HMAC Signature Binding)
         DPCP Atomic Promotion (SQLite WAL Journal -> os.replace)
                      │
                      ▼
     Canonical Knowledge Object relations: block updated on disk
```

---

## 2. Normative Invariants (REX-001–REX-015)

| Invariant | Domain | Specification Rule | Error Code |
|---|---|---|---|
| **REX-001** | Closed Ontology | All extracted relations SHALL be members of `relation_registry.yaml`. Unregistered, hallucinated, or lowercase relation types MUST fail closed. | `E150` |
| **REX-002** | Type Compatibility | Extracted relation endpoints SHALL satisfy normative `source_types` and `target_types` constraints for that relation type. | `E151` |
| **REX-003** | DAG Invariant | Extraction passes proposing hierarchical relations (`PART_OF`, `INSTANCE_OF`) MUST verify that the proposed edge does not create a directed cycle within the canonical graph (`GRAPH-001`). | `E152` |
| **REX-004** | Inverse Non-Duplication | Extractor SHALL NOT propose virtual inverse relations (`EXTENDED_BY`, `SUPERSEDED_BY`, `IMPLEMENTED_BY`). Inverses are computed virtual views per `REL-008`. | `E153` |
| **REX-005** | Quarantine Barrier | All extracted relations MUST be serialized as pending candidate records in `staging/discovery/`. Direct modifications to canonical `relations:` frontmatter by an automated worker are strictly prohibited. | `E154` |
| **REX-006** | Co-Reference Resolution | Entity linking MUST resolve textual mentions to canonical `id`s using case-insensitive NFKC normalization across both `ko.id` and all entries in `ko.aliases`. | `E155` |
| **REX-007** | Epistemic Provenance | Extracted relations MUST record derivation metadata: `extractor_name`, `extractor_version`, `model_fingerprint`, `prompt_hash`, `evidence_excerpt` ($\le 250$ chars), and initial confidence score ($0.0 \le c \le 1.0$). | `E156` |
| **REX-008** | Self-Reference Ban | Proposing a relation where `source_id == target_id` SHALL fail closed with immediate candidate rejection (`REL-004`). | `E157` |
| **REX-009** | Scope Isolation | Extracted relations MUST respect scope boundaries: cross-scope edges between `personal` and `engineering` require explicit policy authorization (`DELTA-CORE-007`). | `E158` |
| **REX-010** | Deduplication Gate | If an identical edge `(source, relation, target)` already exists in canonical storage, the extraction worker SHALL discard it as a redundant candidate. | `E159` |
| **REX-011** | Deterministic Precedence | Where structured metadata or citations exist, relations SHALL be constructed deterministically with zero LLM extraction calls. | `E160` |
| **REX-012** | Constrained Logit Extraction | Where LLM relation classification is performed, extractors SHOULD use constrained token logit filtering over valid predicate tokens. | `E161` |
| **REX-013** | Asserted vs. Augmented Boundary | Candidate relations SHALL be partitioned into *Asserted* vs *Augmented*. Asserted relations require verbatim source text span offsets. Inferred or ungrounded relations MUST be quarantined in `staging/discovery/` as augmented; asserting an ungrounded relation fails with `E162`. | `E162` |

### 2.1 Asserted vs. Augmented Graph Boundary (The 50.4% Cascade Rule)

To prevent cascading error traps where speculative LLM associations pollute factual ground truth, the knowledge architecture enforces a hard boundary between:
1. **Asserted Relations:** Edges backed by exact, verbatim text spans within the source document (`source_ref`, `start_char`, `end_char` or line ranges). Only Asserted relations are eligible for human review and canonical promotion into Knowledge Object frontmatter (`relations:`).
2. **Augmented Relations:** Edges derived via structural graph intelligence, community clustering, ontology rules, or vector embeddings. These relations MUST be quarantined in `staging/discovery/` as candidate discoveries or stored in derived graph layers (`artifacts/derived_edges.json`). Proposing or promoting an ungrounded relation as Asserted without exact verbatim textual support SHALL fail closed with `E162: UngroundedAssertedRelationError`.

---

## 3. Extraction Protocol & Prompt Specification

When executing LLM-based Relation Extraction, the prompt MUST be constructed under the Zero-Tool Capability Firewall:

### Prompt Contract:
1. **Fencing:** Input passages MUST be wrapped in immutable `<untrusted_source>` tags.
2. **Grammar Constraints:** The LLM output MUST be constrained to JSON schema validating against `CandidateRelationPayload`:
   ```json
   {
     "source_id": "PERS-CON-MIG_USMC_SURVIVAL_MANUAL_A3BB86-0001",
     "target_id": "PERS-CON-MIG_US_ARMY_SURVIVAL_MANUAL_8AC16B-0001",
     "relation": "EXTENDS",
     "confidence": 0.88,
     "rationale": "Both manuals share doctrine, with the USMC edition expanding tactical recovery procedures.",
     "evidence_excerpt": "USMC manual expands upon Army standard field operations..."
   }
   ```
3. **Prompt Enum Injection:** The prompt MUST dynamically inject only valid relations applicable to the pair's specific `(source.object_type, target.object_type)`.

---

## 4. CLI Interface Specification

The relation extraction engine is invoked via discovery subcommands:

```bash
trashheap discover extract-relations [OPTIONS]
```

### Options:
- `--corpus-root <DIR>`: Root directory of Knowledge Objects (default: `fixtures/canonical`).
- `--registry-dir <DIR>`: Path to schemas/registry directory.
- `--similarity-cutoff <FLOAT>`: Minimum cosine similarity of pairs to evaluate (default: `0.80`).
- `--cooccurrence-min <INT>`: Minimum chunk co-occurrence threshold to evaluate (default: `2`).
- `--max-candidates <INT>`: Maximum pairs to process in a single execution pass.
- `--model <STR>`: LLM provider/model designation for extraction (default: `offline-heuristic` or configured provider).
- `--discovery-dir <DIR>`: Staging directory for candidate emission (default: `staging/discovery`).
- `--json`: Emit machine-readable summary of generated proposals.

---

## 5. Error Codes (`E150–E169`)

- `E150: UnregisteredRelationTypeError` — Extractor returned relation not in `relation_registry.yaml`.
- `E151: IncompatibleEndpointTypesError` — Proposed relation violates `source_types` or `target_types`.
- `E152: RelationDAGCycleError` — Proposed hierarchical edge introduces a circular graph dependency.
- `E153: VirtualInverseProposalError` — Proposed edge is an inverse view that must not be persisted directly.
- `E154: QuarantineBypassError` — Attempted write to canonical note bypassing review staging.
- `E155: UnresolvedEntityLinkingError` — Text mention could not be resolved to any known canonical ID or alias.
- `E156: EpistemicProvenanceMissingError` — Missing required extraction metadata (model, version, confidence, excerpt).
- `E157: SelfReferentialRelationError` — Extracted relation links an entity ID to itself (`REL-004`).
- `E158: CrossScopeIsolationViolationError` — Unauthorized cross-scope candidate edge without boundary grant.
- `E159: RedundantCanonicalRelationError` — Candidate edge already exists identically in canonical storage.
- `E160: DeterministicPrecedenceBypassError` — Proposing neural extraction where deterministic metadata citations exist.
- `E161: LogitConstraintViolationError` — Extracted relation predicate violates discrete vocabulary token constraints.
- `E162: UngroundedAssertedRelationError` — Proposed Asserted relation lacks exact verbatim text span / character offsets in source document.
