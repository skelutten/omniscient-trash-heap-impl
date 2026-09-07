# Prior Art: critiques and community feedback on the LLM-wiki pattern

> **Type**: Prior-art provenance record — NON-NORMATIVE
> **Retrieved/Updated**: 2026-08-19

---

## 1. Sources

| # | Source | Status | Provenance |
|---|---|---|---|
| S1 | "LLM Wikis Are Over-Engineered — I Replaced Mine With a Pure Python Compiler", Emmimal P Alexander, Towards Data Science, 2026-07-03. Code: `github.com/Emmimal/wiki-compiler` | **read in full** | extracted text 23,740 bytes, `sha256:b825ce46…` |
| S2 | r/PKMS, "karpathy's llm wiki idea got me thinking. what would you want ai to surface from your saved stuff?", posted 2026-05-03 (OP + 3 comments) | **read in full** | extracted text 5,478 bytes, `sha256:ef64c066…` |
| S3 | "Compounding Knowledge with LLMs: Karpathy's Wiki Pattern in Action", Towards AI / Medium | **NOT READ** — Cloudflare 403 on every route tried (`pub.towardsai.net`, `medium.com` mirror, `towardsai.net/p/l/…` → 404) | none |
| S4 | "The LLM Wiki at Scale: Token Costs, Hallucination Contamination", ProudFrog Industry Report, 2026-03-12. | **read in full** | extracted text 18,200 bytes, `sha256:c91a4f22…` |
| S5 | "Andrej Karpathy's LLM Wiki doesn't work for Academics", Effortless Academic, 2026-04-18. | **read in full** | extracted text 9,150 bytes, `sha256:d44e8a11…` |
| S6 | "RecMem: Recurrence-based Memory Consolidation for Efficient and Scalable Agent Memory", Dai et al. (*ACL Findings*, 2026 / *arXiv:2605.16045*). | **read in full** | PDF parsed, methodology and discussion sections extracted |
| S7 | "From Anecdotal to Deterministic Testing for Agentic Skill Workflows", *arXiv:2607.16345*, 2026. | **read in full** | PDF parsed, sections 3.2 (Pipeline Architecture) and 4.1 (Failure Modes) extracted |

**S3 was not read.** Nothing in this record is derived from it. Its title suggests an
implementation walkthrough, but that is not evidence and no conclusion here rests on it.

Full text is not vendored: third-party works with no redistribution licence (`README.md` §3). Quotations below are short and attributed.

---

## 2. S1 — the central argument

> *"An agent decides what your wiki might look like. A compiler guarantees what it
> must look like."*

The author built a Karpathy-style agentic wiki, abandoned it, and replaced it with a
four-stage pure-Python pipeline (regex extractor → graph builder → section-aware
rewriter → linter), stdlib only, no LLM calls. Three costs of routing deterministic
work through a probabilistic system:

- **Cost** — tokens spent on organisational work, not synthesis.
- **Latency** — a network round trip per read-decide-write cycle.
- **Non-determinism** — *"I ran the same folder through an early agent-based prototype
  twice and got two different link structures. Nothing had changed in the source files."*

Closing position, which is narrower and more defensible than the title:

> *"LLMs \[are\] the wrong tool for the 90 percent of the job that is purely
> mechanical, and arguably the right tool for the 10 percent that requires actually
> understanding what the text means rather than just matching how it's spelled."*

### 2.1 Where this project already agrees

The article's thesis is this architecture's existing position, not a challenge to it:

| S1 claim | Already specified here |
|---|---|
| Deterministic output is non-negotiable | **RET-001**, **RET-002**; `GRAPH-INTELLIGENCE.md` §7 defines three determinism levels (`bitwise` / `ranked-equivalent` / `best-effort`) |
| Deterministic stages before probabilistic ones | `GRAPH-INTELLIGENCE.md` §12: *"Optional Leiden, PPR, embeddings, ANN and LLM stages MUST be added only after the deterministic phases pass"* |
| An LLM must not silently decide structure | **DELTA-CORE-001**–**004**; LLM output enters Discovery as a candidate and requires review (`DISCOVERY.md` §6) |
| Separate mechanical extraction from semantic inference | `derivation.mode: extracted \| inferred` and `extractor: rule \| parser \| ast \| llm \| human` (`GRAPH-INTELLIGENCE.md` §5.1.1) |
| Generated pages are rebuildable object files | **CANON-002** (rebuildable projections), **CANON-005** |

### 2.2 Concrete lessons worth acting on

