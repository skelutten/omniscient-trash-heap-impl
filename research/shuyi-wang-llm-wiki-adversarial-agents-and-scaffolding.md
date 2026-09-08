# Research Note P20: Shuyi Wang on LLM Wiki in Practice, Adversarial Multi-Agent Review & Scaffolding Decay

> **Type**: Non-normative prior-art provenance & architectural analysis  
> **Author Analyzed**: Shuyi Wang (Professor, AI/PKM researcher) & AI in Plain English  
> **Source Articles (20 Raw Documents)**:
>   1. *Should You Actually Try Karpathy’s LLM Wiki?* (April 16, 2026)
>   2. *Why I Tore Down the AI Meta-Skill I Spent Months Building* (September 8, 2026)
>   3. *Claude Code Is Grinding Away at the Work — So Why Do I Insist on Bringing In Codex to Tear It Down?* (June 27, 2026)
>   4. *Human on the Loop: The Researcher’s New Role in the Age of Agents* (June 19, 2026)
>   5. *If AI Did What You Couldn’t Do Yourself, Would You Dare Sign Your Name to It?* (May 27, 2026)
>   6. *How Can AI Help You Automatically Build a Zettelkasten?* (May 22, 2026)
>   7. *Is RAG Outdated?* (March 13, 2026)
>   8. *How to Build a Research Radar That Watches the Literature for You Every Day Without Writing a Line of Code* (September 1, 2026)
>   9. *If You Teach One AI, Can It Teach the Others?* (May 29, 2026)
>   10. *Introduction to Claude Skills: How AI Evolved from Chatbot to Collaborator* (January 9, 2026)
>   11. *Turning a Lecture Transcript Into a Full Teaching Deck: How Do You Build and Polish a Skill Like This?* (June 22, 2026)
>   12. *Reading the Same Paper: Where Does an AI Agent Beat the Chat Box?* (June 30, 2026)
>   13. *Can You Get AI to Run NetLogo Just by Talking to It?* (August 30, 2026)
>   14. *How to Turn the Files You Already Have into an Interactive AI Q&A Site with WorkBuddy* (September 1, 2026)
>   15. *Why I’m So Excited About Codex’s New Cross-Device Remote Control* (May 19, 2026)
>   16. *What Can We Do When AI Runs So Smoothly That Students Stop Thinking for Themselves?* (May 7, 2026)
>   17. *Can Human-AI Collaboration Still Work When AI Knows Far More Than You Do?* (April 25, 2026)
>   18. *Hybrid Intelligence: What You’re Really Buying* (April 19, 2026)
>   19. *I Didn’t Write a Single Config File, Yet Deployed the Entire OpenClaw System* (February 3, 2026)
>   20. *In the Span of a Single Week, an Open-Source Project Went Through Three Name Changes...* (February 2, 2026)
> **Retrieved**: 2026-09-08  
> **Raw Directory**: `research/raw/`  
> **Informs**: `specs/ARCHITECTURE.md` (3-tier storage, plain-text baseline), `specs/REVIEW-PROMOTION.md` (adversarial dual-agent audit), `specs/AGENT-SKILLS.md` (scaffolding lifecycle & pruning), `specs/VALIDATION.md` (verifier vs delegator invariants), `specs/RETRIEVAL.md` (index-first vs RAG-first), `specs/INGEST-STAGING.md` (CSCC & scope isolation)

---

## 1. Executive Summary

This synthesis examines a 20-article corpus (January–September 2026) authored by practitioner-academic Shuyi Wang and associated publications. Wang brings an unusually rigorous, practical perspective: running long-term personal knowledge bases, multi-agent workflows (Claude Code, OpenAI Codex, OpenClaw, Hermes), and university research pipelines in production daily.

Four overarching architectural lessons emerge that directly validate, challenge, and enrich *The Omniscient Trash Heap*:

1. **The LLM Wiki Solves Mechanical Maintenance, Not Epistemic Voice:**  
   In *Should You Actually Try Karpathy’s LLM Wiki?*, Wang evaluates an 84-page active wiki driven by Hermes. He concludes that the LLM Wiki’s historic breakthrough is not a new algorithm, but **eliminating the mechanical maintenance cost** that caused Memex (1945), Luhmann’s Zettelkasten, and digital PKMs to fail for ordinary users. However, he warns against the **"Not Your Voice" Pitfall**: bulk-ingesting the external web into `raw/` creates a structured aggregator of other people's views, not a personal knowledge library.
