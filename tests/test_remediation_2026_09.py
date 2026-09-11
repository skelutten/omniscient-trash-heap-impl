"""Regression tests for the 2026-09-09 full-code review remediation (OpenCode-01).

Pins the behavior of every P0/P1 fix: Stage-2 RCVA wiring (RET-007/RET-011),
path-admissibility tokenization, W016/W017 linter rules (VAL-011/VAL-012),
runaway ring semantics (VAL-014), rename slug/graph/rollback completion,
uniform CLI failure envelopes, corpus symlink containment, REVIEW-011
pre-scoring, DISC-009 fence injection at init, and vector-cache reuse.
"""

import json
import os
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from trashheap.cli import _fail_uniformly, main
from trashheap.constants import ExitCode
from trashheap.corpus import load_corpus
from trashheap.instruction_fence import FENCE_END, FENCE_START, apply_fenced_block
from trashheap.link_mirror import check_link_mirroring
from trashheap.linter import Linter
from trashheap.mermaid import validate_mermaid_block
from trashheap.models import KnowledgeObject
from trashheap.rcva import DEFAULT_TAU_ABSTAIN, entailment_score
from trashheap.registry.loader import load_registries
from trashheap.retrieval import HybridRetriever, epistemic_conflict_key
from trashheap.section_map import build_section_map
from trashheap.textutil import tokenize_with_ids

MINIMAL_KO = """---
id: {id}
title: {title}
schema_version: 3.8.10
scope: engineering
taxonomy_path: 01. Domain & System Architecture
taxonomy_id: TX-ENG-01
object_type: Concept
domain: computer_science
evidence: observed
verification: self_verified
authority: canonical
consensus: accepted
source_type: internal_document
source_refs:
- SRC-TEST
author: human:tester
last_modified: '2026-09-01'
next_review: '2027-09-01'
confidence: 0.9
status: established
relations: {relations}
---
# {title}

{body}
"""


def _write_ko(root: Path, rel: str, id: str, title: str, body: str, relations: str = "[]") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        MINIMAL_KO.format(id=id, title=title, body=body, relations=relations), encoding="utf-8"
    )
    return p


@pytest.fixture
def mini_corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    _write_ko(
        root,
        "engineering/01_x/ENG-CON-ALPHA-2024.md",
        "ENG-CON-ALPHA-2024",
        "Alpha retrieval grounding",
        "alpha content about retrieval grounding and photosynthesis converts light energy",
        relations="\n- type: RELATES_TO\n  target: ENG-CON-BETA-2024",
    )
    _write_ko(
        root,
        "engineering/01_x/ENG-CON-BETA-2024.md",
        "ENG-CON-BETA-2024",
        "Beta expansion",
        "beta content about graph expansion",
    )
    _write_ko(
        root,
        "engineering/01_x/ENG-CON-GAMMA-2024.md",
        "ENG-CON-GAMMA-2024",
        "Gamma isolated",
        "gamma content stands alone",
    )
    return root


def _retriever(corpus_root: Path) -> HybridRetriever:
    return HybridRetriever(corpus=load_corpus(corpus_root), registries=load_registries())


# --- RET-011 / RET-007: claim verification wired into retrieve() -------------


def test_retrieve_claim_grounded(mini_corpus):
    r = _retriever(mini_corpus)
    bundle = r.retrieve("photosynthesis", claim="photosynthesis converts light energy")
    assert bundle["rcva"] is not None
    assert bundle["rcva"]["decision"] == "GROUNDED"
    assert bundle["retrieval_status"] == "ADMISSIBLE"


def test_retrieve_claim_abstention_refuses_stage_2(mini_corpus):
    r = _retriever(mini_corpus)
    bundle = r.retrieve(
        "photosynthesis", claim="quantum chromodynamics confinement asymptotic freedom"
    )
    assert bundle["rcva"]["decision"] == "EPISTEMIC_ABSTENTION"
    assert bundle["retrieval_status"] == "REFUSED"
    assert bundle["refusal"]["stage"] == 2
    assert bundle["refusal"]["reason"] == "INSUFFICIENT_EVIDENCE"
    assert bundle["evidence_bundle"] == []


