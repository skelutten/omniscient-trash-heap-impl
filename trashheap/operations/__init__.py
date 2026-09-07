"""Operational and lifecycle management components for The Omniscient Trash Heap (Plan 05)."""

from trashheap.operations.benchmark import BenchmarkReport, run_benchmark
from trashheap.operations.conformance import (
    ConformanceFamilyEntry,
    ConformanceMatrix,
    DriftFinding,
    DriftReport,
    detect_spec_drift,
    generate_conformance_matrix,
)
from trashheap.operations.connector import (
    BaseAdapter,
    BaseConnector,
    DirectoryConnector,
    DocumentAdapter,
    FileConnector,
    RawPayload,
    TrajectoryAdapter,
)
from trashheap.operations.cursor import CursorState, CursorStore
from trashheap.operations.environment import EnvironmentReport, inspect_environment
from trashheap.operations.reaper import KnowledgeDebtReport, TTLReaper, calculate_knowledge_debt

__all__ = [
    "BenchmarkReport",
    "run_benchmark",
    "ConformanceFamilyEntry",
    "ConformanceMatrix",
    "DriftFinding",
    "DriftReport",
    "detect_spec_drift",
    "generate_conformance_matrix",
    "BaseConnector",
    "FileConnector",
    "DirectoryConnector",
    "BaseAdapter",
    "DocumentAdapter",
    "TrajectoryAdapter",
    "RawPayload",
    "CursorState",
    "CursorStore",
    "EnvironmentReport",
    "inspect_environment",
    "KnowledgeDebtReport",
    "TTLReaper",
    "calculate_knowledge_debt",
]