2. **Scaffolding Decay & The Meta-Skill Lifecycle:**  
   In *Why I Tore Down the AI Meta-Skill I Spent Months Building*, Wang identifies a critical law of agentic systems: **The scaffolding that saves a weaker model can choke a stronger one.** As frontier models advance (e.g. GPT-5 to GPT-6 / Claude 3.5 to Claude 4/Mythos), rigid multi-step micro-prompts, defensive checklist skills, and procedural micro-management become deadweight that impairs reasoning. Systems must implement an explicit **rules deprecation lifecycle**—pruning procedural scaffolding while retaining strict **external outcome verification**.
3. **The Builder-Reviewer Triad (Adversarial Multi-Agent Audit):**  
   In *Claude Code Is Grinding Away — Why Bring In Codex to Tear It Down?*, Wang establishes the foundational rule: **Never let the AI agent that writes the code/content review its own work.** Self-review suffers from confirmation bias and blind spots (e.g., whitespace bypasses, unhandled formatting anomalies). True reliability requires a three-piece triad: (1) an executor agent, (2) an isolated, adversarial reviewer agent from an entirely different model family, and (3) a human-on-the-loop making the final call.
4. **Human-on-the-Loop & The Verifier vs Delegator Contract:**  
   Across *Human on the Loop* and *If AI Did What You Couldn’t Do Yourself*, Wang dissects the illusion of full autonomy. Humans cannot manually replicate million-token processing, so they must transition from **in-the-loop bottlenecks** to **on-the-loop supervisors** who enforce invariants at structural boundaries. If an operator cannot independently verify the output at key gates, they are not delegating—they are gambling.

---

## 2. In-Depth Analysis by Thematic Clusters

### Cluster A: The LLM Wiki in Practice & Knowledge Architecture

#### A1. Real-World Evaluation of Karpathy’s Pattern (*Should You Actually Try Karpathy’s LLM Wiki?*)
Wang evaluates Karpathy’s `llm-wiki.md` pattern running on top of Hermes' `llm-wiki` CLI workflow:
- **The Three-Layer Invariant:** Practical confirmation of the three-tier boundary: `raw/` (immutable capture) + compiled wiki layer (`entities/`, `concepts/`, `comparisons/`) + `SCHEMA.md` (normative rules).
- **The Obsidian / Markdown / Git Asset Rule:** Wang strongly reinforces *The Omniscient Trash Heap*’s plain-text axiom (`CANON-002`, `CANON-003`). Closed, proprietary PKM startups (Roam, Notion, Tana) impose protocol drift, export degradation, and bankruptcy risk. Plain Markdown files in a Git repository are the only durable multi-decade knowledge asset.
- **RAG as Optimizer, Not Starting Point:** Refuting the reflex to deploy vector databases immediately: *“A vector database is an optimizer, not a starting point... My 84-page wiki doesn’t use a single vector database. Navigating via a one-line summary in index.md is already enough.”*

#### A2. The "Not Your Voice" Ingestion Trap
Wang highlights a subtle failure mode when users treat `raw/` as an indiscriminate web dump:
- If an agent compiles a wiki purely from external clippings, paper abstracts, and downloaded articles, the resulting synthesis is coherent but lacks the operator's subjective perspective, hypotheses, and critical discernment.
- **Trash Heap Alignment:** Directly informs our epistemic ontology (`EPISTEMOLOGY.md`). The system must enforce distinction between external `evidence` (citations, source records) and internal `author` notes, preserving human synthesis via the byte-preserved `## Notes` section (`OWN-002`, `BODY-003`).

#### A3. Automatic Zettelkasten & The Timeliness Problem (*How Can AI Help You Automatically Build a Zettelkasten?*)
- Wang explores automated card extraction from linear publications using OpenClaw + Codex.
- The critical problem raised by students: **Timeliness & Obsolescence**. Ingesting historical materials generates rich link graphs, but risks promoting superseded tools, expired APIs, and discredited claims as active knowledge.
- **Trash Heap Alignment:** Validates our temporal and governance invariants: `VAL-001` (chronological validity), `W006` (deprecated dependencies), `W007` (archived dependencies), and `SUPERSEDES` relation semantics (`REL-003`).

---

### Cluster B: Scaffolding Decay & Harness Evolution

#### B1. The Scaffolding Paradox (*Why I Tore Down the AI Meta-Skill...*)
Wang spent months building a complex "meta-skill" (Gangrou) designed to enforce procedural thoroughness on weaker models (preventing skipped steps, forcing directory checks, enforcing 15 stages and 24 contracts).
- When upgrading to GPT-6 Astra, this elaborate scaffolding actively harmed performance. The new model followed instructions so literally that the rigid constraints locked it into bureaucratic loops and prevented intelligent holistic execution.
- **The Solution:** Tear down the procedural meta-scaffolding; allow the model freedom in intermediate reasoning, but enforce strict **external verification at the boundary**.

