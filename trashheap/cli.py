"""Command-line interface for The Omniscient Trash Heap (trashheap).

Implements non-interactive, scriptable subcommands with deterministic exit codes (ExitCode 0..4)
and standardized machine-readable --json outputs.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from trashheap.bundle import BundleSelector, build_bundle, import_bundle
from trashheap.constants import VERSION, ExitCode
from trashheap.corpus import load_corpus
from trashheap.graph import (
    DiscoveryEngine,
    DiscoveryLifecycleManager,
    GraphAnalyzer,
    build_and_publish_manifest,
)
from trashheap.ingest import (
    AccessDeniedError,
    IntegrityConflictError,
    QuarantineError,
    SourceValidationError,
    intake_source,
    stage_lint,
)
from trashheap.linter import Finding, Linter
from trashheap.operations import (
    TTLReaper,
    calculate_knowledge_debt,
    detect_spec_drift,
    generate_conformance_matrix,
    inspect_environment,
    run_benchmark,
)
from trashheap.promotion import (
    ApprovalBindingError,
    ConflictError,
    ValidationRollbackError,
    approve_candidate,
    get_journal,
    list_candidates,
    load_candidate,
    promote_candidate,
    reject_candidate,
)
from trashheap.rebuild import rebuild_indexes
from trashheap.registry.loader import RegistryLoadError, load_registries
from trashheap.registry.validator import RegistryFinding, validate_cross_registries
from trashheap.rename import rename_entity
from trashheap.retrieval import HybridRetriever
from trashheap.skills import check_agent_skills, write_agent_skills
from trashheap.structural import (
    BridgeEngine,
    StructuralGraphAnalyzer,
    StructuralGraphIndexer,
)


def build_parser() -> argparse.ArgumentParser:
    """Build root CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="trashheap",
        description="The Omniscient Trash Heap: deterministic knowledge compiler and verification system",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"trashheap {VERSION}",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # 0. init / new
    init_parser = subparsers.add_parser(
        "init",
        aliases=["new"],
        help="Initialize and scaffold a new Knowledge Library wiki instance",
    )
    init_parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target directory to initialize wiki in (default: current directory)",
    )
    init_parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Human-readable name of the knowledge library",
    )
    init_parser.add_argument(
        "--scope",
        type=str,
        default="all",
        choices=["personal", "engineering", "all"],
        help="Scopes to scaffold (default: all)",
    )
    init_parser.add_argument(
        "--author",
        type=str,
        default="human:owner",
        help="Default author/reviewer actor identifier (default: human:owner)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite or initialize even if directory is not empty",
    )
    init_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output",
    )

    # 1. check-registries
    check_reg_parser = subparsers.add_parser(
        "check-registries",
        help="Validate all 10 YAML registry schemas and cross-registry consistency",
    )
    check_reg_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )
    check_reg_parser.add_argument(
        "--registry-dir", type=str, default=None, help="Custom path to schemas/registry"
    )
    check_reg_parser.add_argument(
        "--repo-root", type=str, default=None, help="Root repository directory"
    )

    # 2. lint
    lint_parser = subparsers.add_parser(
        "lint",
        help="Run multi-layered validation (Layers 1–5, E001–E051, W001–W015) across the corpus",
    )
    lint_parser.add_argument(
        "path", nargs="?", default="fixtures/canonical", help="Path to corpus or file to lint"
    )
    lint_parser.add_argument(
        "--warnings-as-errors", action="store_true", help="Treat warnings as errors"
    )
    lint_parser.add_argument(
        "--strict", action="store_true", help="Strict mode (elevates warnings)"
    )
    lint_parser.add_argument(
        "--scope", choices=["personal", "engineering"], default=None, help="Filter scope"
    )
    lint_parser.add_argument(
        "--now", type=str, default=None, help="Reference date (YYYY-MM-DD) for temporal checks"
    )
    lint_parser.add_argument(
        "--registry-dir", type=str, default=None, help="Custom path to schemas/registry"
    )
    lint_parser.add_argument(
        "--no-check-skills", action="store_true", help="Skip agent skills drift check"
    )
    lint_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )

    # 3. validate
    val_parser = subparsers.add_parser(
        "validate",
        help="Validate frontmatter and integrity for a single file within the full corpus context",
    )
    val_parser.add_argument("file", type=str, help="Path to Markdown file to validate")
    val_parser.add_argument("--corpus-root", type=str, default=None, help="Corpus root directory")
    val_parser.add_argument(
        "--registry-dir", type=str, default=None, help="Custom path to schemas/registry"
    )
    val_parser.add_argument("--now", type=str, default=None, help="Reference date (YYYY-MM-DD)")
    val_parser.add_argument("--strict", action="store_true", help="Strict mode")
    val_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    # 4. rename
    rename_parser = subparsers.add_parser(
        "rename",
        help="Atomically rename an entity and propagate all backlinks and graph references",
    )
    rename_parser.add_argument("--old-id", required=True, help="Existing entity ID")
    rename_parser.add_argument("--new-id", required=True, help="New target entity ID")
    rename_parser.add_argument(
        "--corpus-root", type=str, default="fixtures/canonical", help="Corpus root directory"
    )
    rename_parser.add_argument(
        "--dry-run", action="store_true", help="Simulate without modifying files"
    )
    rename_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )

    # 5. query
    query_parser = subparsers.add_parser(
        "query",
        help="Execute hybrid RRF retrieval and return an evidence bundle",
    )
    query_parser.add_argument("prompt", type=str, help="Query text or node ID")
    query_parser.add_argument(
        "--corpus-root", type=str, default="fixtures/canonical", help="Corpus root directory"
    )
    query_parser.add_argument(
        "--registry-dir", type=str, default=None, help="Custom path to schemas/registry"
    )
    query_parser.add_argument(
        "--scope", choices=["personal", "engineering"], default=None, help="Scope filter"
    )
    query_parser.add_argument("--seed-top-k", type=int, default=10, help="Number of seeds")
    query_parser.add_argument(
        "--max-depth", type=int, default=2, help="Max BFS graph expansion depth"
    )
    query_parser.add_argument(
        "--max-results", type=int, default=20, help="Max results in evidence bundle"
    )
    query_parser.add_argument(
        "--min-confidence", type=float, default=0.0, help="Min confidence knob"
    )
    query_parser.add_argument("--min-relevance", type=float, default=0.0, help="Min relevance knob")
    query_parser.add_argument(
        "--json", action="store_true", default=True, help="Emit machine-readable JSON output"
    )
    query_parser.add_argument(
        "--vector",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable opt-in vector retrieval (Plan 90)",
    )
    query_parser.add_argument(
        "--include-drafts",
        action="store_true",
        default=False,
        help="Include draft objects in query results",
    )
    query_parser.add_argument(
        "--include-deprecated",
        action="store_true",
        default=False,
        help="Include deprecated objects in query results",
    )
    query_parser.add_argument(
        "--include-body",
        action="store_true",
        default=False,
        help="Include full body text in evidence bundle",
    )
    query_parser.add_argument(
        "--graph-enhanced",
        action="store_true",
        default=False,
        help="Enable opt-in graph-enhanced retrieval (Plan 91 / GRAPH-RETRIEVAL.md)",
    )

    # show (display full content of a Knowledge Object)
    show_parser = subparsers.add_parser(
        "show",
        help="Display the full content of a Knowledge Object by node ID or path",
    )
    show_parser.add_argument("target", type=str, help="Node ID or file path")
    show_parser.add_argument(
        "--corpus-root", type=str, default="fixtures/canonical", help="Corpus root directory"
    )

    # 6. rebuild
    rebuild_parser = subparsers.add_parser(
        "rebuild",
        help="Idempotently reconstruct disposable caches and graph projections from Markdown notes",
    )
    rebuild_parser.add_argument(
        "--corpus-root", type=str, default="fixtures/canonical", help="Corpus root directory"
    )
    rebuild_parser.add_argument(
        "--output-dir", type=str, default=None, help="Output directory for rebuilt projections"
    )
    rebuild_parser.add_argument(
        "--registry-dir", type=str, default=None, help="Custom path to schemas/registry"
    )
    rebuild_parser.add_argument(
        "--vector", action="store_true", help="Also rebuild offline vector index (Plan 90)"
    )
    rebuild_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )

    # 7. generate-skills
    skills_parser = subparsers.add_parser(
        "generate-skills",
        help="Generate or verify .agents/skills/trashheap/SKILL.md (AGENT-SKILLS.md §4, E050)",
    )
    skills_parser.add_argument(
        "--check", action="store_true", help="Verify that SKILL.md is identical bit-for-bit"
    )
    skills_parser.add_argument(
        "--repo-root", type=str, default=None, help="Repository root directory"
    )
    skills_parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Install skill globally to ~/.agents/skills/trashheap/SKILL.md",
    )
    skills_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )

    # 8. stage-lint
    stage_parser = subparsers.add_parser(
        "stage-lint",
        help="Scan staging/ area and report candidate ingestion objects",
    )
    stage_parser.add_argument(
        "--staging-dir", type=str, default="staging", help="Path to staging directory"
    )
    stage_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )

    # 9. ingest
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Intake a raw source file into staging with SHA-256 calculation",
    )
    ingest_parser.add_argument("file", type=str, help="Path to source file to ingest")
    ingest_parser.add_argument(
        "--source-type", type=str, default="document", help="Source type classification"
    )
    ingest_parser.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )
    ingest_parser.add_argument(
        "--staging-dir", type=str, default="staging", help="Target staging directory"
    )
    ingest_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )

    # 10. review
    review_parser = subparsers.add_parser(
        "review",
        help="Review and governance operations for candidate proposals (specs/REVIEW-PROMOTION.md)",
    )
    review_subs = review_parser.add_subparsers(dest="review_action", required=True)

    # review list
    r_list = review_subs.add_parser("list", help="List candidate proposals")
    r_list.add_argument("--scope", type=str, default=None, choices=["personal", "engineering"])
    r_list.add_argument("--status", type=str, default=None, help="Filter by candidate state")
    r_list.add_argument("--workspace-root", type=str, default=".", help="Workspace root directory")
    r_list.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    # review show
    r_show = review_subs.add_parser("show", help="Show candidate proposal details")
    r_show.add_argument("candidate_id", type=str, help="Candidate proposal ID")
    r_show.add_argument("--workspace-root", type=str, default=".", help="Workspace root directory")
    r_show.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    # review approve
    r_approve = review_subs.add_parser("approve", help="Approve candidate proposal (REVIEW-002)")
    r_approve.add_argument("candidate_id", type=str, help="Candidate proposal ID")
    r_approve.add_argument(
        "--reviewer", type=str, required=True, help="Reviewer actor (e.g. human:alice)"
    )
    r_approve.add_argument(
        "--reason", type=str, default="Approved via review", help="Approval rationale"
    )
    r_approve.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )
    r_approve.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    # review reject
    r_reject = review_subs.add_parser("reject", help="Reject candidate proposal (REVIEW-009)")
    r_reject.add_argument("candidate_id", type=str, help="Candidate proposal ID")
    r_reject.add_argument("--reviewer", type=str, required=True, help="Reviewer actor")
    r_reject.add_argument("--reason", type=str, required=True, help="Rejection rationale")
    r_reject.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )
    r_reject.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    # review promote
    r_promote = review_subs.add_parser("promote", help="Promote approved candidate via DPCP (§9)")
    r_promote.add_argument("candidate_id", type=str, help="Candidate proposal ID")
    r_promote.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )
    r_promote.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    # review recover
    r_recover = review_subs.add_parser(
        "recover", help="Crash recovery for interrupted DPCP promotions (§9.2)"
    )
    r_recover.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )
    r_recover.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    # 11. promote (top-level alias for review promote)
    promote_parser = subparsers.add_parser(
        "promote",
        help="Promote approved candidate via DPCP (§9, PROMO-001..PROMO-010)",
    )
    promote_parser.add_argument("candidate_id", type=str, help="Candidate proposal ID")
    promote_parser.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )
    promote_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )

    # 12. status
    status_parser = subparsers.add_parser(
        "status",
        help="Display environment durability, dependency availability, and knowledge debt metrics",
    )
    status_parser.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )
    status_parser.add_argument(
        "--ttl-days", type=int, default=180, help="Retention TTL in days (default: 180)"
    )
    status_parser.add_argument(
        "--corpus-root",
        type=str,
        default=None,
        help="Optional corpus root directory to inspect canonical knowledge objects",
    )
    status_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )

    # 13. reap
    reap_parser = subparsers.add_parser(
        "reap",
        help="Execute deterministic staging retention reaper pass (INGEST-CORE-022, §7.3)",
    )
    reap_parser.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )
    reap_parser.add_argument(
        "--ttl-days", type=int, default=180, help="Retention TTL in days (default: 180)"
    )
    reap_parser.add_argument(
        "--grace-days",
        type=int,
        default=7,
        help="Grace period before tombstone purging (default: 7)",
    )
    reap_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )

    # 14. conformance
    conformance_parser = subparsers.add_parser(
        "conformance",
        help="Generate conformance projection or detect status dashboard drift (D90, CONFORM-001)",
    )
    conformance_parser.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )
    conformance_parser.add_argument(
        "--output",
        type=str,
        default="artifacts/conformance_matrix.yaml",
        help="Output path for matrix",
    )
    conformance_parser.add_argument(
        "--check", action="store_true", help="Run drift detector validating SPEC_STATUS.md"
    )
    conformance_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )

    # 15. benchmark
    bench_parser = subparsers.add_parser(
        "benchmark",
        help="Measure performance baseline and evaluate scale transition criteria (SCALE-001)",
    )
    bench_parser.add_argument(
        "--workspace-root", type=str, default=".", help="Workspace root directory"
    )
    bench_parser.add_argument(
        "--fixtures-dir", type=str, default=None, help="Directory containing canonical fixtures"
    )
    bench_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output"
    )
    bench_parser.add_argument(
        "--pubmed", action="store_true", help="Run PubMedQA hybrid retrieval and refusal benchmark"
    )
    bench_parser.add_argument(
        "--pubmed-sample", type=int, default=50, help="Number of PubMedQA questions to sample (default: 50)"
    )
    bench_parser.add_argument(
        "--pubmed-file", type=str, default=None, help="Custom path to PubMedQA questions JSON or PubMed XML file"
    )

    # 16. bundle
    bundle_parser = subparsers.add_parser(
        "bundle",
        help="Materialize or import Knowledge Bundles and OKF concepts (specs/OKF-INTEROP.md)",
    )
    bundle_subs = bundle_parser.add_subparsers(dest="bundle_action", required=True)

    # bundle export
    b_export = bundle_subs.add_parser("export", help="Materialize a Knowledge Bundle")
    b_export.add_argument("--selector", type=str, default=None, help="Path to bundle selector YAML")
    b_export.add_argument("--bundle-id", type=str, default=None, help="Bundle ID")
    b_export.add_argument("--title", type=str, default=None, help="Bundle Title")
    b_export.add_argument("--scope", type=str, default=None, help="Scope filter")
    b_export.add_argument("--output-dir", type=str, required=True, help="Target output directory")
    b_export.add_argument("--corpus-root", type=str, default="fixtures/canonical", help="Corpus root")
    b_export.add_argument("--registry-dir", type=str, default=None, help="Custom path to schemas/registry")
    b_export.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    # bundle import
    b_import = bundle_subs.add_parser("import", help="Permissively import an OKF Knowledge Bundle")
    b_import.add_argument("bundle_dir", type=str, help="Directory containing OKF bundle")
    b_import.add_argument("--target-scope", type=str, default="engineering", help="Target scope")
    b_import.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    # 17. graph
    graph_parser = subparsers.add_parser(
        "graph",
        help="Graph intelligence analysis, manifest, and derived projections (specs/GRAPH-INTELLIGENCE.md)",
    )
    graph_subs = graph_parser.add_subparsers(dest="graph_action", required=True)

    g_manifest = graph_subs.add_parser("manifest", help="Generate canonical input manifest atomically")
    g_manifest.add_argument("--workspace-root", type=str, default=".", help="Workspace root directory")
    g_manifest.add_argument("--corpus-root", type=str, default=None, help="Corpus root directory")
    g_manifest.add_argument("--output-dir", type=str, default="derived", help="Output directory")
    g_manifest.add_argument("--json", action="store_true", help="Emit JSON output")

    g_analyze = graph_subs.add_parser("analyze", help="Calculate graph metrics and derived edges")
    g_analyze.add_argument("--workspace-root", type=str, default=".", help="Workspace root directory")
    g_analyze.add_argument("--corpus-root", type=str, default=None, help="Corpus root directory")
    g_analyze.add_argument("--output-dir", type=str, default="derived/graph", help="Output directory")
    g_analyze.add_argument("--json", action="store_true", help="Emit JSON output")

    # 18. discover
    discover_parser = subparsers.add_parser(
        "discover",
        help="Discover duplicates, topological gaps, and ontological gaps (specs/DISCOVERY.md)",
    )
    discover_subs = discover_parser.add_subparsers(dest="discover_action", required=True)

    d_scan = discover_subs.add_parser("scan", help="Run discovery scans across canonical corpus")
    d_scan.add_argument("--workspace-root", type=str, default=".", help="Workspace root directory")
    d_scan.add_argument("--corpus-root", type=str, default=None, help="Corpus root directory")
    d_scan.add_argument("--discovery-dir", type=str, default="discovery", help="Discovery directory")
    d_scan.add_argument("--json", action="store_true", help="Emit JSON output")

    d_list = discover_subs.add_parser("list", help="List discovered candidates")
    d_list.add_argument("--discovery-dir", type=str, default="discovery", help="Discovery directory")
    d_list.add_argument("--status", type=str, default=None, help="Filter by status (e.g. pending, approved)")
    d_list.add_argument("--json", action="store_true", help="Emit JSON output")

    d_review = discover_subs.add_parser("review", help="Review a discovery candidate")
    d_review.add_argument("candidate_id", type=str, help="Candidate ID")
    d_review.add_argument(
        "--decision",
        type=str,
        required=True,
        choices=["approved", "rejected", "reviewed"],
        help="Review decision",
    )
    d_review.add_argument("--actor", type=str, default="operator", help="Reviewer actor identity")
    d_review.add_argument("--reason", type=str, default="Operator review", help="Review rationale")
    d_review.add_argument("--discovery-dir", type=str, default="discovery", help="Discovery directory")
    d_review.add_argument("--json", action="store_true", help="Emit JSON output")

    d_promote = discover_subs.add_parser("promote", help="Validate and promote an approved candidate")
    d_promote.add_argument("candidate_id", type=str, help="Candidate ID")
    d_promote.add_argument("--actor", type=str, default="operator", help="Promoting actor identity")
    d_promote.add_argument("--corpus-root", type=str, default=None, help="Corpus root directory")
    d_promote.add_argument("--discovery-dir", type=str, default="discovery", help="Discovery directory")
    d_promote.add_argument("--workspace-root", type=str, default=".", help="Workspace root directory")
    d_promote.add_argument("--json", action="store_true", help="Emit JSON output")

    d_sweep = discover_subs.add_parser("sweep", help="Sweep and archive expired candidates older than 90 days")
    d_sweep.add_argument("--discovery-dir", type=str, default="discovery", help="Discovery directory")
    d_sweep.add_argument("--current-date", type=str, default=None, help="Optional simulated ISO UTC date")
    d_sweep.add_argument("--json", action="store_true", help="Emit JSON output")

    # Structural commands (specs/STRUCTURAL-GRAPH.md, SG-001..SG-020)
    structural_parser = subparsers.add_parser(
        "structural", help="Structural Knowledge Graph commands (SG-001..SG-020)"
    )
    struct_subs = structural_parser.add_subparsers(dest="structural_action", required=True)

    s_index = struct_subs.add_parser("index", help="Index codebase AST into structural graph")
    s_index.add_argument("--repo-root", type=str, default=".", help="Repository root path")
    s_index.add_argument("--revision", type=str, default="HEAD", help="Source revision (git SHA or ref)")
    s_index.add_argument("--incremental", action="store_true", help="Perform incremental indexing")
    s_index.add_argument("--cache-dir", type=str, default=None, help="Cache directory")
    s_index.add_argument("--json", action="store_true", help="Emit JSON output")

    s_inspect = struct_subs.add_parser("inspect", help="Inspect a structural node by ID")
    s_inspect.add_argument("node_id", type=str, help="Structural node ID")
    s_inspect.add_argument("--repo-root", type=str, default=".", help="Repository root path")
    s_inspect.add_argument("--cache-dir", type=str, default=None, help="Cache directory")
    s_inspect.add_argument("--json", action="store_true", help="Emit JSON output")

    s_impact = struct_subs.add_parser("impact", help="Calculate blast radius impact for a structural node")
    s_impact.add_argument("node_id", type=str, help="Target structural node ID")
    s_impact.add_argument("--max-depth", type=int, default=3, help="Max traversal depth")
    s_impact.add_argument("--node-ceiling", type=int, default=50, help="Max node ceiling")
    s_impact.add_argument("--repo-root", type=str, default=".", help="Repository root path")
    s_impact.add_argument("--cache-dir", type=str, default=None, help="Cache directory")
    s_impact.add_argument("--json", action="store_true", help="Emit JSON output")

    s_bridge = struct_subs.add_parser("bridge", help="Bridge Knowledge Objects to structural nodes")
    s_bridge.add_argument("bridge_action", choices=["scan", "list", "review"], help="Bridge action")
    s_bridge.add_argument("--workspace-root", type=str, default=".", help="Workspace root")
    s_bridge.add_argument("--cache-dir", type=str, default=None, help="Cache directory")
    s_bridge.add_argument("--bridge-id", type=str, default=None, help="Bridge ID for review")
    s_bridge.add_argument("--status", type=str, default=None, help="Status for review or filter")
    s_bridge.add_argument("--json", action="store_true", help="Emit JSON output")

    # Migration commands (plans/60-OLD-WIKI-MIGRATION.md)
    migrate_parser = subparsers.add_parser(
        "migrate", help="Legacy wiki corpus migration commands (Plan 60)"
    )
    migrate_subs = migrate_parser.add_subparsers(dest="migrate_action", required=True)

    m_plan = migrate_subs.add_parser("plan", help="Dry-run migration analysis and proposal generation")
    m_plan.add_argument("--source-dir", type=str, required=True, help="Source legacy corpus directory")
    m_plan.add_argument("--target-dir", type=str, required=True, help="Target canonical corpus directory")
    m_plan.add_argument("--derived-frontmatter", action="store_true", help="Opt-in derived frontmatter mode (Rule 11, D95)")
    m_plan.add_argument("--target-scope", type=str, default=None, choices=["engineering", "personal"], help="Verified target scope")
    m_plan.add_argument("--registry-dir", type=str, default="schemas/registry", help="Registry directory")
    m_plan.add_argument("--json", action="store_true", help="Emit JSON output")

    m_exec = migrate_subs.add_parser("execute", help="Execute migration with fresh-target checks and idempotency")
    m_exec.add_argument("--source-dir", type=str, required=True, help="Source legacy corpus directory")
    m_exec.add_argument("--target-dir", type=str, required=True, help="Target canonical corpus directory")
    m_exec.add_argument("--derived-frontmatter", action="store_true", help="Opt-in derived frontmatter mode (Rule 11, D95)")
    m_exec.add_argument("--target-scope", type=str, default=None, choices=["engineering", "personal"], help="Verified target scope")
    m_exec.add_argument("--registry-dir", type=str, default="schemas/registry", help="Registry directory")
    m_exec.add_argument("--force", action="store_true", help="Force overwrite even if source changed")
    m_exec.add_argument("--json", action="store_true", help="Emit JSON output")

    # Staging commands (plans/93-OPT-IN-PARQUET-STAGING.md)
    staging_parser = subparsers.add_parser(
        "staging", help="Opt-in Parquet/DuckDB discovery staging and backend seam (Plan 93)"
    )
    staging_subs = staging_parser.add_subparsers(dest="staging_action", required=True)

    st_status = staging_subs.add_parser("status", help="Inspect staging backend status and dependencies")
    st_status.add_argument("--backend", type=str, default="parquet", choices=["baseline", "parquet"], help="Target backend to inspect")
    st_status.add_argument("--workspace-root", type=str, default=None, help="Path to workspace root")
    st_status.add_argument("--json", action="store_true", help="Emit JSON output")

    st_sync = staging_subs.add_parser("sync", help="Sync proposals from baseline staging to Parquet staging")
    st_sync.add_argument("--workspace-root", type=str, default=None, help="Path to workspace root")
    st_sync.add_argument("--json", action="store_true", help="Emit JSON output")

    st_equiv = staging_subs.add_parser("verify-equivalence", help="Verify equivalence between baseline and Parquet staging")
    st_equiv.add_argument("--workspace-root", type=str, default=None, help="Path to workspace root")
    st_equiv.add_argument("--json", action="store_true", help="Emit JSON output")

    st_manifest = staging_subs.add_parser("manifest", help="Emit and inspect atomic staging manifest")
    st_manifest.add_argument("--backend", type=str, default="parquet", choices=["baseline", "parquet"], help="Target backend")
    st_manifest.add_argument("--workspace-root", type=str, default=None, help="Path to workspace root")
    st_manifest.add_argument("--json", action="store_true", help="Emit JSON output")

    st_recover = staging_subs.add_parser("recover", help="Recover pending DSCP staging transactions and sweep orphans")
    st_recover.add_argument("--workspace-root", type=str, default=None, help="Path to workspace root")
    st_recover.add_argument("--json", action="store_true", help="Emit JSON output")

    return parser