def test_rcva_stopwords_do_not_inflate_entailment():
    assert entailment_score("the of and to", "the of and to") == 0.0
    assert DEFAULT_TAU_ABSTAIN == 0.65


# --- RET-006: path-admissibility gate sees hyphenated node IDs ---------------


def test_tokenize_with_ids_preserves_node_ids():
    tokens = tokenize_with_ids("compare ENG-CON-ALPHA-2024 with ENG-CON-GAMMA-2024")
    assert "eng-con-alpha-2024" in tokens
    assert "eng-con-gamma-2024" in tokens


def test_path_admissibility_gate_refuses_unconnected_ids(mini_corpus):
    r = _retriever(mini_corpus)
    bundle = r.retrieve(
        "alpha ENG-CON-ALPHA-2024 ENG-CON-GAMMA-2024",
        cli_params={"enforce_structural_gates": True},
    )
    assert bundle["retrieval_status"] == "REFUSED"
    assert bundle["refusal"]["reason"] == "NO_ADMISSIBLE_PATH"


def test_path_admissibility_gate_passes_connected_ids(mini_corpus):
    r = _retriever(mini_corpus)
    bundle = r.retrieve(
        "alpha ENG-CON-ALPHA-2024 ENG-CON-BETA-2024",
        cli_params={"enforce_structural_gates": True},
    )
    assert bundle["stage_1_structural_gates"]["gates"]["path_admissibility"]["passed"] is True


# --- Determinism: parameters_used ordering and conflict tie-break ------------


def test_parameters_used_is_deterministically_ordered(mini_corpus):
    r = _retriever(mini_corpus)
    bundle = r.retrieve("alpha", cli_params={"max_results": 5})
    keys = list(bundle["parameters_used"].keys())
    assert keys == sorted(keys)


def test_conflict_tiebreak_lowest_id_wins_for_prefixes():
    fm = {
        "verification": "peer_verified",
        "authority": "authoritative",
        "consensus": "accepted",
        "evidence": "observed",
        "confidence": 0.9,
        "last_verified": "2026-01-01",
    }
    ko_short = KnowledgeObject(Path("a.md"), dict(fm), "", None)
    ko_long = KnowledgeObject(Path("b.md"), dict(fm), "", None)
    ko_short.frontmatter_dict["id"] = "ENG-A-1"
    ko_long.frontmatter_dict["id"] = "ENG-A-10"
    winner = max([ko_short, ko_long], key=epistemic_conflict_key)
    assert winner.frontmatter_dict["id"] == "ENG-A-1"


# --- VAL-011 / VAL-012: W016 + W017 linter rules ------------------------------


def test_w016_link_mirroring_warning(mini_corpus):
    linter = Linter(load_registries(), check_skills=False)
    corpus = load_corpus(mini_corpus)
    findings = linter.lint_corpus(corpus)
    w016 = [f for f in findings if f.code == "W016"]
    assert w016, "unmirrored relation must emit W016"
    assert any("ENG-CON-BETA-2024" in f.message for f in w016)

    mirrored = mini_corpus / "engineering/01_x/ENG-CON-ALPHA-2024.md"
    mirrored.write_text(
        mirrored.read_text(encoding="utf-8") + "\nSee [[ENG-CON-BETA-2024]] for details.\n",
        encoding="utf-8",
    )
    findings = linter.lint_corpus(load_corpus(mini_corpus))
    assert not [f for f in findings if f.code == "W016"]


def test_link_mirror_exact_match_not_substring():
    body = "See [ENG-COMP-10](./ENG-COMP-10.md) here."
    findings = check_link_mirroring(body, [{"type": "RELATES_TO", "target": "ENG-COMP-1"}])
    assert findings, "ENG-COMP-10 link must NOT mirror ENG-COMP-1"
    body2 = "See [ENG-COMP-1](./ENG-COMP-1.md) here."
    assert check_link_mirroring(body2, [{"type": "RELATES_TO", "target": "ENG-COMP-1"}]) == []


