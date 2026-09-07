# LLM Wiki — Market & Prior Art Analysis (v3.8.10 Grounded Baseline)

> **Document Type**: Review Input Artifact; not a normative owner
> **Status**: Refined via First Principles, Epistemic Classification & Competitive Mapping
> **Scope**: Landscape Comparison & Strategic Positioning

---

## 1. Competitive Landscape Matrix

| System / Category | Source of Truth | AI Integration Model | Knowledge Integrity Risk | Rebuildable Projections |
| :--- | :--- | :--- | :--- | :--- |
| **Traditional Markdown Vaults (Obsidian, Foam, Logseq)** | Local Markdown files | None / Ad-hoc chat plugins | Low (manual), but high friction and dead file accumulation | No (proprietary graph plugins) |
| **Naive Agentic Memory (Self-Modifying Graphs / Daemons)** | Vector DB / SQLite | Unconstrained write access | **Critical:** Silent semantic drift, hallucinated relations | No (state trapped in DB) |
| **Generic RAG & GraphRAG Tools** | Document chunks / Vector Index | Read-only chunk search | Medium: Chunking loss, context fragmentation | Partial (rebuildable, but not a knowledge base) |
| **Karpathy's LLM Wiki (Raw Pattern)** | Filesystem Markdown | Prompt-driven agent updates | Medium: Agent write permissions risk subtle corruption | Yes |
| **LLM Wiki (`llm-wiki-oe`)** | **Canonical Markdown + Declarative Registries** | **Governed Proposal & Compilation Model** | **Zero:** Immutable staging + deterministic linter gate | **Yes (100% disposable derived layer)** |

---

## 2. Strategic Differentiation & Core Gap

Existing tools force users to choose between two unacceptable extremes:
1. **The Static Manual Burden:** Complete manual control with zero active synthesis, leading to abandoned notes.
2. **The Ungoverned Autonomous Black Box:** Fast automated tagging and linking that quickly corrupts ground truth.

**LLM Wiki bridges this gap** by implementing the **"Compiler Paradigm"**:
- The LLM acts as an untrusted, highly creative parser and compiler that drafts candidate proposals (`discovery/`, `staging/`).
- The deterministic linter (`VALIDATION.md`) and declarative registries (`schemas/registry/`) act as the type checker.
- The user retains absolute governance, approving promotion with full atomic safety (`.tmp` + `os.replace`).

---

## 3. Technology & Standard Alliances

- **Google Open Knowledge Format (OKF):** Directly aligns with Google's Git-friendly typed Markdown packaging standard for cross-agent interoperability.
- **AST / Graphify Integration:** Enables deterministic structural graphs for codebases and technical documentation.
