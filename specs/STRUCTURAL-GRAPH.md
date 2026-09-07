# LLM Wiki Structural Knowledge Graph Specification

> **Part of**: LLM Wiki Knowledge Architecture v3.8.10
> **Document ID**: `LLM-WIKI-STRUCTURAL-GRAPH-001`
> **Version**: `0.1.0`
> **Updated**: `2026-08-17`
> **Source**: Extracted from `research/GRAPH-RAG-RESEARCH-NOTES.md` §1–§12
> **Status**: `PROPOSED`
> **Implementation status**: `UNIMPLEMENTED`
> **Compatibility target**: Additive, isolated, opt-in
> **Base specification**: v3.8.10 (`ARCHITECTURE.md`, `ONTOLOGY.md`, `EPISTEMOLOGY.md`)
> **Normative owner**: This document owns the Structural Knowledge Graph extension and error family `E301–E399`
> **Related documents**: `ARCHITECTURE.md`, `ONTOLOGY.md`, `EPISTEMOLOGY.md`, `VALIDATION.md`

---

## 15. Structural Knowledge Graph (SKG)

### 15.1 Purpose & Scope

`GRAPH-INTELLIGENCE.md` §14 explicitly defers structural extraction
(AST/Tree-sitter/LSP), structural registry, source-revision binding,
reconciliation and impact analysis to **a separate specification**. This
document is that specification.

The structural knowledge graph is a **machine-built, deterministic** graph over
artifacts' structure (files, modules, symbols, calls, imports, routes, tests).
It is orthogonal to the **curated semantic** knowledge graph in
`ONTOLOGY.md`, which describes knowledge claims.

```text
Knowledge Graph
├── Semantic Graph   (curated, human-reviewed)
│   └── relation_registry.yaml
│
└── Structural Graph (machine-built, deterministic)
    └── structural_registry.yaml
```

These are two graphs with **different semantics**, not two subsets of the same
relation registry.

**Non-goals:** LLM Wiki SHALL NOT become yet another codebase graph. SKG is a
deterministic foundation on top of which the semantic/epistemic knowledge layer
sits.

### 15.2 Separation Axioms

- **SKG-AX-001**: Structural relation types (`CALLS`, `IMPORTS`, `CONTAINS`,
  `DEFINED_IN`, `INHERITS`, `ROUTES_TO`, `TESTS_SYMBOL`) MUST NOT be registered in
  `relation_registry.yaml`. They belong to `structural_registry.yaml`.
- **SKG-AX-002**: Structural nodes are not Knowledge Objects and MUST NOT be
  assigned IDs according to `DATA_MODEL.md` §6 (ID-001–ID-005).
- **SKG-AX-003**: Graph centrality (degree, betweenness, PageRank) is NOT
  epistemic confidence and MUST NOT be mapped to `epistemology.*` or
  `provenance.confidence` (cf. `EPISTEMOLOGY.md` EPI-001).
- **SKG-AX-004**: SKG is a **rebuildable projection**. Markdown, YAML and
  source code revisions are canonical; the graph is never the source of truth
  (`ARCHITECTURE.md` §2.2).

### 15.3 Normative Invariants (SG-001–SG-020)

| Invariant | Domain | Rule |
|---|---|---|
| **SG-001** | Graph | SKG SHALL be a separate graph from the semantic knowledge graph and SHALL have its own registry (`structural_registry.yaml`). |
| **SG-002** | Node model | Structural node types (`FILE`, `MODULE`, `CLASS`, `FUNCTION`, `METHOD`, `SYMBOL`, `ROUTE`, `TEST`) SHALL be defined normatively and MUST NOT be mixed with `ObjectTypeEnum`. |
| **SG-003** | Edge registry | Each structural edge type SHALL declare `source_types`, `target_types`, `dag` and `symmetric` according to the same contract form as `relation_registry.yaml`. |
| **SG-004** | Extraction | AST extraction SHALL be deterministic and SHALL declare parser, parser version and grammar version. |
| **SG-005** | Type resolution | LSP-based semantic type resolution is OPTIONAL; when used, server, server version and resolution status per edge SHALL be registered. |
| **SG-006** | Indexing | Incremental indexing SHALL be idempotent and SHALL produce the same final graph as a full re-indexing of the same revision. |
| **SG-007** | Revision | Each structural node and edge SHALL be bound to a `source_revision` (git SHA or resolved ref like `main@HEAD`) as well as a normalized file content hash. |
| **SG-008** | Change detection | Change detection SHALL be done via content hash, never only via mtime. |
| **SG-009** | Reconciliation | Removed or changed inputs SHALL invalidate their derived edges before publishing (temp file + atomic `rename`). |
| **SG-010** | Impact | Impact propagation (blast radius) SHALL be a bounded traversal with explicit max depth and node ceiling, and the result SHALL be a derived artifact. |
| **SG-011** | Context budget | Structural responses SHALL report context budget according to `GRAPH-INTELLIGENCE.md` §5.1.3 without affecting ranking. |
| **SG-012** | Retrieval | Structural retrieval SHALL be an explicit, versioned Layer 7 profile and MUST NOT change the baseline retrieval's results. |
| **SG-013** | Bridge | Bridge relations between structural node and Knowledge Object SHALL be derived, typed and reviewable; they MUST NOT create canonical relations automatically. |
| **SG-014** | Provenance | Each structural edge SHALL carry `derivation` according to `GRAPH-INTELLIGENCE.md` §5.1.1 with `mode: extracted` and `extractor: ast \| parser`. |
| **SG-015** | Coverage | The graph's coverage (indexed files/symbols, unresolved references) SHALL be reported as observability, never as conformance status. |
| **SG-016** | Determinism | Structural queries SHALL be deterministic at the level `bitwise` or `ranked-equivalent` (`GRAPH-INTELLIGENCE.md` §7). |
| **SG-017** | Interface | An agent interface (e.g. MCP) MAY expose structural queries read-only; it MUST NOT expose write operations against canonical files. |
| **SG-018** | Evidence Bundle | Structural hits SHALL be carried in the Evidence Bundle with node ID, file, revision and line interval. |
| **SG-019** | Conformance | Incremental indexing, reconciliation and revision binding SHALL be covered by their own conformance tests. |
| **SG-020** | Degradation | On partial extraction failure the pipeline SHALL degrade explicitly (reported coverage loss) and MUST NOT publish a silently incomplete graph. |

