import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from trashheap.corpus import load_corpus


class RenameResult:
    def __init__(self, old_id: str, new_id: str):
        self.old_id = old_id
        self.new_id = new_id
        self.renamed_file: Optional[Path] = None
        self.updated_referencing_files: List[Path] = []
        self.graph_updated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "old_id": self.old_id,
            "new_id": self.new_id,
            "renamed_file": str(self.renamed_file) if self.renamed_file else None,
            "updated_referencing_files": [str(p) for p in self.updated_referencing_files],
            "graph_updated": self.graph_updated,
        }


def atomic_write(path: Path, content: str) -> None:
    """Write content to file atomically using a temporary file and os.replace."""
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)


def rename_entity(
    corpus_root: Path,
    old_id: str,
    new_id: str,
    dry_run: bool = False,
    graph_path: Optional[Path] = None,
) -> RenameResult:
    """Atomically rename an entity and propagate all backlinks across the corpus."""
    result = RenameResult(old_id=old_id, new_id=new_id)
    corpus = load_corpus(corpus_root)

    target_obj = corpus.get_by_id(old_id)
    if target_obj is None:
        raise KeyError(f"Entity with id '{old_id}' not found in corpus")

    # 1. Update target object frontmatter (id -> new_id, add old_id to aliases)
    with open(target_obj.path, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1])
    fm["id"] = new_id

    aliases = fm.get("aliases", [])
    if old_id not in aliases:
        aliases.append(old_id)
    fm["aliases"] = aliases

    new_fm_str = yaml.dump(fm, sort_keys=False, allow_unicode=True)
    new_target_content = f"---\n{new_fm_str}---\n{parts[2]}"

    new_target_path = target_obj.path.with_name(f"{new_id}.md")
    result.renamed_file = new_target_path

    if not dry_run:
        # Write updated content to new path or existing path
        atomic_write(new_target_path, new_target_content)
        if new_target_path != target_obj.path:
            try:
                target_obj.path.unlink()
            except FileNotFoundError:
                pass

    # 2. Propagate backlinks across all other files
    wikilink_pattern = re.compile(rf"\[\[\s*{re.escape(old_id)}\s*\]\]")

    for ko in corpus.objects:
        if ko.id == old_id:
            continue

        file_changed = False
        with open(ko.path, "r", encoding="utf-8") as f:
            file_text = f.read()

        file_parts = file_text.split("---", 2)
        if len(file_parts) < 3:
            continue

        curr_fm = yaml.safe_load(file_parts[1])
        curr_body = file_parts[2]

        # Check relations
        relations = curr_fm.get("relations", [])
        if isinstance(relations, list):
            for r in relations:
                if isinstance(r, dict) and r.get("target") == old_id:
                    r["target"] = new_id
                    file_changed = True

        # Check wikilinks in body
        if wikilink_pattern.search(curr_body):
            curr_body = wikilink_pattern.sub(f"[[{new_id}]]", curr_body)
            file_changed = True

        if file_changed:
            result.updated_referencing_files.append(ko.path)
            if not dry_run:
                updated_fm_str = yaml.dump(curr_fm, sort_keys=False, allow_unicode=True)
                updated_content = f"---\n{updated_fm_str}---\n{curr_body}"
                atomic_write(ko.path, updated_content)

    # 3. Update graph.json if present
    if graph_path and graph_path.exists():
        try:
            with open(graph_path, "r", encoding="utf-8") as f:
                graph_data = json.load(f)

            # 1. Update nodes (dict or list)
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

            # 2. Update adjacency (dict)
            if "adjacency" in graph_data and isinstance(graph_data["adjacency"], dict):
                if old_id in graph_data["adjacency"]:
                    graph_data["adjacency"][new_id] = graph_data["adjacency"].pop(old_id)
                for _src, rels in graph_data["adjacency"].items():
                    if isinstance(rels, list):
                        for r in rels:
                            if isinstance(r, dict) and r.get("target") == old_id:
                                r["target"] = new_id

            # 3. Update edges (list)
            if "edges" in graph_data and isinstance(graph_data["edges"], list):
                for edge in graph_data["edges"]:
                    if isinstance(edge, dict):
                        if edge.get("source") == old_id:
                            edge["source"] = new_id
                        if edge.get("target") == old_id:
                            edge["target"] = new_id

            if not dry_run:
                atomic_write(graph_path, json.dumps(graph_data, indent=2))
            result.graph_updated = True
        except Exception:
            pass

    return result
