"""One-read corpus loader with read-count tracking (02-DETERMINISTIC-CORE.md WP 2)."""

from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml
from pydantic import ValidationError

from trashheap.models import FrontmatterModel, KnowledgeObject


class Corpus:
    """In-memory collection of Knowledge Objects loaded from disk in a single read pass."""

    def __init__(self, root: Path):
        self.root = root
        self.objects: List[KnowledgeObject] = []
        self.objects_by_id: Dict[str, KnowledgeObject] = {}
        self.objects_by_path: Dict[Path, KnowledgeObject] = {}
        self.read_count: int = 0
        self.errors: List[tuple[Path, Exception]] = []

    def __len__(self) -> int:
        return len(self.objects)

    def get_by_id(self, node_id: str) -> Optional[KnowledgeObject]:
        return self.objects_by_id.get(node_id)

    def get_by_path(self, path: Path) -> Optional[KnowledgeObject]:
        return self.objects_by_path.get(path)


def load_single_file(file_path: Path) -> KnowledgeObject:
    """Read and parse a single Markdown file exactly once."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        err = ValueError(f"File missing starting YAML frontmatter fence ('---'): {file_path}")
        return KnowledgeObject(
            path=file_path,
            frontmatter_dict={},
            raw_body=content,
            frontmatter=None,
            load_error=err,
        )

    parts = content.split("---", 2)
    if len(parts) < 3:
        err = ValueError(f"File missing YAML frontmatter fence ('---'): {file_path}")
        return KnowledgeObject(
            path=file_path,
            frontmatter_dict={},
            raw_body=content,
            frontmatter=None,
            load_error=err,
        )

    fm_raw = parts[1]
    body = parts[2]

    try:
        fm_dict = yaml.safe_load(fm_raw)
        if not isinstance(fm_dict, dict):
            err = ValueError(f"Frontmatter is not a YAML dictionary: {file_path}")
            return KnowledgeObject(
                path=file_path,
                frontmatter_dict={},
                raw_body=body,
                frontmatter=None,
                load_error=err,
            )
    except yaml.YAMLError as e:
        return KnowledgeObject(
            path=file_path,
            frontmatter_dict={},
            raw_body=body,
            frontmatter=None,
            load_error=e,
        )

    # Attempt Pydantic model validation
    fm_model: Optional[FrontmatterModel] = None
    load_err: Optional[Exception] = None
    try:
        fm_model = FrontmatterModel.model_validate(fm_dict)
    except ValidationError as e:
        load_err = e

    return KnowledgeObject(
        path=file_path,
        frontmatter_dict=fm_dict,
        raw_body=body,
        frontmatter=fm_model,
        load_error=load_err,
    )


#: Repository-structure directories excluded only at the corpus root. A canonical
#: taxonomy directory deeper in the tree may legitimately carry one of these
#: names (e.g. ``personal/.../tools/``), so they MUST NOT be excluded at depth.
DEFAULT_EXCLUDED_TOP_DIRS = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    "schemas",
    "specs",
    "plans",
    "research",
    "prompts",
    "external-specs",
    "review-outputs",
    "input-artifacts",
    ".agents",
    "tools",
    "tests",
    "scripts",
    "examples",
}

#: Non-canonical storage, derived working directories (CANON-005) and generated
#: report directories. These are system-owned at any depth: a canonical
#: Knowledge Object MUST NOT live inside them, so they are excluded wherever
#: they appear in the path.
DEFAULT_EXCLUDED_ANY_DEPTH = {
    "raw",
    "staging",
    "artifacts",
    "derived",
    "discovery",
    ".cache",
    ".trashheap",
    "docs",
}

ROOT_FILE_SKIP_NAMES = {
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "CHANGELOG.md",
    "SECURITY.md",
    # Root instruction files are human/agent-owned scaffolding (DISC-009),
    # never canonical Knowledge Objects.
    "AGENTS.md",
    "CLAUDE.md",
}


def load_corpus(
    root: Path,
    scope: Optional[str] = None,
    exclude_dirs: Optional[Set[str]] = None,
) -> Corpus:
    """Scan and load the corpus in a single read pass.

    Reads each Markdown file exactly once, incrementing read_count. Symlinked
    files resolving outside the corpus root are skipped (containment policy,
    mirroring the ingest sandbox at the canonical read boundary).
    """
    corpus = Corpus(root=root)
    if exclude_dirs is None:
        excluded_top = DEFAULT_EXCLUDED_TOP_DIRS
        excluded_any = DEFAULT_EXCLUDED_ANY_DEPTH
    else:
        excluded_top = set(exclude_dirs)
        excluded_any = set()

    # Find candidate Markdown files
    candidate_paths: List[Path] = []
    if root.is_file():
        candidate_paths = [root]
    else:
        root_resolved = root.resolve()
        for p in root.rglob("*.md"):
            # Check exclusions
            rel = p.relative_to(root)
            if rel.parts and rel.parts[0] in excluded_top:
                continue
            if excluded_any and any(part in excluded_any for part in rel.parts[:-1]):
                continue
            if len(rel.parts) == 1 and rel.name in ROOT_FILE_SKIP_NAMES:
                continue
            if scope and not any(part == scope for part in rel.parts):
                continue
            if p.is_symlink():
                try:
                    resolved = p.resolve()
                except OSError:
                    continue
                if not resolved.is_relative_to(root_resolved):
                    continue
            candidate_paths.append(p)

    candidate_paths.sort()

    for p in candidate_paths:
        corpus.read_count += 1
        ko = load_single_file(p)
        corpus.objects.append(ko)
        corpus.objects_by_path[p] = ko
        if ko.id:
            # Note: duplicate IDs will be caught by Layer 5 / E001
            if ko.id not in corpus.objects_by_id:
                corpus.objects_by_id[ko.id] = ko

    return corpus
