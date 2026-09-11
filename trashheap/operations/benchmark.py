"""Performance measurements and evidence-based scale transition criteria (SCALE-001, ARCHITECTURE.md §6)."""

import glob
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import ValidationError

from trashheap.corpus import Corpus
from trashheap.linter import Linter
from trashheap.models import FrontmatterModel, KnowledgeObject
from trashheap.registry.loader import load_registries
from trashheap.retrieval import HybridRetriever

QUERY_BUDGET_MS = 100.0
DOC_PROCESSING_BUDGET_MS = 50.0


@dataclass
class BenchmarkReport:
    """Measured performance baseline and scale transition assessment (SCALE-001)."""

    corpus_document_count: int
    total_bytes: int
    total_lines: int
    parse_total_sec: float
    parse_ms_per_doc: float
    parse_docs_per_sec: float
    lint_total_sec: float
    lint_ms_per_doc: float
    lint_finding_count: int
    retrieval_index_sec: float
    retrieval_query_count: int
    retrieval_mean_query_ms: float
    retrieval_min_query_ms: float
    retrieval_max_query_ms: float
    scale_transition_assessment: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "corpus_document_count": self.corpus_document_count,
            "total_bytes": self.total_bytes,
            "total_lines": self.total_lines,
            "parse": {
                "total_sec": round(self.parse_total_sec, 4),
                "ms_per_doc": round(self.parse_ms_per_doc, 3),
                "docs_per_sec": round(self.parse_docs_per_sec, 1),
            },
            "lint": {
                "total_sec": round(self.lint_total_sec, 4),
                "ms_per_doc": round(self.lint_ms_per_doc, 3),
                "finding_count": self.lint_finding_count,
            },
            "retrieval": {
                "index_build_sec": round(self.retrieval_index_sec, 4),
                "query_count": self.retrieval_query_count,
                "mean_query_ms": round(self.retrieval_mean_query_ms, 3),
                "min_query_ms": round(self.retrieval_min_query_ms, 3),
                "max_query_ms": round(self.retrieval_max_query_ms, 3),
            },
            "scale_transition_assessment": self.scale_transition_assessment,
        }