def test_w017_mermaid_warning(tmp_path: Path):
    root = tmp_path / "corpus"
    _write_ko(
        root,
        "engineering/01_x/ENG-CON-DIAG-2024.md",
        "ENG-CON-DIAG-2024",
        "Diagram note",
        "intro text\n\n```mermaid\nnot_a_diagram (\n```\n",
    )
    linter = Linter(load_registries(), check_skills=False)
    findings = linter.lint_corpus(load_corpus(root))
    w017 = [f for f in findings if f.code == "W017"]
    assert w017 and "mermaid" in w017[0].message.lower()


def test_mermaid_quoted_labels_and_crlf():
    ok, _ = validate_mermaid_block('graph TD\n  A["foo (bar"] --> B\n')
    assert ok
    body = "```mermaid\r\ngraph TD\r\n  A --> B\r\n```"
    from trashheap.mermaid import extract_mermaid_blocks

    blocks = extract_mermaid_blocks(body)
    assert len(blocks) == 1
    assert validate_mermaid_block(blocks[0]["inner"])[0]


# --- SCHEMA-005: section map is code-fence aware ------------------------------


def test_section_map_ignores_headings_inside_code_fences():
    body = "## Real\n\ntext\n\n```\n## Fake Inside Fence\n```\n\n## Also Real\nmore\n"
    titles = [e.title for e in build_section_map(body)]
    assert titles == ["Real", "Also Real"]


# --- DISC-009: instruction fence ----------------------------------------------


def test_instruction_fence_preserves_trailing_newline_state():
    with_nl = apply_fenced_block("# Human\n\ncontent\n", "block")
    assert with_nl.endswith("\n")
    without_nl = apply_fenced_block("# Human\n\ncontent", "block")
    assert not without_nl.endswith("\n")


def test_instruction_fence_first_start_wins():
    content = (
        f"human\n{FENCE_START}\nold\n{FENCE_END}\nmid\n{FENCE_START}\nstray\n"
    )
    out = apply_fenced_block(content, "new")
    assert "old" not in out
    assert "new" in out
    assert out.count(FENCE_START) == 2  # second (malformed) start untouched as human content


def test_init_injects_fenced_instruction_block(tmp_path: Path):
    from trashheap.init import init_wiki

    target = tmp_path / "wiki"
    res = init_wiki(target, name="Fence Test")
    assert res["status"] == "ok"
    agents_md = target / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text(encoding="utf-8")
    assert FENCE_START in content and FENCE_END in content
    assert "Fence Test" in content
    assert res["instruction_files_updated"] == ["AGENTS.md"]

    # Existing human-owned CLAUDE.md content survives; fence is appended.
    claude_md = target / "CLAUDE.md"
    claude_md.write_text("# My human instructions\nDo great things.\n", encoding="utf-8")
    init_wiki(target, name="Fence Test", force=True)
    content = claude_md.read_text(encoding="utf-8")
    assert content.startswith("# My human instructions")
    assert FENCE_START in content


# --- Corpus containment + exclusions ------------------------------------------


def test_corpus_skips_symlinks_escaping_root(tmp_path: Path):
    root = tmp_path / "corpus"
    root.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("---\nid: OUT-0001\n---\n# Outside\n", encoding="utf-8")
    (root / "real.md").write_text("---\nid: REAL-0001\n---\n# Real\n", encoding="utf-8")
    os.symlink(outside, root / "escaped.md")
    ids = {ko.id for ko in load_corpus(root).objects}
    assert ids == {"REAL-0001"}


# --- Uniform CLI failure envelope ----------------------------------------------


class _Args:
    def __init__(self, json_flag=False):
        self.json = json_flag