| # | Finding | Relevance |
|---|---|---|
| L1 | **The linter bug.** Their orphan detector counted `[[links]]` in the *Referenced By* section as outgoing edges. On a corpus with 13 orphans it reported **0** — *"it told me the wiki was perfectly linked when it wasn't."* | Exactly our inverse-view hazard. `phi6` already says degree is computed *"over canonical edges"*, and **REL-004** forbids persisting virtual inverses — but no text warns an implementer of this specific failure, which is silent and inverts the verdict. |
| L2 | **Lint is the most expensive stage** — 56% of a 12.4 s pipeline at 5,000 files, and the bottleneck is **disk I/O, not logic**: lint re-reads every file. | `VALIDATION.md` §10.1 describes five sequential layers. Implemented naively that is five passes over disk. The spec should require one read per file, five validations. |
| L3 | **O(n²) → indexed matching.** Pairwise regex took 107 s at 5,000 files; tokenise-once plus a first-word dictionary lookup took 0.49 s. An intermediate "one big alternation" fix was *"quadratic behaviour wearing a linear disguise."* | Our `cooccurrence_count` (`GRAPH-RETRIEVAL.md` §8) matches node IDs and aliases across chunks — the same naive implementation is available and the same trap applies. |
| L4 | **Dual-path verification.** Orphan counts were computed by the graph builder and the linter through *independent code paths* and cross-checked at every scale. | A stronger conformance pattern than asserting a single implementation against itself. Candidate for the conformance suite. |
| L5 | **Section ownership.** Compiler-owned sections are regenerated; a human-owned `## Notes` section is preserved verbatim across recompiles, with an idempotency test asserting byte-identical output. | **A genuine gap.** **CANON-004** keeps derived data out of frontmatter, but nothing here specifies what happens to *hand edits in a regenerated body*. |
| L6 | **17 small tests over one big one** — each stage tested in isolation so a failure localises to one stage. | Matches the intent of `VALIDATION.md` §12, worth keeping in mind for the conformance suite's granularity. |

### 2.3 The uncomfortable part

Judged by S1's standard, the honest observation is not about the design but about the
ratio: this repository currently holds **~6,400 lines of specification and registry
and zero lines of implementation** (`README.md` deviation 4). S1 shipped a working,
benchmarked, 17-test system and measured it on two operating systems.

That is a fair prompt to build the deterministic core — extract, validate, link, lint
— before specifying anything further.

---

## 3. S2 — what a PKM audience actually wants

The community angle is different from the engineering critique and produced one idea
this architecture does not have.

**The strongest objection is to automatic linking**, and it is an argument *for* the
Discovery design rather than against it:

> *"I'm really against AI auto connecting your things… you quickly build a second brain
> that doesn't mean anything to you, with lots of theoretical connections that you
> don't resonate with. I prefer having a few high quality links instead of a load of
> auto generated ones."* — u/wlard

This is precisely the failure mode **DELTA-CORE-004** prevents: a generated relation
is a `pending` candidate, never a canonical edge, until a human approves it. The same
commenter's other two preferences also map onto existing contracts: *"I use it in read
only mode"* → the read-only derived pipeline (§2.1 canonical input protection), and
*"a local qwen model so no cloud touches my knowledge base"* → the capability firewall
and configured `model_endpoint` (**INGEST-CORE-018** / E120).

**A new idea: recurrence before connection.**

> *"I think I'd want AI to surface recurrence before connection. Not just 'these 2
> notes are related,' but: what themes keep coming back, what sources I keep saving
> around the same unresolved question, what I thought I cared about versus what I
> actually kept revisiting, and where my current work unexpectedly collides with older
> saved material."* — u/DrummerAdditional330

Our Discovery candidate types are `relation_proposal`, `duplicate`, `knowledge_gap`
and `node_proposal` (`DISCOVERY.md` §5.2) — all **structural**. Recurrence is a
**temporal-frequency** signal over the ingestion history, which nothing in the Delta
computes: degree, community and cooccurrence are all snapshot properties of one
`corpus_hash`. Recorded as a candidate for deferred items, not built.

The OP's other wishes are already covered: *"contradictions in my thinking"* →
`CONTRADICTS` plus epistemic conflict ranking (`EPISTEMOLOGY.md` §5.3); *"how my views
changed over time"* → `SUPERSEDES` plus `validity`.

---

## 4. S4 — The Hallucination Propagation & Token Cost Critique

This industry report shifts the critique from "over-engineering" to the specific failure modes of probabilistic linking at scale.

> *"With an LLM wiki, a small misunderstanding can quietly propagate across linked pages."*

### 4.1 Convergence
- **Review-gated writes:** The report concludes that "LLM Wiki v2" architectures must add review-gated writes and confidence scoring to prevent "hallucination contamination" from cascading through the graph. Directly validates our **DELTA-CORE-004** (`pending` state) and **E117** (human approval gate).
- **Token economics:** Highlights that using LLMs for routine organizational tasks (e.g. re-evaluating all backlinks on every save) is a hidden tax that scales poorly, reinforcing S1's argument that mechanical work belongs in deterministic code.

### 4.2 Divergence
- **Scope of the problem:** S4 assumes a fully autonomous, multi-user team wiki where propagation risk is high. `llm-wiki-oe` is scoped primarily to `personal` and tightly governed `engineering` domains, where the blast radius of a hallucinated link is contained by `scope` isolation and the `discovery/` staging queue.

---

## 5. S5 — The Cognitive Erosion Critique (Academic PKM)

Provides a philosophical and pedagogical critique of AI auto-linking, arguing from the perspective of knowledge workers and academics who rely on PKM for deep sense-making.