def _percentile(values: List[float], pct: float) -> float:
    """Return the linear-interpolated percentile of ``values`` (empty -> 0.0)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (pct / 100.0) * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    frac = rank - low
    return ordered[low] * (1.0 - frac) + ordered[high] * frac


def compute_scale_transition_assessment(
    mean_query_ms: float,
    p95_query_ms: float,
    parse_ms_per_doc: float,
    lint_ms_per_doc: float,
) -> Dict[str, Any]:
    """Compute the SCALE-001 assessment by comparing measurements against budgets.

    The status is derived from the measured latencies rather than hardcoded: any
    breach of the per-query budget (mean or p95) or the per-document processing
    budget (parse or lint) yields ``exceeds_budget``; otherwise
    ``within_baseline_limits``.
    """
    exceeds = (
        mean_query_ms > QUERY_BUDGET_MS
        or p95_query_ms > QUERY_BUDGET_MS
        or parse_ms_per_doc > DOC_PROCESSING_BUDGET_MS
        or lint_ms_per_doc > DOC_PROCESSING_BUDGET_MS
    )
    status = "exceeds_budget" if exceeds else "within_baseline_limits"

    if exceeds:
        rationale = (
            "Measured latencies breach a resource budget (query mean %.2f ms / p95 %.2f ms vs "
            "%.0f ms; parsing %.2f ms/doc, linting %.2f ms/doc vs %.0f ms/doc). Per SCALE-001 a "
            "repeated breach is the trigger to evaluate higher operating tiers (e.g. dedicated "
            "vector database, structural graph store)."
            % (
                mean_query_ms,
                p95_query_ms,
                QUERY_BUDGET_MS,
                parse_ms_per_doc,
                lint_ms_per_doc,
                DOC_PROCESSING_BUDGET_MS,
            )
        )
    else:
        rationale = (
            "Measured baseline latencies (query mean %.2f ms / p95 %.2f ms, parsing %.2f ms/doc, "
            "linting %.2f ms/doc) operate within the %.0f ms/query and %.0f ms/doc budgets. Per "
            "SCALE-001, higher operating tiers (e.g. dedicated vector database, structural graph "
            "store) are NOT justified without repeated breach of resource budgets."
            % (
                mean_query_ms,
                p95_query_ms,
                parse_ms_per_doc,
                lint_ms_per_doc,
                QUERY_BUDGET_MS,
                DOC_PROCESSING_BUDGET_MS,
            )
        )

    return {
        "status": status,
        "evidence_type": "measured_baseline",
        "governing_invariant": "SCALE-001",
        "measured": {
            "mean_query_ms": round(mean_query_ms, 3),
            "p95_query_ms": round(p95_query_ms, 3),
            "parse_ms_per_doc": round(parse_ms_per_doc, 3),
            "lint_ms_per_doc": round(lint_ms_per_doc, 3),
        },
        "budgets": {
            "max_query_budget_ms": QUERY_BUDGET_MS,
            "max_doc_processing_budget_ms_per_doc": DOC_PROCESSING_BUDGET_MS,
        },
        "rationale": rationale,
        "uncalibrated_targets": {
            "max_query_budget_ms": QUERY_BUDGET_MS,
            "max_lint_budget_ms_per_doc": DOC_PROCESSING_BUDGET_MS,
            "note": "Targets are non-normative uncalibrated benchmarks; not production claims.",
        },
    }


def _parse_knowledge_object(path: Path, text: str) -> KnowledgeObject:
    """Parse already-read Markdown text into a KnowledgeObject (mirrors corpus.load_single_file)."""
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return KnowledgeObject(
            path=path,
            frontmatter_dict={},
            raw_body=text,
            frontmatter=None,
            load_error=ValueError(f"File missing starting YAML frontmatter fence ('---'): {path}"),
        )

    parts = stripped.split("---", 2)
    if len(parts) < 3:
        return KnowledgeObject(
            path=path,
            frontmatter_dict={},
            raw_body=text,
            frontmatter=None,
            load_error=ValueError(f"File missing YAML frontmatter fence ('---'): {path}"),
        )

    fm_raw = parts[1]
    body = parts[2]

    try:
        fm_dict = yaml.safe_load(fm_raw)
    except yaml.YAMLError as exc:
        return KnowledgeObject(
            path=path, frontmatter_dict={}, raw_body=body, frontmatter=None, load_error=exc
        )

    if not isinstance(fm_dict, dict):
        return KnowledgeObject(
            path=path,
            frontmatter_dict={},
            raw_body=body,
            frontmatter=None,
            load_error=ValueError(f"Frontmatter is not a YAML dictionary: {path}"),
        )

    fm_model: Optional[FrontmatterModel] = None
    load_err: Optional[Exception] = None
    try:
        fm_model = FrontmatterModel.model_validate(fm_dict)
    except ValidationError as exc:
        load_err = exc

    return KnowledgeObject(
        path=path, frontmatter_dict=fm_dict, raw_body=body, frontmatter=fm_model, load_error=load_err
    )


def run_benchmark(
    workspace_root: Path,
    fixtures_dir: Optional[Path] = None,
    test_queries: Optional[List[str]] = None,
) -> BenchmarkReport:
    """Execute reproducible performance baseline measurement over canonical fixtures."""
    fx_dir = fixtures_dir or (workspace_root / "fixtures" / "canonical")
    files = sorted(glob.glob(str(fx_dir / "**" / "*.md"), recursive=True))
    if not files:
        raise ValueError(f"No canonical fixtures found at {fx_dir}")

    doc_count = len(files)

    # 1. Single read pass: read each fixture exactly once, derive raw-file stats,
    #    and benchmark frontmatter parsing + schema validation (SCALE-001).
    total_bytes = 0
    total_lines = 0
    objects: List[KnowledgeObject] = []

    t0 = time.perf_counter()
    for f_path in files:
        path = Path(f_path)
        text = path.read_text(encoding="utf-8")
        total_bytes += len(text.encode("utf-8"))
        total_lines += len(text.splitlines())
        objects.append(_parse_knowledge_object(path, text))
    parse_dur = time.perf_counter() - t0
    parse_ms_per_doc = (parse_dur / doc_count) * 1000.0
    parse_docs_per_sec = doc_count / parse_dur if parse_dur > 0 else 0.0

    # Assemble the corpus from the single read pass (no second disk read).
    corpus = Corpus(root=fx_dir)
    corpus.read_count = len(objects)
    for ko in objects:
        corpus.objects.append(ko)
        corpus.objects_by_path[ko.path] = ko
        if ko.id and ko.id not in corpus.objects_by_id:
            corpus.objects_by_id[ko.id] = ko

    # 2. Benchmark multi-layer linter
    registries = load_registries(workspace_root / "schemas" / "registry")
    linter = Linter(registries=registries)

    t1 = time.perf_counter()
    findings = linter.lint_corpus(corpus)
    lint_dur = time.perf_counter() - t1
    lint_ms_per_doc = (lint_dur / doc_count) * 1000.0

    # 3. Benchmark hybrid retrieval
    queries = test_queries or [
        "knowledge compiler",
        "epistemic status",
        "crash safety",
        "taxonomy forest",
        "provenance trail",
    ]

    t2 = time.perf_counter()
    retriever = HybridRetriever(corpus=corpus, registries=registries)
    retrieval_index_dur = time.perf_counter() - t2

    # Warm up once so the timed loop measures steady-state per-query latency and
    # excludes one-time lazy initialization (SCALE-001 interactive query budget).
    retriever.retrieve(query=queries[0], cli_params={"max_results": 5})

    query_latencies_ms: List[float] = []
    for q in queries:
        tq = time.perf_counter()
        _ = retriever.retrieve(query=q, cli_params={"max_results": 5})
        query_latencies_ms.append((time.perf_counter() - tq) * 1000.0)

    mean_query_ms = sum(query_latencies_ms) / len(query_latencies_ms)
    min_query_ms = min(query_latencies_ms)
    max_query_ms = max(query_latencies_ms)
    p95_query_ms = _percentile(query_latencies_ms, 95.0)

    # 4. Scale transition assessment (SCALE-001), computed from the measurements above.
    transition_assessment = compute_scale_transition_assessment(
        mean_query_ms=mean_query_ms,
        p95_query_ms=p95_query_ms,
        parse_ms_per_doc=parse_ms_per_doc,
        lint_ms_per_doc=lint_ms_per_doc,
    )

    return BenchmarkReport(
        corpus_document_count=doc_count,
        total_bytes=total_bytes,
        total_lines=total_lines,
        parse_total_sec=parse_dur,
        parse_ms_per_doc=parse_ms_per_doc,
        parse_docs_per_sec=parse_docs_per_sec,
        lint_total_sec=lint_dur,
        lint_ms_per_doc=lint_ms_per_doc,
        lint_finding_count=len(findings),
        retrieval_index_sec=retrieval_index_dur,
        retrieval_query_count=len(queries),
        retrieval_mean_query_ms=mean_query_ms,
        retrieval_min_query_ms=min_query_ms,
        retrieval_max_query_ms=max_query_ms,
        scale_transition_assessment=transition_assessment,
    )