def test_fail_uniformly_maps_exception_types(capsys):
    assert _fail_uniformly(_Args(), FileNotFoundError("x")) == ExitCode.NOT_FOUND
    assert _fail_uniformly(_Args(), ValueError("x")) == ExitCode.CONFIG_OR_ARG_ERROR
    assert _fail_uniformly(_Args(), RuntimeError("x")) == ExitCode.VALIDATION_ERROR
    assert _fail_uniformly(_Args(), FileExistsError("x")) == ExitCode.VALIDATION_ERROR
    capsys.readouterr()
    code = _fail_uniformly(_Args(json_flag=True), RuntimeError("boom"))
    out = capsys.readouterr().out
    assert code == ExitCode.VALIDATION_ERROR
    payload = json.loads(out)
    assert payload["status"] == "error"
    assert payload["error_type"] == "RuntimeError"


def test_query_missing_registry_dir_is_clean_not_found(tmp_path, capsys):
    corpus_dir = tmp_path / "c"
    corpus_dir.mkdir()
    rc = main(
        ["--json", "query", "x", "--corpus-root", str(corpus_dir), "--registry-dir", str(tmp_path / "nope")]
    )
    out = capsys.readouterr().out
    assert rc == ExitCode.NOT_FOUND
    assert json.loads(out)["status"] == "error"


# --- validate --corpus-root is honored -----------------------------------------


def test_validate_honors_corpus_root(tmp_path, capsys):
    corpus_a = tmp_path / "a"
    corpus_b = tmp_path / "b"
    for root in (corpus_a, corpus_b):
        root.mkdir()
    note = """---
id: ENG-CON-SRC-2024
title: Source note
schema_version: 3.8.10
scope: engineering
taxonomy_path: 01. Domain & System Architecture
taxonomy_id: TX-ENG-01
object_type: Concept
domain: computer_science
evidence: observed
verification: self_verified
authority: canonical
consensus: accepted
source_type: internal_document
source_refs:
- SRC-TEST
author: human:tester
last_modified: '2026-09-01'
next_review: '2027-09-01'
confidence: 0.9
status: established
relations:
- type: RELATES_TO
  target: ENG-CON-DST-2024
---
# Source
body
"""
    (corpus_a / "src.md").write_text(note, encoding="utf-8")
    (corpus_b / "src.md").write_text(note, encoding="utf-8")
    (corpus_b / "dst.md").write_text(
        note.replace("ENG-CON-SRC-2024", "ENG-CON-DST-2024").replace(
            "  target: ENG-CON-DST-2024", "  target: ENG-CON-SRC-2024"
        ),
        encoding="utf-8",
    )

    # Without override: corpus = parent dir of the file (corpus_a, no target) -> E009
    def _codes(out: str) -> set:
        payload = json.loads(out)
        return {f["code"] for f in payload.get("errors", []) + payload.get("warnings", [])}

    rc_a = main(["validate", str(corpus_a / "src.md"), "--json"])
    codes_a = _codes(capsys.readouterr().out)
    assert "E009" in codes_a
    assert rc_a == ExitCode.VALIDATION_ERROR
    assert rc_a == ExitCode.VALIDATION_ERROR
    assert rc_a == ExitCode.VALIDATION_ERROR

    # With override to corpus_b: target exists -> no E009 for the file
    rc_b = main(["validate", str(corpus_b / "src.md"), "--corpus-root", str(corpus_b), "--json"])
    codes_b = _codes(capsys.readouterr().out)
    assert "E009" not in codes_b
    assert rc_b in (ExitCode.SUCCESS, ExitCode.VALIDATION_ERROR)


# --- rename: graph wiring, rollback, slug fallback ------------------------------


def _rename_workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    shutil.copytree("schemas", ws / "schemas")
    corpus = ws / "corpus"
    src = Path("fixtures/canonical/engineering/01_domain_system_architecture")
    (corpus / "engineering/01_domain_system_architecture").mkdir(parents=True)
    for name in ("ENG-CMP-PARSER-0001.md", "ENG-FET-LINTER-0001.md"):
        shutil.copy(src / name, corpus / "engineering/01_domain_system_architecture" / name)
    return ws