def format_findings_text(findings: List[RegistryFinding]) -> str:
    """Format findings for human-readable terminal output."""
    lines = []
    errors = [f for f in findings if f.level == "ERROR"]
    warnings = [f for f in findings if f.level == "WARNING"]

    for f in findings:
        prefix = "❌ ERROR" if f.level == "ERROR" else "⚠️ WARNING"
        field_str = f" in [{f.field}]" if f.field else ""
        lines.append(f"{prefix} ({f.code}) {f.registry}{field_str}: {f.message}")
        if f.suggestion:
            lines.append(f"   Suggestion: {f.suggestion}")

    lines.append(f"\nSummary: {len(errors)} error(s), {len(warnings)} warning(s)")
    return "\n".join(lines)


def format_findings_json(findings: List[RegistryFinding], passed: bool) -> str:
    """Format findings as deterministic machine-readable JSON."""
    data: Dict[str, Any] = {
        "status": "passed" if passed else "failed",
        "errors": [
            {
                "code": f.code,
                "registry": f.registry,
                "field": f.field,
                "message": f.message,
                "suggestion": f.suggestion,
            }
            for f in findings
            if f.level == "ERROR"
        ],
        "warnings": [
            {
                "code": f.code,
                "registry": f.registry,
                "field": f.field,
                "message": f.message,
                "suggestion": f.suggestion,
            }
            for f in findings
            if f.level == "WARNING"
        ],
        "summary": {
            "errors": sum(1 for f in findings if f.level == "ERROR"),
            "warnings": sum(1 for f in findings if f.level == "WARNING"),
            "passed": passed,
        },
    }
    return json.dumps(data, indent=2, sort_keys=True)


