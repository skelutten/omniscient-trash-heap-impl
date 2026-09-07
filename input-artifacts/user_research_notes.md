# LLM Wiki — User Research & Behavioral Dynamics (v3.8.10 Grounded Baseline)

> **Document Type**: Review Input Artifact; not a normative owner
> **Status**: Refined via Cognitive Empathy, Second-Order Analysis & Empirical Observations
> **Scope**: User Psychology, Review Friction & Operational Invariants

---

## 1. Key Behavioral Observations & Real-World Friction

1. **Burst Capture vs. Zero-Discipline Filing:** Technical users capture information in erratic, high-intensity bursts (papers, URLs, CLI traces, meeting fragments) but rarely maintain the discipline to file, tag, and cross-reference immediately. Any system that assumes manual filing discipline fails.
2. **The "Link Soup" Backlash (Trust Erosion):** When AI tools automatically inject links into notes without explicit human verification, users rapidly lose trust in the entire graph. A few false or hallucinated connections cause users to mentally discount all connections.
3. **Quality Over Quantity:** Users vastly prefer a sparse graph of verified, high-conviction relationships over a dense, automated web of statistically plausible noise.
4. **Recurrence as Truth Signal:** A concept or connection that recurs across multiple independent captures carries significantly higher epistemic weight than a one-off mention.

---

## 2. Architectural Guardrails Derived from User Dynamics

| User Friction / Behavior | Design Flaw in Other Tools | LLM Wiki Invariant Solution |
| :--- | :--- | :--- |
| **Filing Backlog Panic** | Requiring upfront manual classification at capture time. | **Zero-Friction Staging Area (`staging/`):** Capture raw text instantly; automated LLM triage drafts metadata in the background. |
| **Loss of Trust in Graph** | Autonomous, silent background editing of note files. | **Propose-Then-Promote Gate:** Candidate diffs are rendered explicitly; no link or relation is written without review. |
| **Review Fatigue** | Monolithic, all-or-nothing manual verification of every word. | **Batch Triage & Epistemic Ranking:** System groups related proposals, calculates confidence scores, and enables batch promotion. |
| **Context Lock-in Fear** | Notes trapped in proprietary database structures. | **100% Plain-Text Sovereignty:** All notes remain standard Markdown + YAML frontmatter readable in any editor. |

---

## 3. The "Studio Paradigm" vs. "The Warehouse"

- **The Warehouse (Anti-Pattern):** Passive hoarding of static files where notes enter and never interact.
- **The Studio (Target Experience):** An active workshop where the LLM continuously synthesizes connections, flags contradictions across documents, drafts topic summaries, and serves as an evidence-grounded sparring partner.