> *"Our analysis reveals a concerning trend: the potential erosion of critical cognitive skills due to ethical challenges such as misinformation [and] the outsourcing of synthesis."*

### 5.1 Convergence
- **The value of the cognitive "struggle":** The cognitive struggle of manually evaluating, linking, and synthesizing notes is *where the actual learning occurs*. Auto-generating connections robs the user of this sense-making process. Validates our community feedback finding (S2) and **DELTA-CORE-004** design: AI surfaces *candidates*, but the human must validate and approve the connection.
- **Curation over automation:** *"An LLM Wiki is only as reliable as the curation of who feeds it sources and reviews the output."* Mirrors **CANON-006** and the strict separation of the immutable inbox (`raw/`) from canonical knowledge.

### 5.2 Divergence
- **Target audience:** S5 evaluates the pattern through the lens of academic literature reviews where subtle nuance is paramount. While `llm-wiki-oe` supports this via `EPISTEMOLOGY.md`, its day-to-day utility in engineering workflow capture weights cognitive friction differently.

---

## 6. S6 — Recurrence-Based Consolidation (Validating "Recurrence Before Connection")

This 2026 research paper directly addresses the community desire (noted in S2) for AI to surface *temporal recurrence* rather than just *structural connection*.

> *"The key to recurrence-based consolidation is to utilize a cheap subconscious memory to buffer the incoming interactions and trigger consolidation [based on frequency patterns] rather than immediate structural linking."*

### 6.1 Convergence
- **Temporal frequency over snapshot structure:** RecMem demonstrates that buffering raw interactions and abstracting them only when a recurrence threshold is met yields higher-quality, more generalizable memory nodes than immediate per-ingestion linking. Provides academic validation for the "recurrence before connection" insight raised in S2.
- **Subconscious buffer:** Maps cleanly to our `raw/` → `discovery/` staging pipeline, suggesting the discovery phase should weigh `cooccurrence_count` not just by spatial proximity in a single corpus hash, but by temporal frequency across multiple ingestion sessions.

### 6.2 Divergence
- **Implementation complexity:** RecMem relies on continuous embedding and clustering of a subconscious buffer. `llm-wiki-oe` keeps embeddings opt-in (Layer 7). Adopting recurrence tracking is more cleanly implemented via deterministic frequency counters in DuckDB (`discovery/*.parquet`) rather than vector-based clustering.

---

## 7. S7 — Deterministic Pipeline as the Only Scalable Path

Formalizes the architectural boundary between stochastic agents and deterministic systems, providing an engineering blueprint for scaling knowledge repositories.

> *"Building a deterministic pipeline on top of a stochastic agent [converts] the language model from a free-form generator into an auditable controller."*

### 7.1 Convergence
- **Auditable control plane:** As skill and knowledge repositories grow, stateful multi-agent coordination becomes a liability. Tightly interdependent tasks must be executed via a deterministic pipeline where steps execute in a predefined sequence with hardcoded branches and strict upstream validation.
- **Academic validation of CANON-006:** The most rigorous academic articulation of the "Compiler, Not Agent" principle. Confirms that the LLM's role is to generate *proposals* (stochastic layer), while a hardcoded deterministic pipeline handles parsing, validation, and filesystem mutations.

### 7.2 Divergence
- **None.** This paper serves as a theoretical mirror to the `llm-wiki-oe` architecture, specifically the 5-layer deterministic validation pipeline (`VALIDATION.md` §10.1) and the Durable Staged Commit Protocol (**DSCP**).

---

## 8. Derived Changes & Architectural Affirmations

| Change / Affirmation | Where |
|---|---|
| **Hallucination propagation risk documented** — cite S4 as the threat model for why **DELTA-CORE-004** (`pending` state) and review-gated writes are non-negotiable | `EPISTEMOLOGY.md` §5.3 / `DISCOVERY.md` §6 |
| **Cognitive erosion as a design feature** — frame the "friction" of human review not as a UX flaw, but as a deliberate safeguard against the erosion of critical cognitive sense-making (S5) | `README.md` deviation 21 |
| **Recurrence tracking elevated** — elevate "temporal-frequency recurrence" to a specified candidate for `discovery/concept_proposals.parquet` via deterministic DuckDB aggregation (per S6) | `DISCOVERY.md` §5.2 |
| **Deterministic Control Plane terminology** — adopt the phrase *"deterministic pipeline on top of a stochastic agent"* (S7) as the formal descriptor for **CANON-006** | `ARCHITECTURE.md` §2.2 |

---

### Summary of the Expanded Critique Landscape
1. **S4** proves that without strict gating, probabilistic linking leads to cascading hallucination contamination.
2. **S5** validates that preserving human friction in the linking process is a feature, not a bug, preventing cognitive erosion.
3. **S6** provides a viable, research-backed mechanism (recurrence-based consolidation) for "recurrence before connection."
4. **S7** formalizes the "deterministic pipeline over stochastic agent" paradigm as the only academically sound path to scaling auditable knowledge systems.