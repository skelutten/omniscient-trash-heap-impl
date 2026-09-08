"""Export pipeline for OKF concepts and Knowledge Bundles (specs/OKF-INTEROP.md §16–§17, D109).

Normative invariants enforced:
- OKF-001: Export to conformant OKF document
- OKF-002: Stable identity in trashheap.id; Concept ID is positional
- OKF-003: Preservation of provenance, lifecycle, validity, verification
- OKF-004: Namespaced frontmatter extensions (trashheap.*)
- OKF-005: OKF projection is derived, not canonical source of truth
- OKF-007 / OKF-011: Declared lossy mapping in manifest and frontmatter
- OKF-010 / BUNDLE-003: Deterministic byte-identical output
- BUNDLE-001: Computed selector membership
- BUNDLE-004: Bundle manifest with hashes, closure counts, lossy map
- BUNDLE-005: Bounded relation closure with separate tracking
- BUNDLE-006: Unresolved references listed in manifest (never dropped)
- BUNDLE-007: Cross-scope security defense (personal scope requires explicit policy)
- BUNDLE-009: Root index.md for progressive disclosure
"""

import hashlib
import json
import os
import shutil
import uuid
from collections import deque
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from trashheap.bundle.models import (
    BundleManifest,
    BundleSelector,
    CrossScopeSecurityError,
)
from trashheap.corpus import Corpus
from trashheap.models import KnowledgeObject
from trashheap.registry.loader import LoadedRegistries


def derive_okf_status(status: Optional[str]) -> str:
    """Map canonical 4-state status to OKF 3-state status (§16.4.2)."""
    if status == "established":
        return "stable"
    if status == "draft":
        return "draft"
    if status in ("deprecated", "archived"):
        return "deprecated"
    return "stable"


def derive_trust_tier(verification: Optional[str]) -> str:
    """Derive OKF trust tier from epistemic verification rank (OKF §5.3)."""
    if verification in ("formal_proof", "peer_verified"):
        return "human-reviewed"
    if verification == "self_verified":
        return "machine-confirmed"
    return "unverified"


