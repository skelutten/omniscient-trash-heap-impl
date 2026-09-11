# Comprehensive Test & Conformance Report: The Omniscient Trash Heap

> **Report ID:** `REP-FULL-002` (supersedes REP-FULL-001, which contained a fabricated per-module table — see §7 Erratum)
> **Date:** September 9, 2026
> **Repository:** `skelutten/omniscient-trash-heap-impl` (`master`)
> **Overall Gate Status:** **PASSED (GREEN)** — `tools/check.sh` including the ≥70% coverage gate

---

## 1. Executive Summary

This report aggregates the verification results across the entire test matrix of **The Omniscient Trash Heap (`trashheap`)**:

1. **Repository Test Suite:** 257 tests collected across 35 modules — 255 passed, 2 skipped by design (heavy 30k-article PubMed shard parses, gated behind `TRASHHEAP_RUN_HEAVY=1`; they skip honestly via `pytest.skip` when the local shard cache or the env flag is absent).
2. **Line Coverage:** **83.5%** of the `trashheap` package (gate: ≥ 70%, enforced in `tools/check.sh` via `pytest --cov`).
3. **Architectural Conformance Matrix (`CONFORM-001` / `D90`):** 43 of 45 normative invariant families verified; 215 invariants tracked; 165 executable tests in family-referenced files (`artifacts/conformance_matrix.yaml`).
4. **Canonical Fixture Linter:** All 20 reference Knowledge Objects verified with 0 errors and 0 warnings (including the new W016 link-mirroring and W017 Mermaid rules — fixtures carry mirrored relation links).
5. **Registry & Spec Integrity:** All 10 declarative YAML schemas (now `extra="forbid"` across trust-boundary models) and OKF external spec pins verified.
6. **PubMedQA Hybrid Retrieval Benchmarks:** as recorded in REP-SCALE-002 §4 (100% Top-1 recall over 2,000 pairs); not re-executed for this report.
7. **1.083-Billion-Edge Graph Telemetry:** see §5 — including a mandatory telemetry-integrity disclosure about resume-zeroed counters and wall-clock totals.

---

## 2. Test Execution Telemetry

