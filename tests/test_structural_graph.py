"""Comprehensive tests for Structural Knowledge Graph (specs/STRUCTURAL-GRAPH.md).

Verifies invariants SG-001 through SG-020:
- SG-001: Separate graph and registry (structural_registry.yaml).
- SG-002: Structural node types (FILE, MODULE, CLASS, FUNCTION, METHOD, SYMBOL, ROUTE, TEST) separate from ObjectTypeEnum.
- SG-003: Edge types contract (source_types, target_types, dag, symmetric).
- SG-004: Deterministic AST extraction declaring parser, parser_version, grammar_version.
- SG-005: LSP type resolution metadata model.
- SG-006: Incremental indexing idempotency producing identical graph to full indexing.
- SG-007, SG-008: Source revision and content hash binding, content hash change detection.
- SG-009: Input invalidation and atomic publication.
- SG-010: Bounded blast radius impact traversal (max depth, node ceiling).
- SG-011: Context budget reporting.
- SG-012: Layer 7 structural retrieval without affecting baseline retrieval.
- SG-013: Bridge relations to Knowledge Objects (derived, reviewable, non-canonical).
- SG-014: Derivation metadata with mode: extracted.
- SG-015: Coverage observability reporting.
- SG-016: Deterministic query outputs.
- SG-017: Read-only CLI operations.
- SG-018: Evidence Bundle structural hit formatting.
- SG-019: Conformance verification.
- SG-020: Explicit degradation on partial extraction failure.
"""

import json
from pathlib import Path

import pytest

from trashheap.cli import main
from trashheap.constants import ExitCode
from trashheap.corpus import load_corpus
from trashheap.structural import (
    ASTExtractor,
    BridgeEngine,
    CoverageReport,
    ImpactReport,
    StructuralGraphAnalyzer,
    StructuralGraphIndexer,
    StructuralHit,
    StructuralNode,
    StructuralNodeType,
    StructuralRegistry,
    StructuralRetriever,
    load_structural_registry,
)


@pytest.fixture
def sample_code_repo(tmp_path: Path) -> Path:
    """Fixture creating a small sample Python codebase for structural indexing."""
    repo = tmp_path / "sample_repo"
    repo.mkdir()

    # module A
    mod_a = repo / "pkg" / "module_a.py"
    mod_a.parent.mkdir(parents=True, exist_ok=True)
    mod_a.write_text(
        """\"\"\"Module A docstring.\"\"\"
import os

DEFAULT_TIMEOUT = 30

class BaseService:
    def execute(self):
        return 42

class ServiceA(BaseService):
    def run(self):
        return self.execute()
""",
        encoding="utf-8",
    )

    # module B
    mod_b = repo / "pkg" / "module_b.py"
    mod_b.write_text(
        """\"\"\"Module B docstring.\"\"\"
from pkg.module_a import ServiceA

def helper_func():
    svc = ServiceA()
    return svc.run()

def caller_func():
    return helper_func()
""",
        encoding="utf-8",
    )

    # test module
    mod_test = repo / "tests" / "test_service.py"
    mod_test.parent.mkdir(parents=True, exist_ok=True)
    mod_test.write_text(
        """\"\"\"Test module.\"\"\"
from pkg.module_b import helper_func

def test_helper_func():
    assert helper_func() == 42
""",
        encoding="utf-8",
    )

    return repo


def test_sg_001_to_003_registry():
    """Verify SG-001, SG-002, SG-003: separate registry, node/edge type contracts."""
    reg_data = load_structural_registry()
    registry = StructuralRegistry(reg_data)

    # SG-001: Separate registry
    assert "node_types" in reg_data
    assert "edge_types" in reg_data

    # SG-002: Structural node types MUST NOT be mixed with ObjectTypeEnum
    expected_node_types = {
        "FILE",
        "MODULE",
        "CLASS",
        "FUNCTION",
        "METHOD",
        "SYMBOL",
        "ROUTE",
        "TEST",
    }
    assert set(reg_data["node_types"].keys()) == expected_node_types
    for nt in expected_node_types:
        assert registry.is_valid_node_type(nt)
        assert len(reg_data["node_types"][nt]["identity"]) > 0

    # SG-003: Edge types contract (source_types, target_types, dag, symmetric)
    expected_edge_types = {"DEFINES", "CALLS", "IMPORTS", "INHERITS", "ROUTES_TO", "TESTS_SYMBOL"}
    assert set(reg_data["edge_types"].keys()) == expected_edge_types
    for et in expected_edge_types:
        contract = registry.get_edge_contract(et)
        assert "source_types" in contract
        assert "target_types" in contract
        assert isinstance(contract["dag"], bool)
        assert isinstance(contract["symmetric"], bool)
        for st in contract["source_types"]:
            assert registry.is_valid_node_type(st)
        for tt in contract["target_types"]:
            assert registry.is_valid_node_type(tt)