def export_okf_concept(
    ko: KnowledgeObject,
    bundle_relative_path_map: Dict[str, str],
) -> str:
    """Render a canonical Knowledge Object as a conformant OKF concept document (§16.4)."""
    fm = ko.frontmatter_dict
    node_id = ko.id or ""

    # 1. OKF Core Fields (§16.4.2)
    okf_type = ko.object_type or "Concept"
    title = ko.title or node_id

    # Tags: domain + facets values + scope (sorted, deduplicated)
    tags_set: Set[str] = set()
    if ko.domain:
        tags_set.add(ko.domain)
    if ko.scope:
        tags_set.add(ko.scope)
    for f_key in ["toolchain", "prog_language", "language", "architecture"]:
        val = fm.get(f_key)
        if isinstance(val, list):
            for v in val:
                tags_set.add(str(v))
        elif isinstance(val, str):
            tags_set.add(val)
    tags = sorted(tags_set)

    okf_status = derive_okf_status(fm.get("status"))

    # Generated (author + last_modified)
    author = fm.get("author") or "unknown"
    last_mod = str(fm.get("last_modified") or date.today().isoformat())
    generated = {"by": author, "at": last_mod}

    # Verified (reviewer + last_verified)
    verified: Optional[Dict[str, str]] = None
    reviewer = fm.get("reviewer")
    last_ver = fm.get("last_verified")
    if reviewer or last_ver:
        ver_date = str(last_ver) if last_ver else last_mod
        ver_iso = f"{ver_date}T00:00:00Z" if "T" not in ver_date else ver_date
        verified = {"by": reviewer or "unknown", "at": ver_iso}

    # Stale_after (valid_until or next_review)
    stale_after: Optional[str] = None
    val_dict = fm.get("validity") or {}
    v_until = val_dict.get("valid_until")
    next_rev = fm.get("next_review")
    if v_until and next_rev:
        stale_after = str(min(str(v_until), str(next_rev)))
    elif v_until:
        stale_after = str(v_until)
    elif next_rev:
        stale_after = str(next_rev)

    # Sources
    sources_list: List[Dict[str, str]] = []
    source_refs = fm.get("source_refs", [])
    if isinstance(source_refs, list):
        for ref in source_refs:
            ref_str = str(ref)
            sources_list.append(
                {
                    "id": ref_str,
                    "resource": ref_str,
                    "title": f"Source {ref_str}",
                }
            )

    # 2. Namespaced trashheap.* Extension Fields (OKF-004, OKF-011)
    facets_dict: Dict[str, Any] = {}
    for f_key in [
        "toolchain",
        "prog_language",
        "language",
        "audience",
        "architecture",
        "lifecycle",
        "test_level",
    ]:
        if f_key in fm and fm[f_key] is not None:
            facets_dict[f_key] = fm[f_key]

    raw_rels = fm.get("relations", [])
    preserved_relations = []
    if isinstance(raw_rels, list):
        for r in raw_rels:
            if isinstance(r, dict) and "type" in r and "target" in r:
                preserved_relations.append({"type": r["type"], "target": r["target"]})

    trashheap_extension: Dict[str, Any] = {
        "id": node_id,  # Stable identity (OKF-002)
        "schema_version": "3.8.10",
        "taxonomy_id": fm.get("taxonomy_id"),
        "taxonomy_path": fm.get("taxonomy_path"),
        "domain": ko.domain,
        "status": fm.get("status"),  # Unreduced status (OKF-011)
        "facets": facets_dict,
        "epistemology": {
            "evidence": fm.get("evidence"),
            "verification": fm.get("verification"),
            "authority": fm.get("authority"),
            "consensus": fm.get("consensus"),
        },
        "provenance": {
            "confidence": fm.get("confidence"),
            "next_review": str(fm.get("next_review")) if fm.get("next_review") else None,
            "source_type": fm.get("source_type"),
        },
        "relations": preserved_relations,
    }

    # Assemble frontmatter in deterministic key order
    frontmatter_dict: Dict[str, Any] = {
        "type": okf_type,
        "title": title,
        "tags": tags,
        "status": okf_status,
        "generated": generated,
    }
    if verified:
        frontmatter_dict["verified"] = verified
    if stale_after:
        frontmatter_dict["stale_after"] = stale_after
    if sources_list:
        frontmatter_dict["sources"] = sources_list

    frontmatter_dict["trashheap"] = trashheap_extension

    # Convert body cross-links to bundle-relative form (/path/to/target.md)
    body = ko.raw_body
    for target_id, target_bundle_path in bundle_relative_path_map.items():
        # Replace Markdown link [text](target_id) or [[target_id]]
        body = body.replace(f"[[{target_id}]]", f"[[{target_bundle_path}]]")
        body = body.replace(f"({target_id})", f"({target_bundle_path})")

    # Serialize to YAML frontmatter + body
    fm_yaml = yaml.dump(frontmatter_dict, sort_keys=False, allow_unicode=True)
    return f"---\n{fm_yaml}---\n\n{body.lstrip()}"


