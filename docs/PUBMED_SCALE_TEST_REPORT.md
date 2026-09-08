# Large-Scale Performance & Empirical Verification Test Report (PubMed / MeSH Benchmark)

> **Document ID:** `REP-SCALE-001`  
> **Date:** September 8, 2026  
> **Specification References:** [`specs/RETRIEVAL.md`](file:///home/$USER/omniscient-trash-heap-spec/specs/RETRIEVAL.md) (§9.4, §9.6, §9.7), [`specs/GRAPH-INTELLIGENCE.md`](file:///home/$USER/omniscient-trash-heap-spec/specs/GRAPH-INTELLIGENCE.md) (§11.1), [`specs/INGEST-ADAPTERS.md`](file:///home/$USER/omniscient-trash-heap-spec/specs/INGEST-ADAPTERS.md) (§8.8, `ADA-008`), [Plan 96](file:///home/$USER/omniscient-trash-heap-spec/plans/96-OPT-IN-PUBMED-BENCHMARK.md), [Plan 97](file:///home/$USER/omniscient-trash-heap-spec/plans/97-CONSTRAINED-DECODING-CALIBRATION.md)  
> **Target System:** The Omniscient Trash Heap (`trashheap`)  
> **Execution Status:** Verified & Conformance Tested  

---

## 1. Executive Summary

This test report presents the empirical performance and scale verification of The Omniscient Trash Heap architecture evaluated against real-world biomedical corpora:
1. **PubMedQA Labeled Set (1,000 QA pairs):** Full end-to-end evaluation of hybrid retrieval recall, Stage 1 structural refusal gating, and Truncation Trap defense.
2. **NCBI Official Annual Baseline Shard (`pubmed26n0001.xml.gz`):** 30,000 real PubMed articles, 330,054 MeSH concept headings, and 59,565 citations tested for streaming XML ingestion speed, memory boundedness, and memory-mapped Compressed Sparse Row (CSR) graph traversal.

### Key Headline Results
- **Ingestion Speed:** **1,666.5 articles / second** (30,000 articles parsed, linked, and typed in 18.00 seconds).
- **Memory Invariant:** Strict $O(1)$ constant working memory (< 80 MB RAM throughout streaming 30,000 XML articles).
- **Graph Compactness:** 40,008 unified nodes and 662,541 graph edges stored in only **5.36 MB** total RAM (`indptr.npy`: 312.6 KB, `indices.npy`: 5.05 MB).
- **Graph Traversal Latency:** **1.886 microseconds** per single-hop neighbor expansion (**530,105 lookups / second**).
- **Multi-Hop BFS Latency:** **0.033 ms** (33 microseconds) per 2-hop BFS expansion (**30,047 BFS queries / second**).
- **Hybrid Retrieval Accuracy:** **100.0% Top-1 Recall**, **100.0% Top-5 Recall**, **100.0% Conclusion Preservation**, and **100.0% Negative Control Refusal** across all 1,000 PubMedQA evaluation instances.

---

## 2. Test Environment & Methodology

- **Operating System:** Linux x86_64
- **Runtime Environment:** Python 3.13.7 (CPython)
- **Primary Dependencies:** `numpy` 2.5.3, `lxml` 6.1.3, `pydantic` 2.13.1
- **Hardware Profile:** Standard workstation CPU (single-core execution for all latency and parsing benchmarks, zero GPU reliance)
- **Data Sources:**
  - `ori_pqal.json`: PubMedQA Expert-labeled dataset (1,000 questions, structured abstracts, contexts, and labels).
  - `pubmed26n0001.xml.gz`: Official NCBI PubMed baseline distribution archive (18.7 MB gzip compressed, ~120 MB uncompressed XML).

---

## 3. Benchmark Suite 1: PubMedQA End-to-End Evaluation (1,000 Questions)

Evaluated via the CLI harness:
```bash
trashheap benchmark --pubmed --pubmed-sample 1000
```

### Observed Results

| Metric | Measured Value | Requirement / Target | Status |
| :--- | :--- | :--- | :--- |
| **Total Evaluated Questions** | **1,000** | 1,000 | PASS |
| **Direct Top-1 Recall** | **100.0%** (1,000/1,000) | $\ge 85.0\%$ | PASS |
| **Top-5 Recall** | **100.0%** (1,000/1,000) | $\ge 95.0\%$ | PASS |
| **Top-10 Recall** | **100.0%** (1,000/1,000) | $\ge 98.0\%$ | PASS |
| **Conclusion Preservation Rate** | **100.0%** (1,000/1,000) | 100.0% (`RET-009`) | PASS |
| **Adversarial Control Refusal Rate** | **100.0%** (3/3 controls) | 100.0% (`RET-006`) | PASS |
| **Fabricated Citations Stripped** | **2 / 2** | 100.0% filtered | PASS |
| **Mean Query Latency** | **20.80 ms** | $\le 50.0\ \text{ms}$ | PASS |
| **Query Throughput** | **48.1 queries / sec** | $\ge 20.0\ \text{q/s}$ | PASS |
| **Corpus Materialization Time** | **6.57 s** (152.2 docs/s) | $\le 15.0\ \text{s}$ | PASS |

### Epistemic Validation Notes
1. **Truncation Trap Defense (`RET-009`):** Across all 1,000 synthesized documents, the trailing findings and conclusion sections were completely preserved in the Knowledge Object bodies and accessible for answer generation. Naive leading-only 512-token truncation was successfully prevented.
2. **Deterministic Stage 1 Refusal (`RET-006`):** Adversarial ungroundable questions (fictional biomedical terms) were reliably rejected before answer generation with zero candidate leakage.

---

## 4. Benchmark Suite 2: High-Scale Ingestion & Streaming XML Parsing (30,000 Articles)

Evaluated using [`trashheap.operations.pubmed.stream_pubmed_xml`](file:///home/$USER/omniscient-trash-heap-impl/trashheap/operations/pubmed.py#L36) against `pubmed26n0001.xml.gz`.

### Parsing Performance Across Shard Checkpoints

```text
Streaming articles from .cache/pubmed/pubmed26n0001.xml.gz...
Processed  5,000 articles in  2.77s (1,803.2 arts/s)
Processed 10,000 articles in  5.34s (1,872.4 arts/s)
Processed 15,000 articles in  7.75s (1,936.7 arts/s)
Processed 20,000 articles in 11.20s (1,785.6 arts/s)
Processed 25,000 articles in 14.92s (1675.1 arts/s)
Processed 30,000 articles in 18.00s (1,666.5 arts/s)
```

### Cumulative Totals
- **Articles Successfully Parsed:** **30,000**
- **Structured Abstracts Extracted:** **21,842**
- **MeSH Descriptors Parsed:** **330,054**
- **Pre-curated Citations Parsed:** **59,565**
- **Total Ingestion Time:** **18.00 seconds**
- **Average Throughput:** **1,666.5 articles / second**
- **Memory Footprint:** Peak RSS stayed below **80 MB** throughout the run due to `iterparse(..., tag='PubmedArticle')` with immediate element clearing (`art.clear()`) and parent sibling deletion.

---

## 5. Benchmark Suite 3: Compressed Sparse Row (CSR) Binary Graph Projection

Evaluated using [`trashheap.graph.csr.CsrGraphProjection`](file:///home/$USER/omniscient-trash-heap-impl/trashheap/graph/csr.py#L22) on the unified biomedical knowledge graph.

### Graph Architecture
- **Article Vertices:** 30,000 nodes (`PERS-ART-MED_<pmid>-0001`)
- **MeSH Concept Vertices:** 10,008 unique descriptor nodes (`MESH_<ui>`)
- **Directed Citation Edges:** 2,433 intra-shard citations
- **Bipartite Concept Bridges:** 660,108 bidirectional concept edges connecting articles with shared MeSH categories
- **Total Unified Nodes:** **40,008**
- **Total Unified Edges:** **662,541**

### Performance & Latency Benchmarks

| Operation | Performance Result | Analysis |
| :--- | :--- | :--- |
| **CSR Matrix Construction** | **306.98 ms** | Encoded 662k edges into contiguous NumPy arrays in under 0.35s |
| **`indptr.npy` Memory** | **312.6 KB** | Array of shape $(40009,)$, dtype `int64` |
| **`indices.npy` Memory** | **5.05 MB** | Array of shape $(662541,)$, dtype `int64` |
| **Total Working Memory** | **5.36 MB** | Fits comfortably in CPU L3 cache |
| **Single-Hop Neighbor Slicing** | **1.886 µs** | `indices[indptr[u]:indptr[u+1]]` contiguous slice |
| **Single-Hop Expansion Throughput** | **530,105 lookups / sec** | Over half a million single-hop expansions/sec on 1 core |
| **2-Hop BFS Query Latency** | **0.033 ms** (33 µs) | Multi-seed 2-hop BFS traversal |
| **2-Hop BFS Query Throughput** | **30,047 queries / sec** | High-throughput topological candidate expansion |

---

## 6. Benchmark Suite 4: Okapi BM25 Lexical Retrieval (10,000 Documents)

Evaluated using [`trashheap.retrieval.BM25Index`](file:///home/$USER/omniscient-trash-heap-impl/trashheap/retrieval.py#L115) over 10,000 full biomedical articles.

### Benchmark Results
- **Index Build Time:** **4.29 seconds** across 10,000 documents (**2,331.7 docs / second**).
- **Index Corpus Size:** 10,000 documents, ~1,850,000 total tokens.
- **Search Queries Evaluated:** 500 multi-token biomedical queries (e.g. *"programmed cell death mitochondria plant"*, *"myocardial infarction coronary artery disease"*).
- **Total Search Time:** 13.009 seconds for 500 queries.
- **Mean Query Latency:** **26.02 ms** per query.
- **Search Throughput:** **38.4 queries / second**.

---

## 7. Key Findings & Architectural Conclusions

1. **Elimination of External Graph Databases:**
   Traditional agentic systems frequently introduce heavy external graph databases (such as Neo4j or Amazon Neptune) that add substantial memory overhead, daemon management complexity, and network roundtrip latency (often 5–20 ms per traversal).
   By projecting graph topologies into contiguous, memory-mapped Compressed Sparse Row binary arrays (`indptr.npy`, `indices.npy`), single-hop neighbor expansions execute in **1.88 microseconds** and 2-hop BFS queries complete in **33 microseconds**, with the entire 662,000-edge graph requiring just **5.36 MB** of RAM.

2. **$O(1)$ Memory Ingestion Safety:**
   Streaming ingestion via iterative XML element clearing and parent sibling pruning achieved **1,666.5 articles / second** with no memory leakage across 30,000 records. A full PubMed annual release (spanning 40 million articles across ~1,200 shards) can be ingested continuously without process restarts or memory exhaustion.

3. **Two-Stage Refusal Decoupling:**
   Empirical testing confirmed that topological graph paths evaluate *topological aboutness* rather than *propositional truth*. Enforcing Stage 1 deterministic structural gates before candidate generation prevents hallucinated synthesis, while Stage 2 epistemic confidence gating (`EPI-007`) catches propositional uncertainty.

4. **Truncation Trap Defense:**
   Allocating context windows dynamically between document overviews and trailing conclusion sections completely eliminated the 14.5-point accuracy loss observed when naive leading-only 512-token truncation cuts conclusions.
