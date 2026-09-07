"""Scaffold and initialize a new Knowledge Library wiki instance (trashheap init / new)."""

import shutil
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from trashheap.constants import REGISTRY_FILES
from trashheap.skills import write_agent_skills

DEFAULT_TAXONOMY_DIRS = [
    "01_philosophy_science_logic",
    "02_formal_sciences_mathematics",
    "03_natural_science",
    "04_psychology_cognition",
    "05_society_economics_politics",
    "06_history_culture_humanities",
    "07_computer_science_ai_it_security",
    "08_technology_engineering",
    "09_strategy_management_leadership",
    "10_practical_knowledge_skills",
]

GITIGNORE_TEMPLATE = """# The Omniscient Trash Heap — Disposable Indexes & Caches
.trashheap/
*.db
*.db-shm
*.db-wal
*.parquet
*.idx
.staging_cache/
__pycache__/
*.pyc
.DS_Store
"""

WELCOME_NOTE_TEMPLATE = """---
id: PERS-DOC-WELCOME-0001
title: {title}
schema_version: 3.8.10
keywords:
- welcome
- trashheap
- personal-wiki
scope: personal
taxonomy_path: 07. Computer Science, AI & IT Security
taxonomy_id: TX-PERS-07
object_type: Document
domain: computer_science
language:
- en
evidence: observed
verification: self_verified
authority: canonical
consensus: accepted
source_type: internal_document
source_refs:
- SRC-INIT-WELCOME
author: {author}
last_modified: '{today}'
reviewer: {author}
last_verified: '{today}'
next_review: '{next_review}'
confidence: 1.0
status: established
validity:
  valid_from: '{today}'
  valid_until: null
relations: []
---

# {title}

Welcome to your new Knowledge Library, compiled and governed by **The Omniscient Trash Heap** (`trashheap`).

## Summary
Initial seed document for your personal knowledge repository.

## Notes
Add your verified knowledge, thoughts, and connections here. All canonical notes are plain Markdown with strict YAML frontmatter.
"""

README_TEMPLATE = """# {name}

> *Compiled with The Omniscient Trash Heap (`trashheap`)*

This is a deterministic, plain-text Knowledge Library.

## 📂 Layout
- `personal/`: Personal, organization-independent knowledge categorized by taxonomy.
- `engineering/`: Systems, platforms, and toolchains knowledge.
- `schemas/registry/`: Declarative YAML registries (object types, relations, taxonomy, governance).
- `staging/`: Intake pipeline (`raw/` capture and `discovery/` candidate proposals).
- `.agents/skills/trashheap/`: Agent Skills specification interface for AI assistants.

## 🚀 Common Commands
```bash
# Search the knowledge base
trashheap query "welcome" --corpus-root .

# Display full content of a note
trashheap show PERS-DOC-WELCOME-0001 --corpus-root .

# Validate and lint all notes
trashheap lint .

# Ingest new raw documents safely
trashheap ingest <path/to/source.md>

# Rebuild disposable indexes from Markdown
trashheap rebuild
```
"""


def find_source_registries() -> Path:
    """Locate the canonical source schemas/registry directory."""
    candidates = [
        Path("schemas/registry"),
        Path(__file__).resolve().parent / "schemas" / "registry",
        Path(__file__).resolve().parent.parent / "schemas" / "registry",
    ]
    for c in candidates:
        if c.is_dir() and (c / "object_registry.yaml").exists():
            return c
    raise FileNotFoundError("Could not locate canonical schemas/registry directory")