def test_rename_updates_graph_and_backlinks(tmp_path):
    from trashheap.rename import rename_entity

    ws = _rename_workspace(tmp_path)
    corpus = ws / "corpus"
    graph_dir = corpus / ".cache"
    graph_dir.mkdir()
    graph_file = graph_dir / "graph.json"
    graph_file.write_text(
        json.dumps(
            {
                "nodes": {"ENG-CMP-PARSER-0001": {"id": "ENG-CMP-PARSER-0001"}},
                "adjacency": {
                    "ENG-CMP-PARSER-0001": [{"type": "PART_OF", "target": "ENG-FET-LINTER-0001"}]
                },
            }
        ),
        encoding="utf-8",
    )

    res = rename_entity(
        corpus,
        "ENG-CMP-PARSER-0001",
        "ENG-CMP-PARSER-0002",
        graph_path=graph_file,
    )
    assert res.graph_updated is True
    assert res.graph_error is None
    graph = json.loads(graph_file.read_text(encoding="utf-8"))
    assert "ENG-CMP-PARSER-0002" in graph["nodes"]
    assert "ENG-CMP-PARSER-0002" in graph["adjacency"]
    renamed = corpus / "engineering/01_domain_system_architecture/ENG-CMP-PARSER-0002.md"
    assert renamed.exists()
    fm = yaml.safe_load(renamed.read_text(encoding="utf-8").split("---", 2)[1])
    assert fm["id"] == "ENG-CMP-PARSER-0002"
    assert "ENG-CMP-PARSER-0001" in fm["aliases"]


def test_rename_rolls_back_on_midway_failure(tmp_path):
    from trashheap import rename as rename_mod

    ws = _rename_workspace(tmp_path)
    corpus = ws / "corpus"
    linter_file = corpus / "engineering/01_domain_system_architecture/ENG-FET-LINTER-0001.md"
    linter_file.write_text(
        linter_file.read_text(encoding="utf-8") + "\nBacklink: [[ENG-CMP-PARSER-0001]].\n",
        encoding="utf-8",
    )
    before = linter_file.read_text(encoding="utf-8")

    real_write = rename_mod.atomic_write
    calls = {"n": 0}

    def flaky(path, content):
        calls["n"] += 1
        if calls["n"] >= 2:
            raise OSError("simulated mid-propagation crash")
        real_write(path, content)

    with patch.object(rename_mod, "atomic_write", side_effect=flaky):
        with pytest.raises(OSError):
            rename_mod.rename_entity(corpus, "ENG-CMP-PARSER-0001", "ENG-CMP-PARSER-0003")

    assert linter_file.read_text(encoding="utf-8") == before, "rollback must restore referencing file"
    old = corpus / "engineering/01_domain_system_architecture/ENG-CMP-PARSER-0001.md"
    assert old.exists(), "rollback must restore the original target file"
    assert not (
        corpus / "engineering/01_domain_system_architecture/ENG-CMP-PARSER-0003.md"
    ).exists()


# --- REVIEW-011: pre-score surfaces in review show -----------------------------


def test_review_show_includes_pre_score(tmp_path, capsys):
    from trashheap.promotion import create_candidate_proposal

    ws = tmp_path / "ws"
    (ws / "staging" / "proposals").mkdir(parents=True)
    (ws / "staging" / "transactions" / "locks").mkdir(parents=True)
    (ws / "engineering" / "01_domain_system_architecture").mkdir(parents=True)
    create_candidate_proposal(candidate_id="CAND-PRESCORE", workspace_root=ws)

    rc = main(["review", "show", "CAND-PRESCORE", "--workspace-root", str(ws), "--json"])
    out = capsys.readouterr().out
    assert rc == ExitCode.SUCCESS
    payload = json.loads(out)
    assert "pre_score" in payload
    assert payload["pre_score"]["flag"] in {
        "PRE_SCORE_FAILED",
        "PRE_SCORE_PASSED",
        "PRE_SCORE_UNAVAILABLE",
    }


def test_pre_score_delegates_to_rcva():
    from trashheap.promotion.pre_score import span_entailment_score

    assert span_entailment_score("alpha beta", "alpha gamma") == entailment_score(
        "alpha beta", "alpha gamma"
    )


