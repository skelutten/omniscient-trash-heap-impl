# Research Note P17: Fareed Khan on 10M-Document RAG & Disk-Streaming Architectures

> **Type**: Non-normative prior-art provenance & architectural analysis
> **Sources**:
>   1. Fareed Khan, *Building a RAG Pipeline for 10M+ Documents With Near-Zero Hallucination* (Level Up Coding / Medium, June 15, 2026)
>   2. Fareed Khan, *Building Kimi K3 2.8T Model in C to Run on 8GB RAM* (Level Up Coding / Medium, August 3, 2026)
> **Retrieved**: 2026-09-08
> **URLs**:
>   - `https://levelup.gitconnected.com/building-a-rag-pipeline-for-10m-documents-with-near-zero-hallucination-788e4b5b7f25`
>   - `https://levelup.gitconnected.com/building-kimi-k3-2-8t-model-in-c-to-run-on-8gb-ram-a5792cbf3b59`
> **Canonical Source Raws**:
>   - `research/raw/2026-06-15-building-a-rag-pipeline-for-10m-documents-with-near-zero-hallucination.md`
>   - `research/raw/2026-08-03-building-kimi-k3-28t-model-in-c-to-run-on-8gb-ram.md`
> **Informs**: `specs/RETRIEVAL.md` (§9.6, §9.7 two-stage refusal & abstention gates), `specs/INGEST-ADAPTERS.md` (`ADA-008` streaming XML & $O(1)$ memory invariance), `specs/GRAPH-INTELLIGENCE.md` (§11.1 CSR projections), `plans/96-OPT-IN-PUBMED-BENCHMARK.md`, `plans/97-CONSTRAINED-DECODING-CALIBRATION.md`

---

## 1. Executive Summary

Across two extraordinarily detailed, production-grade technical articles (totaling over 34,000 words of implementation code and empirical benchmarks), Fareed Khan tackles two of the most critical bottlenecks in modern AI engineering:
1. **Near-Zero Hallucination at 10M-Document Scale:** Designing a four-stage defense pipeline ("Retrieve, Constrain, Verify, Abstain" / RCVA) that combines hybrid dense/BM25 retrieval, query decomposition, cited generation, a deterministic verification gate, and a calibrated epistemic abstention gate.
2. **Disk-Streaming MoE Inference in Pure C ($O(1)$ RAM Invariant):** Implementing an inference runtime in raw C (without BLAS, PyTorch, or GPU dependencies) that executes a **1.56 TB checkpoint of a 2.8-trillion parameter Mixture-of-Experts (MoE) model on a standard consumer machine with only 8 GB of RAM**. By treating high-speed NVMe storage as the primary compute substrate via memory-mapped I/O (`mmap`), streaming expert weights on-demand, and enforcing constant KV-cache memory, Khan proves that **storage throughput beats RAM capacity**.

These two works provide direct empirical and algorithmic validation for *The Omniscient Trash Heap*'s foundational performance invariants: the Two-Stage Refusal Architecture (`EPI-006`, `EPI-007`, `RET-006`, `RET-007`), Constrained Logit Decoding (`RET-008`), $O(1)$ RSS Streaming Ingestion (`ADA-008`), and In-Memory Compressed Sparse Row (CSR) graph projections.

---

## 2. The 10M-Document RAG Architecture: "Retrieve, Constrain, Verify, Abstain"

Khan demonstrates that naive RAG fails catastrophically at multi-million document scale due to context contamination, retrieval ambiguity, and unchecked model confabulation. His 10M-document system enforces four strict pipeline stages:

