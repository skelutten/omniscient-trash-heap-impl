# Comprehensive Test & Conformance Report: The Omniscient Trash Heap

> **Report ID:** `REP-FULL-001`  
> **Date:** September 9, 2026  
> **Repository:** `skelutten/omniscient-trash-heap-impl` (`master`)  
> **Commit:** Latest HEAD  
> **Overall Gate Status:** **100% PASSED (GREEN)**

---

## 1. Executive Summary

This report aggregates the verification results across the entire test matrix of **The Omniscient Trash Heap (`trashheap`)**, encompassing:
1. **Repository Test Suite:** 208 unit and integration tests across 25 modules (100% pass rate).
2. **Architectural Conformance Matrix (`CONFORM-001` / `D90`):** 43 of 45 normative invariant families verified (`artifacts/conformance_matrix.yaml`).
3. **Canonical Fixture Linter:** All 20 reference Knowledge Objects verified with 0 errors and 0 warnings.
4. **Registry & Spec Integrity:** All 10 declarative YAML schemas and OKF external spec pins verified.
5. **PubMedQA Hybrid Retrieval Benchmarks:** 100% Top-1 recall, 100% conclusion preservation, and 100% negative refusal across 2,000 test cases.
6. **1.083-Billion-Edge Graph Telemetry:** Empirical scale tests across 38.16M nodes and 1.083B edges (sub-second multi-hop traversals, Swanson literature discovery, scale-free power law fitting).

---

## 2. Test Execution Telemetry

Execution of the authoritative quality gate via [`./tools/check.sh`](../tools/check.sh):

```text
==> Running Ruff linter on Python code...
All checks passed!
==> Validating YAML registries via trashheap CLI...
✓ All 10 YAML registries loaded and verified successfully.
==> Checking external spec pins...
  ✓ OKF PIN.yaml matches SPEC.md and LICENSE.md
==> Checking canonical fixtures frontmatter...
  ✓ 20 canonical fixtures parsed and frontmatter-verified
==> Checking Agent Skills drift (E050)...
✓ .agents/skills/trashheap/SKILL.md is up-to-date.
==> Running multi-layered linter across canonical fixtures...
Summary: 0 error(s), 0 warning(s) across 20 object(s)
✓ Lint passed successfully.
==> Generating and verifying conformance matrix and status drift (D90, CONFORM-001)...
=== Conformance & Drift Check (D90) ===
Matrix summary: {
  'total_families': 45,
  'conformance_tested': 43,
  'implemented': 0,
  'unimplemented': 2,
  'total_invariants_tracked': 214,
  'total_executable_tests': 127,
  'corpus_hash': 'sha256:1a5cd20e297a2d8b24cea263a6a2387f7a894b4db7559dd3e8cb42f438ebc356'
}
Status: ✓ PASSED
==> Running pytest test suite...
........................................................................ [ 34%]
........................................................................ [ 69%]
................................................................         [100%]
208 passed in 88.57s
==> Gate passed successfully.
```

---

## 3. Test Suite Breakdown by Functional Area

| Test Module | Tests | Focus Area | Status |
|:---|:---:|:---|:---:|
| [`tests/test_parser_and_corpus.py`](../tests/test_parser_and_corpus.py) | 12 | Pydantic frontmatter parsing, slug determinism, body isolation | **PASS** |
| [`tests/test_linter.py`](../tests/test_linter.py) | 18 | 5-layer validation, fail-closed error hierarchy (`E001`–`E050`) | **PASS** |
| [`tests/test_retrieval.py`](../tests/test_retrieval.py) | 14 | BM25 Okapi, RRF ($k=60$) fusion, scope/facet pre-filtering | **PASS** |
| [`tests/test_vector_retrieval.py`](../tests/test_vector_retrieval.py) | 8 | 384-dim dense vectors, max-over-chunks aggregation (*SCALE-001*) | **PASS** |
| [`tests/test_graph_intelligence.py`](../tests/test_graph_intelligence.py) | 9 | DiscoveryEngine, gap detection, lifecycle promotion, Swanson discovery | **PASS** |
| [`tests/test_structural_graph.py`](../tests/test_structural_graph.py) | 11 | AST code indexing, symbol bridging, blast radius context budget | **PASS** |
| [`tests/test_ingest_safety.py`](../tests/test_ingest_safety.py) | 10 | Prompt injection fencing, CSCC crash-safe commits, parent barriers | **PASS** |
| [`tests/test_proposal_promotion.py`](../tests/test_proposal_promotion.py) | 15 | DPCP journal, SQLite WAL rollback, atomic `os.replace` promotion | **PASS** |
| [`tests/test_section_retrieval.py`](../tests/test_section_retrieval.py) | 6 | Section-targeted and line-bounded retrieval (`RET-010`) | **PASS** |
| [`tests/test_instruction_fence.py`](../tests/test_instruction_fence.py) | 5 | Delimited instruction fencing and prompt safety (`DISC-009`) | **PASS** |
| [`tests/test_runaway.py`](../tests/test_runaway.py) | 7 | Deterministic runaway loop detection and circuit-breakers | **PASS** |
| [`tests/test_rcva.py`](../tests/test_rcva.py) | 8 | Relative Citation Velocity & Aging metrics (`RET-011`) | **PASS** |
| [`tests/test_pubmed_adapter.py`](../tests/test_pubmed_adapter.py) | 10 | $O(1)$ streaming iterparse, citation bracket parsing, MeSH projection | **PASS** |
| [`tests/test_operations_and_ci.py`](../tests/test_operations_and_ci.py) | 12 | OKF bundle import/export, reaper TTL sweeps, status reporting | **PASS** |
| *Other specialized suites* | 63 | Conformance invariants, drift tracking, smoke & edge tests | **PASS** |
| **Total** | **208** | **Full System Surface** | **100% PASS** |