def build_bundle(
    corpus: Corpus,
    selector: BundleSelector,
    output_dir: Path,
    registries: LoadedRegistries,
    exporter_version: str = "0.1.0",
    architecture_version: str = "3.8.10",
) -> BundleManifest:
    """Compute and materialize an idempotent Knowledge Bundle (BUNDLE-001..BUNDLE-009)."""
    _ = registries
    # 1. Selection: Evaluate Selector Over Corpus (BUNDLE-001)
    selected_ids: Set[str] = set()

    for ko in corpus.objects:
        if not ko.id:
            continue
        fm = ko.frontmatter_dict

        # Security check (BUNDLE-007): Cross-scope personal protection
        if ko.scope == "personal":
            if not selector.allow_personal_scope and "personal" not in (
                selector.redact_scopes or []
            ):
                # Personal scope inclusion requires explicit allowance or redaction policy
                if "personal" in selector.scopes:
                    raise CrossScopeSecurityError(
                        f"Attempted to include personal scope object '{ko.id}' without an explicit redaction policy (BUNDLE-007 / E207)"
                    )
                continue

        # Scopes filter
        if selector.scopes and ko.scope not in selector.scopes:
            continue

        # Taxonomy filter
        if selector.taxonomy_ids:
            ko_tax_id = fm.get("taxonomy_id") or ""
            matched_tax = False
            for target_tax in selector.taxonomy_ids:
                if ko_tax_id == target_tax:
                    matched_tax = True
                    break
                if selector.include_descendants and ko_tax_id.startswith(target_tax):
                    matched_tax = True
                    break
            if not matched_tax:
                continue

        # Object types filter
        if selector.object_types and ko.object_type not in selector.object_types:
            continue

        # Domains filter
        if selector.domains and ko.domain not in selector.domains:
            continue

        # Statuses filter
        if selector.statuses and fm.get("status") not in selector.statuses:
            continue

        # Confidence threshold
        conf = float(fm.get("confidence", 0.0))
        if conf < selector.min_confidence:
            continue

        # Temporal validity
        if selector.valid_at:
            try:
                val_date = date.fromisoformat(selector.valid_at)
                val_dict = fm.get("validity") or {}
                v_from = val_dict.get("valid_from")
                v_until = val_dict.get("valid_until")
                if v_from and val_date < date.fromisoformat(str(v_from)):
                    continue
                if v_until and val_date > date.fromisoformat(str(v_until)):
                    continue
            except ValueError:
                pass

        # Facets filter
        if selector.facets:
            facet_match = True
            for f_key, expected_vals in selector.facets.items():
                act_val = fm.get(f_key)
                if isinstance(act_val, list):
                    if not (set(act_val) & set(expected_vals)):
                        facet_match = False
                        break
                elif act_val not in expected_vals:
                    facet_match = False
                    break
            if not facet_match:
                continue

        selected_ids.add(ko.id)

    # 2. Relation Closure (BUNDLE-005)
    closure_ids: Set[str] = set()
    if selector.closure_relations and selector.closure_max_depth > 0:
        target_relations = set(selector.closure_relations)
        visited = set(selected_ids)
        queue: deque[Tuple[str, int]] = deque([(nid, 0) for nid in sorted(selected_ids)])

        corpus_by_id = {ko.id: ko for ko in corpus.objects if ko.id}

        while queue:
            curr_id, curr_depth = queue.popleft()
            if curr_depth >= selector.closure_max_depth:
                continue

            curr_ko = corpus_by_id.get(curr_id)
            if not curr_ko:
                continue

            rels = curr_ko.frontmatter_dict.get("relations", [])
            if isinstance(rels, list):
                for r in rels:
                    if isinstance(r, dict) and r.get("type") in target_relations:
                        tgt = r.get("target")
                        if tgt and tgt in corpus_by_id and tgt not in visited:
                            tgt_ko = corpus_by_id[tgt]
                            # Check personal scope boundary for closure
                            if tgt_ko.scope == "personal" and not selector.allow_personal_scope:
                                continue
                            visited.add(tgt)
                            closure_ids.add(tgt)
                            queue.append((tgt, curr_depth + 1))

    # Total member objects (selected + closure)
    all_member_ids = sorted(selected_ids | closure_ids)
    all_objects: List[KnowledgeObject] = [ko for ko in corpus.objects if ko.id in all_member_ids]
    all_objects.sort(key=lambda ko: ko.id or "")

    # 3. Path Mapping & Unresolved References (BUNDLE-006)
    # Compute relative path in bundle for each object
    bundle_relative_path_map: Dict[str, str] = {}
    obj_by_id: Dict[str, KnowledgeObject] = {}

    for ko in all_objects:
        assert ko.id is not None
        obj_by_id[ko.id] = ko
        # Map path relative to corpus root
        try:
            rel_p = ko.path.relative_to(corpus.root)
        except ValueError:
            rel_p = Path(ko.scope or "engineering") / f"{ko.id}.md"
        bundle_relative_path_map[ko.id] = f"/{rel_p.as_posix()}"

    # Identify unresolved references (external relations)
    unresolved_refs_list: List[Dict[str, str]] = []
    for ko in all_objects:
        rels = ko.frontmatter_dict.get("relations", [])
        if isinstance(rels, list):
            for r in rels:
                if isinstance(r, dict):
                    tgt = r.get("target")
                    rtype = r.get("type", "RELATED_TO")
                    if tgt and tgt not in obj_by_id:
                        unresolved_refs_list.append(
                            {
                                "from": ko.id,
                                "relation": rtype,
                                "target": tgt,
                            }
                        )

    # Sort unresolved references deterministically
    unresolved_refs_list.sort(key=lambda x: (x["from"], x["relation"], x["target"]))

    # 4. Compute Corpus and Selector Hashes
    h_corp = hashlib.sha256()
    for ko in sorted(corpus.objects, key=lambda x: x.id or ""):
        if ko.id:
            h_corp.update(ko.id.encode("utf-8"))
            h_corp.update(ko.raw_body.encode("utf-8"))
    corpus_hash = f"sha256:{h_corp.hexdigest()}"
    selector_hash = selector.compute_hash()

    # 5. Deterministic Materialization (BUNDLE-002, BUNDLE-003)
    tmp_output_dir = output_dir.parent / f".tmp_{output_dir.name}_{os.getpid()}"
    if tmp_output_dir.exists():
        shutil.rmtree(tmp_output_dir)
    tmp_output_dir.mkdir(parents=True, exist_ok=True)

    # Emit each OKF concept
    for ko in all_objects:
        assert ko.id is not None
        rel_target = bundle_relative_path_map[ko.id].lstrip("/")
        dest_file = tmp_output_dir / rel_target
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        content = export_okf_concept(ko, bundle_relative_path_map)
        dest_file.write_text(content, encoding="utf-8")

    # Emit root index.md (BUNDLE-009)
    if selector.emit_index:
        index_fm = {
            "type": "Index",
            "title": selector.title,
            "okf_version": "0.2",
            "description": f"Knowledge Bundle for {selector.title}",
            "trashheap": {
                "bundle_id": selector.bundle_id,
                "selector_hash": selector_hash,
                "corpus_hash": corpus_hash,
                "total_objects": len(all_objects),
            },
        }
        index_yaml = yaml.dump(index_fm, sort_keys=False, allow_unicode=True)

        lines = [
            f"---\n{index_yaml}---\n",
            f"# {selector.title}\n",
            f"Knowledge Bundle `{selector.bundle_id}` containing {len(all_objects)} concepts.\n",
            "## Concepts\n",
        ]
        for ko in all_objects:
            rel_link = bundle_relative_path_map[ko.id]
            lines.append(f"- [{ko.title or ko.id}]({rel_link}) (`{ko.object_type}`)")
        lines.append("")

        index_path = tmp_output_dir / "index.md"
        index_path.write_text("\n".join(lines), encoding="utf-8")

    # 6. Build and Write Manifest (BUNDLE-004, BUNDLE-008, OKF-007, OKF-011)
    gen_at = datetime.now(timezone.utc).isoformat()
    manifest = BundleManifest(
        bundle_id=selector.bundle_id,
        title=selector.title,
        selector_hash=selector_hash,
        corpus_hash=corpus_hash,
        generated_at=gen_at,
        generator="trashheap-bundle/0.1.0",
        exporter_version=exporter_version,
        architecture_version=architecture_version,
        target_directory=str(output_dir),
        object_ids=sorted(selected_ids),
        closure_object_ids=sorted(closure_ids),
        total_objects=len(all_objects),
        unresolved_references=unresolved_refs_list,
        lossy={
            "taxonomy": True,
            "relations": True,
            "epistemology": True,
            "status": True,
            "confidence": True,
        },
    )

    manifest_file = tmp_output_dir / "bundle_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest.to_dict(), f, indent=2, sort_keys=True)

    # Atomic swap into target directory. The previous bundle is renamed aside
    # and only deleted once the new bundle is published; any failure (including
    # KeyboardInterrupt) restores it so a crash never leaves no bundle at all.
    backup_dir = None
    if output_dir.exists():
        backup_dir = output_dir.with_name(f".{output_dir.name}.old.{uuid.uuid4().hex[:8]}")
        os.rename(output_dir, backup_dir)
    try:
        os.rename(tmp_output_dir, output_dir)
    except BaseException:
        if backup_dir and backup_dir.exists():
            os.rename(backup_dir, output_dir)
        raise
    if backup_dir and backup_dir.exists():
        shutil.rmtree(backup_dir, ignore_errors=True)

    return manifest
