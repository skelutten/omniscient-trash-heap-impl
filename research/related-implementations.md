# Prior Art: related implementations

> **Type**: Prior-art provenance record — NON-NORMATIVE
> **Retrieved/Updated**: 2026-08-19

---

## 1. Sources

| # | Project | What it is | Status read |
|---|---|---|---|
| P1 | [`Aaryanverma/graybox`](https://github.com/Aaryanverma/graybox) | Shipped local-first CLI/TUI that captures notes and compiles them into a typed, cross-linked Markdown wiki | README read in full (512 lines) |
| P2 | [`microsoft/graphrag`](https://github.com/microsoft/graphrag) | Graph-based RAG indexing pipeline; the origin of the community-report / local-global retrieval ideas | README read in full |
| P3 | [`bingreeky/GMemory`](https://github.com/bingreeky/GMemory) — *G-Memory: Tracing Hierarchical Memory for Multi-Agent Systems*, [arXiv 2506.07398](https://arxiv.org/abs/2506.07398) | Research implementation of hierarchical agent memory | README + arXiv abstract read |
| P4 | [`zakirullin/files.md`](https://github.com/zakirullin/files.md) | Local-first, LLM-friendly note-taking app using chat as a "write-only entrance" to a plain Markdown knowledge base | README + architecture notes read |
| P5 | [`axoviq-ai/synthadoc`](https://github.com/axoviq-ai/synthadoc) | Open-source LLM knowledge compilation engine; a self-contained wiki of Markdown pages maintained and cross-referenced by deterministic scripts | README + core pipeline code read |
| P6 | **HiSkill: Empowering LLM Agents with Hierarchical Skill Graphs** (*arXiv:2607.25853*, 2026) | Research framework organizing distilled agent trajectories into a hierarchical, queryable skill graph | Full paper + methodology read |
| P7 | **A Deterministic Control Plane for LLM Coding Agents** (*arXiv:2606.26924*, 2026 / Rel(AI)Build) | Research proposal introducing a deterministic guardrail layer above the LLM harness for auditable filesystem and tool operations | Full paper + threat model read |
| P8 | [`langchain-ai/openwiki`](https://github.com/langchain-ai/openwiki) (David R Oliver road test) | Codebase knowledge compiler with Grounded Claims, OKF v0.2 export, durable checkpoint state machine | Full article, codebase architecture notes, run logs read |
| P9 | [`FareedKhan-dev/agentic-knowledge-graph`](https://github.com/FareedKhan-dev/agentic-knowledge-graph) | Deterministic 929M-edge biomedical graph (0 LLM calls), CSR in RAM, constrained decoding, self-debunking benchmark | Full repo, architecture notes, benchmark code read |
| P10 | [`FareedKhan-dev/all-agentic-architectures`](https://github.com/FareedKhan-dev/all-agentic-architectures) & [`FareedKhan-dev/production-grade-agentic-system`](https://github.com/FareedKhan-dev/production-grade-agentic-system) | 35 agentic architectures, Deterministic-Picker Pattern, and 7 enterprise production hardening layers | Full repos, patterns catalog, production layers read |
| P11 | [David R Oliver: *The State of the Nation in LLM Knowledge Bases in 2026* / AIX v0.2](state-of-the-nation-llm-knowledge-bases-2026.md) | Industry survey on Luhmann Zettelkasten, the Folder Ceiling, SQLite FTS, the Open Graph crisis, and AIX v0.2 | Full essay + AIX v0.2 specification read |

Full texts not vendored (third-party, no redistribution licence — `README.md` §3).

---

## 2. P1 — graybox: the closest comparable artifact

A working implementation of substantially this pattern. Its frontmatter is
`id, type, title, created, updated, aliases, related, backlinks, sources, tags, status`
— recognisably our IDENTITY / CLASSIFICATION / ONTOLOGY / PROVENANCE / GOVERNANCE
categories under different names.

### 2.1 Convergence

| graybox | Here |
|---|---|
| **Immutable inbox** — *"Your raw notes are never edited or deleted by the organizer"* | **CANON-005** evidential source of truth; **INGEST-CORE-001** non-invasive observation |
| **Workspaces**, switchable, isolated | `scope` (`personal` / `engineering`) |
| No vector DB by default; embeddings an *opt-in* upgrade | `GRAPH-INTELLIGENCE.md` §12.3 corpus-size guidance; vector adapter optional in Layer 7 |
| Retrieval walks **one hop** through `related`/`backlinks` | bounded BFS with `max_depth` (`RETRIEVAL.md` §9.4) |
| Every page carries `sources:`; every fact traces to an inbox item | mandatory `provenance.source_*` |
| *"Answers are grounded or honest, never invented… would rather be unhelpful than wrong"* | evidence-bundle grounding; **RET-003** |
| Pluggable LLM endpoint (LiteLLM) | configured `model_endpoint` (**INGEST-CORE-018**) |
| *"Small, single-purpose modules… swap any one out without touching the rest"* | the seven-layer separation (`ARCHITECTURE.md` §2) |

### 2.2 Their sharpest principle — better stated than ours was

> *"**The LLM only reasons — it never touches the filesystem directly.** All page
> creation, slugging, merging, and backlink maintenance is deterministic Python, so
> behavior is auditable and doesn't drift between runs."*

This is the unifying principle behind the "compiler not agent" critique
(`critiques-and-community-feedback.md` S1) as well. We held it only for the
*extraction* LLM (**INGEST-CORE-018** / E120 capability firewall) and for derived
pipelines (**DELTA-CORE-001**), never as a system-wide statement. It is now
**CANON-006** in `ARCHITECTURE.md` §2.2.

### 2.3 Divergence: they persist `backlinks`, we forbid it

graybox stores `backlinks:` in frontmatter. **REL-004** / **E019** forbids persisting
virtual inverse relations here, and **REL-004a** forbids counting them as edges.

Both positions are defensible. Theirs: an offline reader sees inbound links without
computing them, and the staleness risk is contained because *"backlink maintenance is
deterministic Python"*. Ours: a persisted inverse is a second copy of one fact that
can drift, and it is precisely the value that produced the silent orphan-detection
inversion documented in `critiques-and-community-feedback.md` L1. Recorded as
considered-and-rejected, not as an oversight.

### 2.4 A legitimate critique of our design: threshold proliferation

> *"embeddings are… scored on the same 0–1 scale as everything else, so **one
> `min_score` threshold governs relevance everywhere** rather than introducing a
> second threshold to learn."*

Our specs currently expose at least five thresholds on different scales and semantics:
`min_confidence` (provenance, 0–1), `semantic_similarity_cutoff` (0.75),
`min_edge_strength` (0.15), knowledge-gap `semantic_similarity >= 0.80`, and
`contextual_cooccurrence_min_chunks` (2). That is several numbers an operator must
learn and tune. Recorded as an open simplification target (`README.md` deviation 23);
consolidating them changes retrieval semantics and is a design decision, not a fix.

### 2.5 Where we are ahead

Their roadmap lists as **unbuilt**: *"Typed relationship edges (causal/dependency
traversal — 'what's blocking X,' 'why was Y decided' — beyond simple co-occurrence
links)."* That is `ONTOLOGY.md` §4 — 30 typed, registry-governed relations — already
specified. Useful evidence that untyped co-occurrence linking is felt as a real
limitation in practice, and that typed relations are the right investment.

### 2.6 A concrete model for the section-ownership gap

graybox's page body separates ownership explicitly: `## Summary` is LLM-owned,
`## Notes` is append-only with a per-entry source reference and timestamp, and
`## Related` / `## Backlinks` / `## Sources` are machine-maintained. Together with the
`## Notes`-preservation and idempotency tests in
`critiques-and-community-feedback.md` L5, this is a working precedent for
`README.md` deviation 21.

---

## 3. P2 — GraphRAG: status correction

Our earlier notes (`GRAPH-RAG-RESEARCH-NOTES.md`) treat GraphRAG as the live
reference architecture. The README now states otherwise:

> *"GraphRAG is a research project… Since our first release in July 2024 the
> capabilities of frontier models have changed dramatically… **This project is largely
> in maintenance mode, and won't be accepting new PRs or implementing new features.**"*

Also: *"not an officially supported Microsoft offering"*, *"the provided code serves as
a demonstration"*, an explicit cost warning (*"GraphRAG indexing can be an expensive
operation… start small"*), and a strong recommendation to fine-tune prompts because
out-of-the-box results *"may not yield the best possible results"*.

**Consequence for us.** The *ideas* we borrowed — hierarchical communities, community
reports, local/global/DRIFT retrieval profiles — remain valid and are already correctly
marked optional and deferred (`GRAPH-INTELLIGENCE.md` §9.2, §14). But GraphRAG is not
a live upstream to track, and the cost and prompt-tuning caveats are independent
support for the existing decision to keep community detection and LLM extraction in
**optional later phases** rather than Phase 1 or 2.

---

## 4. P3 — G-Memory: closest prior art to our ingestion family

A three-tier graph hierarchy — **insight**, **query**, **interaction** — with
bi-directional traversal that retrieves both *"high-level, generalizable insights"* and
*"fine-grained, condensed interaction trajectories"*. The hierarchy evolves by
assimilating new trajectories. Reported gains: up to **+20.89%** success on embodied
action and **+10.12%** on knowledge QA, across five benchmarks, three LLM backbones and
three multi-agent frameworks, without modifying those frameworks.

### 4.1 Convergence with the ontological triad

G-Memory keeps the specific trace *and* the distilled insight, linked. That is our
scope-conditional triad (**INGEST-CORE-004**):

```text
Incident | Observation   →   Lesson        →   Workflow
(the specific trajectory)   (generalizable)   (reusable procedure)
```

Two independent designs arriving at "retain the concrete trace, distil a general
insight, keep them linked" is reasonable evidence the triad is load-bearing rather
than ceremony. Their measured improvement is the strongest quantitative support we
have for that shape.

### 4.2 Divergence: autonomy-first vs governance-first

| | G-Memory | Here |
|---|---|---|
| Objective | maximise agent task success | produce trustworthy, human-readable knowledge |
| Write path | memory updates itself automatically | **INGEST-CORE-003** forbids writing to canonical folders; promotion requires human approval (**E117**, **E124**) |
| Consumer | the agent, at runtime, to shape its next action | a human or agent asking a question, via an Evidence Bundle |

Neither is wrong; the objective functions differ. Worth noting that our governance gate
is exactly what G-Memory omits in order to self-evolve, so their results do **not**
transfer as evidence that automatic promotion is safe here.

### 4.3 One capability we do not have

G-Memory retrieves memory *to inform an agent's next action*, not to answer a question.
Our Evidence Bundle is question-shaped. An action-shaped retrieval contract is a
possible future direction, not a gap in the current design, and is **not** recorded as
a deferred item until there is a concrete use case.

---

## 5. P4 — `files.md`: The purest "immutable inbox" UX

A minimalist local-first implementation treating the chat interface strictly as a frictionless, write-only entrance to a local Markdown vault.

### 5.1 Convergence
- **Write-only capture:** The philosophy that "the chat is a write-only entrance to your knowledge base" mirrors our **INGEST-CORE-001** non-invasive observation and raw capture (`raw/` staging).
- **Interoperability over lock-in:** Relies exclusively on plain Markdown links and standard YAML frontmatter, keeping the knowledge base grep-able, diff-able, and portable without proprietary vector DB dependencies.

### 5.2 Divergence
- **Scope of automation:** `files.md` optimizes for the capture UX (e.g. low-friction dumping) but implements little to no deterministic compilation, linter validation, or typed ontology enforcement downstream. `llm-wiki-oe` assumes the heavy lifting happens *after* capture during staged promotion.

---

## 6. P5 — `synthadoc`: Closest open-source "Compiler, Not Agent" artifact

An open-source engine that treats a wiki as a self-contained, local-first folder of Markdown pages maintained and cross-referenced by deterministic scripts.

### 6.1 Convergence
- **Deterministic filesystem mutation:** Enforces a strict boundary: the LLM proposes content updates or structural links, but deterministic Python handles page creation, slugging, and backlink maintenance. Directly validates **CANON-006**.
- **Local-first compilation:** Operates entirely on local Markdown artifacts, avoiding the opacity and cost of continuous vector re-indexing for structural knowledge.

### 6.2 Divergence
- **Epistemic rigor:** `synthadoc` lacks the multi-layer epistemic validation (provenance tracking, entropy checks for secrets, capability firewalls) defined in `llm-wiki-oe`'s `INGEST-CORE` specifications.

---

## 7. P6 — HiSkill: Quantitative validation of the Ontological Triad

A 2026 research framework (*arXiv:2607.25853*) addressing the limitation where trajectory-to-skill synthesis produces flat, unstructured collections of text skills retrieved independently.

### 7.1 Convergence
- **Hierarchical skill distillation:** HiSkill introduces a hierarchical skill graph mapping raw execution traces to generalized, reusable policies with explicit prerequisites and specializations. Provides independent academic validation for our scope-conditioned ontological triad (**INGEST-CORE-004**): `Incident/Observation` (trace) $\rightarrow$ `Lesson` (generalized insight) $\rightarrow$ `Workflow/Skill` (reusable procedure).
- **Typed relations over co-occurrence:** Confirms that untyped co-occurrence linking is a bottleneck for agent reasoning, and that typed, registry-governed relations (`ONTOLOGY.md` §4) are necessary for effective multi-hop retrieval.

### 7.2 Divergence
- **Objective function:** HiSkill optimizes for *test-time adaptive agent execution*, whereas `llm-wiki-oe` optimizes for *human-readable, evidence-grounded knowledge curation* with strict human review gates before canonical promotion (**E117**, **E124**).

---

## 8. P7 — Deterministic Control Plane (Rel(AI)Build): Formalizing CANON-006

A 2026 architectural proposal (*arXiv:2606.26924*) introducing a deterministic control plane above the LLM harness, enforcing tier-based permissions, historical replay, and audit traces for all filesystem and tool operations.

### 8.1 Convergence
- **Separation of reasoning and execution:** Stochastic LLM outputs must never be granted direct, unmediated access to stateful systems (filesystems or knowledge graphs). This is the strongest formal academic backing for our **CANON-006** axiom ("The LLM only reasons — it never touches the filesystem directly").
- **Auditable guardrails:** Proposes treating agent configurations and file operations as governed, deterministic artifacts, mirroring our Durable Staged Commit Protocol (**DSCP**) and 5-layer validation pipeline.

### 8.2 Divergence
- **Domain focus:** Rel(AI)Build focuses on runtime coding agent security and supply-chain governance. `llm-wiki-oe` adapts this deterministic boundary pattern to the *knowledge ingestion and compilation* pipeline, preventing epistemic drift and prompt injection during knowledge synthesis.

---

---

## 9. P8 — OpenWiki & Grounded Claims (David R Oliver / LangChain OpenWiki)

A 2026 codebase knowledge compiler implementation and empirical local-model road test (*"OpenWiki Turns Your Codebase Into Self-Correcting Memory"*, David R Oliver).

### 9.1 Convergence
- **The Core Epistemic Thesis:** *"Documentation fails because it is write-once. Memory works because it is overwrite-often."* Directly reflects our living compilation model.
- **Grounded Claims & AST Hash Pinning:** Storing dual prose and JSON sidecars pinning claims to `file_path`, line intervals, and SHA-256 line hashes. When source code mutates, hash mismatches trigger targeted page invalidation. Independent industry convergence with our Structural Knowledge Graph (`STRUCTURAL-GRAPH.md`) and AST Bridge Engine (`SG-013`).
- **OKF v0.2 Interoperability:** Emits Google Open Knowledge Format v0.2 bundles, validating our Plan 61 interop spec (`trashheap/bundle/`).
- **Ralph Loop (Durable Checkpoints):** Proves that monolithic agent scripts crash, while state-machine retry loops over durable run journals (`.run.json`) achieve monotonic forward progress. Aligns with our Durable Staged Commit Protocol (**DSCP**).

### 9.2 Divergence
- **Epistemic Scope:** OpenWiki targets codebase architectural maps; *The Omniscient Trash Heap* generalizes across heterogeneous enterprise sources (transcripts, papers, notes, telemetry) with 5-layer validation.

---

## 10. P9 — Zero-LLM Biomedical Knowledge Graph (Fareed Khan)

A 2026 large-scale knowledge graph implementation (`agentic-knowledge-graph`) building a 929.8M-edge citation and ontology graph across 28.3M PubMed abstracts with zero generative LLM calls, evaluated on PubMedQA.

### 10.1 Convergence
- **Topological Admissibility $\neq$ Propositional Truth:** Empirical proof that graph reachability cannot certify factual truth ($\text{AUROC} \approx 0.500$), whereas constrained softmax logit posteriors achieve $\text{AUROC} \approx 0.810$. Directly informs `RET-006`–`RET-008` and `EPI-006`.
- **CSR Adjacency in RAM:** Bypasses graph database overhead by storing raw adjacency matrices in memory as Compressed Sparse Row (CSR) slices, executing neighborhood expansions in $<10\ \mu\text{s}$. Informs `GRAPH-INTELLIGENCE.md` §11.1.
- **The Truncation Trap:** Hardening against arbitrary context truncation (e.g., 1,100 char clip that severed `CONCLUSIONS` in 94.2% of abstracts). Informs `RET-009`.

### 10.2 Divergence
- **Domain Specialization:** Khan focuses on NLM medical XML metadata; *The Omniscient Trash Heap* supports streaming XML invariance (`ADA-008`) alongside multi-format multimodal ingestion.

---

## 11. P10 — 35 Agentic Architectures & 7-Layer Production Hardening (Fareed Khan)

A comprehensive taxonomy of 35 agent architectures (`all-agentic-architectures`) and a 7-layer industrial agent harness (`production-grade-agentic-system`).

### 11.1 Convergence
- **The Deterministic-Picker Pattern:** Proves that stochastic LLM routing suffers from flat-band instability. Restricting LLMs to structured categorical perception (Pydantic/constrained logits) and executing graph traversal via deterministic Python is the exact operational manifestation of **CANON-006**.
- **The 7 Production Layers:** Validates the enterprise necessity of circuit breakers (hysteresis), prompt fencing, durable write-ahead logging (WAL), OpenTelemetry distributed tracing, and calibration drift monitoring. Mirrors our Continuous Staged Commit Coordinator (CSCC) and 5-layer epistemic validation pipeline.

### 11.2 Divergence
- **Orchestration Scope:** Khan’s patterns catalog general-purpose agent interactions; *The Omniscient Trash Heap* specializes deterministic control into a knowledge compiler and epistemic retrieval engine.

---

## 12. P11 — State of the Nation in LLM Knowledge Bases & AIX v0.2 (David R Oliver)

An August 2026 industry survey and format specification (*"The State of the Nation in LLM Knowledge Bases in 2026"*, David R Oliver) analyzing the convergence on plain text Markdown folders (the "1981 Filing Trick"), the folder scaling ceiling, the open graph dilemma, and AIX v0.2.

### 12.1 Convergence
- **The Knowledge Library Paradigm:** Confirms that single-folder vaults fail across teams. Endorses the federated library model with cross-bundle citations (`namespace/note`), permanent short identifiers, and shared type/relation vocabularies (`ARCHITECTURE.md` §2.3, `CORPUS_MANIFEST.yaml`).
- **Pages as Authorship, Bundles as Use:** Independent convergence with our Plan 61 Knowledge Bundles and OKF interop (`specs/OKF-INTEROP.md`).
- **The Open Graph Vacuum:** Exposes that Google's OKF graph story relies on `kcmd` syncing to the paid, proprietary *Google Cloud Knowledge Catalogue*. Confirms that our open, embedded Compressed Sparse Row (CSR) in-memory graph engine (`specs/GRAPH-INTELLIGENCE.md` §11.1, `trashheap/graph/csr.py`) occupies the primary missing layer in the open-source ecosystem.
- **Multimodal Hash Fingerprinting:** Validates our cryptographic SHA-256 byte hashing and embedding slot contracts for diagrammatic and audio artifacts.

### 12.2 Divergence
- **Implementation Scope:** AIX v0.2 is a lightweight format extension proposal authored by one researcher; *The Omniscient Trash Heap* implements an industrial, 5-layer validated, transactional knowledge compiler with live SQLite FTS5 and CSR graph querying.

---

## 13. Derived changes & Architectural Affirmations

| Change / Affirmation | Where |
|---|---|
| **CANON-006 strengthened** — cite *Deterministic Control Plane* (*arXiv:2606.26924*) and *Deterministic-Picker Pattern* (Khan 2026) as proof that LLMs must never directly mutate state | `ARCHITECTURE.md` §2.2 |
| **Ontological Triad validated** — cite *HiSkill* (2026) as quantitative proof that flat trajectory storage fails and hierarchical `Trace → Insight → Skill` compilation is load-bearing | `INGEST-CORE-004` / `ONTOLOGY.md` §4 |
| **Grounded Claims & OKF v0.2 verified** — cite OpenWiki (2026) for AST hash-pinned claim sidecars and OKF v0.2 interop | `STRUCTURAL-GRAPH.md` (SG-013) / `OKF-INTEROP.md` |
| **Knowledge Library & Federation verified** — cite *State of the Nation 2026* (Oliver) for cross-bundle citation syntax and namespace federation | `ARCHITECTURE.md` §2.3 / `CORPUS_MANIFEST.yaml` |
| **Open Graph Imperative validated** — cite Oliver's warning on Google Cloud Knowledge Catalogue lock-in as proof that an open, embedded CSR graph engine is vital | `GRAPH-INTELLIGENCE.md` §11.1 / `specs/RETRIEVAL.md` |
| **Constrained Logits & Refusal Calibration** — cite PubMed 929M graph (Khan 2026) for softmax posteriors outperforming topological path validation | `RETRIEVAL.md` (§9.6, §9.7, RET-008) / `EPI-006` |
| **Section-Aware Truncation Trap Defenses** — cite PubMed 1100-char truncation flaw | `RETRIEVAL.md` (RET-009) |
| **Capture UX precedent** — note `files.md` as a validated pattern for the "write-only entrance" philosophy | `README.md` deviation 21 |
| GraphRAG maintenance-mode caveat | `GRAPH-INTELLIGENCE.md` §9.2 |
| Threshold proliferation recorded as a simplification target | `README.md` deviation 23 |
| Section-ownership gap now cites a working precedent | `README.md` deviation 21 |

No design decision was reversed. P1 through P11 independently corroborate existing `llm-wiki-oe` architectural choices (local-first Markdown, deterministic compilation, hierarchical typing, strict execution boundaries, constrained decoding, durable transactions, embedded CSR graphs).