"""Permissive importer for Google OKF v0.2 Knowledge Bundles (specs/OKF-INTEROP.md §16–§17, D109).

Normative invariants enforced:
- OKF-008: Import MUST NOT silently invent ontology, epistemology or governance semantics
- OKF-009: Unknown OKF / extension fields preserved where round-trip supported
- OKF-012: Importer MUST NOT reject bundle for unknown types, unknown keys, or broken links;
           surfaces them as review findings instead.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from trashheap.models import KnowledgeObject


def import_bundle(
    bundle_dir: Path,
    target_scope: str = "engineering",
) -> Tuple[List[KnowledgeObject], List[Dict[str, Any]]]:
    """Import an OKF v0.2 bundle into Knowledge Objects with permissive error tolerance (OKF-008, OKF-012).

    Returns (imported_objects, review_findings).
    """
    if not bundle_dir.exists() or not bundle_dir.is_dir():
        raise FileNotFoundError(f"Bundle directory does not exist: {bundle_dir}")

    imported_objects: List[KnowledgeObject] = []
    findings: List[Dict[str, Any]] = []

    # Check for index.md
    index_file = bundle_dir / "index.md"
    if not index_file.exists():
        findings.append(
            {
                "level": "INFO",
                "file": "index.md",
                "message": "Bundle root index.md is missing; permissible per OKF §11 / OKF-012",
            }
        )

    # Collect all markdown files in bundle
    md_files = sorted(list(bundle_dir.rglob("*.md")))

    # Track concept ids for cross-link checking
    bundle_concept_ids: set[str] = set()
    for mf in md_files:
        if mf.name in ("index.md", "log.md"):
            continue
        rel = mf.relative_to(bundle_dir).as_posix()
        bundle_concept_ids.add(rel[:-3] if rel.endswith(".md") else rel)
        bundle_concept_ids.add(f"/{rel}")

    for md_file in md_files:
        # Skip top-level index.md and log.md from being imported as canonical Knowledge Objects
        if md_file == index_file or md_file.name == "log.md":
            continue

        rel_path = md_file.relative_to(bundle_dir)
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            findings.append(
                {
                    "level": "ERROR",
                    "file": str(rel_path),
                    "message": f"Failed to read file: {e}",
                }
            )
            continue

        # Parse frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            findings.append(
                {
                    "level": "WARNING",
                    "file": str(rel_path),
                    "message": "Missing YAML frontmatter fence; treated as raw body concept",
                }
            )
            raw_body = content
            raw_fm = {}
        else:
            try:
                raw_fm = yaml.safe_load(parts[1]) or {}
            except Exception as e:
                findings.append(
                    {
                        "level": "WARNING",
                        "file": str(rel_path),
                        "message": f"Malformed YAML frontmatter: {e}",
                    }
                )
                raw_fm = {}
            raw_body = parts[2]

        # OKF-009: Preserve all unknown keys in frontmatter
        extra_keys = {
            k: v
            for k, v in raw_fm.items()
            if k
            not in (
                "type",
                "title",
                "tags",
                "status",
                "generated",
                "verified",
                "sources",
                "stale_after",
                "trashheap",
            )
        }
        if extra_keys:
            findings.append(
                {
                    "level": "INFO",
                    "file": str(rel_path),
                    "message": f"Unknown OKF frontmatter keys preserved (OKF-009): {list(extra_keys.keys())}",
                }
            )

        # Check if trashheap extension block is present
        th_ext = raw_fm.get("trashheap", {})
        if isinstance(th_ext, dict) and th_ext:
            # Reconstruct from full unreduced trashheap.* metadata
            node_id = th_ext.get("id") or rel_path.stem
            obj_type = raw_fm.get("type") or "Article"
            domain = th_ext.get("domain") or "software_engineering"
            taxonomy_id = th_ext.get("taxonomy_id")
            taxonomy_path = th_ext.get("taxonomy_path") or "01. Domain & Architecture"
            status = th_ext.get("status") or "draft"
            epistemology = th_ext.get("epistemology") or {}
            provenance = th_ext.get("provenance") or {}
            relations = th_ext.get("relations") or []
            facets = th_ext.get("facets") or {}

            fm_dict: Dict[str, Any] = {
                "id": node_id,
                "title": raw_fm.get("title") or node_id,
                "schema_version": th_ext.get("schema_version", "3.8.10"),
                "scope": target_scope,
                "taxonomy_path": taxonomy_path,
                "taxonomy_id": taxonomy_id,
                "object_type": obj_type,
                "domain": domain,
                "status": status,
                "evidence": epistemology.get("evidence", "derived"),
                "verification": epistemology.get("verification", "unverified"),
                "authority": epistemology.get("authority", "informative"),
                "consensus": epistemology.get("consensus", "accepted"),
                "confidence": provenance.get("confidence", 0.7),
                "source_type": provenance.get("source_type", "external"),
                "relations": relations,
                "author": raw_fm.get("generated", {}).get("by")
                if isinstance(raw_fm.get("generated"), dict)
                else "unknown",
                "last_modified": raw_fm.get("generated", {}).get("at")
                if isinstance(raw_fm.get("generated"), dict)
                else None,
            }
            # Add facets
            fm_dict.update(facets)
            # Add preserved extra keys
            fm_dict["_okf_extra_keys"] = extra_keys

        else:
            # OKF-008: Native OKF without trashheap extension MUST NOT silently invent semantics
            findings.append(
                {
                    "level": "INFO",
                    "file": str(rel_path),
                    "message": "Raw OKF concept imported without extension block; assigned conservative baseline epistemology (OKF-008)",
                }
            )
            node_id = rel_path.stem
            obj_type = raw_fm.get("type") or "Article"
            okf_status = raw_fm.get("status", "draft")
            status_map = {"stable": "established", "draft": "draft", "deprecated": "deprecated"}
            status = status_map.get(okf_status, "draft")

            sources = raw_fm.get("sources", [])
            source_refs = []
            if isinstance(sources, list):
                for s in sources:
                    if isinstance(s, dict) and "resource" in s:
                        source_refs.append(str(s["resource"]))
                    elif isinstance(s, str):
                        source_refs.append(s)

            gen = raw_fm.get("generated", {})
            author = gen.get("by", "unknown") if isinstance(gen, dict) else "unknown"
            last_mod = gen.get("at") if isinstance(gen, dict) else None

            fm_dict = {
                "id": node_id,
                "title": raw_fm.get("title") or node_id,
                "schema_version": "3.8.10",
                "scope": target_scope,
                "taxonomy_path": "01. Domain & Architecture",
                "taxonomy_id": "TX-GEN-01",
                "object_type": obj_type,
                "domain": "software_engineering",
                "status": status,
                "evidence": "derived",
                "verification": "unverified",
                "authority": "informative",
                "consensus": "accepted",
                "confidence": 0.5,
                "source_type": "external",
                "source_refs": source_refs,
                "author": author,
                "last_modified": str(last_mod) if last_mod else None,
                "relations": [],
                "_okf_extra_keys": extra_keys,
            }

        # Check for broken links (OKF-012: do not fail, surface as finding)
        import re

        links = re.findall(r"\[.*?\]\((.*?)\)", raw_body)
        for link in links:
            if link.endswith(".md") and not link.startswith("http"):
                clean_link = link.lstrip("/")
                if clean_link[:-3] not in bundle_concept_ids and link not in bundle_concept_ids:
                    findings.append(
                        {
                            "level": "WARNING",
                            "file": str(rel_path),
                            "message": f"Broken cross-link to '{link}' tolerated per OKF-012",
                        }
                    )

        ko = KnowledgeObject(
            path=md_file,
            frontmatter_dict=fm_dict,
            raw_body=raw_body,
        )
        imported_objects.append(ko)

    return imported_objects, findings