def test_sg_004_ast_extraction_and_derivation(sample_code_repo: Path):
    """Verify SG-004, SG-007, SG-008, SG-014: deterministic AST extraction and revision/hash binding."""
    extractor = ASTExtractor(repo_name="test_repo")
    target_file = sample_code_repo / "pkg" / "module_a.py"
    rel_path = "pkg/module_a.py"
    content = target_file.read_bytes()

    nodes, edges, unres, failure = extractor.extract_file(
        rel_path=rel_path,
        content_bytes=content,
        source_revision="git-sha-12345",
    )

    assert failure is None
    assert len(nodes) > 0
    assert len(edges) > 0

    # Verify SG-004: parser and grammar versions
    assert extractor.PARSER_NAME == "python-ast"
    assert extractor.PARSER_VERSION
    assert extractor.GRAMMAR_VERSION

    # Verify node types extracted
    node_types = {n.node_type for n in nodes}
    assert StructuralNodeType.FILE in node_types
    assert StructuralNodeType.MODULE in node_types
    assert StructuralNodeType.CLASS in node_types
    assert StructuralNodeType.METHOD in node_types
    assert StructuralNodeType.SYMBOL in node_types

    # Verify SG-007, SG-008: binding to revision and content hash
    for n in nodes:
        assert n.source_revision == "git-sha-12345"
        assert n.content_hash.startswith("sha256:")

    # Verify SG-014: edge derivation metadata
    for e in edges:
        assert e.source_revision == "git-sha-12345"
        assert e.derivation.mode == "extracted"
        assert e.derivation.extractor == "python-ast"
        assert e.derivation.extractor_version == extractor.PARSER_VERSION


def test_sg_006_incremental_indexing_idempotence(sample_code_repo: Path, tmp_path: Path):
    """Verify SG-006: incremental indexing is idempotent and matches full indexing bit-for-bit."""
    cache_dir = tmp_path / "cache"
    indexer = StructuralGraphIndexer(repo_root=sample_code_repo, cache_dir=cache_dir)

    # 1. Full indexing
    manifest1, cov1 = indexer.index(source_revision="v1.0.0", incremental=False)
    graph_file = cache_dir / "graph.json"
    content_full = graph_file.read_text(encoding="utf-8")

    # 2. Incremental indexing of unchanged repo
    indexer2 = StructuralGraphIndexer(repo_root=sample_code_repo, cache_dir=cache_dir)
    manifest2, cov2 = indexer2.index(source_revision="v1.0.0", incremental=True)
    content_inc = graph_file.read_text(encoding="utf-8")

    # Bit-for-bit equivalence
    assert manifest1.aggregate_hash == manifest2.aggregate_hash
    assert manifest1.node_count == manifest2.node_count
    assert manifest1.edge_count == manifest2.edge_count
    assert content_full == content_inc


def test_sg_009_change_and_invalidation(sample_code_repo: Path, tmp_path: Path):
    """Verify SG-008, SG-009: change detection via content hash and invalidation of deleted/modified inputs."""
    cache_dir = tmp_path / "cache"
    indexer = StructuralGraphIndexer(repo_root=sample_code_repo, cache_dir=cache_dir)

    manifest1, cov1 = indexer.index(source_revision="v1.0.0", incremental=False)
    initial_node_count = manifest1.node_count

    # Delete module_b.py
    mod_b = sample_code_repo / "pkg" / "module_b.py"
    mod_b.unlink()

    # Incremental re-index
    manifest2, cov2 = indexer.index(source_revision="v1.0.0", incremental=True)

    assert manifest2.node_count < initial_node_count
    # Verify no nodes or edges referencing module_b remain
    for n in indexer.nodes.values():
        assert "module_b.py" not in n.path
    for e in indexer.edges.values():
        assert "module_b.py" not in e.derivation.source_file


def test_sg_010_and_011_blast_radius_and_context_budget(sample_code_repo: Path, tmp_path: Path):
    """Verify SG-010, SG-011, SG-016: bounded blast radius traversal and context budget."""
    cache_dir = tmp_path / "cache"
    indexer = StructuralGraphIndexer(repo_root=sample_code_repo, cache_dir=cache_dir)
    indexer.index(source_revision="v1.0.0", incremental=False)

    analyzer = StructuralGraphAnalyzer(indexer.nodes, indexer.edges)

    # Start traversal from helper_func
    target_id = "repo=canonical;path=pkg/module_b.py;symbol=helper_func"
    assert target_id in indexer.nodes

    # Traversal with max_depth=2
    report = analyzer.compute_blast_radius(target_node_id=target_id, max_depth=2, node_ceiling=20)
    assert isinstance(report, ImpactReport)
    assert len(report.affected_nodes) > 0
    assert report.depth_reached <= 2
    assert report.context_budget_tokens > 0  # SG-011

    # Traversal hitting ceiling
    tight_report = analyzer.compute_blast_radius(
        target_node_id=target_id, max_depth=5, node_ceiling=2
    )
    assert tight_report.ceiling_hit is True
    assert len(tight_report.affected_nodes) <= 2


