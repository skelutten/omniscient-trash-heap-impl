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

## 9. Derived changes & Architectural Affirmations

| Change / Affirmation | Where |
|---|---|
| **CANON-006 strengthened** — cite *Deterministic Control Plane* (*arXiv:2606.26924*) as the academic foundation for forbidding direct LLM filesystem writes | `ARCHITECTURE.md` §2.2 |
| **Ontological Triad validated** — cite *HiSkill* (2026) as quantitative proof that flat trajectory storage fails and hierarchical `Trace → Insight → Skill` compilation is load-bearing | `INGEST-CORE-004` / `ONTOLOGY.md` §4 |
| **Capture UX precedent** — note `files.md` as a validated pattern for the "write-only entrance" philosophy | `README.md` deviation 21 |
| GraphRAG maintenance-mode caveat | `GRAPH-INTELLIGENCE.md` §9.2 |
| Threshold proliferation recorded as a simplification target | `README.md` deviation 23 |
| Section-ownership gap now cites a working precedent | `README.md` deviation 21 |

No design decision was reversed. P1, P3, P4, P5, P6, and P7 all independently corroborate existing `llm-wiki-oe` architectural choices (local-first Markdown, deterministic compilation, hierarchical typing, strict execution boundaries).