```text
User Query
    │
    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Hybrid Retrieval & Decomposition                                    │
│    • Query routing & sub-query decomposition                           │
│    • BM25 lexical search + Dense vector embeddings                     │
│    • Reciprocal Rank Fusion (RRF) + Cross-encoder reranking            │
└────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. Constrained Context Assembly                                        │
│    • Contextual chunking (prepended document-level metadata & summary) │
│    • Strict token budget allocation (pruning irrelevant passages)      │
└────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. Cited Generation (Propositional Anchoring)                          │
│    • Every generated assertion must carry explicit [doc_id:chunk_id]   │
│    • Prompt-level restriction forbidding unanchored assertions         │
└────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. Verification & Abstention Gate                                      │
│    • Non-Neural Claim Verifier (checking text entailment & citations)  │
│    • Epistemic Abstention Check: If confidence < tau, ABSTAIN          │
│    • Emits typed refusal rather than hallucinating                     │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 The Verification & Abstention Invariant
Khan identifies that **a model must be allowed and incentivized to say "I do not know"**:
- When retrieval evidence is conflicting, missing, or weakly ranked ($P(\text{support}) < \tau$), the system halts generation and returns a formal refusal.
- Hallucination rate drops from $> 22\%$ in baseline RAG to $< 0.4\%$ across 10,000 stress-test queries.

---

## 3. Streaming a 2.8-Trillion Parameter Model in C on 8 GB RAM

In *Building Kimi K3 2.8T Model in C to Run on 8GB RAM*, Khan proves that memory capacity need not constrain AI scale if the runtime adheres to a strict $O(1)$ memory invariant.

### 3.1 The Impossible Math
- Model checkpoint size: **1.56 TB** (2.8 trillion total parameters across 93 layers and 896 MoE experts).
- Target hardware: Standard x86_64 machine with **8 GB RAM** and a standard NVMe SSD (read speed $\sim 3.5$–$7.0$ GB/s).
- Fitting 1.56 TB into 8 GB RAM represents a **195-to-1 deficit**.

### 3.2 The Four Reductions: How Khan Solved It in Pure C
1. **Reduction One: 0.5-Byte Expert Quantization:**
   - MoE experts are stored at 4-bit (0.5 byte per parameter). Only active experts are read.
2. **Reduction Two: Bounded Attention Memory (KDA & MLA):**
   - Multi-Head Latent Attention (MLA) compresses the KV cache into a single low-dimensional latent vector per position, eliminating the quadratic KV memory explosion.
3. **Reduction Three: Sparse Expert Routing (16 of 896):**
   - For each token, the router activates only 16 out of 896 experts. The remaining 880 experts (98.2% of model parameters) are never read from disk for that token.
4. **Reduction Four: Sequential Trunk Streaming via `mmap`:**
   - The non-expert "trunk" weights (attention and router layers across 93 layers) are mapped using POSIX `mmap` with `madvise(..., MADV_SEQUENTIAL)`.
   - The engine reads weights sequentially layer-by-layer as the forward pass executes, dropping already-used pages with `MADV_DONTNEED`.

### 3.3 The Memory Footprint: Complete $O(1)$ RSS
```text
┌──────────────────────────────────────────────────────────┐
│ Operating System & Runtime Base:                ~1.2 GB  │
│ Active MLA KV-Cache & Activation Buffers:       ~2.4 GB  │
│ LRU Expert Weight Cache (in-flight experts):    ~3.2 GB  │
│ Streaming Trunk Read Window:                    ~0.8 GB  │
├──────────────────────────────────────────────────────────┤
│ Total Peak RSS:                                  7.6 GB  │
│ Checkpoint Size On Disk:                        1,560 GB │
└──────────────────────────────────────────────────────────┘
```

> *"Storage is the whole game. The memory ladder from 8 GB to 224 GB is not a difference in correctness; it is merely a dial on throughput."*

---

## 4. Synthesis & Direct Convergence with *The Omniscient Trash Heap*

| Khan's Principle | *The Omniscient Trash Heap* Architecture | Formal Specification / Invariant |
|---|---|---|
| **"Retrieve, Constrain, Verify, Abstain"** | Two-Stage Refusal Architecture & Calibrated Logit Abstention | `RET-006`, `RET-007`, `RET-008`, `EPI-006`, `EPI-007` |
| **Cited Generation** | Evidence Bundles with mandatory provenance excerpts and citation splitting | `RET-003`, `RET-009`, `PROV-007` |
| **Verification Gate** | Deterministic 5-Layer Linter & Non-Neural Verifier Mandate | `VALIDATION.md` Layers 1–5, `VAL-013` |
| **$O(1)$ RAM Invariance** | Incremental XML iterparse & streaming Source Ingestion | `ADA-008` in `INGEST-ADAPTERS.md` ($< 250$ MB RSS) |
| **Disk-Streaming & Memory Mapping** | Compressed Sparse Row (CSR) mmap graph projections | `specs/GRAPH-INTELLIGENCE.md` §11.1, Plan 96 |

---

## 5. Architectural Implications for Trash Heap

1. **Epistemic Abstention Gate Hardening (`EPI-007`):** Khan's empirical data confirms that abstaining on low confidence is the single most effective tool for driving hallucination rates below 1%. Our logit-normalized abstention gate (`plans/97-CONSTRAINED-DECODING-CALIBRATION.md`) must be enabled by default across all decision gates.
2. **Streaming Invariance Over In-Memory Loading (`CANON-006`, `ADA-008`):** Khan proves that multi-terabyte datasets and multi-trillion parameter graphs can be processed on small machines if streaming and `mmap` are strictly enforced. *The Omniscient Trash Heap* must continue to reject any requirement for multi-gigabyte RAM allocations or centralized database servers.
3. **Cited Sentence Verification:** In candidate generation and knowledge synthesis, every proposition must be explicitly tied to a `source_ref` and excerpt span, enabling fast deterministic validation before human review.
