# LLM Wiki — Problem Statement (v3.8.10 Grounded Baseline)

> **Document Type**: Review Input Artifact; not a normative owner
> **Status**: Refined via Cognitive Reasoning (Six Hats, First Principles, Anti-Clerk, PreMortem)
> **Scope**: Problem Boundary & Failure Taxonomies

---

## 1. The Core Problem

Knowledge workers, researchers, and software engineers suffer from severe cognitive fragmentation: valuable notes, papers, literature, terminal logs, transcripts, and emergent ideas accumulate in unorganized, isolated silos.

The systemic breakdown manifests in two equally destructive failure modes:
1. **The Passive Graveyard:** Without automated assistance, personal wikis require unsustainable manual indexing, tagging, and cross-referencing. Filing backlogs grow unbounded, and notes become unsearchable dead files within weeks.
2. **The Naive Autonomous Chaos (Knowledge Corruption):** Delegating organization directly to unconstrained autonomous AI agents results in silent semantic drift, hallucinated connections, unverified structural mutations, and loss of epistemic ground truth.

---

## 2. Root Cause Analysis (First Principles & PreMortem)

The breakdown is driven by four structural flaws in existing knowledge tooling:

- **Conflation of Capture and Belief:** Raw, unverified intake material is placed directly into the knowledge base without an isolated staging/quarantine boundary.
- **Conflation of Orthogonal Semantic Dimensions:** Systems collapse `taxonomy` (WHERE), `object_type` (WHAT KIND), `domain` (WHICH AREA), and `epistemology` (CONFIDENCE) into chaotic, flat tag strings.
- **Stateful Database Lock-in:** Storing primary knowledge in proprietary, binary, or non-deterministic databases creates brittle systems that cannot be audited, version-controlled with Git, or rebuilt from disk.
- **Ungated Model Write Access:** Allowing non-deterministic probabilistic models to execute direct, in-place write mutations over permanent files with no human-in-the-loop review or deterministic schema validation.

---

## 3. Who Experiences This

- **Primary Persona (Day 1):** The individual technical knowledge worker, system architect, or researcher who manages high-context, compounding knowledge over months and years.
- **Secondary Persona (Extension Target):** Engineering teams needing auditable, Git-versioned knowledge packages (e.g. Google OKF bundles) and deterministic architectural documentation.

---

## 4. Anti-Clerk Mandate & Success Criteria

The solution MUST NOT reduce to a passive, static Markdown reader (the "Hollow Shell"). It must actively assist cognition while provably protecting ground truth:

1. **Deterministic Plain-Text Ground Truth:** 100% of canonical state lives in human-readable Markdown + YAML frontmatter.
2. **Propose-Then-Promote Staging Boundary:** Models propose structured candidate diffs; deterministic linters and explicit governance approve writes.
3. **Disposable Derived Projections:** Vector search, inverted indexes, and structural AST graphs are ephemeral and rebuildable from disk in seconds.
4. **Active Synthesis:** Multi-document question synthesis and proactive link/conflict discovery are first-class Phase 1 capabilities.