Execution of the authoritative quality gate via [`./tools/check.sh`](../tools/check.sh) (ruff → registries → spec pins → fixtures → skills drift → lint → conformance drift → pytest with coverage gate):

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
  'total_invariants_tracked': 215,
  'total_executable_tests': 165,
  'corpus_hash': 'sha256:379653ffed98caf8ebab3c4226f0ed00162406bd62f160b4364d807bbe6811b5'
}
Status: ✓ PASSED
==> Running pytest test suite with coverage gate (>= 70%)...
255 passed, 2 skipped
TOTAL coverage: 83.5% (fail-under 70)
==> Gate passed successfully.
```

---

## 3. Test Suite Breakdown by Functional Area

Counts below are the **actual collected test functions per module** (`pytest --collect-only -q`), not estimates.

| Test Module | Tests | Focus Area |
|:---|:---:|:---|
| `tests/test_remediation_2026_09.py` | 30 | 2026-09-09 review remediation: RCVA/Stage-2 wiring, refusal gates, W016/W017, rename rollback, CLI failure envelopes |
| `tests/test_review_fixes.py` | 20 | 2026-09-09 review fixes R1–R8: crash injection, approval binding, exit-code contract |
| `tests/test_operations_and_ci.py` | 15 | Reaper TTL/quarantine, environment tiers, conformance matrix & drift |
| `tests/test_parquet_staging.py` | 12 | DSCP parquet commits, migrations, equivalence (pyarrow/duckdb importorskip) |
| `tests/test_migration.py` | 11 | Legacy parser rules, deterministic engine, collision detection |
| `tests/test_vector_retrieval.py` | 10 | D79–D84 vector index, fail-closed rehydration, offline-only AST scan |
| `tests/test_ingest_safety.py` | 10 | Path sandboxing, injection fencing, CSCC crash-safe capture |
| `tests/test_structural_graph.py` | 9 | AST structural index, incremental rebuild, blast radius |
| `tests/test_runaway.py` | 9 | VAL-014 sliding-ring circuit breaker, 40% rule |
| `tests/test_registries.py` | 9 | Registry models (extra=forbid), loader, validator |
| `tests/test_graph_intelligence.py` | 9 | Discovery lifecycle, derived edges, Swanson ABC (cache-gated) |
| `tests/test_val_extensions.py` | 8 | VAL-011/012 link mirroring & mermaid degradation |
| `tests/test_proposal_promotion.py` | 8 | DPCP promotion, journals, locks |
| `tests/test_linter.py` | 8 | 5-layer validation, W015 degree cap |
| `tests/test_bundles_and_okf.py` | 8 | OKF export/import, deterministic bundles |
| `tests/test_rcva.py` | 7 | RET-011 constrain/verify/abstain |
| `tests/test_retrieval.py` | 6 | RRF fusion, D82/D93/D94 contracts |
| `tests/test_calibration.py` | 6 | Constrained logit calibration (RET-008) |
| `tests/test_slug_and_paths.py` | 5 | TAX-002 slug determinism |
| `tests/test_section_ownership.py` | 5 | OWN-001..003, E051 |
| `tests/test_section_map.py` | 5 | SCHEMA-005 Document Cards |
| `tests/test_moderator_prescore.py` | 5 | REVIEW-011 pre-scoring |
| `tests/test_instruction_fence.py` | 5 | DISC-009 fenced instruction blocks |
| `tests/test_two_stage_refusal.py` | 4 | RET-006/007 refusal payloads |
| `tests/test_smoke.py` | 4 | CLI end-to-end smoke |
| `tests/test_section_retrieval.py` | 4 | RET-010 `show --section/--lines` |
| `tests/test_pubmed_adapter.py` | 4 | Streaming XML adapter, XXE rejection |
| `tests/test_parser_and_corpus.py` | 4 | Single-pass loader, fence anchoring |
| `tests/test_csr_graph.py` | 4 | CSR projection math, traversal |
| `tests/test_csr_compile.py` | 4 | Out-of-core compile → package loader round-trip, completion markers |
| `tests/test_pubmed_batch.py` | 3 | Batch ingestion (2 heavy parses skip without `TRASHHEAP_RUN_HEAVY=1`) |
| `tests/test_init.py` | 2 | Wiki scaffolding + fence injection |
| `tests/test_agent_skills.py` | 2 | E050 skill drift |
| `tests/test_pubmed_benchmark.py` | 1 | PubMedQA harness (parameterized DuckDB path) |
| `tests/test_atomic_rename.py` | 1 | Atomic rename durability |
| **Total** | **257 collected (255 passed, 2 skipped)** | **Full system surface** |

---

## 4. PubMedQA Benchmark Results (`RET-006`, `RET-009`)

Recorded during the REP-SCALE-002 benchmark session (not re-executed for this report):

| Benchmark Split | Sample Size | Top-1 Exact Recall | Conclusion Preservation (`RET-009`) | Negative Refusal (`RET-006`) | Mean Query Latency |
|:---|:---:|:---:|:---:|:---:|:---:|
| **PubMedQA Gold** | 1,000 QA pairs | **100.0%** (1,000/1,000) | **100.0%** | **100.0%** | 12.28 ms |
| **PubMedQA Unlabeled** | 1,000 QA pairs | **100.0%** (1,000/1,000) | **100.0%** | **100.0%** | 10.79 ms |

---

## 5. Large-Scale Graph Telemetry (38.16M Nodes, 1.083B Edges)

Full PubMed baseline graph compiled from 1,334 XML shards into out-of-core CSR binary format.

| Metric | Target / Baseline | Measured Result | Status |
|:---|:---|:---|:---:|
| **Memory Footprint (Ingestion)** | < 150 MB flat RSS | **108 – 114 MB RSS** (parent process only — see disclosure 3) | **PASSED** |
| **Memory Footprint (Traversal)** | < 500 MB RAM | **< 200 MB RSS** (off NVMe mmap) | **PASSED** |
| **Streaming Throughput** | > 1,000 arts/s | **1,626.8 – 2,718.6 arts/s** | **PASSED** |
| **1-Hop Neighbor Lookup** | < 1 ms | **126.073 µs – 202.51 µs** (unseeded RNG across sessions; see disclosure 4) | **PASSED** |
| **2-Hop Subgraph Expansion** | < 50 ms | **7.52 ms** (~913 nodes) | **PASSED** |
| **Swanson ABC Discovery** | < 10 s | **3.45 s** (Raynaud↔Fish-Oils; reproduced exactly by committed code — `trashheap discover literature`, `tests/test_csr_compile.py`) | **PASSED — REPRODUCIBLE** |
| **4-Hop Directed Pedigree** | < 2 s | **712.19 ms** (CRISPR → Watson & Crick) | **AD-HOC** (disclosure 2) |
| **Citation Scale-Free Fit (γ)** | Theoretical [2.0, 3.0] | **γ = 2.569** (k ≥ 50, n = 1.43M) | **AD-HOC** (disclosure 2) |
| **Citation Gini Index** | Heavy-tailed inequality | **0.7844** (Top 19.4% hold 80.0% cites) | **AD-HOC** (disclosure 2) |

### Telemetry-integrity disclosures (mandatory)

1. **Resume-zeroed counters.** `.cache/pubmed/full_pubmed_report.json` reports `total_citations: 0`, `total_mesh_headings: 0` and `total_elapsed_hours: 0.22`. These counters were **zeroed by the resume logic**: cached shards report zero work on re-runs (`scripts/ingest_full_pubmed.py` shard-cache path). The true wall-clock cost of the full ingestion was **~11.6 hours across 6 process starts** (Sep 8 23:46 → Sep 9 11:22, including a reboot mid-run), as evidenced by `.cache/pubmed/full_job.log`. The 1.083B citation-edge total is real (it is encoded in the CSR `indptr`), but the report JSON's per-run telemetry is not a faithful summary of the whole job.
2. **Ad-hoc experiment rows.** The pedigree, power-law-γ and Gini rows above (and experiments 1/2/4/5 in `PUBMED_ADVANCED_TOPOLOGY_EXPERIMENTS.md`) were produced by an **interactive session whose code was never committed**; `.cache/pubmed/citation_counts.npy` has no committed producer or consumer. They are recorded as observations, **not** as reproducible results. Only the Swanson ABC row is backed by committed, tested code.
3. **RSS telemetry scope.** The ingestion RSS figures measure the parent process (`/proc/self/status`); multiprocessing pool workers holding per-shard edge lists are not included.
4. **Unseeded traversal benchmark.** Historic 1-hop latencies were produced with an unseeded RNG; the benchmark is now seeded (`graph/csr.py`) so future runs are comparable.

### CSR artifact contract (fixed 2026-09-09)

`indices.npy` is now written **with a numpy header** (`np.lib.format.open_memmap`) and a `csr_manifest.json` completion marker is written atomically last; resume validity requires the marker (size-only checks are no longer sufficient). `CsrGraphProjection.load_memmap` accepts both headered and legacy headerless artifacts and validates `indptr[-1] == len(indices)` fail-closed. The pre-existing 8.66 GB legacy artifact can be adopted without recompilation via `scripts/ingest_full_pubmed.py --adopt-legacy-csr`.

---

## 6. Related Reports

- [`docs/FULL_PUBMED_40M_SCALE_REPORT.md`](./FULL_PUBMED_40M_SCALE_REPORT.md): Ingestion, out-of-core CSR compilation, and scale benchmarks.
- [`docs/PUBMED_ADVANCED_TOPOLOGY_EXPERIMENTS.md`](./PUBMED_ADVANCED_TOPOLOGY_EXPERIMENTS.md): Top-20 papers, power-law MLE, and Swanson discoveries (see reproducibility status table therein).
- [`docs/DISCOVERY_AND_EXAMPLES.md`](./DISCOVERY_AND_EXAMPLES.md): User guide and CLI examples for graph discovery and retrieval.

---

## 7. Erratum (REP-FULL-001)

The previous revision of this report (commit `57a0948`) contained a **fabricated per-module test table** (10 of 14 rows did not match the tree at its own commit; "Other specialized suites: 63" was a balancing plug) and stale totals. It is superseded in full by this revision, whose §3 table is generated from `pytest --collect-only -q` output. This erratum is retained deliberately: provenance integrity requires that corrections be visible, not silent.