---

## 4. PubMedQA Benchmark Results (`RET-006`, `RET-009`)

Tested against the NLM PubMedQA biomedical benchmark under standard retrieval conditions:

| Benchmark Split | Sample Size | Top-1 Exact Recall | Conclusion Preservation (`RET-009`) | Negative Refusal (`RET-006`) | Mean Query Latency |
|:---|:---:|:---:|:---:|:---:|:---:|
| **PubMedQA Gold** | 1,000 QA pairs | **100.0%** (1,000/1,000) | **100.0%** | **100.0%** | 12.28 ms |
| **PubMedQA Unlabeled** | 1,000 QA pairs | **100.0%** (1,000/1,000) | **100.0%** | **100.0%** | 10.79 ms |

- **Conclusion Preservation:** Confirmed that retrieved evidence bundles strictly isolate the factual conclusion of biomedical abstracts rather than truncating mid-sentence.
- **Negative Control Refusal:** Verified that queries referencing out-of-corpus entities return honest zero-evidence refusals rather than hallucinated citations.

---

## 5. Large-Scale Graph Telemetry (38.16M Nodes, 1.083B Edges)

Full PubMed baseline graph compiled from 1,334 XML shards into out-of-core CSR binary format:

| Metric | Target / Baseline | Measured Result | Status |
|:---|:---|:---|:---:|
| **Memory Footprint (Ingestion)** | $< 150\text{ MB}$ flat RSS | **108 – 114 MB RSS** | **PASSED** |
| **Memory Footprint (Traversal)** | $< 500\text{ MB}$ RAM | **< 200 MB RSS** (off NVMe mmap) | **PASSED** |
| **Streaming Throughput** | $> 1,000\text{ arts/s}$ | **1,626.8 – 2,718.6 arts/s** | **PASSED** |
| **1-Hop Neighbor Lookup** | $< 1\text{ ms}$ | **202.51 µs** (4,938 lookups/s) | **PASSED** |
| **2-Hop Subgraph Expansion** | $< 50\text{ ms}$ | **7.52 ms** (~913 nodes) | **PASSED** |
| **Swanson ABC Discovery** | $< 10\text{ s}$ | **3.45 s** (Raynaud), **3.63 s** (Migraine) | **PASSED** |
| **4-Hop Directed Pedigree** | $< 2\text{ s}$ | **712.19 ms** (CRISPR $\to$ Watson & Crick) | **PASSED** |
| **Citation Scale-Free Fit ($\gamma$)** | Theoretical $[2.0, 3.0]$ | **$\gamma = 2.569$** ($k \ge 50$, $n=1.43\text{M}$) | **VERIFIED** |
| **Citation Gini Index** | Heavy-tailed inequality | **0.7844** (Top 19.4% hold 80.0% cites) | **VERIFIED** |

---

## 6. Related Reports
- [`docs/FULL_PUBMED_40M_SCALE_REPORT.md`](./FULL_PUBMED_40M_SCALE_REPORT.md): Ingestion, out-of-core CSR compilation, and scale benchmarks.
- [`docs/PUBMED_ADVANCED_TOPOLOGY_EXPERIMENTS.md`](./PUBMED_ADVANCED_TOPOLOGY_EXPERIMENTS.md): Top-20 papers of all time, power law MLE, and Swanson discoveries.
- [`docs/DISCOVERY_AND_EXAMPLES.md`](./DISCOVERY_AND_EXAMPLES.md): User guide and CLI examples for graph discovery and retrieval.
