# Research Note: OpenWiki, Grounded Claims & Local Serving Reliability

> **Type**: Prior-art analysis and empirical road test review — NON-NORMATIVE
> **Source Article**: *"OpenWiki Turns Your Codebase Into Self-Correcting Memory"* by David R Oliver (August 26, 2026)
> **Referenced Systems**: LangChain `openwiki` (`langchain-ai/openwiki`), Andrej Karpathy's LLM Wiki sketch (April 2026), Google Open Knowledge Format (OKF v0.2), Ollama serving stack.
> **Date**: 2026-09-08
> **Informs**: `specs/STRUCTURAL-GRAPH.md` (SG-001–SG-020), `specs/OKF-INTEROP.md` (OKF-001–OKF-010), `specs/RETRIEVAL.md` (RET-009 Truncation Defenses), `specs/INGEST-STAGING.md` (CSCC/DPCP durable checkpointing).

---

## 1. Executive Summary

David R Oliver's road test of LangChain's **OpenWiki** on a fully local open-weight model stack (Ollama + `gpt-oss:20b` / `qwen3.5 4B` on a 24GB Apple Silicon machine) documents the first comprehensive real-world evaluation of Karpathy's *LLM Wiki* pattern applied to codebase architecture documentation.

The article articulates the foundational axiom:
> *"Documentation fails because it is write-once. Memory works because it is overwrite-often. Most of what we call documentation is the first thing wearing the second thing's clothes, and that is why it rots."*

OpenWiki operationalizes this by introducing **Grounded Claims**: dual-persisted assertions where prose descriptions are cryptographically pinned to line intervals and content hashes of the source code.

Oliver's local road test revealed four systematic failure modes in local LLM serving pipelines, all of which were **configuration- and transport-shaped rather than capability-shaped**, and demonstrated how a durable checkpointing state machine rescued the run via a **"Ralph loop"** (monotonic retry harness).

---

## 2. Core Architectural Mechanisms of OpenWiki

### 2.1 The Grounded Claims Mechanism
Every factual assertion in the generated wiki is stored redundantly:
1. **Prose Representation:** Human- and agent-readable Markdown text on the wiki page.
2. **Structured Claim Sidecar:** A JSON record pinning the assertion to:
   - Specific source file path (`file_path`).
   - Line boundaries (`start_line`, `end_line`).
   - Cryptographic content hash of the source code lines at assertion time (`sha256(source[start:end])`).

```text
Source Code (repo.ts) ──[Lines 9-26]──► Content Hash (sha256:4a3b...)
       │                                         │
       ▼                                         ▼
Git Commit / Diff               Sidecar Claim (.claims.json)
       │                                         │
       └────► Modified Lines? ──► Hash Mismatch? ──► Claim Stale!
                                                          │
                                                          ▼
                                            Forces Page Regeneration
```

When a commit lands, OpenWiki evaluates diffs against pinned claim hashes. A hash mismatch marks the claim **stale**, forcing the enclosing wiki page into the regeneration queue even if the macro-level update planner did not flag the page as modified.

### 2.2 Agent Consumption & Context Reduction
OpenWiki writes pointer headers to convention files (`AGENTS.md` and `CLAUDE.md`). Incoming coding agents read the curated architectural map on boot, avoiding expensive repository rediscovery:
- Summary ingestion is $10\times$ to $100\times$ cheaper in latency and token expenditure than reading raw source trees.
- The compiled wiki acts as shared, durable external memory across ephemeral agent sessions.

### 2.3 Format Interoperability: Google OKF v0.2
The generated output packages knowledge according to Google's **Open Knowledge Format (OKF v0.2)**, verifying the convergence of plain Markdown and structured metadata sidecars as the industry standard for agentic knowledge exchange.

---

## 3. The Local Road Test: Four Failures and One Rescue

Oliver attempted to run OpenWiki end-to-end on a 58-file TypeScript repository ("Hangar") without a single byte leaving the host machine. The run encountered four distinct failures:

### Failure 1: The Silent 4,096-Token Truncation Trap
- **Symptom:** Worker exited immediately with `Repository planning worker exited without submit_plan`.
- **Root Cause:** Ollama defaulted context length to 4,096 tokens. The repository-scan prompt overflowed this limit. Rather than throwing an error, Ollama *silently truncated from the top of the prompt*, removing the system instructions that defined the `submit_plan` tool schema.
- **Remedy:** `OLLAMA_CONTEXT_LENGTH=32768 ollama serve`.