def format_linter_findings_json(findings: List[Finding], passed: bool) -> str:
    """Format linter findings as deterministic machine-readable JSON."""
    data: Dict[str, Any] = {
        "status": "passed" if passed else "failed",
        "errors": [f.to_dict() for f in findings if f.level == "ERROR"],
        "warnings": [f.to_dict() for f in findings if f.level == "WARNING"],
        "summary": {
            "errors": sum(1 for f in findings if f.level == "ERROR"),
            "warnings": sum(1 for f in findings if f.level == "WARNING"),
            "passed": passed,
        },
    }
    return json.dumps(data, indent=2, sort_keys=True)


def handle_check_registries(args: argparse.Namespace) -> int:
    """Handle check-registries command execution."""
    reg_dir = args.registry_dir or "schemas/registry"
    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()

    try:
        loaded = load_registries(reg_dir)
    except FileNotFoundError as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return ExitCode.NOT_FOUND
    except RegistryLoadError as e:
        if args.json:
            print(
                json.dumps({"status": "error", "message": str(e), "registry": e.filename}, indent=2)
            )
        else:
            print(f"Registry load error ({e.filename}): {e.message}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR

    findings = validate_cross_registries(loaded, repo_root)
    errors = [f for f in findings if f.level == "ERROR"]
    passed = len(errors) == 0

    if args.json:
        print(format_findings_json(findings, passed))
    else:
        if passed:
            print("✓ All 10 YAML registries loaded and verified successfully.")
        else:
            print(format_findings_text(findings), file=sys.stderr)

    return ExitCode.SUCCESS if passed else ExitCode.VALIDATION_ERROR


def handle_lint(args: argparse.Namespace) -> int:
    """Handle lint command execution."""
    target_path = Path(args.path)
    if not target_path.exists():
        if args.json:
            print(
                json.dumps(
                    {"status": "error", "message": f"Path '{target_path}' not found"}, indent=2
                )
            )
        else:
            print(f"Error: Path '{target_path}' not found", file=sys.stderr)
        return ExitCode.NOT_FOUND

    reg_dir = args.registry_dir or "schemas/registry"
    try:
        registries = load_registries(reg_dir)
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}, indent=2))
        else:
            print(f"Error loading registries: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR

    ref_date: Optional[date] = None
    if args.now:
        try:
            ref_date = date.fromisoformat(args.now)
        except ValueError:
            print(f"Invalid date format for --now: {args.now}", file=sys.stderr)
            return ExitCode.CONFIG_OR_ARG_ERROR

    # Determine corpus root and target file
    if target_path.is_file():
        corpus_root = target_path.parent
        # Walk up to find nearest known root
        curr = target_path.parent
        while curr != curr.parent:
            if (
                (curr / "engineering").exists()
                or (curr / "personal").exists()
                or (curr / "pyproject.toml").exists()
            ):
                corpus_root = curr
                break
            curr = curr.parent
        target_file: Optional[Path] = target_path
    else:
        corpus_root = target_path
        target_file = None

    corpus = load_corpus(corpus_root, scope=args.scope)
    strict = args.strict or args.warnings_as_errors
    check_skills = not getattr(args, "no_check_skills", False)

    linter = Linter(
        registries=registries,
        reference_date=ref_date,
        strict=strict,
        check_skills=check_skills,
    )
    findings = linter.lint_corpus(corpus, target_file=target_file)

    errors = [f for f in findings if f.level == "ERROR"]
    warnings = [f for f in findings if f.level == "WARNING"]
    passed = len(errors) == 0 and (not strict or len(warnings) == 0)

    if args.json:
        print(format_linter_findings_json(findings, passed))
    else:
        for f in findings:
            prefix = "❌ ERROR" if f.level == "ERROR" else "⚠️ WARNING"
            loc = f" [{f.file}]" if f.file else ""
            field_str = f" in {f.field}" if f.field else ""
            print(f"{prefix} ({f.code}){loc}{field_str}: {f.message}")
            if f.suggestion:
                print(f"   Suggestion: {f.suggestion}")
        print(
            f"\nSummary: {len(errors)} error(s), {len(warnings)} warning(s) across {len(corpus)} object(s)"
        )
        if passed:
            print("✓ Lint passed successfully.")

    if len(errors) > 0:
        return ExitCode.VALIDATION_ERROR
    if len(warnings) > 0 and strict:
        return ExitCode.STRICT_WARNING
    return ExitCode.SUCCESS


def handle_validate(args: argparse.Namespace) -> int:
    """Handle validate command on a single file."""
    file_path = Path(args.file)
    if not file_path.exists():
        if args.json:
            print(
                json.dumps(
                    {"status": "error", "message": f"File '{file_path}' not found"}, indent=2
                )
            )
        else:
            print(f"Error: File '{file_path}' not found", file=sys.stderr)
        return ExitCode.NOT_FOUND

    # Delegate to handle_lint with target file
    args.path = str(file_path)
    args.scope = None
    args.warnings_as_errors = False
    args.no_check_skills = True
    return handle_lint(args)


def handle_rename(args: argparse.Namespace) -> int:
    """Handle rename command."""
    corpus_root = Path(args.corpus_root)
    if not corpus_root.exists():
        return ExitCode.NOT_FOUND

    try:
        res = rename_entity(
            corpus_root=corpus_root,
            old_id=args.old_id,
            new_id=args.new_id,
            dry_run=args.dry_run,
        )
    except KeyError as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return ExitCode.NOT_FOUND
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR

    if args.json:
        print(json.dumps(res.to_dict(), indent=2))
    else:
        prefix = "[DRY RUN] " if args.dry_run else ""
        print(f"{prefix}Renamed {args.old_id} -> {args.new_id}")
        if res.renamed_file:
            print(f"  Target file: {res.renamed_file}")
        print(f"  Updated referencing files: {len(res.updated_referencing_files)}")
    return ExitCode.SUCCESS


def handle_query(args: argparse.Namespace) -> int:
    """Handle query command returning an evidence bundle."""
    corpus_root = Path(args.corpus_root)
    if not corpus_root.exists():
        return ExitCode.NOT_FOUND

    reg_dir = args.registry_dir or "schemas/registry"
    registries = load_registries(reg_dir)
    corpus = load_corpus(corpus_root)

    vector_index = None
    embedder = None
    if getattr(args, "vector", False):
        from trashheap.vector import LocalOfflineProvider, VectorIndex

        embedder = LocalOfflineProvider()
        vector_index = VectorIndex()
        vector_index.build(corpus, embedder)

    retriever = HybridRetriever(
        corpus=corpus,
        registries=registries,
        vector_index=vector_index,
        embedder=embedder,
    )
    cli_params = {
        "scope": args.scope,
        "seed_top_k": args.seed_top_k,
        "max_depth": args.max_depth,
        "max_results": args.max_results,
        "min_confidence": args.min_confidence,
        "min_relevance": args.min_relevance,
        "include_drafts": getattr(args, "include_drafts", False),
        "include_deprecated": getattr(args, "include_deprecated", False),
        "include_body": getattr(args, "include_body", False),
        "enable_vector": getattr(args, "vector", False),
        "retrieval_mode": "graph_enhanced" if getattr(args, "graph_enhanced", False) else "canonical",
    }

    bundle = retriever.retrieve(query=args.prompt, cli_params=cli_params)
    print(json.dumps(bundle, indent=2))
    return ExitCode.SUCCESS


def handle_show(args: argparse.Namespace) -> int:
    """Handle show command displaying full Knowledge Object content."""
    target = args.target
    p = Path(target)
    if p.exists() and p.is_file():
        print(p.read_text(encoding="utf-8"))
        return ExitCode.SUCCESS

    corpus_root = Path(args.corpus_root)
    if not corpus_root.exists():
        print(f"Corpus root '{corpus_root}' not found", file=sys.stderr)
        return ExitCode.NOT_FOUND

    corpus = load_corpus(corpus_root)
    found = None
    for ko in corpus.objects:
        if ko.id == target or (ko.path and ko.path.stem == target):
            found = ko
            break

    if not found:
        print(f"Object '{target}' not found in corpus '{corpus_root}'", file=sys.stderr)
        return ExitCode.NOT_FOUND

    if found.path and found.path.exists():
        print(found.path.read_text(encoding="utf-8"))
    else:
        print(found.raw_body)
    return ExitCode.SUCCESS


def handle_rebuild(args: argparse.Namespace) -> int:
    """Handle rebuild command reconstructing index caches directly from Markdown notes."""
    corpus_root = Path(args.corpus_root)
    if not corpus_root.exists():
        return ExitCode.NOT_FOUND

    reg_dir = args.registry_dir or "schemas/registry"
    registries = load_registries(reg_dir)
    out_dir = Path(args.output_dir) if args.output_dir else None

    res = rebuild_indexes(
        corpus_root,
        registries,
        output_dir=out_dir,
        rebuild_vector=getattr(args, "vector", False),
    )
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"✓ Rebuilt projections for {res['rebuilt_objects']} objects in {res['output_dir']}")
        for art in res["artifacts"]:
            print(f"  - {art}")
    return ExitCode.SUCCESS