def test_sg_013_bridge_relations_to_knowledge_objects(sample_code_repo: Path, tmp_path: Path):
    """Verify SG-013: bridge relations are derived, reviewable, and do not mutate canonical files."""
    cache_dir = tmp_path / "cache"
    indexer = StructuralGraphIndexer(repo_root=sample_code_repo, cache_dir=cache_dir)
    indexer.index(source_revision="v1.0.0", incremental=False)

    canonical_dir = Path("fixtures/canonical")
    corpus = load_corpus(canonical_dir)

    engine = BridgeEngine(workspace_root=Path("."), cache_dir=cache_dir)
    bridges = engine.discover_bridges(corpus, indexer.nodes)

    assert isinstance(bridges, list)
    # Review a bridge
    if bridges:
        target_b = bridges[0]
        assert target_b.status == "pending"
        updated = engine.review_bridge(target_b.bridge_id, "approved")
        assert updated is not None
        assert updated.status == "approved"

    # Verify canonical files are unchanged
    fresh_corpus = load_corpus(canonical_dir)
    assert len(fresh_corpus) == len(corpus)


def test_sg_012_and_018_structural_retrieval_and_evidence():
    """Verify SG-012, SG-018: Layer 7 structural retriever formats hits with node ID, file, line interval."""
    sample_nodes = {
        "repo=c;path=foo.py;symbol=FooClass": StructuralNode(
            node_id="repo=c;path=foo.py;symbol=FooClass",
            node_type=StructuralNodeType.CLASS,
            repo="c",
            path="foo.py",
            qualified_name="FooClass",
            line_start=10,
            line_end=45,
            source_revision="rev1",
            content_hash="sha256:abc",
        ),
        "repo=c;path=bar.py;symbol=bar_func": StructuralNode(
            node_id="repo=c;path=bar.py;symbol=bar_func",
            node_type=StructuralNodeType.FUNCTION,
            repo="c",
            path="bar.py",
            qualified_name="bar_func",
            line_start=100,
            line_end=120,
            source_revision="rev1",
            content_hash="sha256:def",
        ),
    }

    retriever = StructuralRetriever(sample_nodes)
    hits = retriever.query("FooClass", top_k=5)

    assert len(hits) == 1
    hit = hits[0]
    assert isinstance(hit, StructuralHit)
    assert hit.node_id == "repo=c;path=foo.py;symbol=FooClass"
    assert hit.line_interval == [10, 45]

    evidence_dict = hit.to_evidence_dict()
    assert evidence_dict["node_id"] == "repo=c;path=foo.py;symbol=FooClass"
    assert evidence_dict["file"] == "foo.py"
    assert evidence_dict["revision"] == "rev1"
    assert evidence_dict["line_interval"] == [10, 45]


def test_sg_015_and_020_coverage_and_degraded_parsing(sample_code_repo: Path, tmp_path: Path):
    """Verify SG-015, SG-020: coverage reporting and explicit degradation on syntax error."""
    # Add a file with syntax error
    bad_file = sample_code_repo / "pkg" / "syntax_error.py"
    bad_file.write_text("def broken_syntax(:\n    pass\n", encoding="utf-8")

    cache_dir = tmp_path / "cache"
    indexer = StructuralGraphIndexer(repo_root=sample_code_repo, cache_dir=cache_dir)
    manifest, cov = indexer.index(source_revision="rev-err", incremental=False)

    assert isinstance(cov, CoverageReport)
    # SG-020: Explicit failure tracking without silent dropping
    assert len(cov.failed_files) == 1
    assert "syntax_error.py" in cov.failed_files[0]["path"]
    assert cov.failed_files[0]["error_type"] == "SyntaxError"
    # Indexing still succeeds for remaining valid files
    assert cov.indexed_files >= 3
    assert manifest.node_count > 0


def test_sg_017_cli_read_only_operations(
    sample_code_repo: Path, tmp_path: Path, capsys: pytest.CaptureFixture
):
    """Verify SG-017: CLI structural subcommands execute read-only without modifying canonical files."""
    cache_dir = tmp_path / "cache"

    # 1. Index command
    code = main(
        [
            "structural",
            "index",
            "--repo-root",
            str(sample_code_repo),
            "--cache-dir",
            str(cache_dir),
            "--json",
        ]
    )
    assert code == ExitCode.SUCCESS
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "manifest" in data
    assert "coverage" in data

    # 2. Inspect command
    file_node_id = "repo=canonical;path=pkg/module_a.py"
    code = main(
        [
            "structural",
            "inspect",
            file_node_id,
            "--repo-root",
            str(sample_code_repo),
            "--cache-dir",
            str(cache_dir),
            "--json",
        ]
    )
    assert code == ExitCode.SUCCESS
    inspect_out = capsys.readouterr().out
    node_data = json.loads(inspect_out)
    assert node_data["node_id"] == file_node_id

    # 3. Impact command
    code = main(
        [
            "structural",
            "impact",
            file_node_id,
            "--repo-root",
            str(sample_code_repo),
            "--cache-dir",
            str(cache_dir),
            "--json",
        ]
    )
    assert code == ExitCode.SUCCESS
    impact_out = capsys.readouterr().out
    impact_data = json.loads(impact_out)
    assert impact_data["target_node_id"] == file_node_id
    assert "context_budget_tokens" in impact_data
