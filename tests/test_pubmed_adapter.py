"""Unit tests for PubMed XML adapter, multi-citation validation, and schema conformance."""

from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from trashheap.models import FrontmatterModel
from trashheap.operations.connector import RawPayload
from trashheap.operations.pubmed import (
    PubmedXmlAdapter,
    stream_pubmed_xml,
    validate_and_filter_citations,
)

SAMPLE_PUBMED_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2024//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_240101.dtd">
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation Status="MEDLINE">
      <PMID Version="1">21645374</PMID>
      <Article PubModel="Print-Electronic">
        <Journal>
          <Title>Annals of botany</Title>
          <JournalIssue>
            <PubDate><Year>2011</Year></PubDate>
          </JournalIssue>
        </Journal>
        <ArticleTitle>Do mitochondria play a role in remodelling lace plant leaves during programmed cell death?</ArticleTitle>
        <Abstract>
          <AbstractText Label="BACKGROUND">Programmed cell death (PCD) is an essential process in plant development.</AbstractText>
          <AbstractText Label="RESULTS">Mitochondrial dynamics change early during perforation formation.</AbstractText>
          <AbstractText Label="CONCLUSIONS">Mitochondria play an active regulatory role in lace plant PCD.</AbstractText>
        </Abstract>
      </Article>
      <MeshHeadingList>
        <MeshHeading>
          <DescriptorName UI="D008928" MajorTopicYN="Y">Mitochondria</DescriptorName>
        </MeshHeading>
        <MeshHeading>
          <DescriptorName UI="D010944" MajorTopicYN="N">Plants</DescriptorName>
        </MeshHeading>
      </MeshHeadingList>
      <CommentsCorrectionsList>
        <CommentsCorrections RefType="ErratumIn">
          <PMID>21998877</PMID>
        </CommentsCorrections>
      </CommentsCorrectionsList>
    </MedlineCitation>
    <PubmedData>
      <ReferenceList>
        <Reference>
          <ArticleIdList>
            <ArticleId IdType="pubmed">18708535</ArticleId>
          </ArticleIdList>
        </Reference>
        <Reference>
          <ArticleIdList>
            <ArticleId IdType="pubmed">19451515</ArticleId>
          </ArticleIdList>
        </Reference>
      </ReferenceList>
    </PubmedData>
  </PubmedArticle>
</PubmedArticleSet>
"""


def test_stream_pubmed_xml():
    records = list(stream_pubmed_xml(SAMPLE_PUBMED_XML))
    assert len(records) == 1
    rec = records[0]
    assert rec.pmid == 21645374
    assert "mitochondria play a role" in rec.title.lower()
    assert rec.year == 2011
    assert rec.journal == "Annals of botany"
    assert len(rec.mesh_headings) == 2
    assert rec.mesh_headings[0]["name"] == "Mitochondria"
    assert rec.mesh_headings[0]["major"] is True
    assert rec.citations == [18708535, 19451515]
    assert len(rec.corrections) == 1
    assert rec.corrections[0]["pmid"] == "21998877"
    assert "CONCLUSIONS" in rec.sections
    assert "Mitochondria play an active regulatory role" in rec.sections["CONCLUSIONS"]


def test_record_to_markdown_conformance():
    adapter = PubmedXmlAdapter(default_scope="personal")
    records = list(stream_pubmed_xml(SAMPLE_PUBMED_XML))
    rec = records[0]
    md_content = adapter.record_to_markdown(rec)

    # Validate frontmatter parses cleanly with Pydantic
    parts = md_content.split("---")
    assert len(parts) >= 3
    fm_raw = yaml.safe_load(parts[1])
    fm = FrontmatterModel.model_validate(fm_raw)
    assert fm.id == "PERS-ART-MED_21645374-0001"
    assert fm.object_type == "Article"
    assert fm.domain == "natural_science"
    assert "PMID:21645374" in fm.aliases
    assert "mitochondria" in fm.keywords
    assert len(fm.relations) == 3  # 2 CITES + 1 SUPERSEDES

    # Validate conclusion section is preserved in body
    assert "### Conclusions" in md_content
    assert "regulatory role in lace plant PCD" in md_content


def test_validate_and_filter_citations_multi_id():
    """Verify that multi-target brackets [ID1, ID2] are correctly split and filtered."""
    valid_ids = {"PERS-ART-MED_00000001-0001", "PERS-ART-MED_00000002-0001", "18708535"}

    text = (
        "Evidence from multiple sources [18708535, 99999999]. "
        "Also supported by [PERS-ART-MED_00000001-0001, PERS-ART-MED_00000002-0001]. "
        "Fabricated source [12345678]."
    )

    clean_text, retained, removed = validate_and_filter_citations(text, valid_ids)

    assert "99999999" in removed
    assert "12345678" in removed
    assert "18708535" in retained
    assert "PERS-ART-MED_00000001-0001" in retained
    assert "PERS-ART-MED_00000002-0001" in retained

    # The fabricated source bracket should be stripped entirely
    assert "[12345678]" not in clean_text
    assert "[18708535]" in clean_text
    assert "[PERS-ART-MED_00000001-0001, PERS-ART-MED_00000002-0001]" in clean_text


def test_pubmed_ingest_adapter_staging():
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        adapter = PubmedXmlAdapter()
        payload = RawPayload(
            source_path="pubmed_sample.xml",
            content_bytes=SAMPLE_PUBMED_XML,
            content_hash="dummy_hash",
        )
        res = adapter.normalize_and_ingest(payload, root)
        assert res.source_id is not None
        assert res.evidence_unit_path.exists()
        assert res.capture_result.content_path.exists()