#### B2. The Packaging Leak Incident
During the teardown, independent verification audited the packaging script:
- The legacy script claimed to package deliverables based on a manifest. In reality, it recursively bundled the entire working directory. A simulated private test document placed in the directory was inadvertently packaged into the export archive.
- **Trash Heap Alignment:** Exactly the vulnerability addressed by our `BUNDLE-007` (Cross-Scope Security Defense) and `test_k3_promotion_path_traversal_rejection` / `export.py` manifest checks. Loose directory walking is a catastrophic security anti-pattern; exports must be strictly filtered against explicit whitelist manifests.

---

### Cluster C: Multi-Agent Adversarial Audits & Quality Control

#### C1. The Builder-Reviewer Triad (*Claude Code vs. Codex*)
Wang documents his dual-agent pipeline:
- Claude Code acts as the primary builder/coder.
- Codex (OpenAI) acts as an isolated, adversarial reviewer instructed to find flaws and bypasses.
- **Four Critical Bypasses Uncovered:**
  1. *Stray Format Bypass:* Non-standard checklist items bypassed inspections entirely.
  2. *Whitespace Trapping:* Missing `.strip()` on status fields allowed `" adopted "` to fail or pass inappropriately.
  3. *Scope Creep:* Undocumented assumptions about file existence.
  4. *Implicit Fallbacks:* Silent defaults masking failures.
- **The Core Axiom:** *“Never let the AI Agent that writes the thing review its own work.”*

```text
┌──────────────────────────────────────────────────────────────┐
│                  THE BUILDER-REVIEWER TRIAD                  │
│                                                              │
│  ┌───────────────────────┐        ┌───────────────────────┐  │
│  │   Builder Agent       │        │   Reviewer Agent      │  │
│  │   (e.g. Claude Code)  │        │   (e.g. OpenAI Codex) │  │
│  │   Constructs solution │        │   Adversarial audit   │  │
│  └──────────┬────────────┘        └───────────┬───────────┘  │
│             │                                 │              │
│             ▼                                 ▼              │
│      Proposed Changes                 Identified Flaws       │
│             │                                 │              │
│             └────────────────┬────────────────┘              │
│                              ▼                               │
│                   ┌───────────────────────┐                  │
│                   │ Human on the Loop     │                  │
│                   │ Signs off / adjudicates│                 │
│                   └───────────────────────┘                  │
└──────────────────────────────────────────────────────────────┘
```

- **Trash Heap Alignment:** Validates the two-stage Promotion State Machine in `REVIEW-PROMOTION.md` (`PROMO-001..010`) and justifies our decoupled review architecture where promotion proposals require explicit review records before compilation into canonical storage.

---

### Cluster D: Human-on-the-Loop & Epistemic Governance

#### D1. Verifier vs. Delegator (*If AI Did What You Couldn’t Do Yourself...*)
- **The Trap:** When AI produces code or analyses beyond the user’s personal domain competence, users succumb to "blind delegation."
- **The Architectural Remedy:** Verification must be structural, not exhaustive manual re-execution:
  1. Are raw data sources authenticated and immutable? (`CSCC`, SHA-256 hashes)
  2. What are the core epistemic assumptions and bounds? (`threshold_policy.yaml`)
  3. Do uncheatable mechanical gates pass? (Syntax checks, acyclicity tests, AST linter)
  4. Can the human operator defend the output under adversarial cross-examination?

#### D2. Cognitive Erosion (*What Can We Do When AI Runs So Smoothly...*)
- In educational and analytical settings, zero-friction AI causes cognitive atrophy. When answers appear effortlessly, critical reasoning degrades.
- **The Architectural Remedy:** **Productive Friction**. Systems must require explicit user sign-offs on high-impact state transitions (such as promotion to canonical knowledge, schema changes, and conflict overwrites under `BODY-004`).

---

### Cluster E: Literature Monitoring & Tool Orchestration

#### E1. Automated Research Radar (*How to Build a Research Radar...*)
- Wang builds an autonomous pipeline monitoring scholarly literature daily via OpenAlex API without manual coding.
- **Key Pain Point:** Open metadata quality. In OpenAlex records, author affiliations frequently corrupt or tag multiple universities erroneously (e.g. tagging all co-authors with a single company affiliation).
- **Trash Heap Alignment:** Confirms why `actor_registry.yaml` and `source_registry.yaml` must maintain decoupled entity namespaces (`ACTOR-001..006`) and enforce strict provenance validation (`PROV-001`, `PROV-007`).

