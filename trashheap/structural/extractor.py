"""Deterministic AST Extractor for Structural Knowledge Graph (SG-004, SG-007, SG-008, SG-014, SG-020)."""

import ast
import hashlib
import sys
from typing import Any, Dict, List, Optional, Tuple

from trashheap.structural.models import (
    DerivationMetadata,
    StructuralEdge,
    StructuralEdgeType,
    StructuralNode,
    StructuralNodeType,
)


def compute_content_hash(content: bytes) -> str:
    """Compute normalized SHA-256 content hash (SG-007, SG-008)."""
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


class ASTExtractor:
    """Deterministic Python AST extractor conforming to SG-004 and SG-014."""

    PARSER_NAME = "python-ast"
    PARSER_VERSION = sys.version.split()[0]
    GRAMMAR_VERSION = f"Python {sys.version_info.major}.{sys.version_info.minor}"

    def __init__(self, repo_name: str = "canonical"):
        self.repo = repo_name

    def extract_file(
        self,
        rel_path: str,
        content_bytes: bytes,
        source_revision: str,
    ) -> Tuple[List[StructuralNode], List[StructuralEdge], List[Dict[str, str]], Optional[Dict[str, str]]]:
        """Extract nodes and edges from a single Python file.

        Returns:
            nodes: List of extracted StructuralNode
            edges: List of extracted StructuralEdge
            unresolved_refs: List of unresolved reference records (SG-015)
            failure: None if successful, or failure record dict if SyntaxError occurred (SG-020)
        """
        content_hash = compute_content_hash(content_bytes)
        try:
            source_text = content_bytes.decode("utf-8")
            tree = ast.parse(source_text, filename=rel_path)
        except (SyntaxError, UnicodeDecodeError) as e:
            # SG-020: Explicit degradation tracking on parse failure
            failure = {
                "path": rel_path,
                "error": str(e),
                "error_type": type(e).__name__,
            }
            return [], [], [], failure

        nodes: List[StructuralNode] = []
        edges: List[StructuralEdge] = []
        unresolved_refs: List[Dict[str, str]] = []

        derivation_proto = {
            "mode": "extracted",
            "extractor": self.PARSER_NAME,
            "extractor_version": self.PARSER_VERSION,
            "grammar_version": self.GRAMMAR_VERSION,
            "source_revision": source_revision,
            "source_file": rel_path,
        }

        # 1. FILE node
        file_node_id = f"repo={self.repo};path={rel_path}"
        file_node = StructuralNode(
            node_id=file_node_id,
            node_type=StructuralNodeType.FILE,
            repo=self.repo,
            path=rel_path,
            source_revision=source_revision,
            content_hash=content_hash,
            metadata={"size_bytes": len(content_bytes)},
        )
        nodes.append(file_node)

        # 2. MODULE node
        mod_name = rel_path
        if mod_name.endswith(".py"):
            mod_name = mod_name[:-3]
        module_path = mod_name.replace("/", ".").replace("\\", ".")
        module_node_id = f"repo={self.repo};module={module_path}"
        module_node = StructuralNode(
            node_id=module_node_id,
            node_type=StructuralNodeType.MODULE,
            repo=self.repo,
            path=rel_path,
            qualified_name=module_path,
            source_revision=source_revision,
            content_hash=content_hash,
        )
        nodes.append(module_node)

        # Edge: FILE DEFINES MODULE
        edges.append(
            StructuralEdge(
                edge_id=f"{file_node_id}#DEFINES#{module_node_id}",
                edge_type=StructuralEdgeType.DEFINES,
                source_id=file_node_id,
                target_id=module_node_id,
                source_revision=source_revision,
                derivation=DerivationMetadata(**derivation_proto),
            )
        )

        # Scope symbol tracker
        defined_symbols: Dict[str, str] = {}  # symbol_name -> node_id

        # AST visitor helper
        def visit_class(class_node: ast.ClassDef, parent_id: str, prefix: str):
            qname = f"{prefix}.{class_node.name}" if prefix else class_node.name
            class_id = f"repo={self.repo};path={rel_path};symbol={qname}"
            start_l = class_node.lineno
            end_l = getattr(class_node, "end_lineno", start_l)

            c_node = StructuralNode(
                node_id=class_id,
                node_type=StructuralNodeType.CLASS,
                repo=self.repo,
                path=rel_path,
                qualified_name=qname,
                line_start=start_l,
                line_end=end_l,
                source_revision=source_revision,
                content_hash=content_hash,
            )
            nodes.append(c_node)
            defined_symbols[class_node.name] = class_id

            # DEFINES edge
            edges.append(
                StructuralEdge(
                    edge_id=f"{parent_id}#DEFINES#{class_id}",
                    edge_type=StructuralEdgeType.DEFINES,
                    source_id=parent_id,
                    target_id=class_id,
                    source_revision=source_revision,
                    derivation=DerivationMetadata(**derivation_proto),
                )
            )

            # INHERITS edges
            for base in class_node.bases:
                if isinstance(base, ast.Name):
                    base_name = base.id
                    target_base_id = f"repo={self.repo};symbol={base_name}"
                    edges.append(
                        StructuralEdge(
                            edge_id=f"{class_id}#INHERITS#{target_base_id}",
                            edge_type=StructuralEdgeType.INHERITS,
                            source_id=class_id,
                            target_id=target_base_id,
                            source_revision=source_revision,
                            derivation=DerivationMetadata(**derivation_proto),
                        )
                    )

            # Visit class members
            for item in class_node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    visit_function(item, class_id, qname, is_method=True)
                elif isinstance(item, ast.ClassDef):
                    visit_class(item, class_id, qname)

        def visit_function(fn_node: Any, parent_id: str, prefix: str, is_method: bool = False):
            qname = f"{prefix}.{fn_node.name}" if prefix else fn_node.name
            fn_id = f"repo={self.repo};path={rel_path};symbol={qname}"
            start_l = fn_node.lineno
            end_l = getattr(fn_node, "end_lineno", start_l)
            arity = len(fn_node.args.args)

            is_test = fn_node.name.startswith("test_") or "test" in rel_path.lower()
            if is_test:
                node_type = StructuralNodeType.TEST
            elif is_method:
                node_type = StructuralNodeType.METHOD
            else:
                node_type = StructuralNodeType.FUNCTION

            f_node = StructuralNode(
                node_id=fn_id,
                node_type=node_type,
                repo=self.repo,
                path=rel_path,
                qualified_name=qname,
                line_start=start_l,
                line_end=end_l,
                source_revision=source_revision,
                content_hash=content_hash,
                metadata={"arity": arity},
            )
            nodes.append(f_node)
            defined_symbols[fn_node.name] = fn_id

            # DEFINES edge
            edges.append(
                StructuralEdge(
                    edge_id=f"{parent_id}#DEFINES#{fn_id}",
                    edge_type=StructuralEdgeType.DEFINES,
                    source_id=parent_id,
                    target_id=fn_id,
                    source_revision=source_revision,
                    derivation=DerivationMetadata(**derivation_proto),
                )
            )

            # If it's a test, check target tested symbol
            if node_type == StructuralNodeType.TEST and fn_node.name.startswith("test_"):
                target_sym = fn_node.name[5:]
                if target_sym:
                    target_test_id = f"repo={self.repo};symbol={target_sym}"
                    edges.append(
                        StructuralEdge(
                            edge_id=f"{fn_id}#TESTS_SYMBOL#{target_test_id}",
                            edge_type=StructuralEdgeType.TESTS_SYMBOL,
                            source_id=fn_id,
                            target_id=target_test_id,
                            source_revision=source_revision,
                            derivation=DerivationMetadata(**derivation_proto),
                        )
                    )

            # Analyze function calls inside body
            for subnode in ast.walk(fn_node):
                if isinstance(subnode, ast.Call):
                    if isinstance(subnode.func, ast.Name):
                        called = subnode.func.id
                        # Check if called symbol is local or external
                        target_call_id = defined_symbols.get(called, f"repo={self.repo};symbol={called}")
                        edges.append(
                            StructuralEdge(
                                edge_id=f"{fn_id}#CALLS#{target_call_id}",
                                edge_type=StructuralEdgeType.CALLS,
                                source_id=fn_id,
                                target_id=target_call_id,
                                source_revision=source_revision,
                                derivation=DerivationMetadata(**derivation_proto),
                            )
                        )

        # Top-level scan
        for item in tree.body:
            if isinstance(item, ast.ClassDef):
                visit_class(item, file_node_id, "")
            elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                visit_function(item, file_node_id, "", is_method=False)
            elif isinstance(item, ast.Import):
                for alias in item.names:
                    target_mod_id = f"repo={self.repo};module={alias.name}"
                    edges.append(
                        StructuralEdge(
                            edge_id=f"{file_node_id}#IMPORTS#{target_mod_id}",
                            edge_type=StructuralEdgeType.IMPORTS,
                            source_id=file_node_id,
                            target_id=target_mod_id,
                            source_revision=source_revision,
                            derivation=DerivationMetadata(**derivation_proto),
                        )
                    )
            elif isinstance(item, ast.ImportFrom):
                if item.module:
                    target_mod_id = f"repo={self.repo};module={item.module}"
                    edges.append(
                        StructuralEdge(
                            edge_id=f"{file_node_id}#IMPORTS#{target_mod_id}",
                            edge_type=StructuralEdgeType.IMPORTS,
                            source_id=file_node_id,
                            target_id=target_mod_id,
                            source_revision=source_revision,
                            derivation=DerivationMetadata(**derivation_proto),
                        )
                    )
            elif isinstance(item, ast.Assign):
                # Top-level constant/symbol
                for target in item.targets:
                    if isinstance(target, ast.Name) and (target.id.isupper() or target.id.startswith("__")):
                        sym_name = target.id
                        sym_id = f"repo={self.repo};path={rel_path};symbol={sym_name}"
                        nodes.append(
                            StructuralNode(
                                node_id=sym_id,
                                node_type=StructuralNodeType.SYMBOL,
                                repo=self.repo,
                                path=rel_path,
                                qualified_name=sym_name,
                                line_start=item.lineno,
                                line_end=getattr(item, "end_lineno", item.lineno),
                                source_revision=source_revision,
                                content_hash=content_hash,
                            )
                        )
                        edges.append(
                            StructuralEdge(
                                edge_id=f"{file_node_id}#DEFINES#{sym_id}",
                                edge_type=StructuralEdgeType.DEFINES,
                                source_id=file_node_id,
                                target_id=sym_id,
                                source_revision=source_revision,
                                derivation=DerivationMetadata(**derivation_proto),
                            )
                        )

        return nodes, edges, unresolved_refs, None
