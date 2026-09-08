"""Tests for PubMedQA benchmark harness, hybrid recall, and refusal metrics."""

from pathlib import Path
from tempfile import TemporaryDirectory

from trashheap.operations.pubmed_benchmark import (
    BenchmarkQuestion,
    PubmedBenchmarkHarness,
)


def test_pubmed_benchmark_harness_local():
    # Build 5 realistic benchmark questions
    sample_questions = [
        BenchmarkQuestion(
            pmid=21645374,
            question="Do mitochondria play a role in remodelling lace plant leaves during programmed cell death?",
            decision="yes",
            labels=["BACKGROUND", "RESULTS", "CONCLUSIONS"],
            contexts=[
                "Programmed cell death is an essential process in plant development.",
                "Mitochondrial dynamics change early during leaf perforation formation.",
                "Mitochondria play an active regulatory role in lace plant programmed cell death.",
            ],
        ),
        BenchmarkQuestion(
            pmid=18708535,
            question="Is autophagy required for chloroplast degradation during senescence?",
            decision="yes",
            labels=["BACKGROUND", "CONCLUSIONS"],
            contexts=[
                "Chloroplasts contain the majority of leaf protein.",
                "Autophagy machinery mediates the delivery of chloroplast proteins to vacuoles.",
            ],
        ),
        BenchmarkQuestion(
            pmid=19451515,
            question="Does nitric oxide modulate programmed cell death in soybean cells under salinity stress?",
            decision="maybe",
            labels=["BACKGROUND", "RESULTS", "CONCLUSIONS"],
            contexts=[
                "Salinity induces severe oxidative damage in legumes.",
                "NO donors decreased cell death at low concentrations but accelerated it at high concentrations.",
                "Nitric oxide exhibits dose-dependent dual modulation of plant cell death.",
            ],
        ),
        BenchmarkQuestion(
            pmid=15753114,
            question="Does low-dose aspirin reduce primary cardiovascular events in healthy women?",
            decision="no",
            labels=["BACKGROUND", "CONCLUSIONS"],
            contexts=[
                "The efficacy of aspirin in primary prevention among women remains uncertain.",
                "Aspirin lowered the risk of stroke without significantly reducing myocardial infarction in healthy women.",
            ],
        ),
        BenchmarkQuestion(
            pmid=41325611,
            question="What is the clinical efficacy of metformin in preventing diabetes progression?",
            decision="yes",
            labels=["BACKGROUND", "CONCLUSIONS"],
            contexts=[
                "Metformin is widely prescribed for insulin resistance.",
                "Metformin significantly delays the onset of type 2 diabetes in high-risk individuals.",
            ],
        ),
    ]

    with TemporaryDirectory() as tmpdir:
        target = Path(tmpdir)
        harness = PubmedBenchmarkHarness(sample_limit=5)
        corpus = harness.build_test_corpus(sample_questions, target)

        assert len(corpus) == 5

        report = harness.run_benchmark(sample_questions, corpus)

        # High gold document recall on realistic queries
        assert report.total_questions == 5
        assert report.top_1_accuracy >= 0.80
        assert report.top_5_recall == 1.0
        assert report.conclusion_preservation_rate == 1.0

        # Negative controls must be refused (Stage 1 refusal)
        assert report.control_questions_tested == 3
        assert report.control_refusal_rate == 1.0

        # Citation filtering verified
        assert report.citation_filter_retained == 1
        assert report.citation_filter_removed == 2
