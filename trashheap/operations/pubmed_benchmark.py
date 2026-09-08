"""PubMedQA evaluation benchmark harness for hybrid retrieval and refusal testing.

Evaluates:
- Gold document recall (Top-1, Top-5, Top-10) using BM25 and graph retrieval.
- Conclusion section preservation (Truncation Trap defense).
- Multi-target citation filtering.
- Structural refusal discrimination on negative controls.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from trashheap.corpus import Corpus, load_corpus
from trashheap.operations.pubmed import (
    PubmedArticleRecord,
    PubmedXmlAdapter,
    validate_and_filter_citations,
)
from trashheap.registry.loader import LoadedRegistries, load_registries
from trashheap.retrieval import HybridRetriever

PUBMEDQA_URL = "https://raw.githubusercontent.com/pubmedqa/pubmedqa/master/data/ori_pqal.json"


@dataclass
class BenchmarkQuestion:
    """A single PubMedQA question instance."""

    pmid: int
    question: str
    decision: str  # 'yes', 'no', 'maybe'
    labels: List[str]
    contexts: List[str]
    gold_canonical_id: str = field(init=False)

    def __post_init__(self):
        self.gold_canonical_id = f"PERS-ART-MED_{self.pmid:08d}-0001"

    @property
    def conclusion_text(self) -> str:
        for lbl, ctx in zip(self.labels, self.contexts):
            if "conclusion" in lbl.lower():
                return ctx
        return ""


@dataclass
class BenchmarkReport:
    """Aggregate benchmark results."""

    total_questions: int
    corpus_size: int
    gold_in_top_1: int
    gold_in_top_5: int
    gold_in_top_10: int
    conclusions_preserved: int
    control_questions_tested: int
    control_questions_refused: int
    citation_filter_retained: int
    citation_filter_removed: int
    corpus_build_time_sec: float = 0.0
    total_query_time_sec: float = 0.0

    @property
    def top_1_recall(self) -> float:
        return self.gold_in_top_1 / max(1, self.total_questions)

    @property
    def top_1_accuracy(self) -> float:
        return self.top_1_recall

    @property
    def top_5_recall(self) -> float:
        return self.gold_in_top_5 / max(1, self.total_questions)

    @property
    def top_10_recall(self) -> float:
        return self.gold_in_top_10 / max(1, self.total_questions)

    @property
    def conclusion_preservation_rate(self) -> float:
        return self.conclusions_preserved / max(1, self.total_questions)

    @property
    def control_refusal_rate(self) -> float:
        return self.control_questions_refused / max(1, self.control_questions_tested)

    @property
    def negative_control_refusal_rate(self) -> float:
        return self.control_refusal_rate

    @property
    def fake_citations_stripped(self) -> int:
        return self.citation_filter_removed

    @property
    def mean_query_ms(self) -> float:
        if self.total_questions == 0:
            return 0.0
        return (self.total_query_time_sec / self.total_questions) * 1000.0

    @property
    def queries_per_sec(self) -> float:
        if self.total_query_time_sec <= 0:
            return 0.0
        return self.total_questions / self.total_query_time_sec

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_questions": self.total_questions,
            "corpus_size": self.corpus_size,
            "top_1_recall": self.top_1_recall,
            "top_5_recall": self.top_5_recall,
            "top_10_recall": self.top_10_recall,
            "conclusion_preservation_rate": self.conclusion_preservation_rate,
            "control_refusal_rate": self.control_refusal_rate,
            "negative_control_refusal_rate": self.negative_control_refusal_rate,
            "fake_citations_stripped": self.fake_citations_stripped,
            "corpus_build_time_sec": round(self.corpus_build_time_sec, 3),
            "total_query_time_sec": round(self.total_query_time_sec, 3),
            "mean_query_ms": round(self.mean_query_ms, 2),
            "queries_per_sec": round(self.queries_per_sec, 1),
        }


class PubmedBenchmarkHarness:
    """Benchmark harness executing retrieval tests on PubMedQA."""

    def __init__(
        self,
        sample_limit: int = 50,
        pubmed_file: Optional[Union[str, Path]] = None,
        registries: Optional[LoadedRegistries] = None,
        registry_dir: Optional[Path] = None,
        sample_size: Optional[int] = None,
    ):
        self.sample_limit = sample_size if sample_size is not None else sample_limit
        self.pubmed_file = Path(pubmed_file) if pubmed_file else None
        self.adapter = PubmedXmlAdapter(default_scope="personal")
        self.registries = registries or load_registries(registry_dir)

    def load_dataset(self, local_cache_path: Optional[Path] = None) -> List[BenchmarkQuestion]:
        """Load PubMedQA benchmark instances from local path or remote URL."""
        cache_path = local_cache_path or self.pubmed_file
        raw_data = None
        if cache_path and cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        else:
            req = urllib.request.Request(PUBMEDQA_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw_data = json.loads(resp.read().decode("utf-8"))
            if local_cache_path:
                local_cache_path.parent.mkdir(parents=True, exist_ok=True)
                with open(local_cache_path, "w", encoding="utf-8") as f:
                    json.dump(raw_data, f)

        questions: List[BenchmarkQuestion] = []
        for pmid_str, item in list(raw_data.items())[: self.sample_limit]:
            try:
                pmid = int(pmid_str)
                questions.append(
                    BenchmarkQuestion(
                        pmid=pmid,
                        question=item["QUESTION"],
                        decision=item.get("final_decision", "maybe"),
                        labels=item.get("LABELS", []),
                        contexts=item.get("CONTEXTS", []),
                    )
                )
            except (ValueError, KeyError):
                continue

        return questions

    def build_test_corpus(
        self,
        questions: List[BenchmarkQuestion],
        target_dir: Path,
    ) -> Corpus:
        """Materialize canonical markdown files from questions into a test Corpus."""
        personal_dir = target_dir / "personal" / "03_natural_science"
        personal_dir.mkdir(parents=True, exist_ok=True)

        for q in questions:
            sections = {lbl: ctx for lbl, ctx in zip(q.labels, q.contexts)}
            full_abstract = "\n\n".join(f"{lbl}: {ctx}" for lbl, ctx in zip(q.labels, q.contexts))
            rec = PubmedArticleRecord(
                pmid=q.pmid,
                title=q.question.rstrip("?"),
                abstract=full_abstract,
                sections=sections,
                mesh_headings=[
                    {"ui": "D000001", "name": "Biomedicine", "major": True},
                    {"ui": "D000002", "name": q.labels[0] if q.labels else "Study", "major": False},
                ],
                citations=[],
            )
            md_content = self.adapter.record_to_markdown(rec)
            note_path = personal_dir / f"{rec.canonical_id}.md"
            note_path.write_text(md_content, encoding="utf-8")

        return load_corpus(target_dir)

    def run_benchmark(
        self,
        questions: List[BenchmarkQuestion],
        corpus: Corpus,
    ) -> BenchmarkReport:
        retriever = HybridRetriever(corpus=corpus, registries=self.registries)

        gold_top_1 = 0
        gold_top_5 = 0
        gold_top_10 = 0
        conclusions_preserved = 0

        for q in questions:
            bundle = retriever.retrieve(query=q.question, cli_params={"max_results": 10})
            candidate_ids = [node["node_id"] for node in bundle.get("evidence_bundle", [])]

            if candidate_ids and candidate_ids[0] == q.gold_canonical_id:
                gold_top_1 += 1
            if q.gold_canonical_id in candidate_ids[:5]:
                gold_top_5 += 1
            if q.gold_canonical_id in candidate_ids[:10]:
                gold_top_10 += 1

            # Check if conclusion text is preserved when reading the object body
            ko = corpus.get_by_id(q.gold_canonical_id)
            if ko and q.conclusion_text:
                if q.conclusion_text in ko.raw_body or q.conclusion_text[:50] in ko.raw_body:
                    conclusions_preserved += 1
            elif ko and not q.conclusion_text:
                conclusions_preserved += 1

        # Test negative controls (adversarial questions designed to fail grounding/path)
        controls = [
            "Wingardium leviosa quidditch broomstick aerodynamics",
            "Does quantum teleportation via vibranium cure Lycanthropy?",
            "Unicorn horn dust effectiveness against Klingon flu",
        ]
        controls_refused = 0
        for ctrl_q in controls:
            ctrl_bundle = retriever.retrieve(
                query=ctrl_q, cli_params={"max_results": 10, "min_relevance": 0.1}
            )
            # Stage 1 refusal: no candidates or zero relevant results
            results = ctrl_bundle.get("evidence_bundle", [])
            if not results or all(
                r.get("score_components", {}).get("final", 0) < 0.1 for r in results
            ):
                controls_refused += 1

        # Test citation bracket filtering
        all_valid_ids = {q.gold_canonical_id for q in questions}
        fake_ans = (
            f"Result based on [{questions[0].gold_canonical_id}, FAKE_PMID_99999999]. "
            "Fabricated source [FAKE_PMID_12345678]."
        )
        _, retained, removed = validate_and_filter_citations(fake_ans, all_valid_ids)

        return BenchmarkReport(
            total_questions=len(questions),
            corpus_size=len(corpus),
            gold_in_top_1=gold_top_1,
            gold_in_top_5=gold_top_5,
            gold_in_top_10=gold_top_10,
            conclusions_preserved=conclusions_preserved,
            control_questions_tested=len(controls),
            control_questions_refused=controls_refused,
            citation_filter_retained=len(retained),
            citation_filter_removed=len(removed),
        )

    def run(self) -> BenchmarkReport:
        """Run end-to-end benchmark in a temporary corpus."""
        import tempfile
        import time

        questions = self.load_dataset(local_cache_path=self.pubmed_file)
        start_build = time.perf_counter()
        with tempfile.TemporaryDirectory() as tmp_dir:
            corpus = self.build_test_corpus(questions, Path(tmp_dir))
            corpus_build_time = time.perf_counter() - start_build

            start_query = time.perf_counter()
            report = self.run_benchmark(questions, corpus)
            query_time = time.perf_counter() - start_query

            report.corpus_build_time_sec = corpus_build_time
            report.total_query_time_sec = query_time
            return report