# --- GRAPH-004: degree cap blocks promotion ------------------------------------


def test_promotion_blocks_on_degree_cap(tmp_path):
    from trashheap.promotion import (
        approve_candidate,
        create_candidate_proposal,
        promote_candidate,
    )
    from trashheap.promotion.exceptions import ValidationRollbackError

    ws = tmp_path / "ws"
    (ws / "staging" / "proposals").mkdir(parents=True)
    (ws / "staging" / "transactions" / "locks").mkdir(parents=True)
    (ws / "engineering" / "01_domain_system_architecture").mkdir(parents=True)

    relations = [
        {"type": "RELATES_TO", "target": f"ENG-CON-SOFT-{i:04d}", "soft_link": True}
        for i in range(21)
    ]
    create_candidate_proposal(
        candidate_id="CAND-DEGREE",
        workspace_root=ws,
        frontmatter_overrides={"relations": relations},
    )
    approve_candidate("CAND-DEGREE", "human:reviewer", "ok", ws)
    with pytest.raises(ValidationRollbackError) as exc:
        promote_candidate("CAND-DEGREE", ws)
    assert "W015" in str(exc.value)


# --- VAL-014: runaway ring semantics -------------------------------------------


def test_runaway_ring_trips_on_alternating_loop():
    from trashheap.runaway import RunawayLoopError, RunawayLoopGuard

    guard = RunawayLoopGuard(max_identical_signatures=5)
    with pytest.raises(RunawayLoopError):
        for i in range(30):
            guard.observe("tool" if i % 2 == 0 else "other", {"k": "v"})


# --- Vector cache reuse ----------------------------------------------------------


def test_query_uses_persisted_vector_cache(tmp_path, capsys):
    corpus_dir = tmp_path / "corpus"
    shutil.copytree("fixtures/canonical", corpus_dir)
    rc = main(["rebuild", "--corpus-root", str(corpus_dir), "--vector", "--json"])
    assert rc == ExitCode.SUCCESS
    capsys.readouterr()
    assert (corpus_dir / ".cache" / "vector_index.json").exists()

    from trashheap.vector import VectorIndex

    with patch.object(VectorIndex, "build", side_effect=AssertionError("must not re-embed")):
        rc = main(["query", "parser", "--corpus-root", str(corpus_dir), "--vector"])
    assert rc == ExitCode.SUCCESS
    bundle = json.loads(capsys.readouterr().out)
    assert "vector" in bundle["modalities_available"]


# --- discover literature: clean failures, no INTERNAL_ERROR crash ----------------


def test_literature_missing_dir_is_not_found(tmp_path, capsys):
    rc = main(
        [
            "discover",
            "literature",
            "--concept-a",
            "MESH_D011928",
            "--concept-c",
            "MESH_D005395",
            "--csr-dir",
            str(tmp_path / "absent"),
        ]
    )
    captured = capsys.readouterr()
    assert rc == ExitCode.NOT_FOUND
    assert "Traceback" not in captured.err


def test_literature_internal_error_is_clean(tmp_path, capsys):
    pytest.importorskip("duckdb")
    csr_dir = tmp_path / "csr"
    csr_dir.mkdir()
    rc = main(
        [
            "discover",
            "literature",
            "--concept-a",
            "MESH_D011928",
            "--concept-c",
            "MESH_D005395",
            "--csr-dir",
            str(csr_dir),
        ]
    )
    captured = capsys.readouterr()
    assert rc == ExitCode.NOT_FOUND
    assert "Traceback" not in captured.err
    assert "INTERNAL_ERROR" not in captured.err
    assert "AttributeError" not in captured.err


def test_literature_top_k_validation(tmp_path, capsys):
    csr_dir = tmp_path / "csr"
    csr_dir.mkdir()
    rc = main(
        [
            "discover",
            "literature",
            "--concept-a",
            "A",
            "--concept-c",
            "C",
            "--csr-dir",
            str(csr_dir),
            "--top-k",
            "0",
        ]
    )
    assert rc == ExitCode.CONFIG_OR_ARG_ERROR