### 15.4 Structural Node & Edge Model (draft)

```yaml
# structural_registry.yaml (draft — not normatively locked)
node_types:
  FILE:      {identity: [repo, path]}
  MODULE:    {identity: [repo, module_path]}
  CLASS:     {identity: [repo, path, qualified_name]}
  FUNCTION:  {identity: [repo, path, qualified_name, arity]}
  METHOD:    {identity: [repo, path, qualified_name, arity]}
  SYMBOL:    {identity: [repo, path, qualified_name]}
  ROUTE:     {identity: [repo, method, pattern]}
  TEST:      {identity: [repo, path, qualified_name]}

edge_types:
  DEFINES:      {source_types: [FILE, CLASS, MODULE], target_types: [CLASS, FUNCTION, METHOD, SYMBOL], dag: true,  symmetric: false}
  CALLS:        {source_types: [FUNCTION, METHOD],     target_types: [FUNCTION, METHOD],                dag: false, symmetric: false}
  IMPORTS:      {source_types: [FILE, MODULE],         target_types: [FILE, MODULE],                    dag: false, symmetric: false}
  INHERITS:     {source_types: [CLASS],                target_types: [CLASS],                           dag: true,  symmetric: false}
  ROUTES_TO:    {source_types: [ROUTE],                target_types: [FUNCTION, METHOD],                dag: false, symmetric: false}
  TESTS_SYMBOL: {source_types: [TEST],                 target_types: [FUNCTION, METHOD, CLASS],         dag: false, symmetric: false}
```

Example of the two graphs' coexistence:

```text
Semantic (canonical)                Structural (derived)
ENG-CMP-0102                        src/cache/cache.cc
   ├── IMPLEMENTS → ENG-FET-0105       ├── DEFINES → CacheManager
   ├── USES       → ENG-IFC-0021       │      ├── DEFINES → CacheManager::get()
   └── VERIFIED_BY→ ENG-EXP-0034       │      └── CALLS   → RemoteCache::fetch()
                                       └── IMPORTS → remote_cache.h
```

### 15.5 Identity & Bridging to Knowledge Objects

A structural node is referenced via a structural identity, not a
Knowledge Object ID. Bridging is done as a derived edge:

```yaml
bridge:
  knowledge_object_id: "ENG-CMP-BAZEL-0101"
  structural_node: "repo=pp;path=src/cache/cache.cc;symbol=CacheManager"
  bridge_type: represented_by      # represented_by | documents | tested_by
  derivation:
    mode: extracted
    extractor: ast
    extractor_version: "0.1.0"
    source_revision: "<git-sha>"
  status: pending                  # pending | reviewed | approved | rejected
```

Bridge edges are Discovery entries according to `DISCOVERY.md` until approval
(SG-013).

### 15.6 Error codes

Structural pipeline errors are allocated in the reserved range **E301–E399**
according to the error code registry in `VALIDATION.md` §10.3. No codes are allocated in
version `0.1.0`; a future version SHALL register them in the same table.

### 15.7 Deferred

- Multi-language AST coverage beyond a first reference parser.
- Cross-repo symbol resolution.
- Historical (per-revision) graph versioning.
- Automatic promotion of bridge edges to canonical relations.

---

## Structural Invariants (summary)

| Invariant | Domain | Error code |
|---|---|---|
| **SG-001**–**SG-003** | Graph & registry | E301–E399 (not allocated) |
| **SG-004**–**SG-009** | Extraction & indexing | E301–E399 (not allocated) |
| **SG-010**–**SG-018** | Analysis & retrieval | E301–E399 (not allocated) |
| **SG-019**–**SG-020** | Conformance & degradation | E301–E399 (not allocated) |

---

**End of LLM Wiki Structural Knowledge Graph Specification v0.1.0**