def init_wiki(
    target_dir: Union[str, Path] = ".",
    name: Optional[str] = None,
    scope: str = "all",
    author: str = "human:owner",
    force: bool = False,
) -> Dict[str, Any]:
    """Initialize and scaffold a new Knowledge Library instance."""
    target_path = Path(target_dir).resolve()
    wiki_name = name or target_path.name or "My Knowledge Library"
    today_dt = date.today()
    today = today_dt.isoformat()
    try:
        next_review = date(today_dt.year + 1, today_dt.month, today_dt.day).isoformat()
    except ValueError:
        next_review = date(today_dt.year + 1, today_dt.month, today_dt.day - 1).isoformat()

    created_files: List[str] = []
    created_dirs: List[str] = []

    if target_path.exists():
        if not target_path.is_dir():
            raise ValueError(f"Target path '{target_path}' is an existing file, not a directory")
        existing_items = [item for item in target_path.iterdir() if item.name != ".git"]
        if existing_items and not force:
            raise ValueError(
                f"Target directory '{target_path}' is not empty. Use --force to initialize anyway."
            )
    else:
        target_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(target_path))

    # 1. Schemas & Registries
    dest_registry = target_path / "schemas" / "registry"
    dest_registry.mkdir(parents=True, exist_ok=True)
    created_dirs.append(str(dest_registry))

    src_registry = find_source_registries()
    for reg_file in REGISTRY_FILES:
        src_fp = src_registry / reg_file
        if src_fp.exists():
            dest_fp = dest_registry / reg_file
            shutil.copy2(src_fp, dest_fp)
            created_files.append(str(dest_fp.relative_to(target_path)))

    # Copy structural_registry.yaml if available
    struct_reg = src_registry / "structural_registry.yaml"
    if struct_reg.exists():
        dest_struct = dest_registry / "structural_registry.yaml"
        shutil.copy2(struct_reg, dest_struct)
        created_files.append(str(dest_struct.relative_to(target_path)))

    # 2. Taxonomy directories for personal scope
    if scope in ("personal", "all"):
        personal_root = target_path / "personal"
        personal_root.mkdir(exist_ok=True)
        created_dirs.append("personal")
        for tdir in DEFAULT_TAXONOMY_DIRS:
            pdir = personal_root / tdir
            pdir.mkdir(exist_ok=True)
            created_dirs.append(f"personal/{tdir}")

    # 3. Engineering scope
    if scope in ("engineering", "all"):
        eng_dir = target_path / "engineering" / "01_domain_system_architecture"
        eng_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append("engineering/01_domain_system_architecture")

    # 4. Staging directories
    (target_path / "staging" / "raw").mkdir(parents=True, exist_ok=True)
    (target_path / "staging" / "discovery").mkdir(parents=True, exist_ok=True)
    created_dirs.extend(["staging/raw", "staging/discovery"])

    # 5. Agent Skills (.agents/skills/trashheap/SKILL.md)
    skills_file = write_agent_skills(repo_root=target_path)
    created_files.append(str(skills_file.relative_to(target_path)))

    # 6. .gitignore
    gitignore_path = target_path / ".gitignore"
    if not gitignore_path.exists() or force:
        gitignore_path.write_text(GITIGNORE_TEMPLATE, encoding="utf-8")
        created_files.append(".gitignore")

    # 7. Starter Welcome Note
    seed_note_dir = target_path / "personal" / "07_computer_science_ai_it_security"
    seed_note_dir.mkdir(parents=True, exist_ok=True)
    welcome_path = seed_note_dir / "PERS-DOC-WELCOME-0001.md"
    if not welcome_path.exists() or force:
        welcome_content = WELCOME_NOTE_TEMPLATE.format(
            title=f"Welcome to {wiki_name}",
            author=author,
            today=today,
            next_review=next_review,
        )
        welcome_path.write_text(welcome_content, encoding="utf-8")
        created_files.append(str(welcome_path.relative_to(target_path)))

    # 8. README.md
    readme_path = target_path / "README.md"
    if not readme_path.exists() or force:
        readme_content = README_TEMPLATE.format(name=wiki_name)
        readme_path.write_text(readme_content, encoding="utf-8")
        created_files.append("README.md")

    return {
        "status": "ok",
        "path": str(target_path),
        "name": wiki_name,
        "created_files": sorted(created_files),
        "created_directories": sorted(created_dirs),
    }
