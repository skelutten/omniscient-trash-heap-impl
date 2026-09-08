# Research & Source Material (non-normative)

> **Status**: Non-normative. Nothing here constrains an implementation. Where this
> material has been turned into obligations, those live in `specs/`.

---

## 1. What belongs here

Material that **informed** the design but that this project does not conform to:
design discussions, articles, patterns, transcripts, prior art, and provenance
records for ideas that were adopted.

| File | Kind | Informs |
|---|---|---|
| `GRAPH-RAG-RESEARCH-NOTES.md` | Raw dialogue transcript | `STRUCTURAL-GRAPH.md` (SG-001–SG-020), `OKF-INTEROP.md` (OKF-001–OKF-010), `ARCHITECTURE.md` §2.2–§2.3 (Knowledge Library paradigm) |
| `llm-wiki-pattern-karpathy.md` | Prior-art provenance record | The overall wiki pattern; `~/.kiro/wiki` conventions; `RETRIEVAL.md`, `BUNDLE-009`, `DISCOVERY.md` promotion lifecycle |
| `related-implementations.md` | Prior-art implementations (P1–P10) | graybox, GraphRAG, G-Memory, `files.md`, `synthadoc`, HiSkill, Rel(AI)Build, OpenWiki, agentic-kg, production-grade-agents: source of **CANON-006**, ontological triad validation, and deviations 21/23 |
| `critiques-and-community-feedback.md` | Critique + community feedback (S1–S7) | Implementation guidance: `VALIDATION.md` §10.1/§12, `ONTOLOGY.md` REL-004a, `GRAPH-RETRIEVAL.md` §8, S4 hallucination propagation, S5 cognitive erosion, S6 RecMem recurrence, S7 deterministic pipelines |
| `openwiki-grounded-claims-and-local-serving.md` | Empirical road test review | `STRUCTURAL-GRAPH.md` (SG-001–SG-020), `OKF-INTEROP.md` (OKF-001–OKF-010), `RETRIEVAL.md` (RET-009), `INGEST-STAGING.md` (durable checkpoints) |
| `pubmed-zero-llm-knowledge-graph.md` | Adversarial benchmark review | `RETRIEVAL.md` (§9.6, §9.7, RET-006–RET-009), `GRAPH-INTELLIGENCE.md` (§11.1 CSR), `INGEST-ADAPTERS.md` (§3.8, ADA-008), `plans/96-OPT-IN-PUBMED-BENCHMARK.md` |
| `agentic-architectures-and-production-systems.md` | Pattern taxonomy & enterprise review | `ARCHITECTURE.md` (CANON-006, 7 layers), `INGEST-STAGING.md` (CSCC/DSCP), `VALIDATION.md` (epistemic firewalls), `RETRIEVAL.md` (deterministic routing) |
| `state-of-the-nation-llm-knowledge-bases-2026.md` | Industry state survey & OpenWiki review | `ARCHITECTURE.md` (§2.3 Knowledge Library), `OKF-INTEROP.md` (OKF-001–OKF-010), `STRUCTURAL-GRAPH.md` (SG-013), `GRAPH-INTELLIGENCE.md` (§11.1 CSR), Plan 61 |
| `aix-okf-superset-and-practitioner-scars.md` | Standard superset & failure mode review | `OKF-INTEROP.md` (OKF-001–OKF-010), `ONTOLOGY.md` (§4, REL-004/REL-004a), `SCHEMA.md` (slug/ID invariance), `VALIDATION.md` |
| `stanford-cs329a-self-improving-agents.md` | Curriculum & frontier lab review | `ARCHITECTURE.md` (CANON-006), `VALIDATION.md` (uncheatable verifiers), `GRAPH-INTELLIGENCE.md` (§11.1 CSR), `INGEST-STAGING.md` |
| `frontier-agentic-foundations-and-test-time-scaling.md` | Master survey: 34 foundational papers (2021–2026) | `ARCHITECTURE.md` (CANON-006), `VALIDATION.md` (uncheatable verifiers), `GRAPH-INTELLIGENCE.md` (§11.1 CSR), `ONTOLOGY.md` §4, `INGEST-STAGING.md` |
| `karpathy-markdown-vault-vs-hierarchical-maps.md` | Prior-art & scaling analysis (P15) | Fabio Yáñez Romero on Karpathy's flat markdown vault breakdown; 2D Map Architecture (`card.md` vs `full.md`), `ARCHITECTURE.md` (§2.3 Knowledge Library), `RETRIEVAL.md` |
| `failure-modes-of-llm-knowledge-graph-extraction.md` | Pipeline failure & modular KG review (P16) | Fabio Yáñez Romero on cascading extraction errors, Asserted vs Augmented KGs, modular CLI framework (`kgb`); `specs/RELATION-EXTRACTION.md`, `ONTOLOGY.md` §4 |
| `fareed-khan-10m-rag-and-disk-streaming-architectures.md` | Large-scale RAG & C streaming review (P17) | Fareed Khan on 10M RAG ("Retrieve, Constrain, Verify, Abstain") & pure C 2.8T MoE disk-streaming ($O(1)$ RAM invariant); `RETRIEVAL.md` (§9.6-§9.7), `INGEST-ADAPTERS.md` (ADA-008) |
| `the-harness-is-the-product-and-open-coding-agents.md` | Production harness & local agent review (P18) | Shrashti Singhal, Hamza Boulahia, Pranit naik on "the harness is the product", OpenCode terminal ergonomics, Sakana AI Fugu router; `ARCHITECTURE.md` (CANON-006), `AGENT-SKILLS.md` |
| `personal-agentic-systems-and-neuroplastic-graphs.md` | Personal AI & neuroplasticity review (P19) | Erdogan T, Codebook Fusion, Fabio Yáñez Romero on "LLM is a CPU", multi-million doc graphs, and HOPE/Delta Gradient Descent; `INGEST-PIPELINE.md`, `GRAPH-INTELLIGENCE.md` |
| `shuyi-wang-llm-wiki-adversarial-agents-and-scaffolding.md` | LLM Wiki practice & adversarial agent review (P20) | Shuyi Wang on Karpathy LLM Wiki in production (84-page Hermes test), scaffolding decay, builder-reviewer triad (Claude Code vs Codex), and human-on-the-loop governance; `ARCHITECTURE.md`, `REVIEW-PROMOTION.md`, `AGENT-SKILLS.md` |
| `stanford-cs329a-projects-and-lmcache-infrastructure.md` | Stanford CS329A projects & LMCache review (P21) | Stanford CS329A Winter 2025 cohort (Batu El on meta-agent inefficiencies, PRIME MCTS planning, Agarwal et al. GRPO+PRM, ARCHON inference modularity, AppBench) & LMCache / CacheGen multi-tier KV-cache tensor offloading; `ARCHITECTURE.md`, `RETRIEVAL.md`, Plan 98 |
| `sources-and-expanded-literature.md` | Curated Survey & Foundations | Core literature (OKF, lat.md, Graphify, Karpathy, Jin, Shuyi Wang, SkillClaw, MemGraphRAG, BM25, RRF, HNSW, ARIES, Shannon, RE2, PROV-O, KR&R, Cyc, SKOS, Facets, Bloom, Chunking, HippoRAG, LightRAG, A-MEM, CoALA, CRAG) |


