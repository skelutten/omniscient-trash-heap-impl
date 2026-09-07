# Prior Art: "LLM Wiki" pattern (Karpathy)

> **Type**: Prior-art provenance record — NON-NORMATIVE
> **Upstream**: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#file-llm-wiki-md
> **Retrieved**: 2026-08-17 · 75 lines · 11,985 bytes · `sha256:dc3efe98ae62f23dd08acad13aba2e95287beb20b6bec2f4af0423557fe37401`
> **Licence**: none declared in the gist → **full text is NOT vendored** (see `README.md` §3)

---

## 1. Why this is not in `external-specs/`

`external-specs/README.md` §2 admits only documents this project writes invariants
*against*. This document fails that test decisively, and says so itself — twice:

- opening: *"This is an idea file, it is designed to be copy pasted to your own LLM
  Agent... your agent will build out the specifics in collaboration with you."*
- closing §Note: *"This document is intentionally abstract. It describes the idea, not
  a specific implementation... The document's only job is to communicate the pattern."*

Measured content: **zero** normative keywords (`MUST`/`SHALL`/`REQUIRED` in the RFC
sense), **zero** field or schema definitions, **no** conformance section. There is
nothing to conform to. It is the highest-value item in `research/`, not a
specification — influence is not conformance.

## 2. What it describes

Three layers, and the operations over them:

| Layer | Role |
|---|---|
| **Raw sources** | Curated, immutable source documents; the LLM reads but never modifies them |
| **The wiki** | LLM-generated interlinked Markdown; the LLM owns this layer entirely |
| **The schema** | A configuration document (`CLAUDE.md` / `AGENTS.md`) telling the LLM the conventions and workflows |

Operations: **ingest** (read a source, discuss, write a summary, update index, update
affected pages, append to log — one source may touch 10–15 pages) and **query**
(search, read, synthesise with citations — and **file good answers back as new pages**
so exploration compounds).

Core thesis: RAG re-derives knowledge on every question; a maintained wiki is a
*persistent, compounding artifact*. What makes it viable is that the bookkeeping cost
— cross-references, currency, contradiction flagging — is near zero for an LLM and
prohibitive for a human.

## 3. Direct derivation

The five principles in `~/.kiro/wiki/SCHEMA.md` — the corpus being migrated into this
architecture — align with this pattern almost one-to-one:

| `~/.kiro/wiki/SCHEMA.md` principle | Corresponding idea in the pattern |
|---|---|
| "The wiki is compiled knowledge — synthesized from raw sources" | knowledge is *compiled once and kept current*, not re-derived per query |
| "The LLM owns the wiki — humans read and direct" | "You never write the wiki yourself... you're in charge of sourcing and asking the right questions" |
| "Provenance is mandatory" | raw sources are immutable and are what claims trace back to |
| "Pages are interlinked — isolated pages are failures" | "the cross-references are already there" |
| "Incremental growth — one source at a time, many pages per ingest" | "a single source might touch 10–15 wiki pages" |

I could not establish which document came first (the GitHub API was rate-limited at
retrieval time), so this is recorded as **alignment, not proven causation**.

## 4. Convergent design (arrived at independently)

Worth recording, because independent convergence is evidence a design is load-bearing
rather than ceremony:

| Idea | Here | Also in |
|---|---|---|
| `index.md` (content catalog) + `log.md` (append-only chronology) | `BUNDLE-009`, progressive disclosure | OKF v0.2 §8/§9 makes both **reserved filenames**; `~/.kiro/wiki` already has both at root |
| Read the index first, then drill into pages | `OKF-INTEROP.md` §16.5 progressive-disclosure flow | the pattern: "avoids the need for embedding-based RAG infrastructure" |
| Index-only is sufficient at small scale | `GRAPH-INTELLIGENCE.md` §12.3: graph-enhanced retrieval not recommended below ~500 nodes | the pattern: works well at "~100 sources, ~hundreds of pages" |
| Hybrid BM25 + vector + LLM re-ranking | `RETRIEVAL.md` §9 Layer 7 (BM25 + vector + cross-encoder + RRF) | the pattern cites `qmd` as exactly this |
| Frontmatter as queryable metadata | facets (`facet_registry.yaml`) | the pattern cites Obsidian Dataview over frontmatter |
| Answers filed back as new pages | `DISCOVERY.md` promotion lifecycle | the pattern: "good answers can be filed back into the wiki" |
| Git repo of Markdown as the substrate | `CANON-001` | the pattern: "the wiki is just a git repo of markdown files" |

## 5. Deliberate divergence

This project is a **governed** instantiation of the pattern. The pattern is
deliberately unopinionated where we are strict — that is not a gap in either:

| Dimension | The pattern | Here |
|---|---|---|
| Page structure | free-form, domain-dependent | 24 object types with mandatory facets (`DATA_MODEL.md` §3) |
| Links | plain Markdown cross-references | 30 typed, registry-governed relations (`ONTOLOGY.md` §4) |
| Trust | citations and provenance | four orthogonal epistemic dimensions + conflict ranking (`EPISTEMOLOGY.md` §5) |
| Lifecycle | log entries | `status` × `facets.lifecycle`, separated by `GOV-001` |
| Validation | "lint passes" mentioned informally | 28 error codes, formal invariants, conformance suite (`VALIDATION.md`) |
| Placement | "whatever fits your domain" | deterministic path from taxonomy (`TAX-002`) |

### 5.1 One divergence that needed reconciling

The pattern calls **raw sources** "your source of truth". `CANON-001` calls the
**canonical Knowledge Objects and registries** the source of truth. Both are correct
about different things, and the distinction is now stated explicitly in
`ARCHITECTURE.md` §2.2:

- raw sources are the **evidential** source of truth — what claims are traced back to
  (`provenance.source_ref`), and they are immutable;
- canonical Knowledge Objects are the **architectural** source of truth — what every
  derived artifact is rebuilt from (`CANON-002`).

Conflating them would license a derived index to be rebuilt from raw sources rather
than from reviewed knowledge, bypassing governance.

## 6. If you later want the full text vendored

It is not vendored because the gist declares no licence, so redistribution terms are
unknown. To change that, either obtain permission or confirm an internal-use policy
covers it, then move it to `external-specs/karpathy-llm-wiki/` **only if** it also
acquires conformance obligations — otherwise keep it here and vendor alongside this
record with a `PIN.yaml` and an explicit licence note.