def handle_generate_skills(args: argparse.Namespace) -> int:
    """Handle generate-skills command and drift verification (E050)."""
    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()

    if getattr(args, "global_install", False):
        from trashheap.skills import generate_agent_skills_content

        global_path = Path.home() / ".agents" / "skills" / "trashheap" / "SKILL.md"
        global_path.parent.mkdir(parents=True, exist_ok=True)
        content = generate_agent_skills_content()
        global_path.write_text(content, encoding="utf-8")
        if args.json:
            print(json.dumps({"status": "passed", "path": str(global_path)}, indent=2))
        else:
            print(f"✓ Installed global Agent Skill to {global_path}")
        return ExitCode.SUCCESS

    if args.check:
        matches = check_agent_skills(repo_root)
        if not matches:
            finding = {
                "code": "E050",
                "field": ".agents/skills/trashheap/SKILL.md",
                "message": "Emitted .agents/skills/trashheap/SKILL.md diverges from code and schemas/registry (AGENT-SKILLS.md §7)",
                "suggestion": "Run 'trashheap generate-skills' to synchronize skill definition",
                "level": "ERROR",
            }
            if args.json:
                print(json.dumps({"status": "failed", "errors": [finding]}, indent=2))
            else:
                print(f"❌ ERROR (E050): {finding['message']}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR
        if args.json:
            print(json.dumps({"status": "passed", "message": "SKILL.md is up-to-date"}, indent=2))
        else:
            print("✓ .agents/skills/trashheap/SKILL.md is up-to-date.")
        return ExitCode.SUCCESS
    else:
        out_path = write_agent_skills(repo_root)
        if args.json:
            print(json.dumps({"status": "passed", "path": str(out_path)}, indent=2))
        else:
            print(f"✓ Emitted {out_path}")
        return ExitCode.SUCCESS


def handle_stage_lint(args: argparse.Namespace) -> int:
    """Handle stage-lint triage command."""
    staging_dir = Path(args.staging_dir)
    report = stage_lint(staging_dir)
    if args.json:
        print(json.dumps({"status": "passed", "report": report.to_dict()}, indent=2))
    else:
        print(f"Staging triage for '{staging_dir}': {report.total_count} Evidence Unit(s) staged.")
        if report.injections_count > 0:
            print(f"  ⚠ {report.injections_count} prompt injection indicator(s) detected.")
        for item in report.items:
            rel_str = (
                f" candidate relations: {item.candidate_relations}"
                if item.candidate_relations
                else ""
            )
            inj_str = (
                f" [INJECTIONS: {len(item.injections_detected)}]"
                if item.injections_detected
                else ""
            )
            print(
                f"  - {item.evidence_unit_ref} (suggested: {item.suggested_object_type}){rel_str}{inj_str}"
            )
    return ExitCode.SUCCESS


def handle_ingest(args: argparse.Namespace) -> int:
    """Handle ingest source intake command."""
    file_arg = args.file
    source_type = args.source_type
    ws_root = getattr(args, "workspace_root", None) or "."

    try:
        res = intake_source(
            source_input=file_arg,
            source_type=source_type,
            workspace_root=ws_root,
        )
        if args.json:
            print(json.dumps({"status": "staged", "result": res.to_dict()}, indent=2))
        else:
            noop_str = " (no-op: duplicate content)" if res.is_noop else ""
            injections_str = (
                f" [WARNING: {len(res.injections_detected)} prompt injection indicators detected]"
                if res.injections_detected
                else ""
            )
            print(
                f"✓ Ingested '{file_arg}' -> {res.source_id}/{res.representation_id}{noop_str}{injections_str}"
            )
            print(
                f"  Staged Evidence Unit: {res.evidence_unit.evidence_unit_ref} at {res.evidence_unit_path}"
            )
        return ExitCode.SUCCESS
    except FileNotFoundError as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return ExitCode.NOT_FOUND
    except AccessDeniedError as e:
        if args.json:
            print(
                json.dumps(
                    {"status": "error", "error_type": "AccessDeniedError", "message": str(e)},
                    indent=2,
                )
            )
        else:
            print(f"Security Error: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR
    except (SourceValidationError, QuarantineError, IntegrityConflictError) as e:
        if args.json:
            print(
                json.dumps(
                    {"status": "error", "error_type": type(e).__name__, "message": str(e)},
                    indent=2,
                )
            )
        else:
            print(f"Ingestion Error: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}, indent=2))
        else:
            print(f"Unexpected Ingestion Error: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR


def _execute_promote(candidate_id: str, ws_root: Path, as_json: bool) -> int:
    try:
        res = promote_candidate(candidate_id, ws_root)
        if as_json:
            print(json.dumps({"status": "promoted", "result": res.to_dict()}, indent=2))
        else:
            noop_str = " (no-op: already promoted)" if res.is_noop else ""
            print(f"✓ Promoted '{candidate_id}' -> {res.target_path}{noop_str}")
        return ExitCode.SUCCESS
    except ApprovalBindingError as e:
        if as_json:
            print(
                json.dumps(
                    {"status": "error", "error_type": "ApprovalBindingError", "message": str(e)},
                    indent=2,
                )
            )
        else:
            print(f"Approval Binding Error: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR
    except ValidationRollbackError as e:
        if as_json:
            print(
                json.dumps(
                    {"status": "error", "error_type": "ValidationRollbackError", "message": str(e)},
                    indent=2,
                )
            )
        else:
            print(f"Validation Rollback: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR
    except ConflictError as e:
        if as_json:
            print(
                json.dumps(
                    {"status": "error", "error_type": "ConflictError", "message": str(e)}, indent=2
                )
            )
        else:
            print(f"Conflict Error: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR
    except FileNotFoundError as e:
        if as_json:
            print(json.dumps({"status": "error", "message": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return ExitCode.NOT_FOUND
    except Exception as e:
        if as_json:
            print(
                json.dumps(
                    {"status": "error", "error_type": type(e).__name__, "message": str(e)}, indent=2
                )
            )
        else:
            print(f"Promotion Error: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR


def handle_review(args: argparse.Namespace) -> int:
    """Handle candidate proposal review operations (specs/REVIEW-PROMOTION.md)."""
    action = getattr(args, "review_action", None)
    ws_root = Path(getattr(args, "workspace_root", ".") or ".").resolve()

    if action == "list":
        candidates = list_candidates(ws_root, state_filter=args.status)
        if args.scope:
            candidates = [
                c for c in candidates if c.proposed_frontmatter.get("scope") == args.scope
            ]
        if args.json:
            print(json.dumps([c.model_dump() for c in candidates], indent=2))
        else:
            print(f"Candidates ({len(candidates)}):")
            for c in candidates:
                print(
                    f"  - {c.candidate_id} [{c.state}] rev:{c.proposal_revision} -> {c.target_path}"
                )
        return ExitCode.SUCCESS

    elif action == "show":
        try:
            c = load_candidate(args.candidate_id, ws_root)
            if args.json:
                print(json.dumps(c.model_dump(), indent=2))
            else:
                print(f"Candidate: {c.candidate_id} (rev {c.proposal_revision})")
                print(f"  State: {c.state} (materialization: {c.materialization_state})")
                print(f"  Target: {c.target_path}")
                print(f"  Hash: {c.proposal_hash}")
                if c.review_decision:
                    print(
                        f"  Decision: {c.review_decision.decision} by {c.review_decision.reviewer}"
                    )
            return ExitCode.SUCCESS
        except FileNotFoundError as e:
            if args.json:
                print(json.dumps({"status": "error", "message": str(e)}, indent=2))
            else:
                print(f"Error: {e}", file=sys.stderr)
            return ExitCode.NOT_FOUND

    elif action == "approve":
        try:
            c = approve_candidate(
                candidate_id=args.candidate_id,
                reviewer=args.reviewer,
                reason=args.reason or "Approved via review",
                workspace_root=ws_root,
            )
            if args.json:
                print(json.dumps({"status": "approved", "candidate": c.model_dump()}, indent=2))
            else:
                print(
                    f"✓ Approved candidate '{c.candidate_id}' (rev {c.proposal_revision}) by {args.reviewer}"
                )
            return ExitCode.SUCCESS
        except ApprovalBindingError as e:
            if args.json:
                print(
                    json.dumps(
                        {
                            "status": "error",
                            "error_type": "ApprovalBindingError",
                            "message": str(e),
                        },
                        indent=2,
                    )
                )
            else:
                print(f"Approval Error: {e}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR
        except Exception as e:
            if args.json:
                print(json.dumps({"status": "error", "message": str(e)}, indent=2))
            else:
                print(f"Error: {e}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR

    elif action == "reject":
        try:
            c = reject_candidate(
                candidate_id=args.candidate_id,
                reviewer=args.reviewer,
                reason=args.reason,
                workspace_root=ws_root,
            )
            if args.json:
                print(json.dumps({"status": "rejected", "candidate": c.model_dump()}, indent=2))
            else:
                print(f"✓ Rejected candidate '{c.candidate_id}' by {args.reviewer}")
            return ExitCode.SUCCESS
        except Exception as e:
            if args.json:
                print(json.dumps({"status": "error", "message": str(e)}, indent=2))
            else:
                print(f"Error: {e}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR

    elif action == "promote":
        return _execute_promote(args.candidate_id, ws_root, args.json)

    elif action == "recover":
        journal = get_journal(ws_root)
        recovered = journal.recover_crash(ws_root)
        if args.json:
            print(json.dumps({"status": "recovered", "log": recovered}, indent=2))
        else:
            print(f"Crash recovery executed: {len(recovered)} action(s) taken.")
            for entry in recovered:
                print(f"  - {entry}")
        return ExitCode.SUCCESS

    return ExitCode.CONFIG_OR_ARG_ERROR


def handle_promote(args: argparse.Namespace) -> int:
    """Handle promote command shortcut."""
    ws_root = Path(getattr(args, "workspace_root", ".") or ".").resolve()
    return _execute_promote(args.candidate_id, ws_root, args.json)


def handle_status(args: argparse.Namespace) -> int:
    """Handle status command displaying environment and knowledge debt."""
    ws_root = Path(getattr(args, "workspace_root", ".") or ".").resolve()
    ttl_days = getattr(args, "ttl_days", 180)

    env_report = inspect_environment(ws_root)
    debt_report = calculate_knowledge_debt(ws_root, ttl_days=ttl_days)

    corpus_arg = getattr(args, "corpus_root", None)
    if corpus_arg:
        corpus_dir = Path(corpus_arg).resolve()
    elif (ws_root / "fixtures" / "canonical").exists():
        corpus_dir = ws_root / "fixtures" / "canonical"
    elif (ws_root / "personal").exists() or (ws_root / "engineering").exists():
        corpus_dir = ws_root
    else:
        corpus_dir = None

    canonical_count = 0
    if corpus_dir and corpus_dir.exists():
        canonical_count = len([p for p in corpus_dir.glob("**/*.md") if p.is_file()])

    total_units = canonical_count + debt_report.pending_backlog_count
    debt_index = round(debt_report.pending_backlog_count / max(1, total_units), 3)
    health_label = (
        "Pristine"
        if debt_index == 0.0
        else ("Nominal" if debt_index < 0.1 else ("Attention Required" if debt_index < 0.3 else "Critical Backlog"))
    )

    if args.json:
        payload = {
            "status": "ok",
            "environment": env_report.to_dict(),
            "knowledge_debt": debt_report.to_dict(),
            "knowledge_health": {
                "canonical_objects": canonical_count,
                "pending_backlog": debt_report.pending_backlog_count,
                "quarantined_count": debt_report.quarantined_count,
                "knowledge_debt_index": debt_index,
                "health_status": health_label,
            },
        }
        print(json.dumps(payload, indent=2))
    else:
        print("=== Omniscient Trash Heap Health & Operations ===")
        print(f"OS: {env_report.os_system}")
        print(f"Durability Tier: {env_report.filesystem_tier}")
        print(f"Atomic Rename: {'✓' if env_report.atomic_rename_supported else '✗'} | Fsync Durability: {'✓' if env_report.fsync_durability_supported else '✗'}")
        print(
            f"Dependencies: SQLite={'✓' if env_report.sqlite_available else '✗'}, "
            f"DuckDB={'✓' if env_report.duckdb_available else '✗'}, "
            f"Git-LFS={'✓' if env_report.git_lfs_available else '✗'}"
        )
        print("\n--- Knowledge Health & Debt ---")
        corpus_label = f"({corpus_dir.relative_to(ws_root) if corpus_dir and corpus_dir.is_relative_to(ws_root) else corpus_dir})" if corpus_dir else "(none)"
        print(f"Canonical Objects:       {canonical_count} {corpus_label}")
        print(f"Pending Backlog:         {debt_report.pending_backlog_count} item(s)")
        print(f"Quarantined Items:       {debt_report.quarantined_count} item(s)")
        print(f"Oldest Item Age:         {debt_report.oldest_item_age_days:.1f} day(s)")
        print(f"Expiry Warning:          {'⚠️ YES' if debt_report.expiry_warning else '✓ No'}")
        print(f"Knowledge Debt Index:    {debt_index:.3f} ({health_label})")

    return ExitCode.SUCCESS


def handle_reap(args: argparse.Namespace) -> int:
    """Handle reap command executing retention pass."""
    ws_root = Path(getattr(args, "workspace_root", ".") or ".").resolve()
    ttl_days = getattr(args, "ttl_days", 180)
    grace_days = getattr(args, "grace_days", 7)

    reaper = TTLReaper(ws_root, ttl_days=ttl_days, grace_days=grace_days)
    result = reaper.run_reap_cycle()

    if args.json:
        print(json.dumps({"status": "reaped", "results": result}, indent=2))
    else:
        print(
            f"✓ Retention reap pass complete: {result['expired_count']} expired, {result['purged_count']} purged."
        )

    return ExitCode.SUCCESS


def handle_conformance(args: argparse.Namespace) -> int:
    """Handle conformance projection and drift check (D90, CONFORM-001)."""
    ws_root = Path(getattr(args, "workspace_root", ".") or ".").resolve()
    out_rel = getattr(args, "output", "artifacts/conformance_matrix.yaml")
    out_path = (ws_root / out_rel).resolve() if not Path(out_rel).is_absolute() else Path(out_rel)

    matrix = generate_conformance_matrix(ws_root, output_path=out_path)

    if getattr(args, "check", False):
        drift = detect_spec_drift(ws_root)
        if args.json:
            print(
                json.dumps(
                    {
                        "status": "checked",
                        "matrix_summary": matrix.summary,
                        "drift": drift.to_dict(),
                    },
                    indent=2,
                )
            )
        else:
            print("=== Conformance & Drift Check (D90) ===")
            print(f"Matrix summary: {matrix.summary}")
            print(f"Status: {'✓ PASSED' if drift.passed else '❌ FAILED'}")
            for f in drift.findings:
                icon = "❌" if f.level == "ERROR" else ("⚠️" if f.level == "WARNING" else "ℹ️")
                print(f"  {icon} [{f.level}] {f.target}: {f.message}")
        return ExitCode.SUCCESS if drift.passed else ExitCode.VALIDATION_ERROR

    if args.json:
        print(json.dumps({"status": "projected", "matrix": matrix.to_dict()}, indent=2))
    else:
        print(
            f"✓ Projected conformance matrix to {out_path.relative_to(ws_root) if out_path.is_relative_to(ws_root) else out_path}"
        )
        print(f"  Total invariant families: {matrix.summary['total_families']}")
        print(f"  Conformance tested: {matrix.summary['conformance_tested']}")
        print(f"  Implemented: {matrix.summary['implemented']}")
        print(f"  Unimplemented: {matrix.summary['unimplemented']}")

    return ExitCode.SUCCESS


def handle_benchmark(args: argparse.Namespace) -> int:
    """Handle performance baseline benchmark (SCALE-001) or PubMed benchmark."""
    if getattr(args, "pubmed", False):
        from trashheap.operations.pubmed_benchmark import PubmedBenchmarkHarness

        harness = PubmedBenchmarkHarness(
            pubmed_file=getattr(args, "pubmed_file", None),
            sample_size=getattr(args, "pubmed_sample", 50),
        )
        report = harness.run()
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print("=== PubMedQA Hybrid Retrieval & Refusal Benchmark (Plan 96) ===")
            print(f"Total Questions Evaluated: {report.total_questions}")
            print(f"Direct Top-1 Recall: {report.top_1_recall * 100:.1f}%")
            print(f"Top-5 Recall: {report.top_5_recall * 100:.1f}%")
            print(f"Top-10 Recall: {report.top_10_recall * 100:.1f}%")
            print(f"Conclusion Preservation Rate: {report.conclusion_preservation_rate * 100:.1f}%")
            print(f"Negative Control Refusal Rate: {report.negative_control_refusal_rate * 100:.1f}%")
            print(f"Fake Citations Stripped: {report.fake_citations_stripped}")
            print(f"Mean Query Latency: {report.mean_query_ms:.2f} ms ({report.queries_per_sec:.1f} q/s)")
            print(f"Corpus Materialization: {report.corpus_build_time_sec:.2f}s ({report.corpus_size} articles)")
        return ExitCode.SUCCESS

    ws_root = Path(getattr(args, "workspace_root", ".") or ".").resolve()
    fx_dir = Path(args.fixtures_dir).resolve() if getattr(args, "fixtures_dir", None) else None

    report = run_benchmark(ws_root, fixtures_dir=fx_dir)

    if args.json:
        print(json.dumps({"status": "ok", "benchmark": report.to_dict()}, indent=2))
    else:
        print("=== Performance Baseline Benchmark (SCALE-001) ===")
        print(
            f"Corpus: {report.corpus_document_count} docs, {report.total_bytes} bytes, {report.total_lines} lines"
        )
        print(
            f"Parsing: {report.parse_ms_per_doc:.2f} ms/doc ({report.parse_docs_per_sec:.1f} docs/sec)"
        )
        print(
            f"Linting: {report.lint_ms_per_doc:.2f} ms/doc (findings: {report.lint_finding_count})"
        )
        print(f"Retrieval Indexing: {report.retrieval_index_sec:.4f} sec")
        print(
            f"Retrieval Query Latency: mean={report.retrieval_mean_query_ms:.2f} ms "
            f"(min={report.retrieval_min_query_ms:.2f}, max={report.retrieval_max_query_ms:.2f})"
        )
        print(f"\nScale Transition Assessment: {report.scale_transition_assessment['status']}")
        print(f"Rationale: {report.scale_transition_assessment['rationale']}")

    return ExitCode.SUCCESS


def handle_bundle(args: argparse.Namespace) -> int:
    """Handle bundle export and import operations (specs/OKF-INTEROP.md §16–§17)."""
    action = getattr(args, "bundle_action", None)
    if action == "export":
        reg_dir = getattr(args, "registry_dir", None) or "schemas/registry"
        registries = load_registries(reg_dir)
        corpus = load_corpus(Path(args.corpus_root))
        out_dir = Path(args.output_dir)

        if args.selector:
            import yaml

            sel_data = yaml.safe_load(Path(args.selector).read_text(encoding="utf-8")) or {}
            selector = BundleSelector(
                bundle_id=sel_data.get("bundle_id", "BND-EXPORT"),
                title=sel_data.get("title", "Export Bundle"),
                scopes=sel_data.get("scopes", ["engineering"]),
                taxonomy_ids=sel_data.get("taxonomy_ids"),
                include_descendants=sel_data.get("include_descendants", True),
                object_types=sel_data.get("object_types"),
                domains=sel_data.get("domains"),
                facets=sel_data.get("facets"),
                statuses=sel_data.get("statuses"),
                min_confidence=float(sel_data.get("min_confidence", 0.0)),
                valid_at=sel_data.get("valid_at"),
                closure_relations=sel_data.get("closure_relations"),
                closure_max_depth=int(sel_data.get("closure_max_depth", 0)),
                allow_personal_scope=bool(sel_data.get("allow_personal_scope", False)),
                redact_scopes=sel_data.get("redact_scopes"),
                emit_index=bool(sel_data.get("emit_index", True)),
            )
        else:
            selector = BundleSelector(
                bundle_id=args.bundle_id or "BND-DEFAULT-001",
                title=args.title or "Default Knowledge Bundle",
                scopes=[args.scope] if args.scope else ["engineering"],
            )

        manifest = build_bundle(
            corpus=corpus,
            selector=selector,
            output_dir=out_dir,
            registries=registries,
        )

        if args.json:
            print(json.dumps(manifest.to_dict(), indent=2))
        else:
            print(
                f"✓ Materialized bundle '{manifest.bundle_id}' with {manifest.total_objects} objects in {out_dir}"
            )
            print(f"  Selector Hash: {manifest.selector_hash}")
            print(f"  Corpus Hash:   {manifest.corpus_hash}")
            if manifest.unresolved_references:
                print(f"  Unresolved References: {len(manifest.unresolved_references)}")
        return ExitCode.SUCCESS

    elif action == "import":
        bundle_dir = Path(args.bundle_dir)
        target_scope = getattr(args, "target_scope", "engineering")
        imported, findings = import_bundle(bundle_dir, target_scope=target_scope)

        if args.json:
            res = {
                "status": "ok",
                "imported_count": len(imported),
                "findings": findings,
            }
            print(json.dumps(res, indent=2))
        else:
            print(
                f"✓ Imported {len(imported)} concepts from {bundle_dir} (target scope: {target_scope})"
            )
            if findings:
                print(f"  Review findings ({len(findings)}):")
                for f in findings:
                    print(f"    - [{f['level']}] {f.get('file', '')}: {f['message']}")
        return ExitCode.SUCCESS

    return ExitCode.CONFIG_OR_ARG_ERROR


def handle_graph(args: argparse.Namespace) -> int:
    """Handle graph commands (manifest, analyze)."""
    action = args.graph_action
    ws_root = Path(args.workspace_root)
    corpus_root = (
        Path(args.corpus_root)
        if getattr(args, "corpus_root", None)
        else (ws_root / "fixtures" / "canonical")
    )
    if action == "manifest":
        out_dir = Path(args.output_dir)
        manifest, m_path = build_and_publish_manifest(ws_root, out_dir, corpus_dir=corpus_root)
        if args.json:
            print(json.dumps(manifest.to_dict(), indent=2))
        else:
            print(f"✓ Generated canonical manifest in {m_path}")
            print(f"  Corpus hash: {manifest.corpus_hash}")
        return ExitCode.SUCCESS
    elif action == "analyze":
        out_dir = Path(args.output_dir)
        corpus = load_corpus(corpus_root)
        analyzer = GraphAnalyzer(corpus, ws_root)
        metrics = analyzer.compute_node_metrics()
        derived_manifest, _ = build_and_publish_manifest(
            ws_root, out_dir.parent, corpus_dir=corpus_root
        )
        edges = analyzer.compute_derived_edges(derived_manifest.corpus_hash)

        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "node_metrics.jsonl", "w", encoding="utf-8") as f:
            for m in metrics.values():
                f.write(json.dumps(m.to_dict()) + "\n")
        with open(out_dir / "derived_edges.jsonl", "w", encoding="utf-8") as f:
            for e in edges:
                f.write(json.dumps(e.to_dict()) + "\n")

        if args.json:
            res = {
                "nodes_analyzed": len(metrics),
                "derived_edges": len(edges),
                "corpus_hash": derived_manifest.corpus_hash,
            }
            print(json.dumps(res, indent=2))
        else:
            print(f"✓ Analyzed graph topology for {len(metrics)} nodes in {out_dir}")
            print(f"  Derived edges: {len(edges)}")
        return ExitCode.SUCCESS
    return ExitCode.CONFIG_OR_ARG_ERROR


def handle_discover(args: argparse.Namespace) -> int:
    """Handle discovery commands (scan, list, review, promote, sweep)."""
    action = args.discover_action
    disc_dir = Path(args.discovery_dir)
    ws_root = Path(getattr(args, "workspace_root", "."))
    corpus_root = (
        Path(args.corpus_root)
        if getattr(args, "corpus_root", None)
        else (ws_root / "fixtures" / "canonical")
    )
    mgr = DiscoveryLifecycleManager(disc_dir, ws_root)

    if action == "scan":
        corpus = load_corpus(corpus_root)
        registries = load_registries(ws_root / "schemas" / "registry")
        engine = DiscoveryEngine(corpus, registries, ws_root)
        manifest, _ = build_and_publish_manifest(
            ws_root, disc_dir.parent / "derived", corpus_dir=corpus_root
        )
        candidates = engine.scan_all_candidates(manifest.corpus_hash)
        added = mgr.add_candidates(candidates)
        if args.json:
            res = {
                "scanned": len(candidates),
                "added_pending": added,
                "total_candidates": len(mgr.candidates),
            }
            print(json.dumps(res, indent=2))
        else:
            print(f"✓ Discovery scan complete: found {len(candidates)} candidates ({added} new pending)")
        return ExitCode.SUCCESS

    elif action == "list":
        status_filter = getattr(args, "status", None)
        items = list(mgr.candidates.values())
        if status_filter:
            items = [c for c in items if c.status == status_filter]
        items.sort(key=lambda c: c.candidate_id)
        if args.json:
            print(json.dumps([c.to_dict() for c in items], indent=2))
        else:
            print(f"Discovery candidates ({len(items)}):")
            for c in items:
                print(f"  [{c.status.upper()}] {c.candidate_id} ({c.candidate_type}, conf: {c.confidence})")
        return ExitCode.SUCCESS

    elif action == "review":
        try:
            cand = mgr.review_candidate(
                candidate_id=args.candidate_id,
                decision=args.decision,
                actor=args.actor,
                reason=args.reason,
            )
            if args.json:
                print(json.dumps(cand.to_dict(), indent=2))
            else:
                print(f"✓ Candidate '{cand.candidate_id}' set to '{cand.status}' by {args.actor}")
            return ExitCode.SUCCESS
        except KeyError as e:
            print(f"Error: {e}", file=sys.stderr)
            return ExitCode.NOT_FOUND

    elif action == "promote":
        try:
            corpus = load_corpus(corpus_root)
            registries = load_registries(ws_root / "schemas" / "registry")
            cand = mgr.validate_and_promote(
                candidate_id=args.candidate_id,
                actor=args.actor,
                corpus=corpus,
                registries=registries,
            )
            if args.json:
                print(json.dumps(cand.to_dict(), indent=2))
            else:
                print(f"✓ Candidate '{cand.candidate_id}' successfully promoted by {args.actor}")
            return ExitCode.SUCCESS
        except ValueError as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR
        except KeyError as e:
            print(f"Error: {e}", file=sys.stderr)
            return ExitCode.NOT_FOUND

    elif action == "sweep":
        count = mgr.sweep_expiry(current_dt_iso=args.current_date)
        if args.json:
            print(json.dumps({"expired_count": count}, indent=2))
        else:
            print(f"✓ Swept expired candidates: {count} archived as expired")
        return ExitCode.SUCCESS

    return ExitCode.CONFIG_OR_ARG_ERROR


def handle_structural(args: argparse.Namespace) -> int:
    """Handle structural graph commands (index, inspect, impact, bridge)."""
    action = args.structural_action
    repo_root = Path(getattr(args, "repo_root", "."))
    cache_dir = Path(args.cache_dir) if getattr(args, "cache_dir", None) else None

    if action == "index":
        indexer = StructuralGraphIndexer(repo_root=repo_root, cache_dir=cache_dir)
        manifest, coverage = indexer.index(
            source_revision=args.revision,
            incremental=args.incremental,
        )
        if args.json:
            print(
                json.dumps(
                    {
                        "manifest": manifest.model_dump(),
                        "coverage": coverage.model_dump(),
                    },
                    indent=2,
                )
            )
        else:
            print(
                f"✓ Indexed {coverage.indexed_files} files ({manifest.node_count} nodes, {manifest.edge_count} edges)"
            )
            print(f"  Revision: {manifest.revision}, aggregate hash: {manifest.aggregate_hash}")
        return ExitCode.SUCCESS

    elif action == "inspect":
        indexer = StructuralGraphIndexer(repo_root=repo_root, cache_dir=cache_dir)
        if not indexer.load_existing_index():
            print("Error: Structural index not found. Run 'trashheap structural index' first.", file=sys.stderr)
            return ExitCode.NOT_FOUND

        node = indexer.nodes.get(args.node_id)
        if not node:
            print(f"Error: Node '{args.node_id}' not found", file=sys.stderr)
            return ExitCode.NOT_FOUND

        if args.json:
            print(json.dumps(node.model_dump(), indent=2))
        else:
            print(f"Node: {node.node_id} ({node.node_type.value})")
            print(f"  Path: {node.path}, lines: {node.line_start}-{node.line_end}")
            print(f"  Revision: {node.source_revision}, hash: {node.content_hash}")
        return ExitCode.SUCCESS

    elif action == "impact":
        indexer = StructuralGraphIndexer(repo_root=repo_root, cache_dir=cache_dir)
        if not indexer.load_existing_index():
            print("Error: Structural index not found. Run 'trashheap structural index' first.", file=sys.stderr)
            return ExitCode.NOT_FOUND

        analyzer = StructuralGraphAnalyzer(indexer.nodes, indexer.edges)
        report = analyzer.compute_blast_radius(
            target_node_id=args.node_id,
            max_depth=args.max_depth,
            node_ceiling=args.node_ceiling,
        )
        if args.json:
            print(json.dumps(report.model_dump(), indent=2))
        else:
            print(f"Blast radius for '{report.target_node_id}':")
            print(f"  Affected nodes ({len(report.affected_nodes)}): {report.affected_nodes}")
            print(f"  Depth reached: {report.depth_reached} (max: {report.max_depth})")
            print(f"  Context budget: {report.context_budget_tokens} tokens")
        return ExitCode.SUCCESS

    elif action == "bridge":
        ws_root = Path(args.workspace_root)
        b_action = args.bridge_action
        engine = BridgeEngine(workspace_root=ws_root, cache_dir=cache_dir)
        engine.load_bridges()

        if b_action == "scan":
            indexer = StructuralGraphIndexer(repo_root=ws_root, cache_dir=cache_dir)
            indexer.load_existing_index()
            corpus = load_corpus(ws_root / "fixtures" / "canonical")
            bridges = engine.discover_bridges(corpus, indexer.nodes)
            if args.json:
                print(json.dumps([b.model_dump() for b in bridges], indent=2))
            else:
                print(f"✓ Discovered {len(bridges)} candidate bridge relations")
            return ExitCode.SUCCESS

        elif b_action == "list":
            bridges = list(engine.bridges.values())
            if args.status:
                bridges = [b for b in bridges if b.status == args.status]
            if args.json:
                print(json.dumps([b.model_dump() for b in bridges], indent=2))
            else:
                print(f"Bridge relations ({len(bridges)}):")
                for b in bridges:
                    print(
                        f"  [{b.status.upper()}] {b.knowledge_object_id} -> {b.structural_node_id} ({b.bridge_type})"
                    )
            return ExitCode.SUCCESS

        elif b_action == "review":
            if not args.bridge_id or not args.status:
                print("Error: --bridge-id and --status required for review", file=sys.stderr)
                return ExitCode.CONFIG_OR_ARG_ERROR
            updated = engine.review_bridge(args.bridge_id, args.status)
            if not updated:
                print(f"Error: Bridge '{args.bridge_id}' not found", file=sys.stderr)
                return ExitCode.NOT_FOUND
            if args.json:
                print(json.dumps(updated.model_dump(), indent=2))
            else:
                print(f"✓ Bridge '{updated.bridge_id}' updated to '{updated.status}'")
            return ExitCode.SUCCESS

    return ExitCode.CONFIG_OR_ARG_ERROR


def handle_migrate(args: argparse.Namespace) -> int:
    """Handle legacy corpus migration commands (plan, execute)."""
    from trashheap.migration import (
        ChangedSourceError,
        FrontmatterMode,
        MigrationEngine,
        MigrationMap,
        UnmanagedTargetError,
    )

    source_dir = Path(args.source_dir)
    target_dir = Path(args.target_dir)

    fm_mode = (
        FrontmatterMode.DERIVED
        if getattr(args, "derived_frontmatter", False)
        else FrontmatterMode.REQUIRED
    )
    migration_map = MigrationMap(
        frontmatter_mode=fm_mode,
        target_scope=getattr(args, "target_scope", None),
    )

    registry_dir = getattr(args, "registry_dir", "schemas/registry")
    registries = load_registries(registry_dir)
    engine = MigrationEngine(migration_map=migration_map, registries=registries)

    try:
        if args.migrate_action == "plan":
            manifest = engine.plan(source_dir=source_dir, target_dir=target_dir)
        elif args.migrate_action == "execute":
            manifest = engine.execute(
                source_dir=source_dir,
                target_dir=target_dir,
                force=getattr(args, "force", False),
            )
        else:
            return ExitCode.CONFIG_OR_ARG_ERROR

        if args.json:
            print(json.dumps(manifest.model_dump(), indent=2))
        else:
            print(f"✓ Migration {manifest.mode} completed successfully")
            print(f"  Source hash: {manifest.source_corpus_hash}")
            print(
                f"  Eligible files: {manifest.counts['eligible_files']}, Quarantined: {manifest.counts['quarantined_files']}"
            )
            if manifest.mode == "execute":
                print(f"  Target hash: {manifest.target_corpus_hash}")
        return ExitCode.SUCCESS

    except UnmanagedTargetError as e:
        print(f"Error: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR
    except ChangedSourceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return ExitCode.NOT_FOUND
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return ExitCode.VALIDATION_ERROR


def handle_staging(args: argparse.Namespace) -> int:
    """Handle opt-in staging operations (Plan 93)."""
    from trashheap.staging import (
        BackendType,
        check_parquet_dependencies,
        get_staging_backend,
        sync_baseline_to_parquet,
        verify_backend_equivalence,
    )

    ws_root = Path(args.workspace_root) if getattr(args, "workspace_root", None) else Path.cwd()

    if args.staging_action == "status":
        b_type = getattr(args, "backend", "parquet")
        if b_type == "parquet":
            avail = check_parquet_dependencies()
            if args.json:
                print(json.dumps(avail.model_dump(), indent=2))
            else:
                if avail.available:
                    print(f"✓ Parquet/DuckDB staging backend: {avail.status.value.upper()}")
                    print(f"  DuckDB: {avail.duckdb_version}, PyArrow: {avail.pyarrow_version}")
                else:
                    print(f"⚠️ Parquet/DuckDB staging backend: {avail.status.value.upper()}")
                    print(f"  Detail: {avail.error_detail}")
            return ExitCode.SUCCESS
        else:
            backend = get_staging_backend(BackendType.BASELINE, workspace_root=ws_root)
            status = backend.get_status()
            if args.json:
                print(json.dumps(status.model_dump(), indent=2))
            else:
                print(f"✓ Baseline staging backend: {status.status.value.upper()}")
            return ExitCode.SUCCESS

    elif args.staging_action == "sync":
        try:
            baseline = get_staging_backend(BackendType.BASELINE, workspace_root=ws_root)
            parquet = get_staging_backend(BackendType.PARQUET, workspace_root=ws_root)
            synced_count = sync_baseline_to_parquet(baseline, parquet)
            if args.json:
                print(json.dumps({"status": "synced", "synced_proposals": synced_count}, indent=2))
            else:
                print(f"✓ Synchronized {synced_count} proposal(s) from baseline to Parquet staging")
            return ExitCode.SUCCESS
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR

    elif args.staging_action == "verify-equivalence":
        try:
            baseline = get_staging_backend(BackendType.BASELINE, workspace_root=ws_root)
            parquet = get_staging_backend(BackendType.PARQUET, workspace_root=ws_root)
            report = verify_backend_equivalence(baseline, parquet)
            if args.json:
                print(json.dumps(report.model_dump(), indent=2))
            else:
                if report.is_equivalent:
                    print(f"✓ Staging backends equivalent ({report.baseline_count} baseline vs {report.parquet_count} parquet)")
                else:
                    print(f"❌ Staging backends not equivalent ({report.baseline_count} baseline vs {report.parquet_count} parquet)")
                    if report.missing_in_parquet:
                        print(f"  Missing in Parquet: {report.missing_in_parquet}")
                    if report.missing_in_baseline:
                        print(f"  Missing in Baseline: {report.missing_in_baseline}")
                    if report.diffs:
                        print(f"  Differences: {len(report.diffs)}")
            return ExitCode.SUCCESS if report.is_equivalent else ExitCode.VALIDATION_ERROR
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR

    elif args.staging_action == "manifest":
        try:
            b_type = getattr(args, "backend", "parquet")
            backend = get_staging_backend(b_type, workspace_root=ws_root)
            manifest = backend.emit_manifest()
            if args.json:
                print(json.dumps(manifest.model_dump(), indent=2))
            else:
                print(f"✓ Staging manifest emitted for backend '{manifest.backend}'")
                print(f"  Total proposals: {manifest.total_proposals}")
                for t_name, info in manifest.tables.items():
                    print(f"  - {t_name}: {info.row_count} row(s), {info.size_bytes} byte(s)")
            return ExitCode.SUCCESS
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR

    elif args.staging_action == "recover":
        try:
            backend = get_staging_backend(BackendType.PARQUET, workspace_root=ws_root)
            res = backend.recover_transactions()
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print("✓ Staging transaction recovery executed")
                print(f"  Committed: {res.get('committed', 0)}, Failed: {res.get('failed', 0)}")
            return ExitCode.SUCCESS
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR

def handle_init(args: argparse.Namespace) -> int:
    """Handle init / new subcommand."""
    from trashheap.init import init_wiki

    try:
        res = init_wiki(
            target_dir=args.target_dir,
            name=args.name,
            scope=args.scope,
            author=args.author,
            force=args.force,
        )
        if getattr(args, "json", False):
            print(json.dumps(res, indent=2))
        else:
            print(f"✓ Initialized new Knowledge Library '{res['name']}' at {res['path']}")
            print(
                f"  Created {len(res['created_files'])} file(s) and {len(res['created_directories'])} directory/ies"
            )
            print("\nNext steps:")
            print(f"  cd {args.target_dir}")
            print("  trashheap lint .")
            print('  trashheap query "welcome" --corpus-root .')
        return ExitCode.SUCCESS
    except Exception as e:
        if getattr(args, "json", False):
            print(json.dumps({"status": "error", "message": str(e)}, indent=2), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return ExitCode.CONFIG_OR_ARG_ERROR


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point returning integer exit code."""
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        parser.print_help()
        return ExitCode.SUCCESS

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else ExitCode.CONFIG_OR_ARG_ERROR

    handlers = {
        "init": handle_init,
        "new": handle_init,
        "check-registries": handle_check_registries,
        "lint": handle_lint,
        "validate": handle_validate,
        "rename": handle_rename,
        "query": handle_query,
        "show": handle_show,
        "rebuild": handle_rebuild,
        "generate-skills": handle_generate_skills,
        "stage-lint": handle_stage_lint,
        "ingest": handle_ingest,
        "review": handle_review,
        "promote": handle_promote,
        "status": handle_status,
        "reap": handle_reap,
        "conformance": handle_conformance,
        "benchmark": handle_benchmark,
        "bundle": handle_bundle,
        "graph": handle_graph,
        "discover": handle_discover,
        "structural": handle_structural,
        "migrate": handle_migrate,
        "staging": handle_staging,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return ExitCode.SUCCESS


if __name__ == "__main__":
    sys.exit(main())