## 2. `research/` vs `external-specs/` vs `specs/`

The distinguishing test is a single question:

> **Do we write code or invariants that must conform to this document?**

| Answer | Home | Obligation |
|---|---|---|
| Yes — it is a contract we implement against | `external-specs/` | Vendored verbatim, pinned by hash, licence included, read-only |
| No — it is an idea, discussion or prior art | `research/` | Cited for provenance; may be summarised rather than copied |
| It is our own normative work | `specs/` | Authored here, section-numbered, invariant-bearing |

A document that describes *a pattern* rather than *a format* belongs here even when
its author is authoritative and the influence on this project is large. Influence is
not conformance.

## 3. Rules

- **Non-normative.** Nothing here may be cited as the reason an implementation must
  behave a certain way. If an idea earned an obligation, that obligation lives in
  `specs/` and the record here says which one.
- **Provenance over reproduction.** Record URL, retrieval date, `sha256` and the
  derivation. Vendor the full text **only** when the licence clearly permits it;
  otherwise summarise and link. Unlicensed third-party text is not vendored.
- **Never deleted.** Source material is retained even after its content has been
  synthesised into `specs/` (`ARCHITECTURE.md` §2.2: the wiki supplements sources,
  it does not replace them).
- **Attributed.** Adopted ideas name their origin, so that convergent design and
  borrowed design can be told apart later.