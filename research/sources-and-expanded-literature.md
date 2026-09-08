# Curated Research Corpus & Theoretical Foundations

> **Type**: Non-normative Research & Provenance Record
> **Status**: Curated & Consolidated (includes 2025–2026 Frontier Literature)
> **Retrieved/Updated**: 2026-08-19

---

## 1. Overview & Selection Criteria

This document indexes the foundational literature, industry specifications, empirical benchmarks, and seminal computer science papers that inform the architecture of **LLM Wiki** (`llm-wiki-oe`).

To ensure a high signal-to-noise ratio, entries are strictly filtered by the following criteria:
1. **Architectural Grounding**: Directly motivates a rule, invariant, layer, or registry in `specs/`.
2. **Seminal Priority**: Prefers primary research papers, formal RFCs/standards, and reference implementations over secondary blog commentary.
3. **Zero Redundancy**: Consolidates overlapping articles into their authoritative canonical sources.

---

## 2. Core Literature & Architectural Derivations

### A. The LLM-Wiki Paradigm, Governance & Agent Orchestration

| Primary Resource | Origin / Authors | Core Concept & Insight | Realization in `llm-wiki-oe` |
|---|---|---|---|
| **`tyrozz/llm-wiki`** | [github.com/tyrozz/llm-wiki](https://github.com/tyrozz/llm-wiki) | Canonical open-source reference implementation of Karpathy's LLM-Wiki pattern using Obsidian and Claude Code. | Validates filesystem-first Markdown + YAML storage; informs `/lint`, `/validate`, and inbox processing workflows. |
| **"Andrej Karpathy's Rules for AI Coding Agents"** | Karpathy / *Creative AI Ninja* (2026) | Establishes the 4 agent behavioral axioms: *Think before coding*, *Simplicity first*, *Surgical changes*, *Goal-driven verification*. | Enforced in agent system prompts (`.agents/skills/llm-wiki/SKILL.md`) to prevent hallucinated refactorings and unbounded file sprawl. |
| **"Spec-Driven Agent Development with CLAUDE.md"** | Jin (System Architect) (2026) | Analyzes why declarative operating specifications outperform ad-hoc natural language prompts in multi-step agent tasks. | Motivated strict declarative YAML registries (`schemas/registry/`) over loose natural-language prompting. |
| **"Automated Vault Ingestion & Trigger Workflows"** | [MindStudio.ai](https://www.mindstudio.ai/blog/how-to-build-llm-wiki-knowledge-base-obsidian-claude-code) (2026) | Demonstrates integrating external event triggers (Slack, Notion) into structured staging vaults. | Informs non-invasive raw capture staging (`raw/` → `discovery/`) in `INGEST-ADAPTERS.md`. |

---

### B. Cognitive Note Systems & Trajectory Harvesting

| Primary Resource | Origin / Authors | Core Concept & Insight | Realization in `llm-wiki-oe` |
|---|---|---|---|
| **"Zettel-Builder & The Studio Paradigm"** | Shuyi Wang (`wshuyi`) (2025–2026) | Distinguishes the *Warehouse* (passive note hoarding) from the *Studio* (active cognitive synthesis); delegates mechanical extraction/linking to AI while keeping curation human-led. | Informs candidate proposal staging in `discovery/concept_proposals.parquet` and the "Compiler not Agent" philosophy (**CANON-006**). |
| **"SkillClaw: Collective Skill Evolution from Trajectories"** | Giljae et al. (*arXiv:2604.08377*, 2026) | Framework that harvests multi-user agent execution trajectories, extracts recurring patterns/fixes, and compiles them into a collective evolving skills library. | Direct quantitative support for our scope-conditioned ontological triad (**INGEST-CORE-004**): Trajectory $\rightarrow$ `Incident` / `Observation` $\rightarrow$ `Lesson` $\rightarrow$ `Workflow` $\rightarrow$ `Skill`. |
| **Infini Memory: Maintainable Topic Documents** | Suozhao Ji et al. (*arXiv:2606.10677*, 2026) | Introduces maintainable topic documents with a hybrid reader for long-term agent memory, avoiding context overflow while preserving continuity. | Informs the `raw/` → `discovery/` compaction strategy, offloading long-term state to deterministic Markdown documents rather than ephemeral vector stores. |
| **SkillAdaptor & WebXSkill** | Multiple Authors (*arXiv:2606.01311*, *arXiv:2604.13318*, 2026) | Distills agent interaction trajectories into a compact, non-redundant library of parameterized skills through self-adapting extraction and revision. | Algorithmic basis for **INGEST-CORE-004**, ensuring harvested workflows are parameterized and deduplicated before canonical promotion. |

---

### C. Standardized Formats & Structural Code Intelligence

| Primary Resource | Origin / Authors | Core Concept & Insight | Realization in `llm-wiki-oe` |
|---|---|---|---|
| **Google Open Knowledge Format (OKF v0.2)** | Google Cloud Knowledge Catalog (2026) | Vendor-neutral, Git-friendly standard using typed Markdown + YAML to package curated knowledge for AI agents without RAG chunking loss. | Grounding for `specs/OKF-INTEROP.md` and vendored `external-specs/okf/` (**CANON-002**: canonical native library vs OKF projection). |
| **`lat.md` (Agent Lattice)** | [Agentic Builders](https://github.com/agentlattice/lat) (2026) | Bidirectional `[[wiki-links]]` between Markdown architecture and source code symbols (`[[src/foo.ts#func]]`, `// @lat: [[section]]`) with CLI referential integrity linting. | Parallels Linter Layer 1–5 invariants (**REL-005**, **E009** BrokenLinkError, **E002** path/slug alignment) and deterministic graph verification. |
| **Graphify: Local AST Knowledge Graphs** | Maher Naija & GOpenAI (2026) | Local tree-sitter AST parsing (`CALLS`, `IMPORTS`, `INHERITS`) benchmarked against dense vector search. Demonstrates graphs excel at relational architecture while dense RAG excels at local facts. | Motivates the hybrid retrieval pipeline in `specs/RETRIEVAL.md`: combined Graph Walk + BM25 + Vector RRF reranking. |
| **Layered Entity Graph Architecture** | Irina Adamchic (2026) | Three-layer knowledge graph separating fixed schema ontology, document chunks, and extracted domain instances for cost-effective deterministic traversal. | Supports the multi-layer separation in `specs/ARCHITECTURE.md` §2 (Layer 1 Registries, Layer 2 Knowledge Objects, Layer 3 Graph Index). |
| **MemGraphRAG: Memory-Based Multi-Agent Graph RAG** | *ACM KDD* (2026) | Memory-enhanced multi-agent Graph RAG outperforming vanilla GraphRAG and HippoRAG in multi-hop reasoning latency and precision. | Informs multi-agent query orchestration in `specs/GRAPH-INTELLIGENCE.md` (separating graph traversal, entity resolution, and summary synthesis). |

---

### D. Information Retrieval, Search & Hybrid Ranking (Layers 4 & 7)

| Primary Paper / Standard | Authors & Venue | Core Theoretical Contribution | Realization in `llm-wiki-oe` |
|---|---|---|---|
| **The Probabilistic Relevance Framework: BM25 and Beyond** | Stephen E. Robertson & Hugo Zaragoza (*FnTIR*, 2009) | Formulates Okapi BM25 and term saturation/length normalization for exact keyword matching. | Foundation of Layer 4 lexical retrieval in `specs/RETRIEVAL.md` §3; essential for exact symbol and ID lookup (`(PERS\|ENG)-*`). |
| **Reciprocal Rank Fusion Outperforms Condorcet & Learning to Rank** | Gordon V. Cormack, Charles L. A. Clarke, Stefan Büttcher (*ACM SIGIR*, 2009) | Introduces **Reciprocal Rank Fusion (RRF)**: $RRF(d) = \sum_{r \in R} \frac{1}{k + r(d)}$ ($k=60$). Aggregates disjoint rank orders without score calibration drift. | The core fusion algorithm in `specs/RETRIEVAL.md` §7, combining sparse BM25, dense vector cosine, and graph seed rankings. |
| **Towards Practical GraphRAG: Efficient KG Construction** | *arXiv:2507.03226* (2025) | Hybrid retrieval combining dense vector similarity with efficient graph traversal via RRF, maintaining separate complementary ranking signals. | Directly validates the Layer 4 + Layer 5 hybrid pipeline in `specs/RETRIEVAL.md`, proving RRF is optimal for combining disjoint BM25, vector, and graph ranks. |
| **Approximate Nearest Neighbor Search Using HNSW Graphs** | Yu. A. Malkov & D. A. Yashunin (*IEEE TPAMI*, 2020) | Logarithmic scaling for high-dimensional approximate vector search using multi-layer proximity graphs. | Standard backend for dense semantic vector retrieval in Layer 4 (`specs/RETRIEVAL.md`). |
| **Passage Re-ranking with BERT (Cross-Encoders)** | Rodrigo Nogueira & Kyunghyun Cho (*arXiv:1901.04085*, 2019) | Full joint attention across query-document pairs to resolve deep semantic relevance beyond bi-encoders. | Secondary stage reranker over top-$K$ candidates produced by RRF fusion in `specs/RETRIEVAL.md` §7.1. |

---

### E. Graph Science, Distributed Systems, Security & Epistemics

| Primary Reference / Standard | Authors / Provenance | Core Scientific Principle | Realization in `llm-wiki-oe` |
|---|---|---|---|
| **Personalized PageRank (PPR)** | Page, Brin, Motwani, Winograd (1999) / Haveliwala (2002) | Random walk with restart from seed nodes; models proximity in directed networks. | Multi-hop neighbor expansion starting from BM25/Vector seeds in `specs/RETRIEVAL.md` §5 & `specs/GRAPH-INTELLIGENCE.md` §12. |
| **Hierarchical Community Detection (Louvain / Leiden)** | Blondel et al. (2008) / Traag et al. (2019) | Modularity optimization to uncover nested topic clusters in large graphs. | Generates derived community summaries and macro-syntheses in `specs/GRAPH-INTELLIGENCE.md` §9.2 without modifying canonical files. |
| **Spreading Activation Theory** | Collins & Loftus (*Psychological Review*, 1975) | Associative search through semantic networks via energy decay and edge weight propagation. | Cognitive foundation for bounded BFS traversal (`max_depth`, `min_edge_strength`) in `specs/RETRIEVAL.md` §9.4. |
| **DuckDB & Vectorized Columnar Storage** | Mark Raasveldt & Hannes Mühleisen (*ACM SIGMOD*, 2019) | Vectorized analytical execution engine operating directly on zero-copy Parquet files without server overhead. | Powers the staging analytics engine (`wiki-ingestd`) for `discovery/*.parquet` in `specs/INGEST-STAGING.md`. |
| **Crash-Safe Commit Protocols (ARIES / 2PC)** | Jim Gray (1978) / C. Mohan et al. (*ACM TODS*, 1992) | Write-ahead logging (WAL), prepare-commit transitions, and compensating rollbacks. | Formulates **DSCP** (Durable Staged Commit Protocol) and **DPCP** (Durable Promotion Commit Protocol) in `specs/INGEST-STAGING.md` §7 & §9. |
| **Content-Addressable Storage (CAS) & Merkle DAGs** | Ralph Merkle (1979) / Git Object Model | Cryptographic hash over canonical normalized byte representation determines identity. | Implemented in **INGEST-CORE-007** (`input_sha256` over recursive NFC UTF-8 JSON) and **CANON-005** (evidentiary grounding). |
| **Indirect Prompt Injection & RAG Security Threat Models** | Kai Greshake et al. (2023) / *arXiv:2509.20324* (2025) | Formalizes threat models for RAG systems: knowledge poisoning, indirect prompt injection, and cross-tenant leakage. | Grounds **INGEST-CORE-018** (E120 Capability Firewall: extraction LLMs run with zero tools/write permissions) and pre-retrieval validation gates. |
| **Black-Box Skill Stealing from Proprietary Agents** | *arXiv:2604.21829* (2026) | Demonstrates vulnerabilities where malicious actors distill proprietary trajectories into reusable parameterized skills. | Motivates **INGEST-CORE-002A** (E102A fail-closed quarantine) and access restrictions on raw trajectory logs in `discovery/`. |
| **Deterministic Validation in LLM Knowledge Extraction** | *QIAS / arXiv:2603.24012* (2026) | Non-LLM deterministic validation steps (verifying cited spans exist verbatim, schema pass/fail checks) drastically eliminate hallucinations. | Enforces the "Compiler, Not Agent" axiom (**CANON-006**), where Python linters (`linter.py`) validate and commit candidate knowledge. |
| **Shannon Information Entropy** | Claude E. Shannon (*BSTJ*, 1948) | Entropy $H = -\sum p_i \log_2 p_i$ measures randomness to detect unclassified keys/tokens. | Realized in **INGEST-CORE-002A** (E102A fail-closed quarantine for fields with $H > 4.5$ bits/char). |
| **Linear Time Regular Expressions (RE2/DFA)** | Russ Cox (2007) | Deterministic finite automata guarantee $O(n)$ search time, eliminating catastrophic backtracking ReDoS vulnerabilities. | Required by **INGEST-CORE-011** (E113 bounded linear regex execution on trajectory logs). |
| **W3C PROV-O (Provenance Ontology)** | Missier, Belhajjame, Cheney (W3C Recommendation, 2013) | Standard conceptual model for tracking Entity, Activity, and Agent lineage. | Grounds our PROVENANCE category (`author`, `reviewer`, `source_type`, `source_ref`, `last_modified`, `last_verified`) in `specs/SCHEMA.md`. |
| **Epistemic Modal Logic & Defeasible Reasoning** | Jaakko Hintikka (1962) / John L. Pollock (1987) | Formal treatment of knowledge vs belief and justification under defeasible evidence. | Drives the 4 orthogonal epistemic dimensions (`evidence`, `verification`, `authority`, `consensus`) in `specs/EPISTEMOLOGY.md`. |

---

### F. Classical Information Science & Knowledge Engineering Foundations

| Foundation / Standard | Canonical Origin | Core Theoretical Principle | Realization in `llm-wiki-oe` |
|---|---|---|---|
| **Faceted Classification (PMEST)** | S.R. Ranganathan (1933) / Modern AI Taxonomy (*arXiv:2604.02618*, 2026) | Decomposing subjects along orthogonal facets (Personality, Matter, Energy, Space, Time) ensures information units are reusable without semantic drift. | Foundation of `schemas/registry/facet_registry.yaml` and `ARCHITECTURE.md` §1 Axioms. Prevents taxonomy tree explosion. |
| **Taxonomy vs Ontology Separation** | Formal Ontology & Info Science | Distinguishes strict subject trees (taxonomies) from entity-relationship graphs (ontologies) and typologies (object types). | Formulates **TAX-009** (taxonomy encodes *subject only*) and separates `taxonomy_registry.yaml` from `relation_registry.yaml` and `object_registry.yaml`. |
| **Knowledge Representation & Reasoning (KR&R)** | Brachman & Levesque | Formal domain representations enabling automated inference and constraint verification without contradiction. | Implemented via the 5-layer deterministic validation pipeline (`linter.py`, `VALIDATION.md`) and typed relation assertions. |
| **Semantic Wikis** | Völkel et al. (Semantic MediaWiki, 2006) | Combines human-readable wiki pages with machine-interpretable formal metadata and typed semantic links. | `llm-wiki-oe` is fundamentally a Git-backed Semantic Wiki where Markdown content is paired with strict YAML frontmatter. |
| **Inference Engine & Knowledge Base Separation** | Classical Artificial Intelligence | Strict separation of declarative facts/rules from algorithmic deduction and query processing. | Canonical Markdown+YAML files form the declarative KB; Layer 4–6 retrieval and traversal code forms the inference engine. |
| **Cyc & Upper Ontologies** | Douglas Lenat (1984–present) | Formalized commonsense ontologies, separation of microtheories (contexts), and explicit truth maintenance. | Reflected in our epistemic quadrant (`EPISTEMOLOGY.md`) and isolated `scope` namespaces (`personal` vs `engineering`). |
| **SKOS (Simple Knowledge Organization System)** | W3C Recommendation (2009) | Standardized conceptual relationships (`broader`, `narrower`, `related`, `exactMatch`) for concept schemes. | Informs the separation between taxonomy and semantic relations. The registry currently provides `RELATED_TO`, which is conceptually related to SKOS `related`, but no complete SKOS-to-registry mapping is normative. |
| **Bloom's Revised Taxonomy** | Anderson & Krathwohl (2001) | Cognitive skill hierarchy: *Remember → Understand → Apply → Analyze → Evaluate → Create*. | Parallels our object type progression: `Concept`/`Principle` (Understand) $\rightarrow$ `Procedure`/`Workflow` (Apply) $\rightarrow$ `Lesson`/`Incident` (Analyze) $\rightarrow$ `Product`/`Architecture` (Create). |
| **Chunking & Cognitive Load Theory** | George A. Miller (1956) | Working memory processes information in bounded chunks ($7 \pm 2$, modernly $4 \pm 1$). | Governs atomic Knowledge Object granularity (`ID_PATTERN`), avoiding giant multi-topic monoliths for human and LLM context fit. |
| **Personal Knowledge Management (PKM)** | Frand & Hixon (1999) | Framework for individuals to capture, transform, store, and retrieve knowledge for personal productivity. | Directly grounds `scope: personal`, managing personal engineering notes, workflows, and tools alongside organization-wide assets. |

---

### G. Frontier Research & Emerging Paradigms (2024–2026)

| Breakthrough Paper / System | Authors & Venue | Core Innovation | Replicability / Ingestion in `llm-wiki-oe` |
|---|---|---|---|
| **HippoRAG & HippoRAG 2** | Bernal Gutiérrez et al. (*arXiv:2405.14831*, *arXiv:2502.14802*, 2024–2025) | Neurobiology-inspired long-term memory combining LLMs with Personalized PageRank (PPR) across a dual neocortex/hippocampus graph for multi-hop associative recall and continual learning. | Strong theoretical validation for our Layer 5 graph walk in `specs/RETRIEVAL.md` (§5) as an alternative to iterative, token-heavy LLM queries. |
| **LightRAG: Simple & Fast GraphRAG** | Zirui Guo et al. (*arXiv:2410.05779*, Oct 2024) | Dual-level retrieval (entity-level + high-level thematic) with real-time incremental graph updating without re-indexing the entire corpus. | Demonstrates real-time incremental graph updates; supports our staging reconciliation model (`wiki-ingestd`). |
| **A-MEM: Agentic Memory for LLM Agents** | Wujiang Xu, W. Zhao et al. (*NeurIPS / arXiv:2502.12110*, 2025) | Agent memory system structured explicitly on the **Zettelkasten method**; dynamically generates structured attributes and evolves/re-links historical memory nodes upon receiving new inputs. | Academic validation of using atomic Zettelkasten cards as an agent memory primitive, closely mirroring our `Incident` → `Lesson` → `Workflow` lifecycle. |
| **CoALA: Cognitive Architectures for Language Agents** | Sumers et al. (*arXiv:2309.02427*, 2023–2024) | Systematizes agent memory into working memory, episodic memory (trajectories), semantic memory (world facts), and procedural memory (executable skills). | Directly maps to our metadata taxonomy: `raw/` = episodic trace; `personal/` & `engineering/` = semantic fact base; `Workflow`/`Skill` = procedural memory. |
| **Corrective RAG (CRAG) & Self-RAG** | Yan et al. (*arXiv:2401.15884*) & Asai et al. (*arXiv:2310.11511*) | Dynamic retrieval evaluators categorizing retrieval confidence (Correct, Ambiguous, Incorrect) and triggering adaptive fallback/web searches. | Parallels our deterministic quality gates (**INGEST-CORE-006** $Q_{\text{composite}}$ threshold and `ambiguous_scope.parquet` review routing in **INGEST-CORE-008**). |
| **LLM Wiki in Production & Scaffolding Decay** | Shuyi Wang (2026, Medium / Research Note P20) | Real-world evaluation of Karpathy's LLM Wiki on an 84-page knowledge base; demonstrates that mechanical maintenance cost is the central barrier solved. Documents scaffolding decay (over-scaffolding choking frontier reasoning), the "not your voice" web-dump trap, and the builder-reviewer triad (Claude Code vs Codex). | Informs `specs/REVIEW-PROMOTION.md` (adversarial dual-agent review), `specs/AGENT-SKILLS.md` (scaffolding lifecycle & pruning), `specs/VALIDATION.md`, and `specs/ARCHITECTURE.md`. |
| **Inefficiencies of Meta-Agents for Agent Design** | Batu El, Mert Yuksekgonul, James Zou (*Stanford CS329A*, 2025 / Research Note P21) | Demonstrates that accumulating past designs in prompt context degrades performance; meta-agents suffer near-zero behavioral diversity; automated design is economically non-viable vs fixed deterministic scaffolds. | Strongly validates **CANON-006** and fixed versioned YAML registries (`spec_ownership.yaml`, `object_registry.yaml`) over unconstrained meta-prompts. |
| **PRIME: Planning with Reflective, Iterative, Multi-Agentic Exploration** | Chelsea Zou, Samuel Liu, Jui Khankari (*Stanford CS329A*, 2025 / Research Note P21) | Formulates planning as recursive MCTS option discovery; couples dynamic reasoning strategy selection (reflexion, debate, voting) with LLM value function pruning. Outperforms LATS on WebShop and PlanBench. | Informs [`plans/98-TEST-TIME-SEARCH-AND-VERIFIERS.md`](file:///home/daniel6651/omniscient-trash-heap-spec/plans/98-TEST-TIME-SEARCH-AND-VERIFIERS.md) for recursive tree search and step-level evaluation during knowledge extraction. |
| **Enhancing Mathematical Reasoning via Distillation, GRPO & Multi-Agent PRM Reranking** | Abhinav Agarwal, Carlo Baronio, Shree Reddy, Shubhra Mishra (*Stanford CS329A*, 2025 / Research Note P21) | Distills reasoning traces into small student models; pairs memory-optimized GRPO (zero KL penalty, no critic) with multi-agent Process Reward Model (PRM) reranking, yielding 79.9% on AIME'24 with 6.3x token reduction. | Informs process-level verification (PRM) over outcome-only evaluation in `specs/VALIDATION.md` and token-budget efficiency in ingestion pipelines. |
| **ARCHON Augmented: Planning & Web-Enhanced Components** | Megan Mou, Sherry Xie, Emily Zhang, Andrew Park (*Stanford CS329A*, 2025 / Research Note P21) | Modular multi-agent architecture fusing Generator, Planner, Web Search, and Verifier layers, enabling open-source models to rival proprietary frontier models on Humanity's Last Exam (HLE). | Reenforces modular agent architecture in `specs/AGENT-SKILLS.md` and external tool integration guidelines. |
| **AppBench: Benchmarking AI-Generated Web Applications** | Ethan Hellman, Brendan McLaughlin, Abhinav Lalwani, Belinda Mo (*Stanford CS329A*, 2025 / Research Note P21) | Benchmark measuring functional UI statefulness and dynamic goal completion beyond static pass@k code generation. | Supports execution sandboxing and behavioral testing in `specs/INGEST-ADAPTERS.md`. |
| **CacheGen & LMCache: KV-Cache Compression and Decentralized Streaming for Fast LLM Serving** | Yuhan Liu, Hanchen Li, Junchen Jiang et al. (*ACM SIGCOMM 2024 / Tensormesh / LMCache 2024–2026*, Research Note P21) | Treats KV cache as a 3D tensor; achieves 3.5–4.3x compression with adaptive streaming and offloads across GPU HBM $\to$ Host RAM $\to$ Local NVMe $\to$ Network/Tensormesh, eliminating TTFT prefill latency. | Informs `specs/ARCHITECTURE.md` (memory tiering: disk-first plain text + multi-tier tensor caching) and `specs/RETRIEVAL.md` (sub-second agent retrieval). |
| **CacheBlend: Fast LLM Serving for RAG with Cached Knowledge Fusion** | Jiayi Yao, Hanchen Li, Junchen Jiang et al. (*arXiv:2405.16444 / UChicago*, 2024 / Research Note P22) | Solves non-prefix KV-cache reuse for multi-chunk RAG; selectively recomputes cross-attention on critical boundary tokens ($\approx 15\%$) while pipelining recompute with multi-tier KV tensor retrieval. Reduces TTFT by 2.2–3.3x and boosts throughput by 2.8–5x. | Connects disk-based canonical knowledge cards to sub-second multi-document synthesis in `specs/RETRIEVAL.md` and `specs/ARCHITECTURE.md`. |
| **The Devil Has A Long Tail (Scaffolding Cancer & Enterprise LLMs)** | Sanjay Krishnan (*UChicago AI + Systems Seminar*, 2024 / Research Note P22) | Identifies that enterprise LLMs recreate the distributed systems trap: instant generality bought at the cost of debugging an endless long tail of failure modes, resulting in uncontrolled scaffolding code growth that obscures core logic. | Strongly reinforces **CANON-006** and deterministic outer compiler linters (`linter.py`, ARIES state machines) over endless prompt patching. |
| **Synthetic Gravity & Model Autophagy Disorder (MAD)** | Hayanan (*AI Advances*, Sept 2026 / Research Note P22) | Formulates next-token probability optimization as an inward gravitational force pulling generative systems toward mediocre center across 6 scales (repetition loops, mode collapse, style homogenization, visual averaging, cultural clustering, and recursive collapse / Shumailov et al. 2024). | Solidifies the necessity of preserving raw human idiosyncratic sources (`scope: personal`, incident logs), avoiding recursive summary loops, and enforcing adversarial review in `specs/REVIEW-PROMOTION.md`. |
| **DeepSeek Harness (`dsh`) & Cordis Plugin Architecture** | DeepSeek AI & Sumit Pandey (*GitHub / Towards Deep Learning*, 2026 / Research Note P22) | Demonstrates that the harness is the product; decouples runtime from model via Cordis microkernel ("everything is a plugin"); establishes verifiable step/turn execution loop (line-numbered file reading, sandboxed bash execution, test-driven self-correction); shows local 27B model in an inspectable harness beats shifting closed cloud APIs. | Informs modular agent architecture in `specs/AGENT-SKILLS.md`, sandboxed execution pipelines in `specs/INGEST-ADAPTERS.md`, and test-driven validation. |

---

## 3. Synthesis: The 6 Architecture Axioms Derived from the Literature

1. **Compiler, Not Agent (CANON-006):** LLMs reason and propose candidate knowledge; deterministic code (linters, ARIES-style state machines, parsers) validates and writes.
2. **From Warehouse to Cognitive Studio:** Notes are not hoarded in passive silos; they are compiled into an actively linked, self-healing semantic graph.
3. **Hybrid Search Supremacy (BM25 + HNSW + Graph + RRF):** Exact keyword precision (Okapi BM25) and conceptual recall (HNSW Vector) are unified scale-free via Reciprocal Rank Fusion (RRF) and expanded via Personalized PageRank.
4. **Faceted Orthogonality Over Hierarchy Bloat:** Ranganathan's faceted model prevents taxonomy explosion by keeping facets (`toolchain`, `audience`, `lifecycle`, `test_level`) strictly orthogonal to subject taxonomies and relation graphs.
5. **Crash-Safe & Adversarial Resilience:** Multi-stage ingestion requires distributed transaction protocols (DPCP/DSCP) paired with fail-closed security against prompt injection, high-entropy secrets, and ReDoS.
6. **Native Typed Library vs Interop Projection (CANON-002):** Internal representations maintain full epistemic and facet richness while projecting downward into OKF, Obsidian, or MkDocs.
