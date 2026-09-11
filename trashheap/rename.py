"""Atomic entity rename with corpus-wide backlink propagation (ID-006).

The rename executes in two phases:

1. **Plan** — compute every updated file content (target note, referencing
   notes, graph projection) fully in memory, including re-derivation of the
   taxonomy slug path so the renamed note satisfies TAX-002/E002.
2. **Apply** — write the planned contents atomically, tracking prior state;
   any failure mid-apply rolls back every already-written file (best-effort
   transactional propagation — a crash can no longer leave a half-renamed
   corpus without an explicit rollback attempt).
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from trashheap.constants import ID_PATTERN
from trashheap.corpus import load_corpus
from trashheap.fsutil import atomic_write_text

_SCOPE_BY_PREFIX = {"PERS": "personal", "ENG": "engineering"}


class RenameResult:
    def __init__(self, old_id: str, new_id: str):
        self.old_id = old_id
        self.new_id = new_id
        self.renamed_file: Optional[Path] = None
        self.updated_referencing_files: List[Path] = []
        self.graph_updated: bool = False
        self.graph_error: Optional[str] = None
        self.path_changed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "old_id": self.old_id,
            "new_id": self.new_id,
            "renamed_file": str(self.renamed_file) if self.renamed_file else None,
            "updated_referencing_files": [str(p) for p in self.updated_referencing_files],
            "graph_updated": self.graph_updated,
            "graph_error": self.graph_error,
            "path_changed": self.path_changed,
        }


def atomic_write(path: Path, content: str) -> None:
    """Write content to file atomically and durably (delegates to fsutil)."""
    atomic_write_text(path, content)


def _find_registry_dir(corpus_root: Path) -> Optional[Path]:
    """Locate schemas/registry at or above the corpus root (None when absent)."""
    current = corpus_root.resolve()
    for candidate in (current, *current.parents):
        reg_dir = candidate / "schemas" / "registry"
        if reg_dir.is_dir():
            return reg_dir
    return None


def _derive_target_path(
    corpus_root: Path, current_path: Path, fm: Dict[str, Any], new_id: str
) -> Path:
    """Re-derive the TAX-002 slug path for ``new_id``; fall back to the current dir.

    A rename that changes scope prefix or taxonomy MUST move the file to the
    directory implied by the registries, otherwise the renamed note immediately
    fails E002 on the next lint.
    """
    new_scope = _SCOPE_BY_PREFIX.get(new_id.split("-", 1)[0])
    taxonomy_id = fm.get("taxonomy_id")
    reg_dir = _find_registry_dir(corpus_root)
    if new_scope is None or not taxonomy_id or reg_dir is None:
        return current_path.with_name(f"{new_id}.md")
    try:
        from trashheap.registry.loader import load_registries
        from trashheap.slug import taxonomy_id_to_directory

        registries = load_registries(reg_dir)
        raw_tax_dict = {
            n.taxonomy_id: {"name": n.name, "parent_id": n.parent_id, "scope": n.scope}
            for n in registries.taxonomy_registry.taxonomy
        }
        expected_dir = taxonomy_id_to_directory(raw_tax_dict, new_scope, taxonomy_id)
        return corpus_root / f"{expected_dir}{new_id}.md"
    except Exception:
        return current_path.with_name(f"{new_id}.md")


def rename_entity(
    corpus_root: Path,
    old_id: str,
    new_id: str,
    dry_run: bool = False,
    graph_path: Optional[Path] = None,
) -> RenameResult:
    """Atomically rename an entity and propagate all backlinks across the corpus."""
    if not re.match(ID_PATTERN, new_id):
        raise ValueError(
            f"Invalid new_id '{new_id}': does not conform to ID_PATTERN ({ID_PATTERN})"
        )

    result = RenameResult(old_id=old_id, new_id=new_id)
    corpus = load_corpus(corpus_root)

    if corpus.get_by_id(new_id) is not None:
        raise FileExistsError(f"Entity with id '{new_id}' already exists in corpus")

    target_obj = corpus.get_by_id(old_id)
    if target_obj is None:
        raise KeyError(f"Entity with id '{old_id}' not found in corpus")

    # 1. Plan the target file update (id -> new_id, old_id -> aliases, slug path)
    with open(target_obj.path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        raise ValueError(
            f"File '{target_obj.path}' does not start with YAML frontmatter fence ('---')"
        )

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(
            f"File '{target_obj.path}' missing closing YAML frontmatter fence ('---')"
        )

    fm = yaml.safe_load(parts[1])
    if not isinstance(fm, dict):
        raise ValueError(f"File '{target_obj.path}' frontmatter is not a dictionary")

    fm["id"] = new_id

    aliases = fm.get("aliases") or []
    if not isinstance(aliases, list):
        aliases = []
    if old_id not in aliases:
        aliases.append(old_id)
    fm["aliases"] = aliases

    new_fm_str = yaml.dump(fm, sort_keys=False, allow_unicode=True)
    new_target_content = f"---\n{new_fm_str}---\n{parts[2]}"

    new_target_path = _derive_target_path(corpus_root, target_obj.path, fm, new_id)
    if new_target_path.exists() and new_target_path.resolve() != target_obj.path.resolve():
        raise FileExistsError(f"Target file '{new_target_path}' already exists on disk")

    result.renamed_file = new_target_path
    result.path_changed = new_target_path.resolve() != target_obj.path.resolve()

    # 2. Plan backlink propagation across all other files (incl. piped wikilinks)
    wikilink_pattern = re.compile(rf"\[\[\s*{re.escape(old_id)}(?:\s*\|\s*([^\]]*))?\s*\]\]")

    def _replace_link(m: re.Match) -> str:
        label = m.group(1)
        if label is not None:
            return f"[[{new_id}|{label}]]"
        return f"[[{new_id}]]"

    planned_writes: List[Tuple[Path, str]] = [(new_target_path, new_target_content)]
    referencing: List[Path] = []

    for ko in corpus.objects:
        if ko.id == old_id:
            continue

        with open(ko.path, "r", encoding="utf-8") as f:
            file_text = f.read()

        if not file_text.startswith("---"):
            continue

        file_parts = file_text.split("---", 2)
        if len(file_parts) < 3:
            continue

        curr_fm = yaml.safe_load(file_parts[1])
        if not isinstance(curr_fm, dict):
            continue
        curr_body = file_parts[2]
        file_changed = False

        relations = curr_fm.get("relations", [])
        if isinstance(relations, list):
            for r in relations:
                if isinstance(r, dict) and r.get("target") == old_id:
                    r["target"] = new_id
                    file_changed = True

        new_curr_body, count = wikilink_pattern.subn(_replace_link, curr_body)
        if count > 0:
            curr_body = new_curr_body
            file_changed = True

        if file_changed:
            referencing.append(ko.path)
            updated_fm_str = yaml.dump(curr_fm, sort_keys=False, allow_unicode=True)
            planned_writes.append((ko.path, f"---\n{updated_fm_str}---\n{curr_body}"))

    result.updated_referencing_files = referencing

    # 3. Plan graph.json update (failures surface in result.graph_error, never swallowed)
    planned_graph: Optional[Tuple[Path, str]] = None
    if graph_path and graph_path.exists():
        try:
            with open(graph_path, "r", encoding="utf-8") as f:
                graph_data = json.load(f)

            if "nodes" in graph_data:
                if isinstance(graph_data["nodes"], dict):
                    if old_id in graph_data["nodes"]:
                        node_val = graph_data["nodes"].pop(old_id)
                        if isinstance(node_val, dict) and "id" in node_val:
                            node_val["id"] = new_id
                        graph_data["nodes"][new_id] = node_val
                elif isinstance(graph_data["nodes"], list):
                    for node in graph_data["nodes"]:
                        if isinstance(node, dict) and node.get("id") == old_id:
                            node["id"] = new_id

            if "adjacency" in graph_data and isinstance(graph_data["adjacency"], dict):
                if old_id in graph_data["adjacency"]:
                    graph_data["adjacency"][new_id] = graph_data["adjacency"].pop(old_id)
                for _src, rels in graph_data["adjacency"].items():
                    if isinstance(rels, list):
                        for r in rels:
                            if isinstance(r, dict) and r.get("target") == old_id:
                                r["target"] = new_id

            if "edges" in graph_data and isinstance(graph_data["edges"], list):
                for edge in graph_data["edges"]:
                    if isinstance(edge, dict):
                        if edge.get("source") == old_id:
                            edge["source"] = new_id
                        if edge.get("target") == old_id:
                            edge["target"] = new_id

            planned_graph = (graph_path, json.dumps(graph_data, indent=2))
        except Exception as exc:
            result.graph_error = f"{type(exc).__name__}: {exc}"

    if dry_run:
        return result

    # 4. Apply phase: write everything with rollback tracking.
    applied: List[Tuple[Path, Optional[str]]] = []
    old_path_content: Optional[str] = None
    try:
        for path, new_content in planned_writes:
            original = path.read_text(encoding="utf-8") if path.exists() else None
            applied.append((path, original))
            atomic_write(path, new_content)

        if result.path_changed:
            old_path_content = content
            applied.append((target_obj.path, old_path_content))
            target_obj.path.unlink()

        if planned_graph is not None:
            g_path, g_content = planned_graph
            original = g_path.read_text(encoding="utf-8") if g_path.exists() else None
            applied.append((g_path, original))
            atomic_write(g_path, g_content)
            result.graph_updated = True
    except BaseException:
        for path, original in reversed(applied):
            try:
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write(path, original)
            except OSError:
                pass
        raise

    return result