### Failure 2: Transport Layer Tool-Call Dropping
- **Symptom:** Identical error (`worker exited without submit_plan`), despite tool calling working in isolated curl tests.
- **Root Cause:** OpenWiki dispatched non-streaming HTTP requests by default. The transport layer between OpenWiki and Ollama dropped structured tool call frames under non-streaming responses.
- **Remedy:** Set `OPENWIKI_OPENAI_COMPATIBLE_STREAMING=true`.

### Failure 3: Long-Context Closing-the-Loop Discipline
- **Symptom:** The 20B model successfully wrote an accurate, detailed architecture page on the event bus directly to disk, but exited with `worker exited without submit_page`.
- **Root Cause:** Under long context, the model completed the generative writing task but skipped the final ceremonial tool call required to close the loop. The pipeline discarded the valid markdown file.

### Failure 4: Context Exhaustion / End-of-Window Evaporation
- **Symptom:** Swapping to `qwen3.5 4B` with a 65k token window completed page 1, but died on page 2 (`worker exited without submit_page`).
- **Root Cause:** Each worker accumulated context monotonically (page draft + retrieved evidence + tool execution history). The closing instructions fell off the trailing edge of the window.

### The Rescue: The "Ralph Loop"
OpenWiki persists generation progress in a durable checkpoint file (`openwiki/.run.json`). Because completed pages are banked atomically, failed iterations do not erase prior progress:
```bash
for i in 1 2 3 4 5 6 7 8; do
  if openwiki code --init --print; then
    echo "COMPLETE after $i iterations"; break
  fi
done
```
- Iterations 1 & 2 banked 4 pages each.
- Iterations 3, 4 & 5 stalled on a complex page.
- Iteration 6 broke through and completed the remaining 15 pages in one pass.
- **Final Result:** 23 pages, 18 grounded claims, exit code 0, 100% private.

---

## 4. Architectural Comparison: OpenWiki vs. The Omniscient Trash Heap

| Dimension | LangChain OpenWiki | The Omniscient Trash Heap |
| :--- | :--- | :--- |
| **Philosophical Basis** | *"Memory works because it is overwrite-often."* | *"A Compiler, Not An Agent"* & *"Determinism over Hallucination"*. |
| **Source Grounding** | Text line spans + line content hashes in sidecar JSON. | **Structural Knowledge Graph (SKG)** (`STRUCTURAL-GRAPH.md`): AST-level extraction (`SG-004`), AST node hashes (`SG-008`), git revision binding (`SG-007`), and deterministic `BridgeEngine` (`SG-013`). |
| **Epistemic Integrity** | Binary freshness: hash match (valid) vs mismatch (stale). | **4-Dimensional Epistemic Model** (`EPISTEMOLOGY.md`): `evidence`, `verification`, `authority`, `consensus` + formal conflict ranking $K(d)$ + Invalidation Cascades. |
| **Storage & Checkpointing** | Single `.run.json` state file. | **CSCC & DPCP Protocols** (`INGEST-STAGING.md`, `REVIEW-PROMOTION.md`): Crash-safe two-phase commit, SQLite WAL journal, and atomic `os.replace` promotion. |
| **Format Standards** | Google OKF v0.2 export. | **Native Knowledge Bundles & OKF Interop** (`OKF-INTEROP.md` / `trashheap/bundle/`): Full bi-directional export/import of Google OKF v0.2 bundles (`OKF-001`–`OKF-010`). |
| **Agent Interface** | Header blocks in `AGENTS.md` and `CLAUDE.md`. | **Certified Open Agent Skills** (`specs/AGENT-SKILLS.md`): Local and global `.agents/skills/trashheap/SKILL.md` exposing `/query`, `/show`, `/lint`, `/init`. |
| **Local Serving Defenses** | Relies on external retry loop (Ralph loop). | **Two-Stage Refusal Architecture** (`RET-006`..`007`), **Constrained Logit Decoding** (`RET-008`), and Section-Aware Preservation (`RET-009`). |

---

## 5. Key Lessons for The Omniscient Trash Heap

1. **Grounded Claims & AST Pointers (`SG-013`):**
   OpenWiki validates our decision in Plan 92 to link Knowledge Objects to code structure. Pinned content hashes over AST nodes guarantee that claims are objectively falsifiable against codebase reality.
2. **The Truncation Trap in Local Contexts:**
   Oliver's findings directly reinforce our `RET-009` invariant. Silent truncation from serving runtimes (Ollama cutting top-of-prompt, or chunkers cutting bottom conclusions) is the primary culprit in agent failures.
3. **Durable Checkpointing as the Ultimate Resilience:**
   The "Ralph loop" works solely because `.run.json` makes progress monotonic. In *The Omniscient Trash Heap*, our CSCC staging and DPCP promotion journals ensure that no aborted run or crash can corrupt existing canonical knowledge or discard completed discovery records.