#### E2. Legacy Tool Orchestration (*NetLogo by Talking to It*)
- Interfacing LLMs with specialized simulation tools (NetLogo) via headless CLI execution, socket communication, and headless batch sweeps.
- Confirms the necessity of our external tool adapter architecture in `specs/INGEST-ADAPTERS.md`.

---

## 3. Concrete Architectural Recommendations for *The Omniscient Trash Heap*

| Finding from Wang Corpus | Architectural Implication | Proposed Specification / Implementation Action |
|---|---|---|
| **Adversarial Multi-Agent Audit** (*Claude Code vs Codex*) | Single-model self-evaluation misses structural blind spots and input sanitization bugs. | Formalize dual-agent review recommendation in `specs/REVIEW-PROMOTION.md` §4 (proposer model $\ne$ reviewer model). |
| **Scaffolding Decay** (*Tearing Down Meta-Skills*) | Over-scaffolding in `AGENTS.md` and skills impairs advanced frontier models. | Establish a regular prompt/rule pruning protocol in `specs/AGENT-SKILLS.md` §8; favor mechanical test gates over verbose prompting. |
| **"Not Your Voice" Ingestion Trap** | Unchecked web capture drowns human synthesis in external summaries. | Reaffirm `OWN-002` (byte-preserved `## Notes`) and enforce source attribution tags in `specs/EPISTEMOLOGY.md`. |
| **Timeliness & Obsolescence** | Ingested legacy knowledge creates active graph pollution. | Ensure periodic `trashheap lint` flags `W002` (review overdue) and `W006`/`W007` (deprecated/archived dependencies) proactively. |
| **Packaging Directory Traversal Bug** | Recursive directory copy leaks sensitive unmanifested files. | Enforce strict manifest-only bundling in `trashheap/bundle/export.py` (`BUNDLE-004`, `BUNDLE-007`). |

---

## 4. Provenance & Archival Record

All 20 full-text source articles have been retrieved via authenticated session fetching and preserved byte-verbatim with YAML metadata in:
- `research/raw/2026-01-09-introduction-to-claude-skills-how-ai-evolved-from-chatbot-to-collaborator.md`
- `research/raw/2026-02-02-in-the-span-of-a-single-week-an-open-source-project-went-through-three-name-chan.md`
- `research/raw/2026-02-03-i-didnt-write-a-single-config-file-yet-deployed-the-entire-openclaw-system.md`
- `research/raw/2026-03-13-is-rag-outdated.md`
- `research/raw/2026-04-16-should-you-actually-try-karpathys-llm-wiki.md`
- `research/raw/2026-04-19-hybrid-intelligence-what-youre-really-buying.md`
- `research/raw/2026-04-25-can-human-ai-collaboration-still-work-when-ai-knows-far-more-than-you-do.md`
- `research/raw/2026-05-07-what-can-we-do-when-ai-runs-so-smoothly-that-students-stop-thinking-for-themselv.md`
- `research/raw/2026-05-19-why-im-so-excited-about-codexs-new-cross-device-remote-control.md`
- `research/raw/2026-05-22-how-can-ai-help-you-automatically-build-a-zettelkasten.md`
- `research/raw/2026-05-27-if-ai-did-what-you-couldnt-do-yourself-would-you-dare-sign-your-name-to-it.md`
- `research/raw/2026-05-29-if-you-teach-one-ai-can-it-teach-the-others.md`
- `research/raw/2026-06-19-human-on-the-loop-the-researchers-new-role-in-the-age-of-agents.md`
- `research/raw/2026-06-22-turning-a-lecture-transcript-into-a-full-teaching-deck-how-do-you-build-and-poli.md`
- `research/raw/2026-06-27-claude-code-is-grinding-away-at-the-work-so-why-do-i-insist-on-bringing-in-codex.md`
- `research/raw/2026-06-30-reading-the-same-paper-where-does-an-ai-agent-beat-the-chat-box.md`
- `research/raw/2026-08-30-can-you-get-ai-to-run-netlogo-just-by-talking-to-it.md`
- `research/raw/2026-09-01-how-to-build-a-research-radar-that-watches-the-literature-for-you-every-day-with.md`
- `research/raw/2026-09-01-how-to-turn-the-files-you-already-have-into-an-interactive-ai-qa-site-with-workb.md`
- `research/raw/2026-09-08-why-i-tore-down-the-ai-meta-skill-i-spent-months-building.md`
